import numpy as np
import matplotlib.pyplot as plt

# Define a custom style for the plot
plt.style.use('seaborn-darkgrid')

class DiscreteTimeSignal:
    def __init__(self, f, n_samples, label=''):
        self.f = f
        self.n_samples = n_samples
        self.label = label
    
    def __call__(self, n):
        return self.f(n)
    
    def plot(self):
        n = np.arange(self.n_samples)
        y = self(n)
        plt.stem(n, y, label=self.label, linefmt='C1-', markerfmt='o', basefmt=' ')
        plt.xlabel('n')
        plt.ylabel('Amplitude')
        plt.title('Discrete Time Signals')
        plt.legend()
        plt.show()

# Define the signals
def cos_signal(n):
    return np.cos((6*np.pi/9) * n)

def cos_squared_signal(n):
    return np.cos((np.pi/6) * n)**2

def product_cosines_signal(n):
    return np.cos(np.pi * n/2) * np.cos(np.pi* n/4)
# Create the signal objects and plot them

signal3 = DiscreteTimeSignal(product_cosines_signal, 100, label='x3(n) = cos(πn/2) * cos(πn/4)')



signal3.plot()
