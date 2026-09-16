import matplotlib.pyplot as plt
import numpy as np

# Load data from the text file
data = np.loadtxt('ECG-320Hz.txt')

# Number of points in FFT
N = 320

# Sampling rate
sampling_rate = 320  # in Hz

# Compute the Fast Fourier Transform (FFT)
fft_result = np.fft.fft(data, N)

# Compute the magnitude of the FFT
magnitude = np.abs(fft_result)

# Generate frequency bins
frequencies = np.fft.fftfreq(N, 1 / sampling_rate)

# Plot the magnitude spectrum for the first N/2 values
plt.figure(figsize=(10, 6))
plt.plot(frequencies[:N//2], magnitude[:N//2])
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('Spectrum of the ECG Signal')
plt.grid(True)
plt.show()
