import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import wave

# Step 1: Load the audio file and extract the sampling frequency
filename = 'recordingX.wav'
with wave.open(filename, 'rb') as wav_file:
    params = wav_file.getparams()
    sr = params.framerate
    print("Sampling Frequency:", sr, "Hz")

# Step 2: Read the audio data using wavfile from scipy
_, audio = wavfile.read(filename)

# Step 3: Compute the Discrete Fourier Transform (DFT) of the signal
dft = np.fft.fft(audio)

# Step 4: Plot the magnitude spectrum (DTFT) of the signal
freq = np.fft.fftfreq(len(dft), d=1/sr)
plt.plot(freq, np.abs(dft))  # Plot full spectrum
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('DTFT of the Signal')
plt.xlim(0, sr)  # Set x-axis limit to the sampling frequency
plt.grid(True)

# Step 5: Identify the three most dominant positive frequencies and add labels to the plot
positive_freqs = freq[:len(freq)//2]  # Consider positive frequencies only
positive_dft = dft[:len(freq)//2]
sorted_indices = np.argsort(np.abs(positive_dft))
dominant_freqs = positive_freqs[sorted_indices][-3:][::-1]
dominant_magnitudes = np.abs(positive_dft[sorted_indices][-3:])[::-1]

for freq, mag in zip(dominant_freqs, dominant_magnitudes):
    plt.annotate(f'{freq:.2f} Hz', xy=(freq, mag), xytext=(5, 10), textcoords='offset points')
    print(f"Frequency: {freq:.2f} Hz")

plt.tight_layout()
plt.show()

