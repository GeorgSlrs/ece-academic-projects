import matplotlib.pyplot as plt
import numpy as np



class PlotFunction:
    def __init__(self):
        self.x_min = -200 * np.pi
        self.x_max = 200 * np.pi
        self.x = np.linspace(self.x_min, self.x_max, 1000)
        self.y = np.zeros_like(self.x)
        inside_range = np.abs(self.x) < 200 * np.pi
        self.y[inside_range] = np.sqrt(4 - (1 / (250**2 * np.pi**2)) * self.x[inside_range]**2)
    
    def plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.x, self.y)
        ax.set_xlim(self.x_min, self.x_max)
        ax.set_ylim(0, np.max(self.y))
        ax.set_xlim(-3000, 3000)
        ax.set_xlabel('Ω')
        ax.set_ylabel('Y1(Ω)')
        ax.set_title(r'$\sqrt{4 - \frac{1}{250^2 \pi^2} Ω^2}$')
        plt.show()

# Usage:
f = PlotFunction()
f.plot()

