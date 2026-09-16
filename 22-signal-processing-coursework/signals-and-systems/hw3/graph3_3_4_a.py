import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

# Load the input signal from the WAV file
fs, x = wavfile.read("recordingX.wav")

# Define the coefficients of the LTI system
b = [1, -1.9999, 1]
a = [1, 1.8999, -0.9025]

# Apply the LTI system to the input signal
y = signal.lfilter(b, a, x)

# Plot the first 80 samples of y(n) as a discrete-time signal
plt.subplot(2, 1, 1)
plt.stem(range(80), y[:80], use_line_collection=True)
plt.xlabel("n")
plt.ylabel("y(n)")
plt.title("Output Signal y(n)")

# Calculate the spectrum of y(n)
freq, spectrum = signal.freqz(b, a, fs=fs)

# Plot the magnitude spectrum of y(n)
plt.subplot(2, 1, 2)
plt.plot(freq, np.abs(spectrum))
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("Magnitude Spectrum of y(n)")

# Display the plots
plt.tight_layout()
plt.show()
