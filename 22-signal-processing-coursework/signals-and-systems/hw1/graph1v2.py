import numpy as np
import matplotlib.pyplot as plt

class FunctionPlotter:
    
    def __init__(self, x_min, x_max, num_points):
        self.x_min = x_min
        self.x_max = x_max
        self.num_points = num_points
        
    def plot(self, function, label, color):
        x = np.linspace(self.x_min, self.x_max, self.num_points)
        y = function(x)
        plt.plot(x, y, label=label, linewidth=2, color=color)
        plt.xlabel('t', fontsize=16)
        plt.ylabel('f(t)', fontsize=16)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(fontsize=14)
        plt.grid(True, linestyle='--', linewidth=0.5)
        
def function_1(x):
    return np.cos(2 * np.pi * x) + np.cos(4 * np.pi * x)

def function_2(x):
    return np.cos(2 * np.pi * x) + np.cos(4 * x)

plotter = FunctionPlotter(-4, 4, 1000)
plotter.plot(function_1, r'$\cos(2\pi t) + \cos(4\pi t)$', 'navy')
plotter.plot(function_2, r'$\cos(2\pi t) + \cos(4t)$', 'crimson')
plt.title('Two Cosine Functions', fontsize=20)
plt.show()
