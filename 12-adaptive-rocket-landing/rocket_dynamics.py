"""
rocket_dynamics.py
==================

Goal of this file
-----------------
You asked for a *single* Python script that contains ONLY the *dynamics equations*
for a 2D rocket landing problem, written in the "state-space" form:

    x_dot = f(x, u)

where:
  - x is the state vector (a single stacked vector)
  - u is the input vector (throttle command and gimbal command)

This file intentionally does NOT:
  - simulate the system
  - design a controller
  - optimize a trajectory
  - plot anything

Those will live in separate scripts that IMPORT this file.

--------------------------------------------------------------------------------
MODEL (2D planar rigid body + some realism)
--------------------------------------------------------------------------------

We model a rocket as a rigid body moving in the x-y plane:

Inertial axes:
  x : horizontal (right is +)
  y : vertical (up is +)

Landing pad center is at (x, y) = (0, 0).

State vector (length 9):
  x = [ px, py, vx, vy, theta, omega, m, u_act, delta_act ]^T

Meaning:
  px, py     : position (m)
  vx, vy     : velocity (m/s)
  theta      : rocket tilt angle from the +y axis (rad)
               theta = 0 means perfectly upright
  omega      : angular rate (rad/s), omega = d(theta)/dt
  m          : mass (kg)  (can be constant if you disable mass depletion)
  u_act      : ACTUAL throttle after actuator lag (dimensionless in [0,1])
  delta_act  : ACTUAL gimbal angle after actuator lag (rad in [-0.2,0.2])

Input vector u (length 2):
  u = [ u_cmd, delta_cmd ]^T

Meaning:
  u_cmd      : COMMANDED throttle in [0,1]
  delta_cmd  : COMMANDED gimbal angle in [-0.2, 0.2] rad

Why do we include u_act and delta_act in the STATE?
---------------------------------------------------
Because you requested a "more advanced" model.
A realistic engine and gimbal do NOT react instantly.
A very common first approximation is a first-order lag:

  u_act_dot     = (u_cmd - u_act) / tau_u
  delta_act_dot = (delta_cmd - delta_act) / tau_delta

plus rate limits (optional).

--------------------------------------------------------------------------------
FORCES
--------------------------------------------------------------------------------

1) Thrust (engine)
------------------
Let T be the thrust magnitude (Newtons). We compute T from u_act:

  T = u_act * T_max

You said:
  - thrust-to-weight ratio is 2
  - throttle 0.5 can hover

To satisfy "hover at 0.5" even if mass changes, we use (by default):

  T_max = (T/W) * m * g   with T/W = 2

So when upright and delta_act ~ 0:
  ay = T/m - g = (2*u_act*g) - g = (2*u_act - 1)*g
So u_act = 0.5 gives ay = 0 (hover).

2) Aerodynamic drag (optional)
------------------------------
Quadratic drag, opposite the air-relative velocity:

  v_rel = v - v_wind
  F_drag = -0.5 * rho * Cd * A * ||v_rel|| * v_rel

This is the standard drag equation written as a vector.

We use an exponential atmosphere density (optional):
  rho(py) = rho0 * exp(-py / H)

3) Gravity
----------
  F_g = [0, -m*g]^T

--------------------------------------------------------------------------------
TRANSLATIONAL DYNAMICS (Newton's 2nd law)
--------------------------------------------------------------------------------

Total force:
  F = F_thrust + F_drag + F_g

Acceleration:
  a = F / m

Kinematics:
  px_dot = vx
  py_dot = vy

--------------------------------------------------------------------------------
ROTATIONAL DYNAMICS (planar Newton–Euler)
--------------------------------------------------------------------------------

We use a simple thrust-vector-control torque model:
  tau_tvc = L * T * sin(delta_act)

where L is an engine lever arm (meters).

Add simple rotational damping:
  tau_damp = - rot_damp * omega

Then:
  theta_dot = omega
  omega_dot = (tau_tvc + tau_damp) / Iyy

--------------------------------------------------------------------------------
MASS DEPLETION (optional)
--------------------------------------------------------------------------------

Using the specific impulse relation:
  Isp = T / (mdot * g0)    ->   mdot = T / (Isp*g0)

So:
  m_dot = - T / (Isp*g0)

--------------------------------------------------------------------------------
NOTES FOR YOUR REPORT
--------------------------------------------------------------------------------
- This is a common "mid-complexity" model: more realistic than a point-mass,
  but much simpler than full 6-DoF rigid-body dynamics.
- In later scripts you can:
    * discretize this ODE (Euler, RK4, etc.)
    * design adaptive control around it
    * include state constraints and touchdown conditions

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import math


# =============================================================================
# Small utility helpers
# =============================================================================

def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp a value x into the interval [lo, hi]."""
    return max(lo, min(hi, x))


