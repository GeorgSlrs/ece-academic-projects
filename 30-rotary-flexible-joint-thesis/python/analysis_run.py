"""
analysis_run.py
==============
A "big" analysis script that generates a fixed set of 20 plots.

PHI-TRACKING UPDATE:
- The main tracking error is e_phi = phi_ref - phi.
- theta is still plotted because it is the motor-side coordinate, but it is no longer the controlled output.

Inputs:
- sim: dictionary returned by simulate.simulate_L2()

Outputs:
- 20 matplotlib figures:
  Time domain:
    1) Angles (phi_ref, phi, phi_hat, theta, theta_hat)
    2) Error e(t) and twist alpha(t)
    3) Velocities (dtheta, dphi, dalpha)
    4) Motor current i(t)
    5) Torques (motor, spring, damper, disturbance)
    6) Command signals (Vcmd_cmd, Vcmd applied, duty)
    7) Disturbance tauL(t)
    8) Measurement errors + histograms
    9) Phase portraits
   10) FFT of alpha and error

  Linear (around x=0,u=0):
   11) Bode of phi/Vcmd
   12) Nyquist of phi/Vcmd
   13) Root locus (u=-k*phi and u=-k*alpha)
   14) Poles in s-plane and z-plane

  Extra diagnostics (always generated so the total count is always 20):
   15) Zoomed tracking/transient view
   16) Command-rate + duty-rate diagnostics
   17) Energy / power diagnostics
   18) Cumulative performance indices
   19) Controller-specific / adaptive diagnostics panel
   20) Summary dashboard

Usage:
- CLI: python run_all.py --analysis --noAnim
- GUI: click "Plots" button or close windows (depending on your GUI wiring)

Note:
- "nominal parameters" for MIT/MRAC here refer to the *nominal adaptive parameters*
  (e.g. MIT nominal k=1, MRAC nominal augmentation params=0).
  These are controller parameters, not physical parameters like Ks/Cs.
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple

from rfj_dynamics import plant_rhs
from analysis_tools import (
    linearize_finite_diff,
    poles,
    damping_from_poles,
    ctrb,
    obsv,
    freqresp_ss,
    root_locus_output_feedback,
    c2d_zoh,
)


# ----------------------------
# small helpers
# ----------------------------
def _safe_dt(t: np.ndarray) -> float:
    """Estimate a reasonable dt from a time array t."""
    if len(t) < 2:
        return 1.0
    dt = float(np.median(np.diff(t)))
    return max(dt, 1e-9)


def _fft_mag(x: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return frequency axis (Hz) and magnitude spectrum of a real signal.
    This is a simple diagnostic, not a super-precise spectral estimator.
    """
    x = np.asarray(x, float)
    x = x - np.mean(x)
    N = len(x)
    if N < 16:
        return np.array([0.0]), np.array([0.0])
    window = np.hanning(N)
    X = np.fft.rfft(x * window)
    f = np.fft.rfftfreq(N, d=dt)
    mag = np.abs(X) / max(N, 1)
    return f, mag


def _maybe_save(fig, save: bool, outdir: str, name: str) -> None:
    """Save a figure if save=True."""
    if not save:
        return
    os.makedirs(outdir, exist_ok=True)
    fig.savefig(os.path.join(outdir, name), dpi=170)


def _running_rms(x: np.ndarray, win: int) -> np.ndarray:
    """Simple running RMS using a rectangular window."""
    x = np.asarray(x, float)
    win = int(max(win, 1))
    if win == 1 or x.size == 0:
        return np.sqrt(np.maximum(x * x, 0.0))
    ker = np.ones(win, float) / float(win)
    return np.sqrt(np.maximum(np.convolve(x * x, ker, mode="same"), 0.0))


