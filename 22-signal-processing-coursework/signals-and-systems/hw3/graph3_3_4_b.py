import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

# Load the input signal from the WAV file
fs, x = wavfile.read("recordingX.wav")

# Calculate the DTFT of x(n)
freq_x, dtft_x = signal.freqz(x, fs=fs)

# Plot the first 80 samples of x(n) as a discrete-time signal
plt.subplot(2, 1, 1)
plt.stem(range(80), x[:80], use_line_collection=True, basefmt=' ')
plt.xlabel("n")
plt.ylabel("x(n)")
plt.title("Input Signal x(n)")

# Plot the DTFT of x(n)
plt.subplot(2, 1, 2)
plt.plot(freq_x, np.abs(dtft_x))
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("DTFT of x(n)")

# Adjust the spacing between subplots
plt.tight_layout()

# Display the plots
plt.show()
