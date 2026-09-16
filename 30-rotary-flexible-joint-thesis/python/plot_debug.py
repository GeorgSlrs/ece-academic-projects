
"""
plot_debug.py
=============
Optional plots for deeper understanding.

PHI-TRACKING UPDATE:
- The tracking plot now compares phi_ref, phi_true, and phi_hat.
- theta is still shown because it explains motor-side motion and elastic twist.

Other panels:
- For SMC: plot sliding variable s(t)
- For MIT: plot adaptive gains and sensitivity filters
- For MRAC: plot adaptive parameter estimates
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any


def plot_debug(sim: Dict[str,Any]):
    dbg = sim.get("dbg", [])
    if not dbg:
        print("[plot_debug] No debug log.")
        return

    t_dbg = np.array([d["t"] for d in dbg])

    phi_ref = np.asarray(sim.get("phi_ref", sim.get("theta_ref", np.zeros_like(sim["t"]))), float)

    plt.figure()
    plt.plot(sim["t"], phi_ref, label="phi_ref")
    plt.plot(sim["t"], sim["x"][:, 1], label="phi_true")
    plt.plot(sim["t"], sim["phi_hat"], label="phi_hat", alpha=0.8)
    plt.plot(sim["t"], sim["x"][:, 0], label="theta_true", alpha=0.65)
    plt.grid(True, alpha=0.2)
    plt.legend()
    plt.title("Phi tracking with theta shown for motor-side context")

    mode = str(sim.get("controller_mode", "")).lower()

    if mode == "smc":
        s = np.array([d.get("s", 0.0) for d in dbg])
        alpha = np.array([d.get("alpha", 0.0) for d in dbg])
        plt.figure()
        plt.plot(t_dbg, s, label="s(t)")
        plt.plot(t_dbg, alpha, label="alpha(t)", alpha=0.8)
        plt.grid(True, alpha=0.2)
        plt.legend()
        plt.title("Sliding surface and twist")

    if mode == "mit":
        rows = [d for d in dbg if "Kp_hat" in d]
        if rows:
            t_mit = np.array([d["t"] for d in rows])

            plt.figure()
            plt.plot(t_mit, [d.get("Kp_hat", np.nan) for d in rows], label="Kp_hat")
            plt.plot(t_mit, [d.get("Ki_hat", np.nan) for d in rows], label="Ki_hat")
            plt.plot(t_mit, [d.get("Kd_hat", np.nan) for d in rows], label="Kd_hat")
            plt.plot(t_mit, [d.get("Kr_hat", np.nan) for d in rows], label="Kr_hat")
            plt.plot(t_mit, [d.get("Kalpha_hat", np.nan) for d in rows], label="Kalpha_hat")
            plt.grid(True, alpha=0.2)
            plt.legend()
            plt.title("MIT adaptive gains for phi tracking")

            plt.figure()
            plt.plot(t_mit, [d.get("psi_p", np.nan) for d in rows], label="psi_p")
            plt.plot(t_mit, [d.get("psi_i", np.nan) for d in rows], label="psi_i")
            plt.plot(t_mit, [d.get("psi_d", np.nan) for d in rows], label="psi_d")
            plt.plot(t_mit, [d.get("psi_r", np.nan) for d in rows], label="psi_r")
            plt.plot(t_mit, [d.get("psi_alpha", np.nan) for d in rows], label="psi_alpha")
            plt.grid(True, alpha=0.2)
            plt.legend()
            plt.title("MIT sensitivity filters")

    if mode == "mrac":
        rows = [d for d in dbg if "Th_hat" in d]
        if rows:
            t_mrac = np.array([d["t"] for d in rows])
            Dx_hat = np.vstack([np.asarray(d.get("Dx_hat", [np.nan, np.nan]), float).reshape(-1) for d in rows])
            Th_hat = np.vstack([np.asarray(d.get("Th_hat", np.full(6, np.nan)), float).reshape(-1) for d in rows])

            plt.figure()
            plt.plot(t_mrac, Dx_hat[:, 0], label="Dx_hat[0]")
            if Dx_hat.shape[1] > 1:
                plt.plot(t_mrac, Dx_hat[:, 1], label="Dx_hat[1]")
            plt.grid(True, alpha=0.2)
            plt.legend()
            plt.title("MRAC Dx_hat for phi tracking")

            plt.figure()
            for j in range(Th_hat.shape[1]):
                plt.plot(t_mrac, Th_hat[:, j], label=f"Th_hat[{j}]")
            plt.grid(True, alpha=0.2)
            plt.legend()
            plt.title("MRAC basis weights")

    plt.show()