# =============================================================================
# Parameters (collect everything in one place)
# =============================================================================

@dataclass
class RocketParams:
    """
    All physical parameters + "modeling knobs".

    You will likely tune these later, but these defaults are reasonable
    to start testing with.

    Important: thrust-to-weight ratio and hover condition
    ----------------------------------------------------
    You told me:
      - T/W = 2
      - u = 0.5 hovers

    If mass changes, there are two interpretations of T_max:

    (A) hover_normalized (DEFAULT):
        T_max = (T/W) * m * g     (depends on current mass)
        This keeps hover at u=0.5 even if m changes.

    (B) constant_Tmax:
        T_max = (T/W) * m0 * g    (constant hardware limit based on initial mass)
        More physical, but hover throttle changes as m decreases.

    Pick with params.thrust_mode.
    """

    # ---- gravity ----
    g: float = 9.81                 # m/s^2
    g0: float = 9.80665             # m/s^2 (standard gravity used with Isp)

    # ---- thrust scaling ----
    thrust_to_weight: float = 2.0
    thrust_mode: str = "hover_normalized"   # "hover_normalized" or "constant_Tmax"
    m0: float = 1000.0                      # kg (used only if constant_Tmax)

    # ---- mass depletion ----
    use_mass_depletion: bool = True
    Isp: float = 250.0                      # s

    # ---- attitude dynamics ----
    Iyy: float = 1200.0                     # kg*m^2
    engine_lever_arm: float = 2.0           # m
    rot_damp: float = 50.0                  # N*m*s/rad

    # ---- aerodynamics ----
    use_aero_drag: bool = True
    Cd: float = 0.6                         # -
    A_ref: float = 3.0                      # m^2

    # Exponential density rho = rho0 exp(-h/H)
    use_exponential_atmos: bool = True
    rho0: float = 1.225                     # kg/m^3
    H: float = 8500.0                       # m

    # Constant wind (disturbance)
    wind_x: float = 0.0                     # m/s
    wind_y: float = 0.0                     # m/s

    # ---- actuator lag + rate limits ----
    # u_act_dot = (u_cmd - u_act)/tau_u, similarly for delta
    tau_u: float = 0.15                     # s
    tau_delta: float = 0.10                 # s
    u_rate_max: float = 2.0                 # 1/s
    delta_rate_max: float = 1.5             # rad/s

    # ---- input limits (project constraints) ----
    u_min: float = 0.0
    u_max: float = 1.0
    delta_min: float = -0.2
    delta_max: float = 0.2


# =============================================================================
# Aerodynamics: density + drag
# =============================================================================

def air_density(py: float, params: RocketParams) -> float:
    """
    Air density model rho(py).

    If use_exponential_atmos:
        rho = rho0 * exp(-py/H)
    else:
        rho = rho0  (constant density)
    """
    if not params.use_exponential_atmos:
        return params.rho0

    # Never allow negative altitude to increase density unphysically:
    h = max(py, 0.0)
    return params.rho0 * math.exp(-h / params.H)


def drag_force(vx: float, vy: float, py: float, params: RocketParams) -> Tuple[float, float]:
    """
    Quadratic drag force vector.

    1) Compute air-relative velocity:
         v_rel = [vx - wind_x, vy - wind_y]

    2) Drag magnitude:
         D = 0.5 * rho * Cd * A * ||v_rel||^2

    3) Convert to vector that opposes v_rel:
         F_drag = - 0.5 * rho * Cd * A * ||v_rel|| * v_rel

    Returns:
      (Fx_drag, Fy_drag)
    """
    vrel_x = vx - params.wind_x
    vrel_y = vy - params.wind_y

    vrel = math.hypot(vrel_x, vrel_y)
    if vrel < 1e-9:
        return (0.0, 0.0)

    rho = air_density(py, params)
    k = 0.5 * rho * params.Cd * params.A_ref

    Fx = -k * vrel * vrel_x
    Fy = -k * vrel * vrel_y
    return (Fx, Fy)


# =============================================================================
# Thrust model
# =============================================================================

