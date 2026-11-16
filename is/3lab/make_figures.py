from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"


def box(ax, x, y, w, h, text, fc, ec="#333333", fs=11, bold=False):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.2, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#111111", wrap=True)


def arrow(ax, x1, y1, x2, y2, text="", color="#444444", rad=0.0):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=14, linewidth=1.3,
        color=color, connectionstyle=f"arc3,rad={rad}",
        shrinkA=0, shrinkB=0,
    ))
    if text:
        dx, dy = x2 - x1, y2 - y1
        if abs(dx) < 1e-9:
            sign = 1 if dy < 0 else -1
            ax.text(x1 + 0.16 * sign, (y1 + y2) / 2, text,
                    ha="left" if sign > 0 else "right", va="center",
                    fontsize=9, color=color)
        elif abs(dy) < 1e-9:
            sign = 1 if dx > 0 else -1
            ax.text((x1 + x2) / 2, y1 + 0.16 * sign, text,
                    ha="center", va="bottom" if sign > 0 else "top",
                    fontsize=9, color=color)
        else:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text,
                    ha="center", va="bottom", fontsize=9, color=color)


def architecture():
    fig, ax = plt.subplots(figsize=(12, 6.4), dpi=180)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.4)
    ax.axis("off")

    box(ax, 2.0, 5.35, 2.8, 0.85, """Пользователь
(ответы y / n)""", "#E8F1FB", fs=12, bold=True)
    box(ax, 2.0, 3.45, 2.8, 1.05, """Рабочая память
known(Ответ, Факт, Глубина)""", "#E8F8EE", fs=11, bold=True)
    box(ax, 8.6, 5.35, 2.8, 0.85, """База правил
rule(Заключение, +Условия, −Условия)""", "#FFF4DE", fs=10.5, bold=True)
    box(ax, 8.6, 3.45, 2.8, 1.05, """Механизм прямого вывода
forward / all_known""", "#FDE8E8", fs=11, bold=True)
    box(ax, 8.6, 1.15, 3.6, 0.9, """Результат:
причина и глубина вывода""", "#EDE7F6", fs=12, bold=True)

    arrow(ax, 2.0, 4.905, 2.0, 3.995, "факты", color="#555555")
    arrow(ax, 3.42, 3.55, 7.18, 3.55, "текущие факты", color="#2E7D32")
    arrow(ax, 7.18, 3.15, 3.42, 3.15, "новые факты", color="#2E7D32")
    arrow(ax, 8.6, 4.905, 8.6, 3.995, "правила", color="#B26A00")
    arrow(ax, 8.6, 2.905, 8.6, 1.62, "заключение", color="#6A1B9A")

    ax.text(0.35, 6.15, "Схема работы экспертной системы с прямой цепочкой рассуждений",
            fontsize=14, fontweight="bold", ha="left", va="center")
    ax.text(0.35, 0.35, "Цикл повторяется, пока на очередном проходе в рабочую память добавляются новые факты.",
            fontsize=10, ha="left", va="center", color="#555555")
    fig.tight_layout()
    fig.savefig(FIG / "es_architecture.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def rule_path():
    fig, ax = plt.subplots(figsize=(14, 7.6), dpi=180)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    symptoms = [
        ("power = yes", 7.3, "#DCEBFA"),
        ("fan = yes", 6.35, "#DCEBFA"),
        ("display = no", 5.4, "#DCEBFA"),
        ("beep = no", 4.45, "#DCEBFA"),
        ("os = no", 3.5, "#DCEBFA"),
    ]
    level1 = [
        ("""power_ok
(1)""", 7.3, "#E8F8EE"),
        ("""fan_ok
(1)""", 6.35, "#E8F8EE"),
        ("""no_video
(1)""", 5.4, "#E8F8EE"),
        ("""post_ok
(1)""", 4.45, "#E8F8EE"),
        ("""boot_error
(1)""", 3.5, "#E8F8EE"),
    ]
    level2 = [
        ("""power_fan
(2)""", 6.8, "#FFF4DE"),
        ("""no_video_post_ok
(2)""", 4.9, "#FFF4DE"),
    ]
    level3 = [("""no_video_post_ok_no_os
(3)""", 4.0, "#FDE8E8")]
    level4 = [("""bad_gpu
(4)""", 5.4, "#EDE7F6")]

    for text, y, fc in symptoms:
        box(ax, 1.35, y, 2.1, 0.62, text, fc, fs=10.5)
    for text, y, fc in level1:
        box(ax, 4.25, y, 2.1, 0.72, text, fc, fs=10.5)
    for text, y, fc in level2:
        box(ax, 7.25, y, 2.5, 0.78, text, fc, fs=10)
    for text, y, fc in level3:
        box(ax, 10.25, y, 2.8, 0.8, text, fc, fs=10)
    for text, y, fc in level4:
        box(ax, 13.55, y, 2.1, 0.75, text, fc, fs=11, bold=True)
        ax.text(13.55, y - 0.55, "глубина 4", ha="center", va="center",
                fontsize=9, color="#555555")

    for i, (_, y, _) in enumerate(symptoms):
        arrow(ax, 2.45, y, 3.15, level1[i][1], color="#777777")

    arrow(ax, 5.35, 7.3, 5.95, 6.8, color="#2E7D32")
    arrow(ax, 5.35, 6.35, 5.95, 6.8, color="#2E7D32")
    arrow(ax, 5.35, 5.4, 5.95, 4.9, color="#2E7D32")
    arrow(ax, 5.35, 4.45, 5.95, 4.9, color="#2E7D32")

    arrow(ax, 8.55, 4.9, 8.8, 4.0, color="#B26A00")
    arrow(ax, 5.35, 3.5, 8.8, 4.0, color="#B26A00")
    arrow(ax, 8.55, 6.8, 12.45, 5.4, color="#6A1B9A")
    arrow(ax, 11.7, 4.0, 12.45, 5.15, color="#6A1B9A")

    ax.text(0.35, 8.0, "Путь прямого вывода для сценария bad_gpu",
            fontsize=14, fontweight="bold", ha="left", va="center")
    ax.text(0.35, 1.25, "Симптомы → гипотезы 1-го уровня → 2-го → 3-го → причина 4-го уровня",
            fontsize=10.5, ha="left", va="center", color="#555555")
    ax.text(0.35, 0.72, "В скобках указана глубина факта. Показаны только факты, необходимые для вывода bad_gpu.",
            fontsize=9.5, ha="left", va="center", color="#777777")
    ax.text(0.35, 0.30, "Побочные факты cool и boot_error_cool (от ответа overheat = no) в выводе bad_gpu не участвуют.",
            fontsize=9.5, ha="left", va="center", color="#777777")

    fig.tight_layout()
    fig.savefig(FIG / "rule_path_bad_gpu.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    rule_path()
    print("figures written to", FIG)
