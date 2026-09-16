import matplotlib.pyplot as plt
import numpy as np

# Define the function f(x) in decibels
def f_db(x, N):
    return 20 * np.log10(1 / np.sqrt(1 + x**(2*N)))

# Create an array of x values from -4 to 4
x = np.linspace(-4, 4, 400)

# Colors for the plots
colors = ['b', 'g', 'r', 'c', 'm']

# Plot f(x) for different values of N with different colors
for i, N in enumerate([1, 2, 3, 5, 10]):
    plt.plot(x, f_db(x, N), label=f'N={N}', color=colors[i])

# Adding labels and title
plt.xlabel('normalised frequency')
plt.ylabel('|H(Ω/Ωc| in dB')
plt.title('Plot of the amplitude of the frequency response for the Butterworth filter of N-th order in dB')
plt.legend()

# Adding grid to the plot
plt.grid(True)

# Show the plot
plt.show()
