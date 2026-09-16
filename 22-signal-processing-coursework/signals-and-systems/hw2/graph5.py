import numpy as np
import matplotlib.pyplot as plt

class SignalPlotter:
    def __init__(self, t, xlabel, ylabel):
        self.t = t
        self.xlabel = xlabel
        self.ylabel = ylabel

    def plot(self, signal, label):
        plt.plot(self.t, signal, label=label)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend()

# Define the time range
t = np.linspace(-np.pi, np.pi, 1000)

# Create a SignalPlotter instance for each signal
plotter = SignalPlotter(t, 't', 'x(t)')
plotter1 = SignalPlotter(t, 't', 'x1(t)')
plotter_e1 = SignalPlotter(t, 't', 'e1(t)')

# Define the signals
x = t
x1 = 2 * np.sin(t)
e1 = t - 2 * np.sin(t)

# Plot each signal using the corresponding SignalPlotter instance
plotter.plot(x, label='x(t) = t')
plotter1.plot(x1, label='x1(t) = 2sin(t)')
plotter_e1.plot(e1, label='e1(t) = t - 2sin(t)')

# Show the plot
plt.show()