def thrust_magnitude(u_act: float, m: float, params: RocketParams) -> float:
    """
    Compute thrust magnitude T (Newtons) from the actual throttle u_act.

    By definition:
        T = u_act * T_max

    with T_max chosen by thrust_mode.
    """
    u_act = clamp(u_act, params.u_min, params.u_max)
    m = max(m, 1e-6)

    if params.thrust_mode == "constant_Tmax":
        # Hardware-limited: T_max fixed from initial mass m0
        T_max = params.thrust_to_weight * params.m0 * params.g
    else:
        # Hover-normalized: T_max tracks mass so that hover throttle stays constant
        T_max = params.thrust_to_weight * m * params.g

    return u_act * T_max


# =============================================================================
# The MAIN thing you asked for: x_dot = f(x, u)
# =============================================================================

def f(x: Tuple[float, ...], u: Tuple[float, float], params: RocketParams) -> Tuple[float, ...]:
    """
    State-space dynamics:

        x_dot = f(x, u)

    Inputs:
      x      : state vector (length 9)
      u      : input vector (length 2) = (u_cmd, delta_cmd)
      params : RocketParams

    Returns:
      x_dot  : time derivative of the state vector (length 9)

    ----------------
    Unpack:
      x = (px, py, vx, vy, theta, omega, m, u_act, delta_act)
      u = (u_cmd, delta_cmd)
    ----------------
    """
    # ----------------------------
    # 1) Unpack state and inputs
    # ----------------------------
    px, py, vx, vy, theta, omega, m, u_act, delta_act = x
    u_cmd, delta_cmd = u

    # Numerical safety:
    m = max(m, 1e-6)

    # ----------------------------
    # 2) Clamp commanded inputs to allowed ranges
    # ----------------------------
    u_cmd = clamp(u_cmd, params.u_min, params.u_max)
    delta_cmd = clamp(delta_cmd, params.delta_min, params.delta_max)

    # ----------------------------
    # 3) Actuator dynamics (first-order lag + rate limits)
    #
    # u_act_dot     = (u_cmd - u_act)/tau_u
    # delta_act_dot = (delta_cmd - delta_act)/tau_delta
    #
    # Then clamp rates (how quickly actuators can change).
    # ----------------------------
    u_act_dot = (u_cmd - u_act) / max(params.tau_u, 1e-6)
    delta_act_dot = (delta_cmd - delta_act) / max(params.tau_delta, 1e-6)

    u_act_dot = clamp(u_act_dot, -params.u_rate_max, params.u_rate_max)
    delta_act_dot = clamp(delta_act_dot, -params.delta_rate_max, params.delta_rate_max)

    # ----------------------------
    # 4) Compute thrust force components
    # ----------------------------
    T = thrust_magnitude(u_act, m, params)

    # Thrust direction relative to inertial vertical:
    #   phi = theta + delta_act
    phi = theta + delta_act

    Fx_thrust = T * math.sin(phi)
    Fy_thrust = T * math.cos(phi)

    # ----------------------------
    # 5) Aerodynamic drag (optional)
    # ----------------------------
    Fx_drag, Fy_drag = (0.0, 0.0)
    if params.use_aero_drag:
        Fx_drag, Fy_drag = drag_force(vx, vy, py, params)

    # ----------------------------
    # 6) Translational accelerations
    # ----------------------------
    ax = (Fx_thrust + Fx_drag) / m
    ay = (Fy_thrust + Fy_drag) / m - params.g

    # ----------------------------
    # 7) Rotational dynamics
    #
    # TVC torque (planar moment-arm approximation):
    #   tau_tvc = L * T * sin(delta_act)
    #
    # plus simple damping:
    #   tau_damp = - rot_damp * omega
    #
    # Then:
    #   omega_dot = (tau_tvc + tau_damp) / Iyy
    # ----------------------------
    tau_tvc = params.engine_lever_arm * T * math.sin(delta_act)
    tau_damp = -params.rot_damp * omega
    omega_dot = (tau_tvc + tau_damp) / max(params.Iyy, 1e-9)

    # Kinematics:
    theta_dot = omega

    # ----------------------------
    # 8) Mass depletion (optional)
    #
    # mdot = T / (Isp * g0)
    # m_dot = -mdot
    # ----------------------------
    m_dot = 0.0
    if params.use_mass_depletion:
        m_dot = - T / max(params.Isp * params.g0, 1e-9)

    # ----------------------------
    # 9) Assemble x_dot
    # ----------------------------
    px_dot = vx
    py_dot = vy
    vx_dot = ax
    vy_dot = ay

    return (
        px_dot, py_dot,
        vx_dot, vy_dot,
        theta_dot, omega_dot,
        m_dot,
        u_act_dot, delta_act_dot
    )
