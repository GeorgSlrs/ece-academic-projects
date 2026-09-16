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
x = np.cos(np.pi * n / 6) ** 2

# Create an instance of DiscreteSignalPlot and plot the signal with a label
signal_plot = DiscreteSignalPlot(n, x, label='x2(n) = cos(np.pi * n / 6) ** 2 ')
signal_plot.plot()
