import numpy as np
import matplotlib.pyplot as plt

class DiscreteSignalPlot:
    def __init__(self, n, x, label):
        self.n = n
        self.x = x
        self.label = label

    def plot(self):
        plt.stem(self.n, self.x, linefmt='b-', markerfmt='bo', basefmt='r-', label=self.label)
        plt.xlabel('n')
        plt.ylabel('x(n)')
        plt.title('Discrete-Time Signal')
        plt.grid(True)
        plt.legend()
        plt.show()

# Generate the discrete-time signal
n = np.arange(0, 100)
x = np.cos((6 * np.pi * n /9) + 1)

# Create an instance of DiscreteSignalPlot and plot the signal with a label
signal_plot = DiscreteSignalPlot(n, x, label='x(n) = cos((6 * np.pi * n /9) + 1)')
signal_plot.plot()
