import numpy as np


# ----------------------------------------------------------------
# 1. Исходная функция f(x)
# ----------------------------------------------------------------
def f(x):
    if -5 <= x <= 3:
        return (5 / 8) * (x + 5)
    elif 3 < x <= 6:
        return (5 / 3) * (6 - x)
    else:
        return 0.0


# ----------------------------------------------------------------
# 2. Периодизация Φ(x) = f(x-2π) + f(x) + f(x+2π)
# ----------------------------------------------------------------
def Phi(x):
    return f(x - 2 * np.pi) + f(x) + f(x + 2 * np.pi)


# ----------------------------------------------------------------
# 3. c_k через численное интегрирование
#    c_k = (1/2π) ∫_{-π}^{π} Φ(x) e^{-ikx} dx
# ----------------------------------------------------------------
def c_k_numeric(k, N=20000):
    p1 = 6 - 2 * np.pi
    p2 = 2 * np.pi - 5
    p3 = 3.0
    a = [-np.pi, p1, p2, p3]
    b = [p1, p2, p3, np.pi]

    total = 0.0 + 0.0j
    for x0, x1 in zip(a, b):
        xs = np.linspace(x0, x1, N)
        ys = np.array([Phi(x) for x in xs])
        integrand = ys * np.exp(-1j * k * xs)
        total += np.trapz(integrand, xs)

    return total / (2 * np.pi)


# ----------------------------------------------------------------
# 4. c_k через аналитическую формулу (= f_hat(k)/(2π))
# ----------------------------------------------------------------
def c_k_formula(k):
    if k == 0:
        return 55 / (4 * np.pi)
    return (5 / (48 * np.pi * k**2)) * (
        11 * np.exp(-3j * k) - 3 * np.exp(5j * k) - 8 * np.exp(-6j * k)
    )


# ----------------------------------------------------------------
# 5. Печать таблицы + сумма
# ----------------------------------------------------------------
K_MIN, K_MAX = -5, 5
sum_num = 0.0 + 0.0j
sum_for = 0.0 + 0.0j

print(f"{'k':>3} | {'c_k (численно)':>28} | {'c_k (формула)':>28} | {'|разность|':>12}")
print("-" * 88)

for k in range(K_MIN, K_MAX + 1):
    c_num = c_k_numeric(k)
    c_for = c_k_formula(k)
    diff = abs(c_num - c_for)

    sum_num += c_num
    sum_for += c_for

    s_num = f"{c_num.real:>+11.6f}{c_num.imag:>+11.6f}i"
    s_for = f"{c_for.real:>+11.6f}{c_for.imag:>+11.6f}i"

    print(f"{k:>3} | {s_num:>28} | {s_for:>28} | {diff:>12.2e}")

print("-" * 88)
print(f"\nСумма от k={K_MIN} до k={K_MAX}:")
print(f"  Численно: {sum_num.real:+.9f} {sum_num.imag:+.9f}i")
print(f"  Формула : {sum_for.real:+.9f} {sum_for.imag:+.9f}i")
print(f"  |разность| = {abs(sum_num - sum_for):.2e}")

# Сравнение с шагом 8 (S_5 из baseline.pdf)
S5_expected = 3.083723337
print(f"\nСравнение с шагом 8:")
print(f"  S_5 (из ИДЗ)   = {S5_expected:.9f}")
print(f"  Σ c_k (числ.)  = {sum_num.real:.9f}")
print(f"  |Δ|            = {abs(sum_num.real - S5_expected):.2e}")
