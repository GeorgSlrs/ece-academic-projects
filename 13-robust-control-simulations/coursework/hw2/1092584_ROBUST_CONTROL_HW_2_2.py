import numpy as np
import matplotlib.pyplot as plt

# 1) Frequency grid: 0.01 to 100 rad/s, log-spaced
omega = np.logspace(-2, 2, 1000)
s = 1j * omega

# 2) Nominal plant G_nom(s) = 2*(s + 1.5) / (8*s + 1)
G_nom = 2 * (s + 1.5) / (8 * s + 1)

# 3) Define weight functions w(s)
weights = {
    'Original w_I(s)=0.5/(s+1.5)':  0.5 / (s + 1.5),
    'Constant w_C(s)=1/3':          np.ones_like(s) * (1/3),
    'Alternate w_A(s)=(0.5*(s/0.5+1))/(s+1.5)': (0.5 * (s/0.5 + 1)) / (s + 1.5),
    'Band-limited w_B(s)': np.where(omega < 10,
                                     0.5 / (s + 1.5),
                                     0.1)
}

# 4) Define controllers
controllers = {
    'PI: k=1.0, τ=0.5':            1.0 * (1 + 1/(0.5 * s)),
    'PID: k=0.8, τ=0.2, Td=0.05':   0.8 * (1 + 1/(0.2 * s) + 0.05 * s)
}

# 5) Create subplots: top for |w·T|, bottom for |T|
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Top: small-gain products |w(s)*T(s)|
for ctrl_name, K in controllers.items():
    L = G_nom * K
    T = L / (1 + L)
    for w_name, w in weights.items():
        mag_db = 20 * np.log10(np.abs(w * T))
        ax1.semilogx(omega, mag_db, label=f'{ctrl_name}, {w_name}')

ax1.axhline(0, color='k', linestyle='--', label='0 dB threshold')
ax1.set_ylabel('20·log₁₀|w(s)·T(s)| [dB]')
ax1.set_title('Small-Gain Robust-Stability Check')
ax1.legend(fontsize='small', ncol=2)
ax1.grid(True, which='both', ls=':')

# Bottom: complementary sensitivity |T(s)|
for ctrl_name, K in controllers.items():
    L = G_nom * K
    T = L / (1 + L)
    mag_db = 20 * np.log10(np.abs(T))
    ax2.semilogx(omega, mag_db, label=f'|T| {ctrl_name}')

ax2.axhline(-6, color='r', linestyle='--', label='-6 dB reference')
ax2.set_ylabel('20·log₁₀|T(jω)| [dB]')
ax2.set_xlabel('Frequency ω [rad/s]')
ax2.set_title('Complementary Sensitivity Magnitude')
ax2.legend(fontsize='small')
ax2.grid(True, which='both', ls=':')

plt.tight_layout()
plt.show()