# ----------------------------
# main entry
# ----------------------------
def run_analysis(sim: Dict[str, Any], save: bool = False, outdir: str = "analysis_out", block: bool = True) -> None:
    # ---- pull signals out of sim dict ----
    t = np.asarray(sim["t"], float)
    x = np.asarray(sim["x"], float)

    theta = x[:, 0]
    phi = x[:, 1]
    dtheta = x[:, 2]
    dphi = x[:, 3]
    i = x[:, 4]

    alpha = theta - phi
    dalpha = dtheta - dphi

    phi_ref = np.asarray(sim.get("phi_ref", sim.get("theta_ref", np.zeros_like(phi))), float)
    theta_hat = np.asarray(sim.get("theta_hat", np.zeros_like(theta)), float)
    phi_hat = np.asarray(sim.get("phi_hat", np.zeros_like(phi)), float)
    alpha_hat = np.asarray(sim.get("alpha_hat", theta_hat - phi_hat), float)

    Vcmd = np.asarray(sim.get("Vcmd", np.zeros_like(t)), float)
    Vcmd_cmd = np.asarray(sim.get("Vcmd_cmd", Vcmd), float)
    duty = np.asarray(sim.get("duty", np.zeros_like(t)), float)

    tauL = np.asarray(sim.get("tauL", np.zeros_like(t)), float)

    # errors
    e = phi_ref - phi
    e_meas_theta = theta_hat - theta
    e_meas_phi = phi_hat - phi
    e_meas_alpha = alpha_hat - alpha

    # torques (recomputed from true params)
    p_true = sim["p_true"]
    tau_m = p_true.Kt * i
    tau_spring = p_true.Ks * alpha + p_true.Ks3 * (alpha ** 3)
    tau_damper = p_true.Cs * dalpha

    dt = _safe_dt(t)

    # -------------------------
    # (1) Angles
    # -------------------------
    fig1 = plt.figure(figsize=(11, 6.5))
    ax = fig1.add_subplot(1, 1, 1)
    ax.plot(t, phi_ref, label="phi_ref")
    ax.plot(t, theta, label="theta")
    ax.plot(t, theta_hat, "--", label="theta_hat")
    ax.plot(t, phi, label="phi")
    ax.plot(t, phi_hat, "--", label="phi_hat")
    ax.plot(t, alpha_hat, ":", label="alpha_hat")
    ax.grid(True)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("angle [rad]")
    ax.set_title("Angles")
    ax.legend()
    _maybe_save(fig1, save, outdir, "01_angles.png")

    # -------------------------
    # (2) Error + alpha
    # -------------------------
    fig2 = plt.figure(figsize=(11, 6.5))
    ax1 = fig2.add_subplot(2, 1, 1)
    ax1.plot(t, e, label="e = phi_ref - phi")
    ax1.grid(True)
    ax1.set_ylabel("error [rad]")
    ax1.legend()

    ax2 = fig2.add_subplot(2, 1, 2)
    ax2.plot(t, alpha, label="alpha = theta - phi")
    ax2.grid(True)
    ax2.set_xlabel("time [s]")
    ax2.set_ylabel("twist [rad]")
    ax2.legend()
    fig2.suptitle("Phi tracking error and twist")
    _maybe_save(fig2, save, outdir, "02_error_alpha.png")

    # -------------------------
    # (3) Velocities
    # -------------------------
    fig3 = plt.figure(figsize=(11, 6.0))
    ax = fig3.add_subplot(1, 1, 1)
    ax.plot(t, dtheta, label="dtheta")
    ax.plot(t, dphi, label="dphi")
    ax.plot(t, dalpha, label="dalpha")
    ax.grid(True)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("rad/s")
    ax.set_title("Angular velocities")
    ax.legend()
    _maybe_save(fig3, save, outdir, "03_velocities.png")

    # -------------------------
    # (4) Current
    # -------------------------
    fig4 = plt.figure(figsize=(11, 5.2))
    ax = fig4.add_subplot(1, 1, 1)
    ax.plot(t, i, label="current i")
    ax.grid(True)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("A")
    ax.set_title("Motor current")
    ax.legend()
    _maybe_save(fig4, save, outdir, "04_current.png")

    # -------------------------
    # (5) Torques
    # -------------------------
    fig5 = plt.figure(figsize=(11, 6.0))
    ax = fig5.add_subplot(1, 1, 1)
    ax.plot(t, tau_m, label="tau_m = Kt*i")
    ax.plot(t, tau_spring, label="tau_spring")
    ax.plot(t, tau_damper, label="tau_damper")
    ax.plot(t, tauL, label="tauL disturbance")
    ax.grid(True)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("N*m")
    ax.set_title("Torques")
    ax.legend()
    _maybe_save(fig5, save, outdir, "05_torques.png")

    # -------------------------
    # (6) Command signals
    # -------------------------
    fig6 = plt.figure(figsize=(11, 6.5))
    ax1 = fig6.add_subplot(2, 1, 1)
    ax1.plot(t, Vcmd_cmd, label="Vcmd_cmd (controller)")
    ax1.plot(t, Vcmd, label="Vcmd applied")
    ax1.grid(True)
    ax1.set_ylabel("V")
    ax1.legend()

    ax2 = fig6.add_subplot(2, 1, 2)
    ax2.plot(t, duty, label="duty")
    ax2.grid(True)
    ax2.set_xlabel("time [s]")
    ax2.set_ylabel("[-]")
    ax2.legend()
    fig6.suptitle("Driver / command signals")
    _maybe_save(fig6, save, outdir, "06_commands.png")

    # -------------------------
    # (7) Disturbance only
    # -------------------------
    fig7 = plt.figure(figsize=(11, 4.8))
    ax = fig7.add_subplot(1, 1, 1)
    ax.plot(t, tauL, label="tauL(t)")
    ax.grid(True)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("N*m")
    ax.set_title("Disturbance torque")
    ax.legend()
    _maybe_save(fig7, save, outdir, "07_tauL.png")

    # -------------------------
    # (8) Measurement errors + hist
    # -------------------------
    fig8 = plt.figure(figsize=(12.0, 7.2))
    ax1 = fig8.add_subplot(2, 3, 1)
    ax1.plot(t, e_meas_theta, label="theta_hat - theta")
    ax1.grid(True); ax1.legend(); ax1.set_title("Theta measurement error")

    ax2 = fig8.add_subplot(2, 3, 2)
    ax2.plot(t, e_meas_phi, label="phi_hat - phi")
    ax2.grid(True); ax2.legend(); ax2.set_title("Phi measurement error")

    ax3 = fig8.add_subplot(2, 3, 3)
    ax3.plot(t, e_meas_alpha, label="alpha_hat - alpha")
    ax3.grid(True); ax3.legend(); ax3.set_title("Alpha measurement error")

    ax4 = fig8.add_subplot(2, 3, 4)
    ax4.hist(e_meas_theta, bins=40)
    ax4.grid(True); ax4.set_title("Histogram: theta error")

    ax5 = fig8.add_subplot(2, 3, 5)
    ax5.hist(e_meas_phi, bins=40)
    ax5.grid(True); ax5.set_title("Histogram: phi error")

    ax6 = fig8.add_subplot(2, 3, 6)
    ax6.hist(e_meas_alpha, bins=40)
    ax6.grid(True); ax6.set_title("Histogram: alpha error")

    fig8.suptitle("Measurement noise diagnostics")
    _maybe_save(fig8, save, outdir, "08_meas_noise.png")

    # -------------------------
    # (9) Phase portraits
    # -------------------------
    fig9 = plt.figure(figsize=(11, 5.5))
    ax1 = fig9.add_subplot(1, 2, 1)
    ax1.plot(alpha, dalpha)
    ax1.grid(True)
    ax1.set_xlabel("alpha [rad]")
    ax1.set_ylabel("dalpha [rad/s]")
    ax1.set_title("Phase: alpha vs dalpha")

    ax2 = fig9.add_subplot(1, 2, 2)
    ax2.plot(theta, dtheta)
    ax2.grid(True)
    ax2.set_xlabel("theta [rad]")
    ax2.set_ylabel("dtheta [rad/s]")
    ax2.set_title("Phase: theta vs dtheta")
    _maybe_save(fig9, save, outdir, "09_phase_portraits.png")

    # -------------------------
    # (10) FFT spectra
    # -------------------------
    f_a, mag_a = _fft_mag(alpha, dt)
    f_e, mag_e = _fft_mag(e, dt)

    fig10 = plt.figure(figsize=(11, 6.0))
    ax1 = fig10.add_subplot(2, 1, 1)
    ax1.semilogy(f_a, np.maximum(mag_a, 1e-12))
    ax1.grid(True, which="both")
    ax1.set_xlabel("Hz")
    ax1.set_ylabel("|FFT(alpha)|")
    ax1.set_title("FFT magnitude: alpha")

    ax2 = fig10.add_subplot(2, 1, 2)
    ax2.semilogy(f_e, np.maximum(mag_e, 1e-12))
    ax2.grid(True, which="both")
    ax2.set_xlabel("Hz")
    ax2.set_ylabel("|FFT(error)|")
    ax2.set_title("FFT magnitude: phi tracking error")
    _maybe_save(fig10, save, outdir, "10_fft.png")

    # ============================================================
    # Linearization + classical control plots
    # ============================================================
    x0 = np.zeros(5)
    u0 = np.zeros(2)  # [V_cmd, tau_L]

    def f_lin(xx, uu):
        return plant_rhs(xx, V_cmd=float(uu[0]), tau_L=float(uu[1]), p=p_true)

    A, B = linearize_finite_diff(f_lin, x0, u0)
    Bv = B[:, [0]]
    C_phi = np.array([[0, 1, 0, 0, 0]], float)
    C_alpha = np.array([[1, -1, 0, 0, 0]], float)
    D0 = np.array([[0.0]], float)

    lam = poles(A)
    wn_lin, zeta_lin = damping_from_poles(lam)

    print("\n==== Linear model around x=0,u=0 ====")
    np.set_printoptions(precision=4, suppress=True)
    print("A=\n", A)
    print("Bv=\n", Bv)
    print("Poles:")
    for i_, li in enumerate(lam):
        print(f"  p{i_+1}: {li.real:+.4f} {li.imag:+.4f}j   wn={wn_lin[i_]:.3f}  zeta={zeta_lin[i_]:.3f}")

    rank_c = np.linalg.matrix_rank(ctrb(A, Bv))
    rank_o = np.linalg.matrix_rank(obsv(A, C_phi))
    print(f"ctrb rank (Vcmd) = {rank_c}/{A.shape[0]}")
    print(f"obsv rank (phi)= {rank_o}/{A.shape[0]}")
    print("====================================\n")

    # (11) Bode
    w = np.logspace(-1, 2.5, 600)
    G = freqresp_ss(A, Bv, C_phi, D0, w)

    fig11 = plt.figure(figsize=(11, 7.0))
    axm = fig11.add_subplot(2, 1, 1)
    axp = fig11.add_subplot(2, 1, 2)

    mag_db = 20 * np.log10(np.maximum(np.abs(G), 1e-12))
    phase_deg = np.unwrap(np.angle(G)) * 180 / np.pi

    axm.semilogx(w, mag_db)
    axm.grid(True, which="both")
    axm.set_ylabel("mag [dB]")
    axm.set_title("Bode: phi / Vcmd")

    axp.semilogx(w, phase_deg)
    axp.grid(True, which="both")
    axp.set_xlabel("ω [rad/s]")
    axp.set_ylabel("phase [deg]")
    _maybe_save(fig11, save, outdir, "11_bode.png")

    # (12) Nyquist
    fig12 = plt.figure(figsize=(6.7, 6.7))
    axn = fig12.add_subplot(1, 1, 1)
    axn.plot(G.real, G.imag, label="Nyquist")
    axn.plot(G.real, -G.imag, alpha=0.25)
    axn.scatter([-1], [0], marker="x", s=90)
    axn.grid(True)
    axn.axis("equal")
    axn.set_title("Nyquist: phi/Vcmd")
    axn.set_xlabel("Re")
    axn.set_ylabel("Im")
    _maybe_save(fig12, save, outdir, "12_nyquist.png")

    # (13) Root locus
    k_list = np.logspace(-3, 3, 300)
    RL_phi = root_locus_output_feedback(A, Bv, C_phi, k_list)
    RL_alpha = root_locus_output_feedback(A, Bv, C_alpha, k_list)

    fig13 = plt.figure(figsize=(11, 5.0))
    axr1 = fig13.add_subplot(1, 2, 1)
    axr2 = fig13.add_subplot(1, 2, 2)

    for j in range(RL_phi.shape[1]):
        axr1.plot(RL_phi[:, j].real, RL_phi[:, j].imag)
    axr1.axvline(0, color="k", lw=0.8)
    axr1.grid(True)
    axr1.set_title("Root locus: u = -k*phi")
    axr1.set_xlabel("Re")
    axr1.set_ylabel("Im")

    for j in range(RL_alpha.shape[1]):
        axr2.plot(RL_alpha[:, j].real, RL_alpha[:, j].imag)
    axr2.axvline(0, color="k", lw=0.8)
    axr2.grid(True)
    axr2.set_title("Root locus: u = -k*alpha")
    axr2.set_xlabel("Re")
    axr2.set_ylabel("Im")
    _maybe_save(fig13, save, outdir, "13_root_locus.png")

    # (14) Poles in s-plane and z-plane
    Ad, Bd = c2d_zoh(A, Bv, float(sim["p_nom"].Ts_ctrl))
    z_poles = np.linalg.eigvals(Ad)

    fig14 = plt.figure(figsize=(11, 5.0))
    ax1 = fig14.add_subplot(1, 2, 1)
    ax1.scatter(lam.real, lam.imag)
    ax1.axvline(0, color="k", lw=0.8)
    ax1.grid(True)
    ax1.set_title("Poles in s-plane (continuous)")
    ax1.set_xlabel("Re")
    ax1.set_ylabel("Im")

    ax2 = fig14.add_subplot(1, 2, 2)
    ax2.scatter(z_poles.real, z_poles.imag)
    ang = np.linspace(0, 2*np.pi, 400)
    ax2.plot(np.cos(ang), np.sin(ang), "k--", lw=1)
    ax2.grid(True)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_title("Poles in z-plane (discrete)")
    ax2.set_xlabel("Re")
    ax2.set_ylabel("Im")
    _maybe_save(fig14, save, outdir, "14_poles.png")

    print("Discrete poles (ZOH):")
    for i_, zi in enumerate(z_poles):
        print(f"  z{i_+1}: {zi.real:+.4f} {zi.imag:+.4f}j  |z|={abs(zi):.4f}")
    print()

    # ============================================================
    # Extra diagnostics to make the total plot count fixed at 20
    # ============================================================
    mode = str(sim.get("controller_mode", "")).lower().strip()
    dbg = sim.get("dbg", [])

    # (15) Zoomed tracking / transient details
    t_end_zoom = min(float(t[-1]), max(1.0, float(t[-1]) * 0.30))
    mask_zoom = t <= t_end_zoom
    if not np.any(mask_zoom):
        mask_zoom = slice(None)

    fig15 = plt.figure(figsize=(11, 7.0))
    ax1 = fig15.add_subplot(3, 1, 1)
    ax1.plot(t[mask_zoom], phi_ref[mask_zoom], label="phi_ref")
    ax1.plot(t[mask_zoom], theta[mask_zoom], label="theta")
    ax1.plot(t[mask_zoom], phi[mask_zoom], label="phi")
    ax1.grid(True)
    ax1.set_ylabel("rad")
    ax1.set_title("Transient zoom")
    ax1.legend(ncol=3, fontsize=8)

    ax2 = fig15.add_subplot(3, 1, 2)
    ax2.plot(t[mask_zoom], e[mask_zoom], label="phi tracking error")
    ax2.axhline(0.0, color="k", lw=0.8)
    ax2.grid(True)
    ax2.set_ylabel("rad")
    ax2.legend(fontsize=8)

    ax3 = fig15.add_subplot(3, 1, 3)
    ax3.plot(t[mask_zoom], alpha[mask_zoom], label="twist alpha")
    ax3.axhline(0.0, color="k", lw=0.8)
    ax3.grid(True)
    ax3.set_xlabel("time [s]")
    ax3.set_ylabel("rad")
    ax3.legend(fontsize=8)
    _maybe_save(fig15, save, outdir, "15_transient_zoom.png")

    # (16) Command-rate + duty-rate diagnostics
    dV = np.gradient(Vcmd, dt) if len(Vcmd) > 1 else np.zeros_like(Vcmd)
    dDuty = np.gradient(duty, dt) if len(duty) > 1 else np.zeros_like(duty)

    fig16 = plt.figure(figsize=(11, 7.0))
    ax1 = fig16.add_subplot(2, 2, 1)
    ax1.plot(t, Vcmd, label="Vcmd")
    ax1.plot(t, Vcmd_cmd, label="Vcmd_cmd", alpha=0.8)
    ax1.grid(True)
    ax1.set_ylabel("V")
    ax1.set_title("Command signals")
    ax1.legend(fontsize=8)

    ax2 = fig16.add_subplot(2, 2, 2)
    ax2.plot(t, dV, label="dVcmd/dt")
    ax2.grid(True)
    ax2.set_ylabel("V/s")
    ax2.set_title("Command rate")
    ax2.legend(fontsize=8)

    ax3 = fig16.add_subplot(2, 2, 3)
    ax3.plot(t, duty, label="duty")
    ax3.plot(t, dDuty, label="dduty/dt", alpha=0.85)
    ax3.grid(True)
    ax3.set_xlabel("time [s]")
    ax3.set_ylabel("[-], [-/s]")
    ax3.set_title("Duty and duty-rate")
    ax3.legend(fontsize=8)

    ax4 = fig16.add_subplot(2, 2, 4)
    ax4.hist(Vcmd, bins=40)
    ax4.grid(True)
    ax4.set_xlabel("Vcmd [V]")
    ax4.set_title("Histogram: applied command")
    _maybe_save(fig16, save, outdir, "16_command_rate.png")

    # (17) Energy / power diagnostics
    spring_energy = 0.5 * p_true.Ks * alpha**2 + 0.25 * p_true.Ks3 * alpha**4
    kin_motor = 0.5 * p_true.Jm * dtheta**2
    kin_link = 0.5 * p_true.Jl * dphi**2
    copper_loss = p_true.R * i**2
    elec_power = Vcmd * i
    mech_power = tau_m * dtheta

    fig17 = plt.figure(figsize=(11, 6.5))
    ax1 = fig17.add_subplot(2, 1, 1)
    ax1.plot(t, spring_energy, label="spring energy")
    ax1.plot(t, kin_motor, label="motor kinetic")
    ax1.plot(t, kin_link, label="link kinetic")
    ax1.grid(True)
    ax1.set_ylabel("J")
    ax1.set_title("Energy-like diagnostics")
    ax1.legend(fontsize=8)

    ax2 = fig17.add_subplot(2, 1, 2)
    ax2.plot(t, elec_power, label="electrical power V*i")
    ax2.plot(t, mech_power, label="mechanical power tau_m*dtheta")
    ax2.plot(t, copper_loss, label="copper loss R*i^2")
    ax2.grid(True)
    ax2.set_xlabel("time [s]")
    ax2.set_ylabel("W")
    ax2.legend(fontsize=8)
    _maybe_save(fig17, save, outdir, "17_energy_power.png")

    # (18) Cumulative performance indices
    abs_e = np.abs(e)
    sq_e = e**2
    iae = np.cumsum(abs_e) * dt
    ise = np.cumsum(sq_e) * dt
    itae = np.cumsum(t * abs_e) * dt
    itse = np.cumsum(t * sq_e) * dt

    fig18 = plt.figure(figsize=(11, 6.8))
    ax1 = fig18.add_subplot(2, 1, 1)
    ax1.plot(t, iae, label="IAE")
    ax1.plot(t, ise, label="ISE")
    ax1.grid(True)
    ax1.set_ylabel("index")
    ax1.set_title("Cumulative performance indices")
    ax1.legend(fontsize=8)

    ax2 = fig18.add_subplot(2, 1, 2)
    ax2.plot(t, itae, label="ITAE")
    ax2.plot(t, itse, label="ITSE")
    ax2.grid(True)
    ax2.set_xlabel("time [s]")
    ax2.set_ylabel("time-weighted index")
    ax2.legend(fontsize=8)
    _maybe_save(fig18, save, outdir, "18_cost_indices.png")

    # (19) Controller-specific / adaptive diagnostics panel
    fig19 = plt.figure(figsize=(11, 7.0))
    ax1 = fig19.add_subplot(2, 2, 1)
    ax2 = fig19.add_subplot(2, 2, 2)
    ax3 = fig19.add_subplot(2, 2, 3)
    ax4 = fig19.add_subplot(2, 2, 4)

    if mode == "mit" and isinstance(dbg, list) and len(dbg) > 5:
        rows = [row for row in dbg if "Kp_hat" in row]
        t_dbg = np.asarray([row.get("t", 0.0) for row in rows], float)

        Kp_hat = np.asarray([row.get("Kp_hat", np.nan) for row in rows], float)
        Ki_hat = np.asarray([row.get("Ki_hat", np.nan) for row in rows], float)
        Kd_hat = np.asarray([row.get("Kd_hat", np.nan) for row in rows], float)
        Kr_hat = np.asarray([row.get("Kr_hat", np.nan) for row in rows], float)
        Kalpha_hat = np.asarray([row.get("Kalpha_hat", np.nan) for row in rows], float)

        Kp_nom = np.asarray([row.get("Kp_nom", np.nan) for row in rows], float)
        Ki_nom = np.asarray([row.get("Ki_nom", np.nan) for row in rows], float)
        Kd_nom = np.asarray([row.get("Kd_nom", np.nan) for row in rows], float)
        Kr_nom = np.asarray([row.get("Kr_nom", np.nan) for row in rows], float)
        Kalpha_nom = np.asarray([row.get("Kalpha_nom", np.nan) for row in rows], float)

        ax1.plot(t_dbg, Kp_hat, label="Kp_hat")
        ax1.plot(t_dbg, Ki_hat, label="Ki_hat")
        ax1.plot(t_dbg, Kd_hat, label="Kd_hat")
        ax1.plot(t_dbg, Kr_hat, label="Kr_hat")
        ax1.plot(t_dbg, Kalpha_hat, label="Kalpha_hat")
        ax1.grid(True)
        ax1.set_title("MIT adaptive gains")
        ax1.legend(fontsize=7, ncol=2)

        ax2.plot(t_dbg, Kp_nom, "--", label="Kp_nom")
        ax2.plot(t_dbg, Ki_nom, "--", label="Ki_nom")
        ax2.plot(t_dbg, Kd_nom, "--", label="Kd_nom")
        ax2.plot(t_dbg, Kr_nom, "--", label="Kr_nom")
        ax2.plot(t_dbg, Kalpha_nom, "--", label="Kalpha_nom")
        ax2.grid(True)
        ax2.set_title("MIT nominal gains")
        ax2.legend(fontsize=7, ncol=2)

        psi_p = np.asarray([row.get("psi_p", np.nan) for row in rows], float)
        psi_i = np.asarray([row.get("psi_i", np.nan) for row in rows], float)
        psi_d = np.asarray([row.get("psi_d", np.nan) for row in rows], float)
        psi_r = np.asarray([row.get("psi_r", np.nan) for row in rows], float)
        psi_alpha = np.asarray([row.get("psi_alpha", np.nan) for row in rows], float)
        ax3.plot(t_dbg, psi_p, label="psi_p")
        ax3.plot(t_dbg, psi_i, label="psi_i")
        ax3.plot(t_dbg, psi_d, label="psi_d")
        ax3.plot(t_dbg, psi_r, label="psi_r")
        ax3.plot(t_dbg, psi_alpha, label="psi_alpha")
        ax3.grid(True)
        ax3.set_title("MIT sensitivity filters")
        ax3.legend(fontsize=7, ncol=2)

        ax4.axis("off")
        ax4.text(0.02, 0.98,
                 f"controller = {mode}\n\n"
                 f"final Kp_hat = {float(Kp_hat[-1]):.4f}\n"
                 f"final Ki_hat = {float(Ki_hat[-1]):.4f}\n"
                 f"final Kd_hat = {float(Kd_hat[-1]):.4f}\n"
                 f"final Kr_hat = {float(Kr_hat[-1]):.4f}\n"
                 f"final Kalpha_hat = {float(Kalpha_hat[-1]):.4f}\n"
                 f"final IAE = {float(iae[-1]):.4f}\n"
                 f"final ISE = {float(ise[-1]):.4f}",
                 va="top", family="monospace", fontsize=10)

    elif mode == "mrac" and isinstance(dbg, list) and len(dbg) > 5:
        t_dbg = []
        Dx_list = []
        Dr_list = []
        Th_list = []
        for row in dbg:
            if "Dx_hat" in row and "Dr_hat" in row and "Th_hat" in row:
                t_dbg.append(row.get("t", 0.0))
                Dx_list.append(np.asarray(row["Dx_hat"], float).reshape(-1))
                Dr_list.append(np.asarray(row["Dr_hat"], float).reshape(-1))
                Th_list.append(np.asarray(row["Th_hat"], float).reshape(-1))

        t_dbg = np.asarray(t_dbg, float)
        Dx_arr = np.vstack(Dx_list)
        Dr_arr = np.vstack(Dr_list)
        Th_arr = np.vstack(Th_list)

        ax1.plot(t_dbg, Dx_arr[:, 0], label="Dx_hat[0]")
        if Dx_arr.shape[1] > 1:
            ax1.plot(t_dbg, Dx_arr[:, 1], label="Dx_hat[1]")
        ax1.grid(True)
        ax1.set_title("MRAC Dx_hat")
        ax1.legend(fontsize=8)

        ax2.plot(t_dbg, Dr_arr[:, 0], label="Dr_hat")
        ax2.grid(True)
        ax2.set_title("MRAC Dr_hat")
        ax2.legend(fontsize=8)

        for j in range(Th_arr.shape[1]):
            ax3.plot(t_dbg, Th_arr[:, j], label=f"Th_hat[{j}]")
        ax3.grid(True)
        ax3.set_title("MRAC basis weights")
        ax3.legend(fontsize=7, ncol=2)

        ax4.axis("off")
        ax4.text(0.02, 0.98,
                 f"controller = {mode}\n\n"
                 f"||Dx_hat(final)|| = {float(np.linalg.norm(Dx_arr[-1])):.4f}\n"
                 f"||Dr_hat(final)|| = {float(np.linalg.norm(Dr_arr[-1])):.4f}\n"
                 f"||Th_hat(final)|| = {float(np.linalg.norm(Th_arr[-1])):.4f}\n"
                 f"final IAE = {float(iae[-1]):.4f}\n"
                 f"final ISE = {float(ise[-1]):.4f}",
                 va="top", family="monospace", fontsize=10)

    else:
        # Non-adaptive modes still get a full figure, so the count stays fixed at 20.
        ax1.plot(t, e, label="phi tracking error")
        ax1.grid(True)
        ax1.set_title("Phi tracking error")
        ax1.legend(fontsize=8)

        ax2.plot(t, alpha, label="twist alpha")
        ax2.grid(True)
        ax2.set_title("Elastic twist")
        ax2.legend(fontsize=8)

        ax3.plot(t, Vcmd, label="Vcmd")
        ax3.plot(t, tauL, label="tauL", alpha=0.85)
        ax3.grid(True)
        ax3.set_title("Command vs disturbance")
        ax3.legend(fontsize=8)

        ax4.axis("off")
        ax4.text(0.02, 0.98,
                 f"controller = {mode or 'unknown'}\n\n"
                 f"No adaptive parameter log for this mode.\n"
                 f"final IAE = {float(iae[-1]):.4f}\n"
                 f"final ISE = {float(ise[-1]):.4f}\n"
                 f"max |e_phi| = {float(np.max(np.abs(e))):.4f}\n"
                 f"max |alpha| = {float(np.max(np.abs(alpha))):.4f}",
                 va="top", family="monospace", fontsize=10)

    fig19.suptitle("Controller-specific diagnostics")
    _maybe_save(fig19, save, outdir, "19_controller_specific.png")

    # (20) Summary dashboard
    rms_win = max(5, int(0.05 * len(t)))
    e_rms = _running_rms(e, rms_win)
    alpha_rms = _running_rms(alpha, rms_win)
    v_rms = _running_rms(Vcmd, rms_win)

    fig20 = plt.figure(figsize=(11, 7.0))
    ax1 = fig20.add_subplot(2, 2, 1)
    ax1.plot(t, e_rms, label="RMS(error)")
    ax1.plot(t, alpha_rms, label="RMS(alpha)")
    ax1.grid(True)
    ax1.set_title("Running RMS")
    ax1.legend(fontsize=8)

    ax2 = fig20.add_subplot(2, 2, 2)
    ax2.scatter(phi_ref, phi, s=10, alpha=0.6)
    ax2.grid(True)
    ax2.set_xlabel("phi_ref [rad]")
    ax2.set_ylabel("phi [rad]")
    ax2.set_title("Phi reference vs output")

    ax3 = fig20.add_subplot(2, 2, 3)
    ax3.plot(t, v_rms, label="RMS(Vcmd)")
    ax3.grid(True)
    ax3.set_xlabel("time [s]")
    ax3.set_ylabel("V")
    ax3.set_title("Running RMS of command")
    ax3.legend(fontsize=8)

    ax4 = fig20.add_subplot(2, 2, 4)
    ax4.axis("off")
    summary = (
        f"controller = {mode or 'unknown'}\n"
        f"samples = {len(t)}\n"
        f"dt ≈ {dt:.6f} s\n"
        f"max |e_phi| = {float(np.max(np.abs(e))):.4f} rad\n"
        f"RMS(e_phi) = {float(np.sqrt(np.mean(e**2))):.4f} rad\n"
        f"max |alpha| = {float(np.max(np.abs(alpha))):.4f} rad\n"
        f"max |Vcmd| = {float(np.max(np.abs(Vcmd))):.4f} V\n"
        f"max |tauL| = {float(np.max(np.abs(tauL))):.4f} N·m\n"
        f"ctrb rank = {rank_c}/{A.shape[0]}\n"
        f"obsv rank = {rank_o}/{A.shape[0]}"
    )
    ax4.text(0.02, 0.98, summary, va="top", family="monospace", fontsize=10)
    fig20.suptitle("Summary dashboard")
    _maybe_save(fig20, save, outdir, "20_summary_dashboard.png")

    plt.show(block=block)
