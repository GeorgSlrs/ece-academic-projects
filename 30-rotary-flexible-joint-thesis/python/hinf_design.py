
"""
hinf_design.py
==============
H∞ mixed-sensitivity design (πραγματικός H∞ controller).

The design does:
  K(s) = mixsyn(G, W1, W2, W3)
and then discretizes the continuous controller K(s) to K(z) with ZOH.

IMPORTANT PHI-TRACKING UPDATE:
- The default plant output is now phi, the link/joint angle.
- theta is still available only for comparison experiments.
- alpha is still available for a dedicated twist-suppression design.

So the default H∞ controller is synthesized for:

    G_phi(s) = phi(s) / V_cmd(s)

not theta(s) / V_cmd(s).
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any

from rfj_params import RFJParams
from rfj_dynamics import plant_rhs
from analysis_tools import linearize_finite_diff, c2d_zoh


def _require_control():
    try:
        import control as ct  # type: ignore
        return ct
    except Exception as e:
        raise ImportError(
            "Για H∞ χρειάζεσαι: pip install control slycot\n"
            f"Import error: {e}"
        )


def _weights(ct, wb: float, Ms: float, As: float, Wu: float,
             wt: float, Mt: float, At: float):
    """
    Classical mixed-sensitivity weights.

    W1(s): sensitivity shaping for tracking / disturbance rejection
      W1(s) = (s/Ms + wb) / (s + wb*As)

    W2(s): constant penalty on control effort
      W2(s) = Wu

    W3(s): complementary-sensitivity shaping (optional)
      W3(s) = (s/Mt + wt) / (At*s + wt)

    If wt <= 0, we disable W3 and keep the older two-weight behavior.
    """
    s = ct.tf([1, 0], [1])

    W1 = (s/float(Ms) + float(wb)) / (s + float(wb)*float(As))
    W2 = ct.tf([float(Wu)], [1])

    if float(wt) > 0.0:
        W3 = (s/float(Mt) + float(wt)) / (float(At)*s + float(wt))
    else:
        W3 = None

    return W1, W2, W3


def design_hinf_controller(p_nom: RFJParams, Ts: float,
                           wb: float = 8.0, Ms: float = 2.0, As: float = 0.01, Wu: float = 0.2,
                           wt: float = 25.0, Mt: float = 2.0, At: float = 0.02,
                           output: str = "phi") -> Dict[str, Any]:
    """
    Return a discrete controller (Ad,Bd,Cd,Dd) driven by error e = r - y.

    Plant input:
        V_cmd

    Plant output options:
        "phi"   -> link/joint angle, default thesis objective
        "theta" -> motor-side angle, retained for comparisons
        "alpha" -> twist = theta - phi, useful for dedicated vibration suppression
    """
    ct = _require_control()

    x0 = np.zeros(5)
    u0 = np.zeros(2)

    def f(x, u):
        return plant_rhs(x, V_cmd=float(u[0]), tau_L=float(u[1]), p=p_nom)

    A, B = linearize_finite_diff(f, x0, u0)
    Bv = B[:, [0]]

    output = str(output).lower().strip()
    if output == "theta":
        C = np.array([[1, 0, 0, 0, 0]], float)
    elif output == "phi":
        C = np.array([[0, 1, 0, 0, 0]], float)
    elif output == "alpha":
        C = np.array([[1, -1, 0, 0, 0]], float)
    else:
        raise ValueError("output must be 'phi', 'theta', or 'alpha'")

    D = np.array([[0.0]], float)
    G = ct.ss(A, Bv, C, D)

    W1, W2, W3 = _weights(ct, wb, Ms, As, Wu, wt, Mt, At)

    Kc, CL, info = ct.mixsyn(G, w1=W1, w2=W2, w3=W3)
    gamma, rcond = info

    Kc_ss = ct.ss(Kc)

    Ac = np.asarray(Kc_ss.A, float)
    Bc = np.asarray(Kc_ss.B, float)
    Cc = np.asarray(Kc_ss.C, float)
    Dc = np.asarray(Kc_ss.D, float)

    Ad, Bd = c2d_zoh(Ac, Bc, float(Ts))
    Cd = Cc
    Dd = Dc

    return {
        "Kd": (Ad, Bd, Cd, Dd),
        "info": {"gamma": float(gamma), "rcond": np.asarray(rcond).tolist()},
        "lin": {"A": A, "B": Bv, "C": C, "D": D},
        "weights": {
            "wb": wb, "Ms": Ms, "As": As, "Wu": Wu,
            "wt": wt, "Mt": Mt, "At": At,
            "output": output,
        },
    }
