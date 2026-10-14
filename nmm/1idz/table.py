import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# 1. Исходная функция f(x)
# ---------------------------------------------------------------
def f(x):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    mask1 = (x >= -5) & (x <= 3)
    y[mask1] = (5 / 8) * (x[mask1] + 5)
    mask2 = (x > 3) & (x <= 6)
    y[mask2] = (5 / 3) * (6 - x[mask2])
    return y


# ---------------------------------------------------------------
# 2. Периодизация Φ(x) = f(x-2π) + f(x) + f(x+2π)
# ---------------------------------------------------------------
def Phi(x):
    return f(x - 2 * np.pi) + f(x) + f(x + 2 * np.pi)


# ---------------------------------------------------------------
# 3. Производная Φ'(x) — кусочно-постоянная
#    (аналитические значения на каждом интервале)
# ---------------------------------------------------------------
def Phi_prime(x):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)

    # Точки разбиения
    p1 = 6 - 2 * np.pi  # ≈ -0.283
    p2 = 2 * np.pi - 5  # ≈  1.283
    p3 = 3.0

    # Интервал 1: (-π, p1)          → -25/24
    m1 = (x > -np.pi) & (x < p1)
    y[m1] = -25 / 24

    # Интервал 2: (p1, p2)          →  5/8
    m2 = (x > p1) & (x < p2)
    y[m2] = 5 / 8

    # Интервал 3: (p2, p3)          →  5/4
    m3 = (x > p2) & (x < p3)
    y[m3] = 5 / 4

    # Интервал 4: (p3, π)           → -25/24
    m4 = (x > p3) & (x < np.pi)
    y[m4] = -25 / 24

    return y


# ---------------------------------------------------------------
# 4. Расчёт на [−π, π]
# ---------------------------------------------------------------
x = np.linspace(-np.pi, np.pi, 2000)
y_Phi = Phi(x)
y_dPhi = Phi_prime(x)

# Точки разбиения и их значения Φ (для маркеров)
p1 = 6 - 2 * np.pi
p2 = 2 * np.pi - 5
p3 = 3.0
x_break = np.array([-np.pi, p1, p2, p3, np.pi])
y_break = Phi(x_break)

# ---------------------------------------------------------------
# 5. Рисуем два графика
# ---------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
)

# --- Верхний: Φ(x) ---
ax1.plot(x, y_Phi, color="tab:blue", linewidth=2, label=r"$\Phi(x)$")
ax1.plot(
    x_break,
    y_break,
    "o",
    color="tab:blue",
    markerfacecolor="white",
    markeredgewidth=2,
    markersize=8,
    zorder=5,
)

# Подписи значений в точках разбиения
for xi, yi in zip(x_break, y_break):
    ax1.annotate(
        f"{yi:.3f}",
        xy=(xi, yi),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        color="tab:blue",
    )

# Вертикальные пунктирные линии в точках разбиения
for xi in x_break[1:-1]:
    ax1.axvline(xi, color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
    ax2.axvline(xi, color="gray", linestyle=":", linewidth=0.8, alpha=0.7)

ax1.set_ylabel(r"$\Phi(x)$", fontsize=13)
ax1.grid(True, alpha=0.3)
ax1.set_title(
    r"Периодизация $\Phi(x)$ и её производная $\Phi\'(x)$ на $[-\pi, \pi]$", fontsize=13
)

# --- Нижний: Φ'(x) ---
# Рисуем горизонтальные отрезки с пустыми кружками на концах
for x0, x1, val in [
    (-np.pi, p1, -25 / 24),
    (p1, p2, 5 / 8),
    (p2, p3, 5 / 4),
    (p3, np.pi, -25 / 24),
]:
    # сама линия
    ax2.plot([x0, x1], [val, val], color="tab:red", linewidth=2)
    # пустые кружки на концах
    ax2.plot(
        [x0, x1],
        [val, val],
        "o",
        markerfacecolor="white",
        markeredgecolor="tab:red",
        markeredgewidth=2,
        markersize=8,
    )

ax2.axhline(0, color="black", linewidth=0.5, alpha=0.5)
ax2.set_ylabel(r"$\Phi'(x)$", fontsize=13)
ax2.set_xlabel("x", fontsize=12)
ax2.grid(True, alpha=0.3)

# --- Оформление оси x ---
ticks = [-np.pi, p1, p2, p3, np.pi]
labels = [r"$-\pi$", r"$6-2\pi$", r"$2\pi-5$", r"$3$", r"$\pi$"]
ax2.set_xticks(ticks)
ax2.set_xticklabels(labels)

plt.tight_layout()
plt.savefig("Phi_and_derivative.png", dpi=150)
plt.show()
