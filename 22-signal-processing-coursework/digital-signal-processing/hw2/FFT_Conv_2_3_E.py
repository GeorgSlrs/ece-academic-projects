
import numpy as np

# Define the input signal x(n) and the impulse response h(n)
x = np.array([2, 1, -1, -2])
h = np.array([1, -1])

# Perform direct linear convolution
y_direct = np.convolve(x, h)

# Perform convolution using FFT
N = len(x) + len(h) - 1  # Length of the output signal
X = np.fft.fft(x, N)     # FFT of x with zero-padding
H = np.fft.fft(h, N)     # FFT of h with zero-padding
Y_fft = np.fft.ifft(X * H)  # Inverse FFT of the product
y_fft = np.real(Y_fft)      # Take the real part

# Compare the results
print("Direct Convolution (y_direct):", y_direct)
print("FFT-based Convolution (y_fft):", Y_fft)
