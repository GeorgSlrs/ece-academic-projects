import numpy as np
import matplotlib.pyplot as plt
import control as ctl

##############################################################################
# 1) Define Laplace variable and original plant/disturbance
##############################################################################
s = ctl.tf('s')

# Original plant and disturbance (given)
G = 6 / ((8*s + 1) * (0.04*s + 1)**2)   # Plant: 6/[(8s+1)*(0.04s+1)^2]
Gd = 4.5 / (8*s + 1)                     # Disturbance path: 4.5/(8s+1)

# Normalization:
#   u_norm = u/3,  y_norm = y/0.1,  d_norm = d/2.
# Then:
#   G_norm(s) = (3/0.1)*G(s) = 30 * G(s)
#   Gd_norm(s) = (2/0.1)*Gd(s) = 20 * Gd(s)
G_norm  = 30 * G
Gd_norm = 20 * Gd

##############################################################################
# 2) Define a P controller based on normalized transfer functions
##############################################################################
# We wish to have an open-loop crossover frequency ωc ≈ 10 rad/s.
# For a P controller: K(s) = Kp (a constant).
# The open-loop is L(s) = G_norm(s) * Kp.
# To have |L(j10)| ≈ 1, we choose:
#   Kp ≈ 1/|G_norm(j10)|
mag_Gnorm, phase_Gnorm, omega_val = ctl.bode(G_norm, [10], plot=False)
Gnorm_at_10 = mag_Gnorm[0]  # Extract the magnitude at ω = 10 rad/s
Kp_value = 1.0 / Gnorm_at_10

# Define the P controller (a pure gain)
K_p = ctl.tf([Kp_value], [1])

##############################################################################
# 3) Build the closed-loop system
##############################################################################
# Open-loop transfer function:
L = G_norm * K_p

# Sensitivity function S(s) = 1/(1+L(s))
S = 1 / (1 + L)

# Complementary sensitivity function: T(s) = 1 - S(s)
T = 1 - S

# Closed-loop transfer from normalized disturbance d_norm to y_norm:
Gd_cl = Gd_norm * S

##############################################################################
# 4) Frequency-domain analysis: Bode plots
##############################################################################
freqs = np.logspace(-2, 3, 300)

# (a) Bode plot of open-loop L(s)
plt.figure(figsize=(10, 6))
mag_L, phase_L, omega_L = ctl.bode(L, freqs, plot=False)
plt.subplot(2, 1, 1)
plt.semilogx(omega_L, 20*np.log10(mag_L), 'b', label='|L(s)|')
plt.title('P Controller: Open-Loop L(s)')
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.legend()
plt.subplot(2, 1, 2)
plt.semilogx(omega_L, np.degrees(phase_L), 'r', label='Phase of L(s)')
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Phase (deg)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# (b) Bode plots for sensitivity S, complementary sensitivity T,
#     and disturbance-to-output transfer Gd_norm * S.
mag_S, _, _ = ctl.bode(S, freqs, plot=False)
mag_T, _, _ = ctl.bode(T, freqs, plot=False)
mag_D, _, _ = ctl.bode(Gd_cl, freqs, plot=False)

plt.figure(figsize=(8, 5))
plt.semilogx(freqs, 20*np.log10(mag_S), label='|S(s)|')
plt.semilogx(freqs, 20*np.log10(mag_T), label='|T(s)|')
plt.semilogx(freqs, 20*np.log10(mag_D), label='|Gd_norm*S(s)|')
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Magnitude (dB)')
plt.title('P Controller: Sensitivity Functions')
plt.grid(True)
plt.legend()
plt.show()

##############################################################################
# 5) Time-domain simulations: step responses
##############################################################################
time = np.linspace(0, 5, 501)

# (a) Reference step response:
# The closed-loop transfer from reference r to y_norm is T(s).
y_ref, t_ref = ctl.step_response(T, time)

# (b) Disturbance step response:
# The closed-loop transfer from normalized disturbance d_norm to y_norm is Gd_cl.
y_dist, t_dist = ctl.step_response(Gd_cl, time)

plt.figure(figsize=(10, 8))
plt.subplot(2, 1, 1)
plt.plot(t_ref, y_ref, 'b', label='Reference Step Response')
plt.title('P Controller: Time-Domain Responses')
plt.ylabel('y_norm')
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(t_dist, y_dist, 'r', label='Disturbance Step Response')
plt.xlabel('Time (s)')
plt.ylabel('y_norm')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

##############################################################################
# 6) Performance Metrics
##############################################################################
def step_metrics(t, y, lower=0.1, upper=0.9):
    """
    Compute the rise time (time from y = lower * final_value to y = upper * final_value)
    and the percentage overshoot (relative to the final value).
    """
    final_val = y[-1]
    t_lower, t_upper = None, None
    for i in range(len(y)):
        if t_lower is None and y[i] >= lower * final_val:
            t_lower = t[i]
        if t_upper is None and y[i] >= upper * final_val:
            t_upper = t[i]
    rise_time = t_upper - t_lower if (t_lower is not None and t_upper is not None) else None
    overshoot = (max(y) - final_val) / final_val * 100.0 if final_val != 0 else 0
    return rise_time, overshoot

rise_time_ref, overshoot_ref = step_metrics(t_ref, y_ref)
print("=== P Controller, Reference Step ===")
print(f"Final y_norm = {y_ref[-1]:.4f}")
print(f"Rise Time (10%-90%) = {rise_time_ref:.4f} s")
print(f"Overshoot = {overshoot_ref:.2f}%")

print("\n=== P Controller, Disturbance Step ===")
print(f"Final y_norm = {y_dist[-1]:.4f}")

# Ensure the index for t = 1.5 s is within bounds.
idx_1p5 = min(np.searchsorted(t_dist, 1.5), len(t_dist) - 1)
print(f"y_norm at t=1.5 s = {y_dist[idx_1p5]:.4f}")

max_y_ref = np.max(np.abs(y_ref))
max_y_dist = np.max(np.abs(y_dist))
print(f"\nMax |y_norm| during reference step = {max_y_ref:.4f}")
print(f"Max |y_norm| during disturbance step = {max_y_dist:.4f}")
print("Criteria: y_norm < 1 at all times (i.e., y < 0.1) and y_norm < 0.1 after 1.5 s (i.e., y < 0.01)")
