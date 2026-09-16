import numpy as np
import matplotlib.pyplot as plt
import control as ctl

# 1) Define original G(s) and Gd(s)
s = ctl.tf('s')
G = 6 / ((8*s + 1)*(0.04*s + 1)**2)
Gd = 4.5 / (8*s + 1)

# Scaling: y_norm = y/0.1, u_norm = u/3, d_norm = d/2
# => G_norm(s) = 30*G(s), Gd_norm(s) = 20*Gd(s)
G_norm  = 30 * G
Gd_norm = 20 * Gd

# 2) Define the PID parameters: 
#    T_i=1 s, T_d=1/ω_c=0.1 s, T_f=T_d/10=0.01 s
#    We'll do a small search for Kp to get the open-loop crossover ~10 rad/s
Ti = 1.0
Td = 0.1
Tf = 0.01

def find_Kp_pid(Gnorm, Ti, Td, Tf, omega_c=10.0):
    kp_candidates = np.logspace(-2, 2, 50)  # from 0.01 to 100
    best_kp = None
    best_diff = 1e9
    for kp in kp_candidates:
        Ktest = kp * (1 + 1/(Ti*s)) * ((Td*s + 1)/(Tf*s + 1))
        mag, phase, _ = ctl.bode(Gnorm * Ktest, [omega_c], plot=False)
        diff = abs(mag[0] - 1)
        if diff < best_diff:
            best_diff = diff
            best_kp = kp
    return best_kp

Kp = find_Kp_pid(G_norm, Ti, Td, Tf, 10.0)
K_pid = Kp * (1 + 1/(Ti*s)) * ((Td*s + 1)/(Tf*s + 1))

# 3) Form the open-loop L(s), and the sensitivity S(s), T(s), dist->out
L = G_norm * K_pid
S = 1/(1+L)
T = 1 - S
Gd_cl = Gd_norm * S

# 4) Frequency analysis: Bode
freqs = np.logspace(-2, 3, 300)
magL, phaseL, omegaL = ctl.bode(L, freqs, plot=False)

plt.figure(figsize=(10,6))
plt.subplot(2,1,1)
plt.semilogx(omegaL, 20*np.log10(magL))
plt.ylabel('Magnitude (dB)')
plt.title('PID Open-Loop L(s)')
plt.grid(True)

plt.subplot(2,1,2)
plt.semilogx(omegaL, np.degrees(phaseL))
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Phase (deg)')
plt.grid(True)
plt.tight_layout()
plt.show()

# S, T, Gd*S
magS, _, _ = ctl.bode(S, freqs, plot=False)
magT, _, _ = ctl.bode(T, freqs, plot=False)
magD, _, _ = ctl.bode(Gd_cl, freqs, plot=False)

plt.figure()
plt.semilogx(freqs, 20*np.log10(magS), label='|S|')
plt.semilogx(freqs, 20*np.log10(magT), label='|T|')
plt.semilogx(freqs, 20*np.log10(magD), label='|Gd_norm*S|')
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Magnitude (dB)')
plt.title('Sensitivity, Comp. Sens., Dist->Out')
plt.grid(True)
plt.legend()
plt.show()

# 5) Time-domain: step in reference (T) and step in disturbance (Gd*S)
time = np.linspace(0, 5, 501)
y_ref, t_ref = ctl.step_response(T, time)
y_dist, t_dist = ctl.step_response(Gd_cl, time)

plt.figure(figsize=(10,8))
plt.subplot(2,1,1)
plt.plot(t_ref, y_ref, label='Ref->y_norm')
plt.ylabel('y_norm')
plt.title('PID Controller: Step Responses')
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(t_dist, y_dist, 'r', label='Dist->y_norm')
plt.xlabel('Time (s)')
plt.ylabel('y_norm')
plt.grid(True)
plt.tight_layout()
plt.show()

# 6) Basic metrics
def step_metrics(t, y, lower=0.1, upper=0.9):
    final_val = y[-1]
    t_low, t_up = None, None
    for i in range(len(y)):
        if t_low is None and y[i]>=lower*final_val:
            t_low=t[i]
        if t_up is None and y[i]>=upper*final_val:
            t_up=t[i]
    rise_time = t_up-t_low if (t_low and t_up) else None
    overshoot= (max(y)-final_val)/final_val*100 if final_val!=0 else 0
    return rise_time, overshoot

rtime, ov= step_metrics(t_ref, y_ref)
print(f"PID: Kp={Kp:.3f}, Ti={Ti}, Td={Td}, Tf={Tf}")
print(f" Reference Step: final y_norm={y_ref[-1]:.3f}, rise_time={rtime}, overshoot={ov:.2f}%")

ss_dist= y_dist[-1]
idx15= min(np.searchsorted(t_dist,1.5), len(t_dist)-1)
print(f" Disturbance Step: final y_norm={ss_dist:.3f}, y_norm(1.5s)={y_dist[idx15]:.3f}")
