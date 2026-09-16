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

# Step 4: Perform downsampling by 2
downsampled_audio = audio[::2]  # Downsampling by 2 (x(2n))

# Step 5: Compute the DFT of the downsampled signal
downsampled_dft = np.fft.fft(downsampled_audio)

# Step 6: Plot the magnitude spectrum (DTFT) of the downsampled signal
downsampled_freq = np.fft.fftfreq(len(downsampled_dft), d=1/sr)
plt.plot(downsampled_freq, np.abs(downsampled_dft))  # Plot full spectrum
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('DTFT of Downsampled Signal (x(2n))')
plt.xlim(0, sr/2)  # Set x-axis limit to one-fourth the sampling frequency
plt.grid(True)

# Step 7: Identify the three most dominant positive frequencies in the downsampled spectrum
downsampled_positive_freqs = downsampled_freq[:len(downsampled_freq)//2]  # Consider positive frequencies only
downsampled_positive_dft = downsampled_dft[:len(downsampled_freq)//2]
downsampled_sorted_indices = np.argsort(np.abs(downsampled_positive_dft))
downsampled_dominant_freqs = downsampled_positive_freqs[downsampled_sorted_indices][-3:][::-1]
downsampled_dominant_magnitudes = np.abs(downsampled_positive_dft[downsampled_sorted_indices][-3:])[::-1]

for freq, mag in zip(downsampled_dominant_freqs, downsampled_dominant_magnitudes):
    scaled_freq = freq / 2  # Scale the frequency by the downsampling factor
    plt.annotate(f'{scaled_freq:.2f} Hz', xy=(freq, mag), xytext=(5, 10), textcoords='offset points')
    print(f"Frequency: {scaled_freq:.2f} Hz")

plt.tight_layout()
plt.show()
