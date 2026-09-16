import numpy as np
import matplotlib.pyplot as plt

# Define the function H(omega)
H_omega = lambda Ω: 0.5 * (1 - 2*Ω**2) / (-2*Ω**2 + 1j*Ω + 1)

# New frequency range from 0 to 2π
omega = np.logspace(np.log10(1e-10), np.log10(2*np.pi), 400)

# Calculate amplitude and phase for the new range
H_values = H_omega(omega)
amplitude_dB = 20 * np.log10(np.abs(H_values))  # Convert amplitude to dB
phase = np.angle(H_values)

# Plotting with logarithmic horizontal axis and linear vertical axis in dB
plt.figure(figsize=(12, 6))

# Amplitude plot in dB with logarithmic horizontal axis
plt.subplot(1, 2, 1)
plt.semilogx(omega, amplitude_dB, color='green', linewidth=2)
plt.title('Amplitude of H(Ω) in dB', fontsize=14)
plt.xlabel('Ω (rad/s)', fontsize=12)
plt.ylabel('|H(Ω)| (dB)', fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.5)

# Phase plot with logarithmic horizontal axis
plt.subplot(1, 2, 2)
plt.semilogx(omega, phase, color='purple', linewidth=2)
plt.title('Phase of H(Ω)', fontsize=14)
plt.xlabel('Ω (rad/s)', fontsize=12)
plt.ylabel('Phase (radians)', fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
