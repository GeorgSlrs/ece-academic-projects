import numpy as np


x = np.array([2, 1, -1, -2, 0, 0, 0, 0])  # Padding with zeros to make it 8-point
X = np.fft.fft(x)
for i, val in enumerate(X):
    magnitude = np.abs(val)
    print(f"X[{i}] = {val:.4f}, Magnitude = {magnitude:.4f}")
