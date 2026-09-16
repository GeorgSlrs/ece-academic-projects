import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

# Load signal x(n) from file
x = np.loadtxt('ECG-320Hz.txt')

# Define h(n)
h = np.array([1, -1.11, 1])

# Zero-pad h(n) to the length of x(n) for spectrum calculation
h_padded = np.zeros(len(x))
h_padded[:len(h)] = h

# Perform convolution to get y(n)
y = np.convolve(x, h, mode='same')

# Function to calculate spectrum
def calculate_spectrum(signal, fs):
    N = len(signal)
    spectrum = fft(signal)
    freq = np.linspace(0, fs, N)
    return freq[:N // 2], np.abs(spectrum)[:N // 2]

# Sampling frequency
fs = 320

# Calculate spectrums
freq_x, spectrum_x = calculate_spectrum(x, fs)
freq_h, spectrum_h = calculate_spectrum(h_padded, fs)
freq_y, spectrum_y = calculate_spectrum(y, fs)

# Plotting
plt.figure(figsize=(12, 10))

# Subplot for x(n)
plt.subplot(3, 2, 1)
plt.plot(x, label='x(n)')
plt.title('Signal x(n)')
plt.grid(True)
plt.legend()

# Subplot for Spectrum of x(n)
plt.subplot(3, 2, 2)
plt.plot(freq_x, spectrum_x, label='X')
plt.title('Spectrum of x(n)')
plt.grid(True)
plt.legend()

# Subplot for Zero-padded h(n)
plt.subplot(3, 2, 3)
plt.plot(h_padded, label='h(n)')
plt.title('Zero-padded h(n)')
plt.grid(True)
plt.legend()

# Subplot for Spectrum of zero-padded h(n)
plt.subplot(3, 2, 4)
plt.plot(freq_h, spectrum_h, label='H')
plt.title('Spectrum of Zero-padded h(n)')
plt.grid(True)
plt.legend()

# Subplot for y(n)
plt.subplot(3, 2, 5)
plt.plot(y, label='y(n)')
plt.title('Filtered Signal y(n)')
plt.grid(True)
plt.legend()

# Subplot for Spectrum of y(n)
plt.subplot(3, 2, 6)
plt.plot(freq_y, spectrum_y, label='Y')
plt.title('Spectrum of y(n)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

