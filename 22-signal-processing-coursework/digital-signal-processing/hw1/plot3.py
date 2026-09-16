import csv
import matplotlib.pyplot as plt
import numpy as np


filenames = ["realisation1.csv", "realisation2.csv", "realisation3.csv", "realisation4.csv"]


def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        
        return [float(row[0]) for row in reader]


def compute_psd(data):
    
    n = len(data)
    fft_values = np.fft.fft(data)
    frequencies = np.fft.fftfreq(n)
    
    
    psd_values = np.abs(fft_values) ** 2
    
    
    return frequencies[frequencies >= 0], psd_values[frequencies >= 0]


fig, axs = plt.subplots(len(filenames), 1, figsize=(10, 8), sharex=True)

for i, filename in enumerate(filenames):
    data = read_csv(filename)
    
    
    frequencies, psd = compute_psd(data)
    
    axs[i].plot(frequencies, psd)
    axs[i].set_title(f"PSD of {filename}")
    axs[i].grid(True)
    axs[i].set_xlabel("Frequency (cycles/sample)")
    axs[i].set_ylabel("Power")


plt.tight_layout()
plt.show()

