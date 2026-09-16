# Python code to plot the function f(x) = 1 / sqrt(1 + x^(2N)) for N = 1, 2, 3, 5, 10
# with different colors for each plot and including a grid.

import matplotlib.pyplot as plt
import numpy as np

# Define the function f(x)
def f(x, N):
    return 1 / np.sqrt(1 + x**(2*N))

# Create an array of x values from -4 to 4
x = np.linspace(-4, 4, 400)

# Colors for the plots
colors = ['b', 'g', 'r', 'c', 'm']

# Plot f(x) for different values of N with different colors
for i, N in enumerate([1, 2, 3, 5, 10]):
    plt.plot(x, f(x, N), label=f'N={N}', color=colors[i])

# Adding labels and title
plt.xlabel('normalised frequency')
plt.ylabel('|H(Ω/Ωc|')
plt.title('Plot of the amplitude of the frequency response for the Butterworth filter of N-th order')
plt.legend()

# Adding grid to the plot
plt.grid(True)

# Show the plot
plt.show()
