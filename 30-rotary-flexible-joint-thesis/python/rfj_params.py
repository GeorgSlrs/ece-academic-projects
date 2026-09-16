"""
rfj_params.py
=============
All physical + simulation parameters in one place.

We separate:
- p_nom  : nominal model used by controllers/design
- p_true : true plant used in simulation (p_nom plus uncertainties)

Advanced dynamics added (beginner-friendly but more realistic):
- Nonlinear torsional spring: tau_spring = Ks*alpha + Ks3*alpha^3
- Smooth Coulomb friction: tau_c * tanh(omega / w_c)
- Driver deadzone on voltage (handled in simulate.py)

Uncertainty knobs (deltaKs etc.) are multiplicative:
  Ks_true = Ks_nom * (1 + deltaKs)
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class RFJParams:
    # -----------------------------
    # Mechanical parameters
    # -----------------------------
    Jm: float = 1.20e-4     # hub/motor-side inertia [kg*m^2]
    Jl: float = 2.50e-3     # link inertia [kg*m^2]

    Ks: float = 0.40        # torsional stiffness [N*m/rad]
    Cs: float = 0.020       # torsional damping [N*m*s/rad]

    # NEW: cubic stiffness (nonlinear spring)
    Ks3: float = 0.0        # [N*m/rad^3] (set >0 to stiffen at large deflection)

    # Viscous friction
    Bm: float = 2.0e-4      # hub viscous friction [N*m*s/rad]
    Bl: float = 1.0e-4      # link viscous friction [N*m*s/rad]

    # NEW: smooth Coulomb friction magnitudes
    tau_c_m: float = 0.0008  # hub Coulomb friction magnitude [N*m]
    tau_c_l: float = 0.0010  # link Coulomb friction magnitude [N*m]
    w_c: float = 0.05        # smoothing speed for tanh() [rad/s]

    # Optional link stiffness
    Kl: float = 0.0          # [N*m/rad]

    # -----------------------------
    # Motor electrical parameters
    # -----------------------------
    R: float  = 2.0         # armature resistance [ohm]
    L: float  = 2.0e-3      # armature inductance [H]
    Kt: float = 0.030       # torque constant [N*m/A]
    Ke: float = 0.030       # back-EMF constant [V/(rad/s)]

    Vbus: float = 12.0      # supply voltage [V]

    # NEW: driver deadzone (very common in cheap drivers/H-bridges)
    v_deadzone: float = 0.15  # [V] anything below this becomes ~0

    # -----------------------------
    # Digital control / simulation
    # -----------------------------
    Ts_ctrl: float = 0.005  # controller sample time [s]
    dt_sim:  float = 0.001  # integrator step [s]

    # Encoder resolution for quantization
    counts_per_rev: int = 4096

    # -----------------------------
    # Uncertainty knobs (true plant)
    # -----------------------------
    deltaJm: float = 0.0
    deltaJl: float = 0.0
    deltaKs: float = 0.0
    deltaCs: float = 0.0
    deltaKs3: float = 0.0
    deltaBm: float = 0.0
    deltaBl: float = 0.0
    deltaKt: float = 0.0
    deltaKe: float = 0.0
    deltaR: float = 0.0

    # disturbance amplitude (used by simulate.py)
    tauL_max: float = 0.0

    def true_params(self) -> "RFJParams":
        """Return parameters with uncertainties applied."""
        p = RFJParams(**asdict(self))

        p.Jm = self.Jm * (1.0 + self.deltaJm)
        p.Jl = self.Jl * (1.0 + self.deltaJl)

        p.Ks  = self.Ks  * (1.0 + self.deltaKs)
        p.Cs  = self.Cs  * (1.0 + self.deltaCs)
        p.Ks3 = self.Ks3 * (1.0 + self.deltaKs3)

        p.Bm = self.Bm * (1.0 + self.deltaBm)
        p.Bl = self.Bl * (1.0 + self.deltaBl)

        p.Kt = self.Kt * (1.0 + self.deltaKt)
        p.Ke = self.Ke * (1.0 + self.deltaKe)
        p.R  = self.R  * (1.0 + self.deltaR)

        return p

    def dtheta_q(self) -> float:
        """Encoder quantization step [rad]."""
        return float(2.0*np.pi / max(1, int(self.counts_per_rev)))

    def summary(self) -> str:
        return (
            f"[RFJ] Ks={self.Ks:.3f} Cs={self.Cs:.3f} Ks3={self.Ks3:.3f}  "
            f"Jm={self.Jm:.2e} Jl={self.Jl:.2e} Vbus={self.Vbus:.1f}V\n"
            f"     Ts_ctrl={self.Ts_ctrl:.4f}s dt_sim={self.dt_sim:.4f}s counts/rev={self.counts_per_rev}\n"
            f"     friction: tau_c_m={self.tau_c_m:.4g}, tau_c_l={self.tau_c_l:.4g}, w_c={self.w_c:.3g}, deadzone={self.v_deadzone:.3g}V"
        )


def default_params() -> RFJParams:
    return RFJParams()