import os
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
EXE = Path(os.environ.get(
    "ES_EXE",
    r"C:\Users\user\AppData\Local\Temp\opencode\vp3build\ES_COMPUTER.exe",
))

QUESTIONS = [
    "Компьютер включается (есть реакция на кнопку питания)?",
    "Вращается вентилятор блока питания или процессора?",
    "Есть изображение на мониторе?",
    "Слышны звуковые сигналы BIOS?",
    "Начинается загрузка операционной системы?",
    "Компьютер перегревается или выключается через некоторое время?",
]

SCENARIOS = {
    "bad_gpu": ("y", "y", "n", "n", "n", "n"),
    "bad_outlet": ("n", "n", "n", "n", "n", "n"),
    "bad_power_button": ("n", "y", "n", "n", "n", "n"),
    "no_cause": ("y", "y", "y", "n", "y", "n"),
}


def run(exe: Path, answers):
    inp = "".join(a + "\n" for a in answers).encode()
    p = subprocess.run([str(exe)], input=inp, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    return p.stdout.decode("cp1251", errors="replace")


def transcript(out: str, answers):
    marker = "--- Прямой вывод ---"
    body = out.split(marker, 1)[1].lstrip("\r\n")
    lines = [
        "Экспертная система: причины неработоспособности компьютера",
        "Вариант 4: прямая цепочка рассуждений",
        "Отвечайте y (да) или n (нет).",
        "",
    ]
    for q, a in zip(QUESTIONS, answers):
        lines.extend(textwrap.wrap(f"{q} (y/n): {a}", width=92,
                                   subsequent_indent="    "))
    lines.append("")
    lines.append(marker)
    for line in body.replace("\r", "").split("\n"):
        if not line:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(line, width=92,
                                   subsequent_indent="    "))
    while lines and not lines[-1]:
        lines.pop()
    return lines


def render(lines, title: str, path: Path):
    font_path = Path(r"C:\Windows\Fonts\consola.ttf")
    bold_path = Path(r"C:\Windows\Fonts\consolab.ttf")
    font = ImageFont.truetype(str(font_path), 18)
    bold = ImageFont.truetype(str(bold_path), 18)

    line_h = 24
    width = 1180
    top = 46
    height = top + 24 + len(lines) * line_h + 24
    img = Image.new("RGB", (width, height), "#0C0C0C")
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, width, top], fill="#2D2D2D")
    d.text((18, 11), title, font=font, fill="#F0F0F0")
    d.ellipse([width - 86, 16, width - 72, 30], fill="#E5C07B")
    d.ellipse([width - 60, 16, width - 46, 30], fill="#98C379")
    d.ellipse([width - 34, 16, width - 20, 30], fill="#E06C75")

    y = top + 18
    for line in lines:
        color = "#D4D4D4"
        f = font
        if line.startswith("---"):
            color = "#DCDCAA"
            f = bold
        elif line.startswith("  Сработало"):
            color = "#9CDCFE"
        elif line.startswith("Найденные причины") or line.startswith(" - "):
            color = "#B5CEA8"
        elif line.startswith("Причина не определена"):
            color = "#E5C07B"
        elif line.startswith("Экспертная система"):
            color = "#4FC1FF"
            f = bold
        elif line.startswith("Вариант 4"):
            color = "#4FC1FF"
        d.text((20, y), line, font=f, fill=color)
        y += line_h

    img.save(path)
    print("saved", path, img.size)


def main():
    if not EXE.exists():
        raise SystemExit(f"EXE not found: {EXE}")
    for name, answers in SCENARIOS.items():
        out = run(EXE, answers)
        lines = transcript(out, answers)
        render(lines, "ES_COMPUTER.exe — Text mode", FIG / f"result_{name}.png")


if __name__ == "__main__":
    main()
