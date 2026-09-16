
# metrics.py (FULL)
from __future__ import annotations
import numpy as np
from typing import Dict, Any


def compute_metrics(sim: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute controller-agnostic performance metrics.

    PHI-TRACKING UPDATE:
    The tracking error is now:

        e_phi = phi_ref - phi

    because the controlled output is the joint/link angle phi.

    Metrics:
    - IAE  = integral of absolute phi error |e_phi|
    - ITAE = integral of time-weighted absolute phi error t|e_phi|
    - RMS(e_phi)
    - RMS(alpha), max|alpha|
    - RMS(Vcmd)
    - saturation ratio (fraction of time near Vbus)
    """
    t = np.asarray(sim["t"], float)
    x = np.asarray(sim["x"], float)

    theta = x[:, 0]
    phi = x[:, 1]
    phi_ref = np.asarray(sim.get("phi_ref", sim.get("theta_ref", np.zeros_like(phi))), float)

    V = np.asarray(sim["Vcmd"], float)
    Vbus = float(sim["p_nom"].Vbus)

    e = phi_ref - phi
    alpha = theta - phi

    T = float(t[-1] - t[0]) if len(t) > 1 else 1.0

    IAE = float(np.trapz(np.abs(e), t))
    ITAE = float(np.trapz((t - t[0]) * np.abs(e), t))
    e_rms = float(np.sqrt(np.trapz(e**2, t) / max(T, 1e-12)))

    alpha_rms = float(np.sqrt(np.trapz(alpha**2, t) / max(T, 1e-12)))
    alpha_max = float(np.max(np.abs(alpha)))

    V_rms = float(np.sqrt(np.trapz(V**2, t) / max(T, 1e-12)))
    sat_ratio = float(np.mean(np.abs(V) >= 0.99 * Vbus))

    return dict(
        IAE=IAE, ITAE=ITAE, e_rms=e_rms,
        alpha_rms=alpha_rms, alpha_max=alpha_max,
        V_rms=V_rms, sat_ratio=sat_ratio,
    )


def print_metrics(sim: Dict[str, Any]) -> None:
    m = compute_metrics(sim)
    print("\n=== RFJ metrics ===")
    print(f"mode={sim['controller_mode']}  ref={sim['ref_type']}  dist={sim['disturb_kind']}  output=phi")
    print(f"IAE(phi)     = {m['IAE']:.4f} rad*s")
    print(f"ITAE(phi)    = {m['ITAE']:.4f} rad*s^2")
    print(f"RMS(e_phi)   = {m['e_rms']:.4f} rad")
    print(f"RMS(alpha)   = {m['alpha_rms']:.4f} rad")
    print(f"max|alpha|   = {m['alpha_max']:.4f} rad")
    print(f"RMS(Vcmd)    = {m['V_rms']:.4f} V")
    print(f"sat ratio    = {100*m['sat_ratio']:.1f}%")
    print("===================\n")
