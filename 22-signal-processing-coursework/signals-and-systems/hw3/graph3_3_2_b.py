import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

# Load the audio file
filename = 'recordingX.wav'
data, sample_rate = sf.read(filename)

# Take the first 40 samples of x(2n)
samples = data[:81:2][:40]

# Create the time axis
time = np.arange(len(samples))

# Plot the signal as a stem plot
plt.stem(time, samples, use_line_collection=True, basefmt=' ')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.title('Discrete Time Signal x(2n) - 40 samples')
plt.grid(True)
plt.show()
