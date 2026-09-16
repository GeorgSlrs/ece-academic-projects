
"""
controllers.py
==============
All controllers for the Rotary Flexible Joint (RFJ) project.

------------------------------------------------------------
BIG PICTURE (beginner-friendly)
------------------------------------------------------------
The simulator runs in two time scales:

1) FAST continuous-time plant integration (every dt_sim):
     x_dot = f(x, V_cmd, tau_L)
   where V_cmd is the applied motor voltage (driver output).

2) SLOW digital controller update (every Ts_ctrl):
   - sample sensors -> create measurements (theta_hat, phi_hat)
   - compute control command -> output V_cmd_cmd (desired voltage)
   - then the "driver layer" in simulate.py applies delay/noise/deadzone/saturation
     to get V_cmd (the voltage actually sent to the motor model)

So every controller in this file outputs:
    V_cmd_cmd  [Volts]

------------------------------------------------------------
Unified controller interface
------------------------------------------------------------
Every controller class implements:

    V_cmd_cmd, dbg = ctrl.step(meas, ref, Ts)

Where:
- meas: dict of measured signals (at least theta_hat, phi_hat)
- ref : dict of references (now at least phi_ref)
- Ts  : controller sample time [seconds]

- dbg : a debug dictionary (stored in sim["dbg"] by simulate.py),
        used for analysis plots and controller parameter plots.

------------------------------------------------------------
Controller modes available
------------------------------------------------------------
- PID   : classic baseline
- SMC   : sliding mode (robust-ish)
- MIT   : adaptive controller with reference-model sensitivity filters
- LQR   : optimal state feedback (linear model)
- LQG   : LQR + Kalman observer (linear model + noisy measurements)
- HINF  : H∞ mixed-sensitivity synthesis (requires control+slycot)
- MRAC  : adaptive augmentation MRAC (nominal + adaptive term + projection + σ-mod)

------------------------------------------------------------
IMPORTANT DESIGN UPDATE: PHI CONTROL
------------------------------------------------------------
The controlled angle is now the LINK / JOINT angle:

    phi_ref - phi_hat

not the motor-side angle theta.

This is the physically meaningful objective when the thesis says:
"I want the joint/link to move to a commanded angle."  Theta is still important,
because the motor must twist the spring before the link moves, but theta is now
an internal actuator-side coordinate, not the main output to track.

The elastic twist is still:

    alpha = theta - phi

and it is used as an auxiliary vibration/deflection signal:
- PID/MIT can add an optional anti-twist term.
- SMC can include alpha and dalpha in the sliding surface.
- LQR/LQG penalize alpha and dalpha in Q.
- H∞ can regulate phi by default, or alpha if you explicitly request that mode.
- MRAC basis functions include alpha/dalpha so adaptation can learn flexible-joint corrections.

Backward compatibility:
- simulate.py still stores theta_ref as an alias of phi_ref, so old plotting code will not crash.
- Controllers prefer ref["phi_ref"], but fall back to ref["theta_ref"] if needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional

import numpy as np

from rfj_params import RFJParams
from rfj_dynamics import plant_rhs
from analysis_tools import (
    linearize_finite_diff,
    c2d_zoh,
    dlqr,
    dkalman_gain,
)
from hinf_design import design_hinf_controller


# =============================================================================
# Small generic helper functions
# =============================================================================

def sat_sym(x: float, lim: float) -> float:
    """
    Symmetric saturation:
        sat(x,lim) = clamp(x, -lim, +lim)
    """
    lim = float(lim)
    return float(np.clip(float(x), -lim, lim))


def sat_sign(x: float, phi: float) -> float:
    """
    Smooth sign approximation for sliding-mode control:

      sat_sign(x, phi) = clip(x/phi, -1, +1)

    - When phi is small, it becomes more like sign(x)
    - When phi is larger, it becomes smoother (less chattering)

    Used in SMC.
    """
    phi = float(phi)
    if phi <= 0:
        return 1.0 if x >= 0 else -1.0
    return float(np.clip(x / phi, -1.0, 1.0))


def get_phi_ref(ref: Dict[str, float]) -> float:
    """
    Return the joint/link reference.

    New code should pass ref["phi_ref"].  We keep a fallback to theta_ref so older
    scripts or notebooks that still create {"theta_ref": ...} do not immediately fail.
    """
    if "phi_ref" in ref:
        return float(ref["phi_ref"])
    return float(ref.get("theta_ref", 0.0))


def solve_lyapunov_ct(A: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """
    Solve continuous-time Lyapunov equation:
        A^T P + P A = -Q

    We do it using the vectorization + Kronecker trick:
        vec(A^T P + P A) = (I ⊗ A^T + A^T ⊗ I) vec(P)

    This is fully NumPy-based (no SciPy required).
    """
    A = np.asarray(A, float)
    Q = np.asarray(Q, float)
    n = A.shape[0]
    I = np.eye(n)

    K = np.kron(I, A.T) + np.kron(A.T, I)
    vecP = np.linalg.solve(K, -Q.reshape(-1))
    P = vecP.reshape(n, n)
    return 0.5 * (P + P.T)


def proj_box(theta: np.ndarray, dtheta: np.ndarray, bound: np.ndarray) -> np.ndarray:
    """
    Very simple projection operator (box constraints):

    - theta: current parameter estimate vector
    - dtheta: desired update direction (gradient)
    - bound: positive bounds for each component (|theta_i| <= bound_i)

    Rule:
    - If theta_i is strictly inside bounds -> allow dtheta_i
    - If theta_i is at +bound and dtheta_i > 0 -> block it (set to 0)
    - If theta_i is at -bound and dtheta_i < 0 -> block it (set to 0)

    This keeps adaptive parameters bounded (important for robustness).
    """
    theta = np.asarray(theta, float)
    dtheta = np.asarray(dtheta, float)
    bound = np.asarray(bound, float)

    out = dtheta.copy()
    for i in range(theta.size):
        b = max(float(bound[i]), 1e-12)
        if abs(theta[i]) < b:
            continue
        if theta[i] >= b and out[i] > 0:
            out[i] = 0.0
        if theta[i] <= -b and out[i] < 0:
            out[i] = 0.0
    return out


def build_lqr_state_cost(g) -> np.ndarray:
    """
    Build the LQR/LQG state-cost matrix.

    State ordering:
      x = [theta, phi, dtheta, dphi, i]^T

    Since the thesis objective is now phi tracking, q_phi should usually be the
    dominant angle weight.  We still keep q_theta because excessive motor-side
    motion is undesirable, and we still add direct penalties on:

      alpha  = theta - phi
      dalpha = dtheta - dphi

    Those alpha/dalpha penalties reduce flexible oscillation.
    """
    Q = np.diag([g.q_theta, g.q_phi, g.q_dtheta, g.q_dphi, g.q_i]).astype(float)

    c_alpha = np.array([[1.0, -1.0, 0.0, 0.0, 0.0]], float)
    c_dalpha = np.array([[0.0, 0.0, 1.0, -1.0, 0.0]], float)

    Q += float(g.q_alpha) * (c_alpha.T @ c_alpha)
    Q += float(g.q_dalpha) * (c_dalpha.T @ c_dalpha)
    return Q


def reference_prefilter(Ad: np.ndarray, Bd: np.ndarray, K: np.ndarray, Cref: np.ndarray) -> float:
    """
    Compute a discrete steady-state reference prefilter Nbar.

    LQR gives state feedback:
        u = -K x + Nbar*r

    For a constant reference r and no disturbance, steady state satisfies:
        x_ss = (Ad - Bd K) x_ss + Bd Nbar r
        y_ss = Cref x_ss

    We choose Nbar so y_ss = r:
        Nbar = 1 / ( Cref (I - Ad + Bd K)^(-1) Bd )

    Here Cref = [0 1 0 0 0], because the tracked output is phi.
    """
    Ad = np.asarray(Ad, float)
    Bd = np.asarray(Bd, float)
    K = np.asarray(K, float)
    Cref = np.asarray(Cref, float).reshape(1, -1)

    n = Ad.shape[0]
    M = np.eye(n) - Ad + Bd @ K
    try:
        dc_gain = (Cref @ np.linalg.solve(M, Bd)).item()
        if abs(dc_gain) < 1e-9:
            return 0.0
        return float(1.0 / dc_gain)
    except Exception:
        return 0.0


# =============================================================================
# PID Controller
# =============================================================================

@dataclass
class PIDGains:
    Kp: float = 2.0
    Ki: float = 5.0
    Kd: float = 0.0
    Kalpha: float = 0.0   # optional anti-twist penalty


class PIDController:
    """
    Classic PID on the link/joint angle phi.

    Measured output:
      phi_hat

    Reference:
      phi_ref

    Control law:
      e_phi = phi_ref - phi_hat
      u     = Kp*e_phi + Ki*integral(e_phi) - Kd*dphi_hat - Kalpha*alpha_hat

    Why derivative on phi and not theta?
    - The output we care about is phi, so derivative damping should primarily
      oppose phi motion.

    Why keep alpha?
    - alpha = theta - phi measures elastic twist.  Large alpha means the spring
      is loaded and can excite oscillations.  Kalpha is optional because too much
      anti-twist action can slow link tracking.
    """
    def __init__(self, g: PIDGains):
        self.g = g
        self.ei = 0.0
        self.phi_prev = 0.0

    def reset(self):
        self.ei = 0.0
        self.phi_prev = 0.0

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        Ts = float(Ts)

        theta = float(meas.get("theta_hat", 0.0))
        phi = float(meas["phi_hat"])
        phi_ref = get_phi_ref(ref)

        e = phi_ref - phi
        self.ei += Ts * e

        dphi_hat = (phi - self.phi_prev) / max(Ts, 1e-9)
        self.phi_prev = phi

        alpha_hat = float(meas.get("alpha_hat", theta - phi))
        u_alpha = -self.g.Kalpha * alpha_hat

        u = self.g.Kp * e + self.g.Ki * self.ei - self.g.Kd * dphi_hat + u_alpha

        dbg = {
            "e": e,
            "e_phi": e,
            "ei": self.ei,
            "dphi_hat": dphi_hat,
            "alpha_hat": alpha_hat,
            "u_alpha": u_alpha,
            "phi_ref": phi_ref,
        }
        return float(u), dbg


# =============================================================================
# Sliding Mode Controller (SMC)
# =============================================================================

@dataclass
class SMCGains:
    lam: float = 5.0
    k: float = 0.3
    phi: float = 0.05
    lam_alpha: float = 0.0
    lam_dalpha: float = 0.0


class SMCController:
    """
    Sliding Mode Control for phi tracking.

    We now define the tracking variables using the LINK angle:

      x1 = phi - phi_ref
      x2 = dphi - dphi_ref

    Sliding surface:

      s = x2 + lam*x1 + lam_alpha*alpha + lam_dalpha*dalpha

    Sign intuition:
    - If phi is below the reference, x1 is negative, so s tends to be negative.
    - The switching term u_sw = -k*sat(s/phi_bl) becomes positive.
    - Positive voltage tends to increase motor torque, twist the spring, and pull
      the link in the positive direction.

    This is intentionally practical and educational rather than a full exact
    feedback-linearizing SMC derivation, because the voltage-to-phi path is
    indirect through motor current and spring dynamics.
    """
    def __init__(self, g: SMCGains, p_nom: RFJParams):
        self.g = g
        self.p = p_nom
        self.th_prev = 0.0
        self.ph_prev = 0.0
        self.r_prev = 0.0

    def reset(self):
        self.th_prev = 0.0
        self.ph_prev = 0.0
        self.r_prev = 0.0

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        Ts = float(Ts)

        th = float(meas.get("theta_hat", 0.0))
        ph = float(meas["phi_hat"])
        r = get_phi_ref(ref)

        dth = (th - self.th_prev) / max(Ts, 1e-9)
        dph = (ph - self.ph_prev) / max(Ts, 1e-9)
        dr = (r - self.r_prev) / max(Ts, 1e-9)

        self.th_prev = th
        self.ph_prev = ph
        self.r_prev = r

        x1 = ph - r
        x2 = dph - dr

        alpha = float(meas.get("alpha_hat", th - ph))
        dalpha = dth - dph

        s = x2 + self.g.lam * x1 + self.g.lam_alpha * alpha + self.g.lam_dalpha * dalpha

        # Equivalent/proportional part in voltage units.  This gives a smooth
        # action even inside the boundary layer, while u_sw gives robustness.
        u_eq = -0.25 * s
        u_sw = -self.g.k * sat_sign(s, self.g.phi)
        u = u_eq + u_sw

        dbg = {
            "s": s,
            "x1": x1,
            "x2": x2,
            "alpha": alpha,
            "dalpha": dalpha,
            "u_eq": u_eq,
            "u_sw": u_sw,
            "phi_ref": r,
        }
        return float(u), dbg


# =============================================================================
# MIT-rule controller (adaptive tracking with sensitivity filters)
# =============================================================================

@dataclass
class MITGains:
    """
    Parameters for the adaptive MIT-style controller.

    We use a reference model y_m driven by phi_ref and a controller of the form:

        u = Kp_hat*e_phi + Ki_hat*∫e_phi dt - Kd_hat*dphi + Kr_hat*phi_ref - Kalpha_hat*alpha

    where:
      e_phi = phi_ref - phi
      alpha = theta - phi

    So the adaptive controller now follows the joint/link output phi, not theta.
    """
    Kp: float = 2.0
    Ki: float = 5.0
    Kd: float = 0.0
    Kr: float = 1.0
    Kalpha: float = 0.0
    gamma: float = 0.5
    wn: float = 6.0
    zeta: float = 0.9
    int_limit: float = 2.5
    param_limit: float = 200.0


class MITController:
    """
    Practical MIT-style adaptive controller for phi tracking.

    Big picture:
    1) A 2nd-order reference model generates the desired output y_m ≈ phi_desired.
    2) The model-following error is e_m = phi - y_m.
    3) The control law is linear in adaptive parameters:

           u = Theta^T * omega

       with:
           omega = [e_phi, integral(e_phi), -dphi, phi_ref, -alpha]

    4) MIT rule updates the parameters using sensitivity derivatives:

           Theta_dot = -gamma * e_m * psi

    IMPORTANT:
    - The plant output in the MIT objective is phi.
    - theta only enters indirectly through alpha = theta - phi.
    """
    def __init__(self, g: MITGains):
        self.g = g

        self.Kp_nom = float(g.Kp)
        self.Ki_nom = float(g.Ki)
        self.Kd_nom = float(g.Kd)
        self.Kr_nom = float(g.Kr)
        self.Kalpha_nom = float(g.Kalpha)

        self.Kp_hat = float(g.Kp)
        self.Ki_hat = float(g.Ki)
        self.Kd_hat = float(g.Kd)
        self.Kr_hat = float(g.Kr)
        self.Kalpha_hat = float(g.Kalpha)

        self.ei = 0.0
        self.phi_prev = 0.0

        wn = float(g.wn)
        zeta = float(g.zeta)
        self.Am = np.array([[0.0, 1.0],
                            [-(wn**2), -2.0*zeta*wn]], float)
        self.Bm = np.array([[0.0],
                            [wn**2]], float)
        self.xm = np.zeros((2, 1))

        self.psi_p = np.zeros((2, 1))
        self.psi_i = np.zeros((2, 1))
        self.psi_d = np.zeros((2, 1))
        self.psi_r = np.zeros((2, 1))
        self.psi_alpha = np.zeros((2, 1))

    def reset(self):
        self.Kp_hat = float(self.Kp_nom)
        self.Ki_hat = float(self.Ki_nom)
        self.Kd_hat = float(self.Kd_nom)
        self.Kr_hat = float(self.Kr_nom)
        self.Kalpha_hat = float(self.Kalpha_nom)

        self.ei = 0.0
        self.phi_prev = 0.0
        self.xm[:] = 0.0
        self.psi_p[:] = 0.0
        self.psi_i[:] = 0.0
        self.psi_d[:] = 0.0
        self.psi_r[:] = 0.0
        self.psi_alpha[:] = 0.0

    def _ref_filter_step(self, xpsi: np.ndarray, u_in: float, Ts: float) -> np.ndarray:
        xdot = self.Am @ xpsi + self.Bm * float(u_in)
        return xpsi + float(Ts) * xdot

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        Ts = float(Ts)

        theta = float(meas.get("theta_hat", 0.0))
        phi = float(meas["phi_hat"])
        r = get_phi_ref(ref)

        dphi = (phi - self.phi_prev) / max(Ts, 1e-9)
        self.phi_prev = phi

        e_track = r - phi
        self.ei += Ts * e_track
        self.ei = float(np.clip(self.ei, -self.g.int_limit, self.g.int_limit))

        alpha = float(meas.get("alpha_hat", theta - phi))

        xm_dot = self.Am @ self.xm + self.Bm * r
        self.xm = self.xm + Ts * xm_dot
        y_m = float(self.xm[0, 0])
        dy_m = float(self.xm[1, 0])

        e_m = phi - y_m

        omega_p = e_track
        omega_i = self.ei
        omega_d = -dphi
        omega_r = r
        omega_alpha = -alpha

        self.psi_p = self._ref_filter_step(self.psi_p, omega_p, Ts)
        self.psi_i = self._ref_filter_step(self.psi_i, omega_i, Ts)
        self.psi_d = self._ref_filter_step(self.psi_d, omega_d, Ts)
        self.psi_r = self._ref_filter_step(self.psi_r, omega_r, Ts)
        self.psi_alpha = self._ref_filter_step(self.psi_alpha, omega_alpha, Ts)

        psi_p = float(self.psi_p[0, 0])
        psi_i = float(self.psi_i[0, 0])
        psi_d = float(self.psi_d[0, 0])
        psi_r = float(self.psi_r[0, 0])
        psi_alpha = float(self.psi_alpha[0, 0])

        gamma = float(self.g.gamma)
        self.Kp_hat -= gamma * e_m * psi_p * Ts
        self.Ki_hat -= gamma * e_m * psi_i * Ts
        self.Kd_hat -= gamma * e_m * psi_d * Ts
        self.Kr_hat -= gamma * e_m * psi_r * Ts
        self.Kalpha_hat -= gamma * e_m * psi_alpha * Ts

        lim = float(self.g.param_limit)
        self.Kp_hat = float(np.clip(self.Kp_hat, -lim, lim))
        self.Ki_hat = float(np.clip(self.Ki_hat, -lim, lim))
        self.Kd_hat = float(np.clip(self.Kd_hat, -lim, lim))
        self.Kr_hat = float(np.clip(self.Kr_hat, -lim, lim))
        self.Kalpha_hat = float(np.clip(self.Kalpha_hat, -lim, lim))

        u_p = self.Kp_hat * omega_p
        u_i = self.Ki_hat * omega_i
        u_d = self.Kd_hat * omega_d
        u_r = self.Kr_hat * omega_r
        u_alpha = self.Kalpha_hat * omega_alpha
        u = u_p + u_i + u_d + u_r + u_alpha

        dbg = {
            "theta": theta,
            "phi": phi,
            "alpha": alpha,
            "phi_ref": r,
            "ym": y_m,
            "dym": dy_m,
            "e_track": e_track,
            "e_phi": e_track,
            "e_m": e_m,
            "ei": self.ei,
            "dphi_hat": dphi,
            "omega_p": omega_p,
            "omega_i": omega_i,
            "omega_d": omega_d,
            "omega_r": omega_r,
            "omega_alpha": omega_alpha,
            "psi_p": psi_p,
            "psi_i": psi_i,
            "psi_d": psi_d,
            "psi_r": psi_r,
            "psi_alpha": psi_alpha,
            "u_p": u_p,
            "u_i": u_i,
            "u_d": u_d,
            "u_r": u_r,
            "u_alpha": u_alpha,
            "u": u,
            "Kp_hat": self.Kp_hat,
            "Ki_hat": self.Ki_hat,
            "Kd_hat": self.Kd_hat,
            "Kr_hat": self.Kr_hat,
            "Kalpha_hat": self.Kalpha_hat,
            "Kp_nom": self.Kp_nom,
            "Ki_nom": self.Ki_nom,
            "Kd_nom": self.Kd_nom,
            "Kr_nom": self.Kr_nom,
            "Kalpha_nom": self.Kalpha_nom,
        }
        return float(u), dbg


# =============================================================================
# LQR Controller (discrete-time, linear model)
# =============================================================================

@dataclass
class LQRGains:
    # State penalty weights.
    # For phi tracking, q_phi should usually be larger than q_theta.
    q_theta: float = 10.0
    q_phi: float = 80.0
    q_dtheta: float = 1.0
    q_dphi: float = 2.0
    q_i: float = 0.1

    # Explicit penalties on elastic twist and twist-rate
    q_alpha: float = 5.0
    q_dalpha: float = 0.5

    # Control penalty
    r_v: float = 1.0


class LQRController:
    """
    LQR on the linearized model around x=0,u=0, with phi as the reference output.

    Steps:
    1) Linearize nonlinear plant: x_dot = A x + B u
       where u = V_cmd (voltage input).
    2) Discretize with ZOH at Ts_ctrl: x[k+1] = Ad x[k] + Bd u[k].
    3) Solve discrete Riccati -> K.
    4) Apply:

          u = -K*xhat + Nbar*phi_ref

       where Nbar is a steady-state prefilter chosen for y = phi.

    This replaces the old hard-coded "+2*r" injection, which was theta-oriented
    and not mathematically tied to the controlled output.
    """
    def __init__(self, p_nom: RFJParams, g: LQRGains):
        self.p = p_nom
        self.g = g
        self.K = None
        self.Nbar = 0.0
        self.th_prev = 0.0
        self.ph_prev = 0.0
        self._design()

    def _design(self):
        x0 = np.zeros(5)
        u0 = np.zeros(2)

        def f(x, u):
            return plant_rhs(x, V_cmd=float(u[0]), tau_L=float(u[1]), p=self.p)

        A, B = linearize_finite_diff(f, x0, u0)
        Bv = B[:, [0]]
        Ad, Bd = c2d_zoh(A, Bv, float(self.p.Ts_ctrl))

        Q = build_lqr_state_cost(self.g)
        R = np.array([[self.g.r_v]], float)

        K, _, _ = dlqr(Ad, Bd, Q, R)
        self.K = np.asarray(K, float)

        C_phi = np.array([[0, 1, 0, 0, 0]], float)
        self.Nbar = reference_prefilter(Ad, Bd, self.K, C_phi)

    def reset(self):
        self.th_prev = 0.0
        self.ph_prev = 0.0

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        Ts = float(Ts)

        th = float(meas.get("theta_hat", 0.0))
        ph = float(meas["phi_hat"])
        r = get_phi_ref(ref)

        dth = (th - self.th_prev) / max(Ts, 1e-9)
        dph = (ph - self.ph_prev) / max(Ts, 1e-9)
        self.th_prev = th
        self.ph_prev = ph

        i_hat = float(meas.get("i_hat", 0.0))
        xhat = np.array([[th], [ph], [dth], [dph], [i_hat]], float)
        alpha_hat = th - ph

        u_fb = -(self.K @ xhat).item()
        u_ff = self.Nbar * r
        u = u_fb + u_ff

        dbg = {"u_lqr": u, "u_fb": u_fb, "u_ff": u_ff, "Nbar": self.Nbar,
               "alpha_hat": alpha_hat, "phi_ref": r}
        return float(u), dbg


# =============================================================================
# LQG Controller (LQR + Kalman observer)
# =============================================================================

@dataclass
class LQGNoise:
    q_proc: float = 1e-5
    r_meas: float = 1e-4


class LQGController:
    """
    LQG = LQR + steady-state discrete Kalman filter.

    Measurements:
      y = [theta_hat, phi_hat]^T

    The observer estimates the full state:
      xhat = [theta, phi, dtheta, dphi, i]^T

    Control law:
      u = -K*xhat + Nbar*phi_ref

    The regulated/reference output is phi, while theta is still measured because
    theta helps reconstruct alpha and the motor-side dynamics.
    """
    def __init__(self, p_nom: RFJParams, lqr_g: LQRGains, kf_n: LQGNoise):
        self.p = p_nom
        self.lqr_g = lqr_g
        self.kf_n = kf_n

        self.Ad = None
        self.Bd = None
        self.Cd = None
        self.K = None
        self.L = None
        self.Nbar = 0.0
        self.xhat = np.zeros((5, 1))
        self._design()

    def _design(self):
        x0 = np.zeros(5)
        u0 = np.zeros(2)

        def f(x, u):
            return plant_rhs(x, V_cmd=float(u[0]), tau_L=float(u[1]), p=self.p)

        A, B = linearize_finite_diff(f, x0, u0)
        Bv = B[:, [0]]
        self.Ad, self.Bd = c2d_zoh(A, Bv, float(self.p.Ts_ctrl))

        self.Cd = np.array([[1, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0]], float)

        Q = build_lqr_state_cost(self.lqr_g)
        R = np.array([[self.lqr_g.r_v]], float)
        self.K, _, _ = dlqr(self.Ad, self.Bd, Q, R)
        self.K = np.asarray(self.K, float)

        C_phi = np.array([[0, 1, 0, 0, 0]], float)
        self.Nbar = reference_prefilter(self.Ad, self.Bd, self.K, C_phi)

        Qn = self.kf_n.q_proc * np.eye(5)
        Rn = self.kf_n.r_meas * np.eye(2)
        self.L = dkalman_gain(self.Ad, self.Cd, Qn, Rn)

    def reset(self):
        self.xhat[:] = 0.0

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        th = float(meas.get("theta_hat", 0.0))
        ph = float(meas["phi_hat"])
        r = get_phi_ref(ref)

        y = np.array([[th], [ph]], float)
        innov = y - self.Cd @ self.xhat

        u_fb = -(self.K @ self.xhat).item()
        u_ff = self.Nbar * r
        u = u_fb + u_ff

        self.xhat = self.Ad @ self.xhat + self.Bd * float(u) + self.L @ innov

        dbg = {
            "innov_theta": float(innov[0]),
            "innov_phi": float(innov[1]),
            "alpha_hat": float(self.xhat[0] - self.xhat[1]),
            "u_fb": u_fb,
            "u_ff": u_ff,
            "Nbar": self.Nbar,
            "phi_ref": r,
        }
        return float(u), dbg


# =============================================================================
# H∞ controller wrapper
# =============================================================================

@dataclass
class HinfWeights:
    wb: float = 8.0
    Ms: float = 2.0
    As: float = 0.01
    Wu: float = 0.2
    wt: float = 25.0
    Mt: float = 2.0
    At: float = 0.02

    # Output selection:
    # - "phi"  : default thesis objective, joint/link angle tracking
    # - "theta": motor-side tracking, retained only for comparison experiments
    # - "alpha": dedicated twist-suppression design
    output: str = "phi"


class DiscreteSSController:
    """
    A tiny discrete state-space controller object:

      xk+1 = Ad xk + Bd e
      u    = Cd xk + Dd e

    Here e is the error signal (reference - measured output).
    """
    def __init__(self, Ad, Bd, Cd, Dd):
        self.Ad = np.asarray(Ad, float)
        self.Bd = np.asarray(Bd, float)
        self.Cd = np.asarray(Cd, float)
        self.Dd = np.asarray(Dd, float)
        self.x = np.zeros((self.Ad.shape[0], 1))

    def reset(self):
        self.x[:] = 0.0

    def step_error(self, e: float) -> float:
        evec = np.array([[float(e)]], float)
        u = (self.Cd @ self.x + self.Dd @ evec).item()
        self.x = self.Ad @ self.x + self.Bd @ evec
        return float(u)


class HinfController:
    """
    H∞ mixed-sensitivity controller.

    Default runtime error:
        e = phi_ref - phi_hat

    because the controlled output is now the joint/link angle phi.

    You can still set output="alpha" to synthesize a twist-suppression controller
    with e = alpha_ref - alpha_hat, or output="theta" for motor-side comparison.
    """
    def __init__(self, p_nom: RFJParams, w: HinfWeights):
        self.p = p_nom
        self.w = w
        self.gamma = None
        self.ss = None
        self._design()

    def _design(self):
        out = design_hinf_controller(
            self.p,
            Ts=float(self.p.Ts_ctrl),
            wb=self.w.wb, Ms=self.w.Ms, As=self.w.As, Wu=self.w.Wu,
            wt=self.w.wt, Mt=self.w.Mt, At=self.w.At,
            output=self.w.output,
        )
        Ad, Bd, Cd, Dd = out["Kd"]
        self.gamma = out["info"]["gamma"]
        self.ss = DiscreteSSController(Ad, Bd, Cd, Dd)

    def reset(self):
        self.ss.reset()

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        th = float(meas.get("theta_hat", 0.0))
        ph = float(meas["phi_hat"])
        alpha_hat = float(meas.get("alpha_hat", th - ph))

        if self.w.output == "alpha":
            y_ref = float(ref.get("alpha_ref", 0.0))
            y = alpha_hat
        elif self.w.output == "theta":
            y_ref = float(ref.get("theta_ref", get_phi_ref(ref)))
            y = th
        else:
            y_ref = get_phi_ref(ref)
            y = ph

        e = y_ref - y
        u = self.ss.step_error(e)
        dbg = {
            "e": e,
            "gamma": float(self.gamma),
            "output_mode": self.w.output,
            "alpha_hat": alpha_hat,
            "phi_ref": get_phi_ref(ref),
        }
        return float(u), dbg


# =============================================================================
# MRAC Adaptive Augmentation controller (SISO)
# =============================================================================

@dataclass
class MRACCfg:
    """
    Practical MRAC "adaptive augmentation" configuration.

    Reference model is a 2nd-order stable system for phi tracking:
      x_m = [phi_m, dphi_m]
      x_m_dot = A_m x_m + B_m phi_ref

    sigma is σ-modification (robustness against noise/unmodeled dynamics):
      theta_hat_dot includes -sigma*theta_hat

    The basis functions include alpha and dalpha explicitly, so the adaptive
    augmentation can learn flexible-joint corrections.
    """
    wn: float = 6.0
    zeta: float = 0.9
    gamma_scale: float = 5.0
    sigma: float = 0.05

    Dx_bound: float = 40.0
    Dr_bound: float = 40.0
    Th_bound: float = 60.0

    # nominal stabilizer gains u_nom for phi tracking
    k_p: float = 18.0
    k_d: float = 4.0
    k_r: float = 18.0

    N: int = 6


class MRACAugController:
    """
    MRAC Adaptive Augmentation (SISO) for phi tracking:

      u = u_nom + u_ad

    u_nom = k_r*phi_ref - k_p*phi - k_d*dphi
    u_ad  = Dx_hat^T x + Dr_hat*phi_ref + Th_hat^T Phi(x)

    where x = [phi_hat, dphi_hat]

    Basis functions:
      Phi = [phi, dphi, alpha, dalpha, phi^3, tanh(dphi)]

    theta appears only through alpha/dalpha because theta is no longer the
    controlled output.
    """
    def __init__(self, cfg: MRACCfg):
        self.cfg = cfg
        self.th_prev = 0.0
        self.ph_prev = 0.0
        self.xm = np.zeros((2, 1))

        wn = float(cfg.wn)
        zeta = float(cfg.zeta)
        self.Am = np.array([[0.0, 1.0],
                            [-(wn**2), -2.0*zeta*wn]], float)
        self.Bm = np.array([[0.0],
                            [wn**2]], float)
        self.B = np.array([[0.0],
                           [1.0]], float)

        Q = np.diag([10.0, 1.0])
        self.P = solve_lyapunov_ct(self.Am, Q)

        self.Dx_hat = np.zeros(2)
        self.Dr_hat = np.zeros(1)
        self.Th_hat = np.zeros(6)

        g = float(cfg.gamma_scale)
        self.Gx = g * np.eye(2)
        self.Gr = g * np.eye(1)
        self.Gt = g * np.eye(6)

    def reset(self):
        self.th_prev = 0.0
        self.ph_prev = 0.0
        self.xm[:] = 0.0
        self.Dx_hat[:] = 0.0
        self.Dr_hat[:] = 0.0
        self.Th_hat[:] = 0.0

    def _phi(self, phi: float, dphi: float, alpha: float, dalpha: float) -> np.ndarray:
        return np.array([
            phi,
            dphi,
            alpha,
            dalpha,
            phi**3,
            np.tanh(dphi),
        ], float)

    def step(self, meas: Dict[str, float], ref: Dict[str, float], Ts: float) -> Tuple[float, Dict[str, float]]:
        Ts = float(Ts)

        theta = float(meas.get("theta_hat", 0.0))
        phi = float(meas["phi_hat"])

        dtheta = (theta - self.th_prev) / max(Ts, 1e-9)
        dphi = (phi - self.ph_prev) / max(Ts, 1e-9)
        self.th_prev = theta
        self.ph_prev = phi

        alpha = float(meas.get("alpha_hat", theta - phi))
        dalpha = dtheta - dphi

        x = np.array([[phi], [dphi]], float)
        r = get_phi_ref(ref)

        xm_dot = self.Am @ self.xm + self.Bm * r
        self.xm = self.xm + Ts * xm_dot

        e = x - self.xm
        s = float((e.T @ self.P @ self.B).item())

        u_nom = self.cfg.k_r * r - self.cfg.k_p * phi - self.cfg.k_d * dphi

        phi_vec = self._phi(phi, dphi, alpha, dalpha)
        u_ad = float(
            self.Dx_hat @ np.array([phi, dphi]) +
            self.Dr_hat[0] * r +
            self.Th_hat @ phi_vec
        )

        u = u_nom + u_ad

        dDx = -(self.Gx @ (np.array([phi, dphi]) * s))
        dDr = -(self.Gr @ (np.array([r]) * s))
        dTh = -(self.Gt @ (phi_vec * s))

        Dx_bound = np.array([self.cfg.Dx_bound, self.cfg.Dx_bound], float)
        Dr_bound = np.array([self.cfg.Dr_bound], float)
        Th_bound = np.array([self.cfg.Th_bound] * self.Th_hat.size, float)

        dDx = proj_box(self.Dx_hat, dDx, Dx_bound)
        dDr = proj_box(self.Dr_hat, dDr, Dr_bound)
        dTh = proj_box(self.Th_hat, dTh, Th_bound)

        sig = float(self.cfg.sigma)
        dDx = dDx - sig * self.Dx_hat
        dDr = dDr - sig * self.Dr_hat
        dTh = dTh - sig * self.Th_hat

        self.Dx_hat = self.Dx_hat + Ts * dDx
        self.Dr_hat = self.Dr_hat + Ts * dDr
        self.Th_hat = self.Th_hat + Ts * dTh

        Dx_nom = np.zeros_like(self.Dx_hat)
        Dr_nom = np.zeros_like(self.Dr_hat)
        Th_nom = np.zeros_like(self.Th_hat)

        dbg = {
            "theta": theta,
            "phi": phi,
            "alpha": alpha,
            "dtheta": dtheta,
            "dphi": dphi,
            "dalpha": dalpha,
            "phi_ref": r,
            "xm_phi": float(self.xm[0]),
            "xm_dphi": float(self.xm[1]),
            "e1": float(e[0]),
            "e2": float(e[1]),
            "s": s,
            "u_nom": u_nom,
            "u_ad": u_ad,
            "Dx_hat": self.Dx_hat.copy(),
            "Dr_hat": self.Dr_hat.copy(),
            "Th_hat": self.Th_hat.copy(),
            "Dx_nom": Dx_nom.copy(),
            "Dr_nom": Dr_nom.copy(),
            "Th_nom": Th_nom.copy(),
        }
        return float(u), dbg


# =============================================================================
# Controller factory
# =============================================================================

def make_controller(mode: str, p_nom: RFJParams, cfg: Optional[Dict[str, Any]] = None):
    """
    Factory function: create a controller instance by mode string.

    cfg is a dict-of-dicts like:
      cfg = {
        "pid": {"Kp":..., "Ki":..., ...},
        "mrac": {"wn":..., "zeta":..., ...},
        "hinf": {...},
      }
    """
    cfg = cfg or {}
    mode = mode.lower().strip()

    if mode == "pid":
        return PIDController(PIDGains(**cfg.get("pid", {})))

    if mode == "smc":
        return SMCController(SMCGains(**cfg.get("smc", {})), p_nom=p_nom)

    if mode == "mit":
        return MITController(MITGains(**cfg.get("mit", {})))

    if mode == "lqr":
        return LQRController(p_nom=p_nom, g=LQRGains(**cfg.get("lqr", {})))

    if mode == "lqg":
        return LQGController(
            p_nom=p_nom,
            lqr_g=LQRGains(**cfg.get("lqr", {})),
            kf_n=LQGNoise(**cfg.get("lqg", {})),
        )

    if mode == "hinf":
        return HinfController(p_nom=p_nom, w=HinfWeights(**cfg.get("hinf", {})))

    if mode == "mrac":
        return MRACAugController(MRACCfg(**cfg.get("mrac", {})))

    raise ValueError(f"Unknown controller mode: {mode}")
