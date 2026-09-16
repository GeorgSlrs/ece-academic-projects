"""
rfj_dynamics.py
===============
Nonlinear dynamics of the rotary flexible joint (RFJ) + RK4 integrator.

State:
  x = [theta, phi, dtheta, dphi, i]

Where:
  theta  : hub (motor-side) angle
  phi    : link angle
  dtheta : hub angular velocity
  dphi   : link angular velocity
  i      : motor current

Derived:
  alpha  = theta - phi         (twist/deflection)
  dalpha = dtheta - dphi

Motor torque:
  tau_m = Kt * i

Spring & damper torques (advanced):
  tau_spring = Ks*alpha + Ks3*alpha^3
  tau_damper = Cs*dalpha

Friction (advanced):
  tau_coulomb ≈ tau_c * tanh(omega / w_c)
  (tanh is used so the friction model is smooth, not discontinuous)

Equations:
  Jm*ddtheta = tau_m - tau_spring - tau_damper - Bm*dtheta - tau_c_m*tanh(dtheta/w_c)
  Jl*ddphi   = +tau_spring + tau_damper - Bl*dphi - tau_c_l*tanh(dphi/w_c) - Kl*phi - tau_L
  L*di       = -R*i - Ke*dtheta + V_cmd

Notes:
- V_cmd is the voltage applied by the driver (after saturation, deadzone, etc.)
- tau_L is a disturbance torque acting on the link side
"""

from __future__ import annotations
import numpy as np
from typing import Callable
from rfj_params import RFJParams


def plant_rhs(x: np.ndarray, V_cmd: float, tau_L: float, p: RFJParams) -> np.ndarray:
    # Unpack states
    theta, phi, dtheta, dphi, i = x

    # Twist across flexible joint
    alpha = theta - phi
    dalpha = dtheta - dphi

    # Motor torque
    tau_m = p.Kt * i

    # Nonlinear spring (linear + cubic)
    tau_spring = p.Ks * alpha + p.Ks3 * (alpha ** 3)

    # Torsional damper
    tau_damper = p.Cs * dalpha

    # Smooth Coulomb friction
    w_c = max(float(p.w_c), 1e-6)
    tau_fc_m = p.tau_c_m * np.tanh(dtheta / w_c)
    tau_fc_l = p.tau_c_l * np.tanh(dphi / w_c)

    # Hub acceleration
    ddtheta = (
        tau_m
        - tau_spring
        - tau_damper
        - p.Bm * dtheta
        - tau_fc_m
    ) / p.Jm

    # Link acceleration
    ddphi = (
        + tau_spring
        + tau_damper
        - p.Bl * dphi
        - tau_fc_l
        - p.Kl * phi
        - tau_L
    ) / p.Jl

    # Motor current dynamics (electrical)
    di = (-p.R * i - p.Ke * dtheta + V_cmd) / p.L

    return np.array([dtheta, dphi, ddtheta, ddphi, di], dtype=float)


def rk4_step(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray, dt: float) -> np.ndarray:
    """Classic fixed-step Runge–Kutta 4 integrator."""
    k1 = f(x)
    k2 = f(x + 0.5 * dt * k1)
    k3 = f(x + 0.5 * dt * k2)
    k4 = f(x + dt * k3)
    return x + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)