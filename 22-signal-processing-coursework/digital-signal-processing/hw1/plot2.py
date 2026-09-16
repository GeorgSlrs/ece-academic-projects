import csv
import matplotlib.pyplot as plt
import numpy as np

filenames = ["realisation1.csv", "realisation2.csv", "realisation3.csv", "realisation4.csv"]

def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        return [float(row[0]) for row in reader]


def autocorrelation(data):
    n = len(data)
    result = np.correlate(data, data, mode='full')
    return result[result.size // 2:]


fig, axs = plt.subplots(len(filenames), 1, figsize=(10, 8), sharex=True)

for i, filename in enumerate(filenames):
    data = read_csv(filename)
    

    autocorr = autocorrelation(data)
    
    axs[i].plot(autocorr)
    axs[i].set_title(f"Autocorrelation of {filename}")
    axs[i].grid(True)


plt.tight_layout()
plt.xlabel("Lag")
plt.show()
