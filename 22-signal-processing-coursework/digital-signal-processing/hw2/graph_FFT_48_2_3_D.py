import numpy as np
import matplotlib.pyplot as plt

# Given signal x(n)
x = np.array([2, 1, -1, -2, 0, 0, 0, 0])  # Padding with zeros to make it 8-point

# Calculating the 8-point FFT
X_8_point = np.fft.fft(x)

# Compute the magnitude (amplitude) of the 8-point spectrum
magnitude_8_point = np.abs(X_8_point)

# Sampling frequency
fs = 40  # in Hz

# Frequency bins for 8-point FFT
freq_8_point = np.fft.fftfreq(len(X_8_point), 1/fs)

# Compute the 4-point FFT (taking the first 4 samples of the signal)
X_4_point = np.fft.fft(x[:4])

# Compute the magnitude (amplitude) of the 4-point spectrum
magnitude_4_point = np.abs(X_4_point)

# Frequency bins for 4-point FFT
freq_4_point = np.fft.fftfreq(len(X_4_point), 1/fs)

# Creating two subplots
fig, axs = plt.subplots(2, 1, figsize=(12, 12))

# Plotting the 8-point FFT with dots
axs[0].stem(freq_8_point, magnitude_8_point, 'b', markerfmt="bo", basefmt="-b")
axs[0].set_title('8-point FFT Amplitude Spectrum')
axs[0].set_xlabel('Frequency (Hz)')
axs[0].set_ylabel('Amplitude')
axs[0].grid()

# Plotting the 4-point FFT with dots
axs[1].stem(freq_4_point, magnitude_4_point, 'r', markerfmt="ro", basefmt="-r")
axs[1].set_title('4-point FFT Amplitude Spectrum')
axs[1].set_xlabel('Frequency (Hz)')
axs[1].set_ylabel('Amplitude')
axs[1].grid()

# Displaying the plots
plt.tight_layout()
plt.show()

