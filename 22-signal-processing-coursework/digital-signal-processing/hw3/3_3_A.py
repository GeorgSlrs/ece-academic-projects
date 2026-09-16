import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt('ECG-320Hz.txt')

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(data, color='royalblue', linestyle='-', linewidth=1.5)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

ax.tick_params(axis='both', which='major', labelsize=12)
ax.set_xlabel('Sample Number (n)', fontsize=14)
ax.set_ylabel('Signal Amplitude', fontsize=14)
ax.set_title('ECG Signal x(n)', fontsize=16)
plt.show()
