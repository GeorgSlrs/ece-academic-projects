import matplotlib.pyplot as plt
import numpy as np

class FunctionPlotter:
    def __init__(self, functions, x_range):
        self.functions = functions
        self.x_range = x_range

    def plot(self):
        x = np.linspace(*self.x_range, 100)

        for f in self.functions:
            y = f(x)
            label = f.__name__
            plt.plot(x, y, label=label)

        plt.legend()
        plt.show()

def cos2x_plus_sin2x(x):
    return np.cos(2*x) + np.sin(2*x)

functions = [
    np.cos,
    np.sin,
    cos2x_plus_sin2x,
    lambda x: np.cos(np.sqrt(3*x)) + np.sin(np.sqrt(3*x)),
    lambda x: np.cos(x) + np.sin(5*x) + np.cos(np.sqrt(7*x))
]

plotter = FunctionPlotter(functions, (-10*np.pi, 10*np.pi))
