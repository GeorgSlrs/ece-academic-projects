import numpy as np
import matplotlib.pyplot as plt
import control as ctl

##############################################################################
# 1) Define the Laplace variable and original plant/disturbance
##############################################################################
s = ctl.tf('s')

G = 6 / ((8*s + 1)*(0.04*s + 1)**2)   # Original plant
Gd = 4.5 / (8*s + 1)                  # Disturbance path

# Normalization:
#   u_norm = u / 3,  y_norm = y / 0.1,  d_norm = d / 2
# => G_norm(s) = 30*G(s)
# => Gd_norm(s) = 20*Gd(s)

G_norm  = 30 * G
Gd_norm = 20 * Gd

##############################################################################
# 2) Inverse-based controller for ω_c=10
#    L(s) = ω_c / s --> K_inv(s) = (ω_c / s)*[1/G_norm(s)]
##############################################################################
omega_c = 10.0
K_inv = (omega_c / s) * (1 / G_norm)

# Open-loop transfer:
L = G_norm * K_inv  # ~ ω_c / s

##############################################################################
# 3) Compute Sensitivity, Complementary Sensitivity, Dist->Output
##############################################################################
S = 1 / (1 + L)
T = 1 - S
Gd_cl = Gd_norm * S

##############################################################################
# 4) Plot frequency responses (using bode with plot=False)
##############################################################################
freqs = np.logspace(-2, 3, 300)

plt.figure(figsize=(10, 6))
mag_L, phase_L, omega_L = ctl.bode(L, freqs, plot=False)  # might warn about deprecation
plt.subplot(2,1,1)
plt.semilogx(omega_L, 20*np.log10(mag_L), label='|L|')
plt.title('Inverse-Based Controller: Open-Loop L(s)')
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.legend()

plt.subplot(2,1,2)
plt.semilogx(omega_L, np.degrees(phase_L), label='Phase of L')
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Phase (deg)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

mag_S, _, _ = ctl.bode(S, freqs, plot=False)
mag_T, _, _ = ctl.bode(T, freqs, plot=False)
mag_Gd, _, _ = ctl.bode(Gd_cl, freqs, plot=False)

plt.figure(figsize=(8, 5))
plt.semilogx(freqs, 20*np.log10(mag_S), label='|S|')
plt.semilogx(freqs, 20*np.log10(mag_T), label='|T|')
plt.semilogx(freqs, 20*np.log10(mag_Gd), label='|Gd_norm*S|')
plt.title('S, T, Dist->Out (Inverse-Based)')
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.legend()
plt.show()

##############################################################################
# 5) Time-domain simulations
##############################################################################
time = np.linspace(0, 5, 501)

# (a) Reference step: y_norm(t) = T(s)*1
y_ref, t_ref = ctl.step_response(T, time)

# (b) Disturbance step: y_norm(t) = Gd_norm*S*1
y_dist, t_dist = ctl.step_response(Gd_cl, time)

plt.figure(figsize=(10, 8))
plt.subplot(2,1,1)
plt.plot(t_ref, y_ref, label='Ref -> y_norm')
plt.title('Inverse-Based Controller: Step Responses')
plt.ylabel('y_norm')
plt.grid(True)
plt.legend()

plt.subplot(2,1,2)
plt.plot(t_dist, y_dist, 'r', label='Dist -> y_norm')
plt.xlabel('Time (s)')
plt.ylabel('y_norm')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

##############################################################################
# 6) Performance metrics
##############################################################################
def step_metrics(t, y, lower=0.1, upper=0.9):
    """
    Return (rise_time, overshoot) relative to final value.
    'rise_time' is time from y=lower*final to y=upper*final.
    'overshoot' is in percent.
    """
    final_val = y[-1]
    idx_lower = None
    idx_upper = None
    for i in range(len(y)):
        if idx_lower is None and y[i] >= lower*final_val:
            idx_lower = i
        if idx_upper is None and y[i] >= upper*final_val:
            idx_upper = i
    if idx_lower is not None and idx_upper is not None:
        rise_time = t[idx_upper] - t[idx_lower]
    else:
        rise_time = None
    if abs(final_val) > 1e-12:
        overshoot = (max(y) - final_val)/final_val * 100.0
    else:
        overshoot = 0
    return rise_time, overshoot

# Reference step
rise_time, overshoot = step_metrics(t_ref, y_ref)
print("=== Inverse-based Controller, Reference Step ===")
print(f"Final y_norm = {y_ref[-1]:.4f}")
print(f"Rise Time (10-90%) = {rise_time}")
print(f"Overshoot = {overshoot:.2f}%")

# Disturbance step
final_dist = y_dist[-1]
print("\n=== Disturbance Step ===")
print(f"Final y_norm = {final_dist:.4f}")

# fix index if 1.5 is exactly the last or beyond
idx_1p5 = min(np.searchsorted(t_dist, 1.5), len(t_dist)-1)
y_at_1p5 = y_dist[idx_1p5]
print(f"y_norm at t=1.5 s = {y_at_1p5:.4f}")

max_y_ref = np.max(np.abs(y_ref))
max_y_dist = np.max(np.abs(y_dist))
print(f"Max |y_norm| (ref) = {max_y_ref:.4f}")
print(f"Max |y_norm| (dist) = {max_y_dist:.4f}")
print("Criteria: y_norm<1 always => |y|<0.1, and y_norm<0.1 after 1.5 s => |y|<0.01\n")
