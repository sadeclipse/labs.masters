import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# --- Источник: публичная метеостанция Uniontown на ThingSpeak ---
THINGSPEAK_CHANNEL = 3
THINGSPEAK_FIELD = 1
THINGSPEAK_URL = (
    f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL}"
    f"/fields/{THINGSPEAK_FIELD}.json"
)

# --- Получатель: ваш контроллер на open-monitoring.online ---
# cid и key берутся в разделе "Контроллер" -> "О контроллере".
# p1 = температура в °C, p2 = температура в °F.
OPENMON_URL = "http://open-monitoring.online/get"
OPENMON_CID = 5130
OPENMON_KEY = "AOcmsf"

DAYS = 3
# Бесплатный аккаунт OpenMonitoring принимает не чаще одного пакета в 60 секунд.
SEND_INTERVAL = 65


class RateLimitError(Exception):
    """Сервер отклонил запрос из-за ограничения частоты записи."""


SCRIPT_DIR = Path(__file__).resolve().parent
FALLBACK_FILE = SCRIPT_DIR / "uniontown_3d.json"

# На этой машине системный прокси 127.0.0.1:10808 не работает,
# поэтому ходим напрямую, игнорируя настройки прокси из системы.
SESSION = requests.Session()
SESSION.trust_env = False


def fetch_history(days=DAYS):
    """Читает историю температуры за N дней из публичного канала ThingSpeak."""
    print(f"Запрос истории за {days} дн. из ThingSpeak (канал {THINGSPEAK_CHANNEL})...")
    response = SESSION.get(THINGSPEAK_URL, params={"days": days}, timeout=20)
    response.raise_for_status()
    data = response.json()
    return parse_feeds(data.get("feeds", []))


def load_history(path):
    """Читает заранее сохранённый JSON-снимок ответа ThingSpeak."""
    print(f"Читаю локальный снимок: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    feeds = data.get("feeds", data if isinstance(data, list) else [])
    return parse_feeds(feeds)


def parse_feeds(feeds):
    """Преобразует записи ThingSpeak (°F) в точки с °C и временем измерения."""
    points = []
    for item in feeds:
        raw = item.get("field1")
        if raw is None or raw == "":
            continue
        try:
            degrees_f = float(raw)
        except (TypeError, ValueError):
            continue

        measured_at = None
        created = item.get("created_at")
        if created:
            try:
                measured_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except ValueError:
                measured_at = None

        points.append(
            {
                "time": measured_at,
                "f": degrees_f,
                "c": (degrees_f - 32) / 1.8,
            }
        )

    points.sort(key=lambda p: p["time"] or datetime.min.replace(tzinfo=timezone.utc))
    return dedupe(points)


def dedupe(points, window_minutes=15):
    """Убирает дубли: одинаковое значение, пришедшее почти в одно время."""
    result = []
    for point in points:
        if result:
            prev = result[-1]
            same_value = abs(prev["f"] - point["f"]) < 1e-9
            if same_value and point["time"] and prev["time"]:
                gap = point["time"] - prev["time"]
                if timedelta(0) <= gap < timedelta(minutes=window_minutes):
                    continue
        result.append(point)
    return result


def send_point(point):
    """Отправляет одну точку в OpenMonitoring: p1 = °C, p2 = °F."""
    payload = {
        "cid": OPENMON_CID,
        "key": OPENMON_KEY,
        "p1": round(point["c"], 2),
        "p2": round(point["f"], 2),
    }
    response = SESSION.get(OPENMON_URL, params=payload, timeout=15)
    response.raise_for_status()
    answer = response.text.strip()
    if "Превышена частота" in answer:
        raise RateLimitError(answer)
    return answer


def send_with_retry(point, attempts=3):
    """Повторяет отправку, если сервер ограничил частоту записи."""
    for attempt in range(1, attempts + 1):
        try:
            return send_point(point)
        except RateLimitError:
            if attempt == attempts:
                raise
            print(f"    лимит сервера, жду {SEND_INTERVAL:.0f} с и повторяю...")
            time.sleep(SEND_INTERVAL)


def main():
    parser = argparse.ArgumentParser(
        description="Перенос истории температуры Uniontown (°F) в OpenMonitoring (°C/°F)."
    )
    parser.add_argument("--days", type=int, default=DAYS, help="глубина истории в днях")
    parser.add_argument(
        "--interval",
        type=float,
        default=SEND_INTERVAL,
        help="пауза между отправками, секунд (не меньше 60)",
    )
    parser.add_argument(
        "--from-file",
        default=None,
        help="взять данные из локального JSON вместо ThingSpeak",
    )
    parser.add_argument(
        "--once", action="store_true", help="отправить только последнюю точку"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="отправить только последние N точек"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="показать точки без отправки"
    )
    args = parser.parse_args()

    if args.from_file:
        points = load_history(args.from_file)
    else:
        try:
            points = fetch_history(args.days)
        except Exception as exc:
            print(f"Не удалось получить данные ThingSpeak: {exc}")
            if FALLBACK_FILE.exists():
                points = load_history(FALLBACK_FILE)
            else:
                print(
                    "Локального снимка нет. Сохраните ответ ThingSpeak в "
                    "uniontown_3d.json или укажите --from-file."
                )
                return

    if not points:
        print("Не найдено ни одной корректной точки.")
        return

    if args.once:
        points = points[-1:]
    elif args.limit:
        points = points[-args.limit :]

    print(f"Точек к отправке: {len(points)}")
    if not args.dry_run and len(points) > 1:
        total_minutes = (len(points) - 1) * args.interval / 60
        print(
            f"Интервал {args.interval:.0f} с, заливка займёт ~{total_minutes:.0f} мин."
        )
        print(
            "Ось X в OpenMonitoring — время приёма сервером, "
            "а не исходное время станции."
        )

    sent = 0
    for index, point in enumerate(points, start=1):
        if point["time"]:
            when = point["time"].astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        else:
            when = "время неизвестно"
        line = (
            f"[{index}/{len(points)}] {when}: "
            f"{point['f']:.1f} °F = {point['c']:.2f} °C"
        )

        if args.dry_run:
            print(line + " (dry-run)")
            continue

        try:
            answer = send_with_retry(point)
            sent += 1
            print(line + (f" -> {answer}" if answer else " -> OK"))
        except RateLimitError:
            print(line + " -> ОШИБКА: лимит частоты так и не снялся")
        except Exception as exc:
            print(line + f" -> ОШИБКА: {exc}")

        if index < len(points):
            time.sleep(args.interval)

    print(f"\nГотово. Отправлено точек: {sent}/{len(points)}.")
    if not args.dry_run:
        print("Проверьте графики контроллера на open-monitoring.online.")


if __name__ == "__main__":
    main()
