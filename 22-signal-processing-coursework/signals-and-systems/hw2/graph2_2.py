import numpy as np
import matplotlib.pyplot as plt

def f(x):
    return np.sqrt(4 - (1 / ((250**2 * np.pi) ** 2) * (x **2)))

def g(x):
    return np.where(abs(x) < 200*np.pi, f(x), 0)

def h(x):
    return 1/2 * (g(x-2000*np.pi) + g(x+2000*np.pi))

x = np.linspace(-3000*np.pi, 3000*np.pi, 5000)
y = h(x)

plt.plot(x, y)
plt.title("Function Y2(Ω)")
plt.xlabel("Ω")
plt.ylabel("Y2(Ω)")
plt.show()
