import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

# Load the audio file
filename = 'recordingX.wav'
data, sample_rate = sf.read(filename)

# Take the first 20 samples of x(4n)
samples = data[:80:4]

# Create the time axis
time = np.arange(len(samples))

# Plot the signal as a stem plot
plt.stem(time, samples, use_line_collection=True, basefmt=' ')
plt.xticks(np.arange(0, len(samples), 1))  # Set x-axis tick positions
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.title('Discrete Time Signal x(4n) - First 20 samples')
plt.grid(True)
plt.show()
