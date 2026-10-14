import numpy as np
import matplotlib.pyplot as plt


# Определяем функцию f(x)
def f(x):
    y = np.zeros_like(x)
    mask1 = (x >= -5) & (x <= 3)
    y[mask1] = (5 / 8) * (x[mask1] + 5)
    mask2 = (x > 3) & (x <= 6)
    y[mask2] = (5 / 3) * (6 - x[mask2])
    return y


# Диапазон по x
x = np.linspace(-6 * np.pi, 6 * np.pi, 5000)

# Создаём рисунок
fig, ax = plt.subplots(figsize=(14, 5))

# Рисуем треугольники для разных k
colors = {
    -2: "lightgray",
    -1: "tab:orange",
    0: "tab:blue",
    1: "tab:orange",
    2: "lightgray",
}
labels = {-2: "k = -2", -1: "k = -1", 0: "k = 0", 1: "k = 1", 2: "k = 2"}
linewidths = {0: 2.5, -1: 2.5, 1: 2.5, -2: 2, 2: 2}

for k in [-2, -1, 0, 1, 2]:
    y = f(x + 2 * np.pi * k)
    ax.plot(x, y, color=colors[k], linewidth=linewidths[k], label=labels[k])

# Выделяем полосу [-π, π]
ax.axvspan(-np.pi, np.pi, color="lightblue", alpha=0.4, label=r"$[-\pi, \pi]$")

# Оформление
ax.axhline(0, color="black", linewidth=0.5)
ax.set_xlim(-6 * np.pi, 6 * np.pi)
ax.set_ylim(-0.5, 6)
ax.set_xticks(
    [
        -6 * np.pi,
        -4 * np.pi,
        -2 * np.pi,
        -np.pi,
        0,
        np.pi,
        2 * np.pi,
        4 * np.pi,
        6 * np.pi,
    ]
)
ax.set_xticklabels(
    [
        r"$-6\pi$",
        r"$-4\pi$",
        r"$-2\pi$",
        r"$-\pi$",
        "0",
        r"$\pi$",
        r"$2\pi$",
        r"$4\pi$",
        r"$6\pi$",
    ]
)
ax.set_xlabel("x")
ax.set_ylabel("f(x + 2πk)")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)
ax.set_title("Сдвинутые копии f(x + 2πk) и полоса [-π, π]")

plt.tight_layout()
plt.savefig("shifted_triangles.png", dpi=150)
plt.show()
