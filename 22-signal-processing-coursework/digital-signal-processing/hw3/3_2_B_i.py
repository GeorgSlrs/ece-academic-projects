import numpy as np
import matplotlib.pyplot as plt

# Define the frequency range from 0 to 2π
omega = np.linspace(0, 2*np.pi, 400)

# Define the function H(omega)
H_omega = lambda Ω: 0.5 * (1 - 2*Ω**2) / (-2*Ω**2 + 1j*Ω + 1)

# Calculate amplitude and phase
H_values = H_omega(omega)
amplitude = np.abs(H_values)
phase = np.angle(H_values)

# Plotting
plt.figure(figsize=(12, 6))

# Amplitude plot
plt.subplot(1, 2, 1)
plt.plot(omega, amplitude, color='green', linewidth=2)
plt.title('Amplitude of H(Ω)', fontsize=14)
plt.xlabel('Ω (rad/s)', fontsize=12)
plt.ylabel('|H(Ω)|', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

# Phase plot
plt.subplot(1, 2, 2)
plt.plot(omega, phase, color='purple', linewidth=2)
plt.title('Phase of H(Ω)', fontsize=14)
plt.xlabel('Ω (rad/s)', fontsize=12)
plt.ylabel('Phase (radians)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
