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

# Step 3: Downsample the audio by a factor of 4
audio_downsampled = audio[::4]


# Step 4: Compute the Discrete Fourier Transform (DFT) of the downsampled signal
dft = np.fft.fft(audio_downsampled)

# Step 5: Compute the frequency axis for the downsampled spectrum
freq = np.fft.fftfreq(len(dft), d=1/sr)

# Step 6: Plot the magnitude spectrum of the downsampled signal up to fs/4
plt.plot(freq[:len(freq)//4], np.abs(dft[:len(freq)//4]))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('DTFT of the Downsampled Signal x(4n)')
plt.xlim(0, sr/4)  # Set x-axis limit to the sampling frequency/4
plt.grid(True)

# Step 7: Identify the three most dominant positive frequencies and add labels to the plot
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
