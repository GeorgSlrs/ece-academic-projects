"""
rocket_simulator.py
===================

YOU ASKED FOR (final structure)
------------------------------
You wanted ONLY 3 Python files:

  1) rocket_main.py      -> the ONLY file you run
  2) rocket_simulator.py -> MUST contain: simulator + controller + GUI + plots
  3) rocket_dynamics.py  -> MUST contain ONLY the dynamics equations x_dot = f(x,u)

So this file is the "everything except pure dynamics" file:
  - Numerical integration (RK4)
  - Noise models (process + input)
  - Touchdown logic (LANDED vs CRASHED vs MISSED PAD)
  - A SAFE "brake-immediately" autopilot
  - A live Tkinter GUI with Start/Stop/Restart/End
  - Logging to an .npz file
  - Plotting after you press End

IMPORTANT USER GOAL
-------------------
Land the rocket in the landing zone centered at (x,y) = (0,0).

Constraints:
  - Steer with:
      throttle u in [0,1]
      gimbal delta in [-0.2, 0.2] rad
  - Thrust-to-weight ratio = 2
  - u = 0.5 hovers (in the default thrust mode)
  - Touch down gently (< 5 m/s)

Key practical fact (why "brake immediately" matters):
  With T/W = 2 and a vertical rocket, the maximum *net* upward acceleration
  you can produce is about +g (because at full thrust you get ~2g upward thrust
  minus g gravity = +g net).

  That means if you allow the rocket to reach very large downward speed
  near the ground, it becomes physically impossible to stop in time.

So our autopilot is intentionally conservative and safe.

"""

from __future__ import annotations

# =============================================================================
# Standard library imports
# =============================================================================

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import math
import os
import time
import random

# =============================================================================
# Third-party imports
# =============================================================================

import numpy as np

# Matplotlib is used ONLY for plotting after you press End.
# (We keep it out of the inner simulation loop.)
import matplotlib.pyplot as plt

# Tkinter is used for the live GUI.
import tkinter as tk
from tkinter import ttk

# =============================================================================
# Import the PURE dynamics equations (user requirement: dynamics stay in rocket_dynamics.py)
# =============================================================================

from rocket_dynamics import RocketParams, f, thrust_magnitude


# =============================================================================
# Small helpers
# =============================================================================

def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    return max(lo, min(hi, x))


def wrap_to_pi(angle_rad: float) -> float:
    """Wrap angle to (-pi, pi]."""
    a = (angle_rad + math.pi) % (2.0 * math.pi) - math.pi
    if a <= -math.pi:
        a += 2.0 * math.pi
    return a


def deg2rad(deg: float) -> float:
    """Degrees -> radians."""
    return deg * math.pi / 180.0


def rad2deg(rad: float) -> float:
    """Radians -> degrees."""
    return rad * 180.0 / math.pi


def vec_norm2(x: float, y: float) -> float:
    """Euclidean norm of a 2D vector."""
    return math.hypot(x, y)


# =============================================================================
# Simulation configuration
# =============================================================================

@dataclass
class SimConfig:
    """
    Simulation configuration (NOT physical rocket parameters).

    dt
      Fixed simulation timestep (seconds).

    t_max
      Maximum simulation time (seconds). If exceeded -> TIMEOUT.

    landing_zone_width
      Full width of the landing zone (meters).

      You chose option A: zone width = 10 m
      -> half width = 5 m
      -> a valid touchdown must satisfy |x| <= 5.

    --------------------------------------------------------------------------
    PROCESS NOISE (noise on the PHYSICS / motion)
    --------------------------------------------------------------------------
    noise_mu, noise_sigma
      "Process noise" applied to the motion. After each integration step,
      we randomly perturb:
        vx, vy, omega
      with acceleration-like Gaussian noise.

      Units:
        vx,vy perturbations correspond to (m/s^2)
        omega perturbation corresponds to (rad/s^2)

    --------------------------------------------------------------------------
    INPUT NOISE (noise on the COMMANDS you send in)
    --------------------------------------------------------------------------
    input_u_mu, input_u_sigma
      Noise added to throttle command u_cmd before passing to the dynamics.
      Units: throttle fraction (dimensionless)

    input_delta_mu, input_delta_sigma
      Noise added to gimbal command delta_cmd before passing to the dynamics.
      Units: radians

    Note:
      After adding noise, we CLAMP to the valid command ranges.
    """

    dt: float = 0.02
    t_max: float = 60.0  # safer = give the autopilot more time

    # Landing zone width (full width, meters)
    landing_zone_width: float = 10.0

    # --- process noise (physics) ---
    noise_mu: float = 0.0
    noise_sigma: float = 0.0

    # --- input noise (commands) ---
    input_u_mu: float = 0.0
    input_u_sigma: float = 0.0
    input_delta_mu: float = 0.0
    input_delta_sigma: float = 0.0

    seed: Optional[int] = None

    # Touchdown thresholds (your requirement: gentle touchdown < 5 m/s)
    land_vx_max: float = 5.0
    land_vy_max: float = 5.0
    land_theta_max_deg: float = 10.0
    land_omega_max_deg_s: float = 15.0


# =============================================================================
# Status labels the GUI can display
# =============================================================================

STATUS_RUNNING = "RUNNING"
STATUS_PAUSED  = "PAUSED"
STATUS_CRASHED = "CRASHED"
STATUS_LANDED  = "LANDED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_MISSED  = "MISSED_PAD"  # touched down gently but outside the landing zone


# =============================================================================
# Helper: RK4 integrator
# =============================================================================

def rk4_step(x: Tuple[float, ...],
             u: Tuple[float, float],
             dt: float,
             params: RocketParams) -> Tuple[float, ...]:
    """
    One classic Runge-Kutta 4 integration step.

    We assume x_dot = f(x,u).

    RK4 idea in plain words:
      - Evaluate slope at the beginning (k1)
      - Evaluate slope in the middle using k1 (k2)
      - Evaluate slope in the middle using k2 (k3)
      - Evaluate slope at the end using k3 (k4)
      - Combine them in a weighted average

    This is more accurate than Euler for the same dt (usually).
    """

    k1 = f(x, u, params)

    x2 = tuple(x[i] + 0.5 * dt * k1[i] for i in range(len(x)))
    k2 = f(x2, u, params)

    x3 = tuple(x[i] + 0.5 * dt * k2[i] for i in range(len(x)))
    k3 = f(x3, u, params)

    x4 = tuple(x[i] + dt * k3[i] for i in range(len(x)))
    k4 = f(x4, u, params)

    x_next = tuple(
        x[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i])
        for i in range(len(x))
    )
    return x_next


# =============================================================================
# Main simulator class (physics + noise + touchdown)
# =============================================================================

class RocketSimulator:
    """
    Holds the rocket state and advances it forward in time.

    STATE DEFINITION (must match rocket_dynamics.py)
    -----------------------------------------------
    x = [ px, py, vx, vy, theta, omega, m, u_act, delta_act ]  (length 9)

    INPUTS
    ------
    u = [ u_cmd, delta_cmd ]  (length 2)

    The simulator does NOT decide u_cmd or delta_cmd.
    The controller (autopilot) decides that.

    The GUI will call step() many times per second.
    """

    def __init__(self, params: RocketParams, config: SimConfig):
        self.params = params
        self.config = config

        if config.seed is not None:
            random.seed(config.seed)

        self.t: float = 0.0
        self.x: Tuple[float, ...] = (0.0,) * 9
        self.status: str = STATUS_PAUSED

        # Save initial state so "Restart" is easy
        self._x0: Tuple[float, ...] = self.x

        # For GUI/debug display:
        self.last_u_cmd: float = 0.0
        self.last_delta_cmd: float = 0.0
        self.last_u_applied: float = 0.0
        self.last_delta_applied: float = 0.0

    def reset(self, x0: Tuple[float, ...]) -> None:
        """Reset time and state to x0 and mark as PAUSED."""
        self.t = 0.0
        self.x = tuple(x0)
        self._x0 = tuple(x0)
        self.status = STATUS_PAUSED

        self.last_u_cmd = 0.0
        self.last_delta_cmd = 0.0
        self.last_u_applied = 0.0
        self.last_delta_applied = 0.0

    def restart(self) -> None:
        """Restart back to the last reset() initial condition."""
        self.reset(self._x0)

    def set_process_noise(self, mu: float, sigma: float) -> None:
        """Update process noise parameters on the fly."""
        self.config.noise_mu = float(mu)
        self.config.noise_sigma = float(sigma)

    def set_input_noise(self, u_mu: float, u_sigma: float, delta_mu: float, delta_sigma: float) -> None:
        """Update input noise parameters on the fly."""
        self.config.input_u_mu = float(u_mu)
        self.config.input_u_sigma = float(u_sigma)
        self.config.input_delta_mu = float(delta_mu)
        self.config.input_delta_sigma = float(delta_sigma)

    def landing_zone_half_width(self) -> float:
        """Convenience: half of the landing zone width."""
        return 0.5 * float(self.config.landing_zone_width)

    # -------------------------------------------------------------------------
    # IMPORTANT TOUCHDOWN GEOMETRY (fixes your "it says LANDED too late" issue)
    # -------------------------------------------------------------------------
    #
    # The simulator state uses (px, py) as the rocket's *center* position.
    # But the rocket you SEE in the GUI is a *finite-sized polygon* (it has height).
    #
    # If we detect touchdown using only:
    #     py <= 0
    # then we are effectively checking when the CENTER of the rocket hits the ground.
    # Visually, the bottom of the rocket touches the ground MUCH EARLIER than that,
    # which is exactly why you complained that it "lands" when the rocket is already
    # in the middle of the pad / below where it should be.
    #
    # So we do this correctly:
    #   - we compute the rocket polygon corners in WORLD coordinates
    #   - we find the minimum y value among all corners: y_min
    #   - touchdown happens when y_min <= 0
    #
    # This makes the simulator "agree" with the drawing, because the drawing uses
    # the same polygon geometry.
    #
    # NOTE:
    #   This is still a simplified rigid body contact model (no bounce, no friction),
    #   but it is much more consistent than py<=0.
    # -------------------------------------------------------------------------

    def _rocket_polygon_world(self, px: float, py: float, theta: float) -> List[Tuple[float, float]]:
        """
        Return the rocket outline polygon vertices in WORLD coordinates.

        We intentionally copy the SAME geometry used by the GUI:
          - Height H = 14 m
          - Width  W = 3.2 m
          - A slightly "finned" shape near the base

        Why does the simulator need this?
        Because touchdown should happen when the *bottom* of the rocket touches
        the ground, not when the rocket's center touches.

        Inputs:
          px, py   : rocket center position (meters)
          theta    : rocket angle from +y axis (radians), theta=0 means upright

        Output:
          list of (x,y) world points
        """
        H = 14.0
        W = 3.2

        # Local coordinates (body frame), centered at rocket center.
        local = [
            (0.0, +H / 2),
            (+W / 2, +H * 0.25),
            (+W / 2, -H * 0.35),
            (+W * 0.75, -H / 2),
            (0.0, -H * 0.42),
            (-W * 0.75, -H / 2),
            (-W / 2, -H * 0.35),
            (-W / 2, +H * 0.25),
        ]

        # Body "up" direction in world coordinates:
        #   theta is measured from +y, so:
        #     dir = [sin(theta), cos(theta)]
        dir_x = math.sin(theta)
        dir_y = math.cos(theta)

        # Perpendicular direction (body "right") in world:
        #   perp = rotate(dir) by -90 degrees
        #   perp = [cos(theta), -sin(theta)]
        perp_x = math.cos(theta)
        perp_y = -math.sin(theta)

        world_pts: List[Tuple[float, float]] = []
        for bx, by in local:
            wx = px + bx * perp_x + by * dir_x
            wy = py + bx * perp_y + by * dir_y
            world_pts.append((wx, wy))

        return world_pts

    def _ground_contact_info(self) -> Tuple[float, float]:
        """
        Compute touchdown geometry quantities.

        Returns:
          (y_min, x_at_y_min)

        y_min:
          The smallest y among the rocket polygon points.
          Touchdown happens when y_min <= 0.

        x_at_y_min:
          The x-coordinate of the vertex that is lowest (useful for debugging).

        We DO NOT use x_at_y_min to decide "in the zone",
        because your requirement is explicitly:
          LANDED only if |x_center| <= 5
        i.e., we check px, not the corner.
        """
        px, py, vx, vy, theta, omega, m, u_act, delta_act = self.x
        pts = self._rocket_polygon_world(px, py, theta)

        y_min = pts[0][1]
        x_min = pts[0][0]
        for (xw, yw) in pts:
            if yw < y_min:
                y_min = yw
                x_min = xw

        return float(y_min), float(x_min)

    def _classify_touchdown(self) -> str:
        """
        Called when the BOTTOM of the rocket touches the ground (y_min <= 0).

        Decide if it is:
          - LANDED      : gentle touchdown AND inside landing zone
          - MISSED_PAD  : gentle touchdown BUT outside landing zone
          - CRASHED     : too fast or too tilted

        NOTE:
          We intentionally require only simple checks.
          You can make this fancier later if your assignment demands it.
        """
        px, py, vx, vy, theta, omega, m, u_act, delta_act = self.x

        theta_deg = abs(theta) * 180.0 / math.pi
        omega_deg_s = abs(omega) * 180.0 / math.pi

        gentle = (
            abs(vx) <= self.config.land_vx_max and
            abs(vy) <= self.config.land_vy_max and
            theta_deg <= self.config.land_theta_max_deg and
            omega_deg_s <= self.config.land_omega_max_deg_s
        )

        if not gentle:
            return STATUS_CRASHED

        # Gentle touchdown - now check landing zone.
        half = self.landing_zone_half_width()
        if abs(px) <= half:
            return STATUS_LANDED
        return STATUS_MISSED

    def step(self, u_cmd: float, delta_cmd: float) -> None:
        """
        Advance the simulation by one timestep dt.

        Inputs:
          u_cmd      in [0,1]
          delta_cmd  in [-0.2, 0.2] rad

        This method applies:
          1) INPUT NOISE to commands
          2) RK4 deterministic integration
          3) PROCESS NOISE to (vx, vy, omega)
          4) touchdown classification
        """

        if self.status != STATUS_RUNNING:
            return

        dt = self.config.dt

        # ---------------------------------------------------------
        # 0) Store the raw commands (what the controller requested)
        # ---------------------------------------------------------
        self.last_u_cmd = float(u_cmd)
        self.last_delta_cmd = float(delta_cmd)

        # ---------------------------------------------------------
        # 1) Apply input noise
        # ---------------------------------------------------------
        u_used = self.last_u_cmd
        d_used = self.last_delta_cmd

        if (self.config.input_u_mu != 0.0 or self.config.input_u_sigma != 0.0 or
            self.config.input_delta_mu != 0.0 or self.config.input_delta_sigma != 0.0):

            u_used = u_used + random.gauss(self.config.input_u_mu, self.config.input_u_sigma)
            d_used = d_used + random.gauss(self.config.input_delta_mu, self.config.input_delta_sigma)

        # Clamp to valid limits
        u_used = clamp(u_used, self.params.u_min, self.params.u_max)
        d_used = clamp(d_used, self.params.delta_min, self.params.delta_max)

        self.last_u_applied = float(u_used)
        self.last_delta_applied = float(d_used)

        # ---------------------------------------------------------
        # 2) RK4 integration
        # ---------------------------------------------------------
        x_next = rk4_step(self.x, (u_used, d_used), dt, self.params)

        # ---------------------------------------------------------
        # 3) Process noise
        # ---------------------------------------------------------
        mu = self.config.noise_mu
        sig = self.config.noise_sigma

        if sig != 0.0 or mu != 0.0:
            ax_n = random.gauss(mu, sig)
            ay_n = random.gauss(mu, sig)
            alpha_n = random.gauss(mu, sig)

            px, py, vx, vy, theta, omega, m, u_act, delta_act = x_next
            vx += ax_n * dt
            vy += ay_n * dt
            omega += alpha_n * dt
            x_next = (px, py, vx, vy, theta, omega, m, u_act, delta_act)

        # ---------------------------------------------------------
        # 4) Commit state and advance time
        # ---------------------------------------------------------
        self.t += dt
        self.x = x_next

        # Timeout
        if self.t >= self.config.t_max:
            self.status = STATUS_TIMEOUT
            return

        # Ground contact (BOTTOM of rocket polygon, not the center)
        #
        # We use y_min among the rocket polygon corners:
        #   - y_min <= 0  -> touchdown
        #
        # Then we "snap" the rocket up so that its bottom exactly sits on the ground.
        # This prevents the rocket from visually sinking below the ground line.
        y_min, _x_contact = self._ground_contact_info()
        if y_min <= 0.0:
            # Shift the center upward so the lowest point is exactly y=0.
            px, py, vx, vy, theta, omega, m, u_act, delta_act = self.x
            py = py - y_min
            py = max(py, 0.0)
            self.x = (px, py, vx, vy, theta, omega, m, u_act, delta_act)

            # Classify the touchdown outcome.
            self.status = self._classify_touchdown()
            return


# =============================================================================
# AUTOPILOT: conservative, brake-immediately landing controller
# =============================================================================

@dataclass
class SafeAutopilotGains:
    """
    Beginner-friendly tuning parameters.

    IMPORTANT:
    We tune these for RELIABILITY and SAFETY, not for aggressive performance.
    """

    # Horizontal capture (PD)
    kx: float = 0.08
    kvx: float = 0.35

    # Vertical tracking (PD)
    ky: float = 0.06
    kvy: float = 0.60

    # Brake mode (stronger vertical correction)
    kvy_brake: float = 0.90

    # Attitude stabilization
    k_theta: float = 2.8
    k_omega: float = 3.8

    # Actuator tracking (turn desired actuator values into commanded values)
    #
    # IMPORTANT (your "brake immediately" request):
    #   The engine state u_act has a FIRST-ORDER LAG (tau_u ~ 0.15s).
    #   If k_u_act is too small, u_act ramps up too slowly and the rocket
    #   can pick up a dangerous fall speed before we start braking.
    #
    #   So we use a larger k_u_act to command high thrust quickly when needed.
    k_u_act: float = 6.0

    # Gimbal tracking is also slightly faster so attitude corrections do not lag.
    k_delta_act: float = 4.5

    # Tilt limits (degrees)
    tilt_max_brake_deg: float = 10.0
    tilt_max_align_deg: float = 18.0
    tilt_max_descent_deg: float = 22.0
    tilt_max_flare_deg: float = 8.0

    # Altitudes for phase transitions (meters)
    alt_align: float = 70.0
    alt_flare: float = 10.0
    alt_hold_if_missed: float = 18.0

    # Safe speed limits
    vx_cap_low: float = 6.0

    # If we are climbing (vy > 0), reduce thrust to stop climb
    anti_climb_vy: float = 0.8


class SafeBrakeImmediatelyAutopilot:
    """
    A practical autopilot designed to survive the initial condition you showed:

      x ~ -80..-100 m
      vx ~ +15 m/s
      y  ~ 140..160 m
      vy ~ -30..-35 m/s

    With T/W = 2, we must BRAKE early.

    This controller is NOT "textbook perfect backstepping".
    It is a safe, engineering-style landing autopilot:

      1) BRAKE: immediately reduce the fall speed while keeping upright.
      2) ALIGN: if we are low and not in the landing zone, hover/slow descend
                and slide sideways to get into the zone.
      3) DESCENT: once inside zone, descend with a safe profile.
      4) FLARE: near ground, reduce vertical speed to near zero.

    We also include a tiny bit of "adaptive" behavior:
      - we integrate velocity errors to estimate a constant disturbance bias
        (think wind/drag mismatch).

    That makes the controller more robust without being complicated.
    """

    def __init__(self, params: RocketParams, cfg: SimConfig, gains: Optional[SafeAutopilotGains] = None,
                 mode: str = "adaptive_backstepping"):
        """
        Create the autopilot.

        mode controls WHICH "adaptive" idea we use:

          1) mode = "adaptive_backstepping"  (DEFAULT)
             - this is the same controller you already had:
               a safe backstepping-inspired structure + a tiny disturbance estimate
               (d_hat_x, d_hat_y) that acts like integral action.

          2) mode = "mit"
             - keeps the same safe flight logic / phases,
               but replaces the disturbance-integrator with a simple MIT-rule
               adaptation of a single parameter k_thrust_hat.
               k_thrust_hat estimates "how effective" thrust is at producing
               vertical acceleration (useful if thrust/mass/drag are mismatched).

        IMPORTANT:
          This project is educational. We keep adaptation simple and robust.
          The safe phase logic (BRAKE/ALIGN/DESCENT/FLARE) stays the same in both.
        """
        self.params = params
        self.cfg = cfg
        self.g = params.g
        self.gains = gains if gains is not None else SafeAutopilotGains()
        # Which adaptive strategy are we using? (set by the GUI dropdown)
        self.mode = str(mode)

        # MIT-rule parameter estimate (used only if mode == "mit")
        #
        # Interpretation:
        #   If k_thrust_hat > 1, the controller believes thrust is "more effective"
        #   than nominal, so it will command a bit LESS throttle for the same accel.
        #
        #   If k_thrust_hat < 1, the controller believes thrust is "less effective"
        #   than nominal, so it will command a bit MORE throttle.
        self.k_thrust_hat = 1.0

        # For MIT-rule we need a crude measured vertical acceleration.
        # We approximate it with a finite difference of vy.
        self._vy_prev_for_mit = None

        # "Adaptive" disturbance estimates (acceleration bias)
        self.d_hat_x = 0.0
        self.d_hat_y = 0.0

        # Internal reference altitude (prevents the classic "k * y" dive)
        self.y_ref: Optional[float] = None

        # Phase logic
        self.phase: str = "BRAKE"  # start here by user request
        self._phase_entry_t: float = 0.0

        # For numeric derivative / smoothing
        self._prev_u_cmd: float = 0.5
        self._prev_delta_cmd: float = 0.0

    def reset(self) -> None:
        """Reset internal states."""
        self.d_hat_x = 0.0
        self.d_hat_y = 0.0

        # Reset MIT estimate as well.
        self.k_thrust_hat = 1.0
        self._vy_prev_for_mit = None

        self.y_ref = None
        self.phase = "BRAKE"
        self._phase_entry_t = 0.0
        self._prev_u_cmd = 0.5
        self._prev_delta_cmd = 0.0

    def _aT_effective(self, m: float) -> float:
        """
        Effective thrust acceleration per unit throttle.

        In hover_normalized mode:
          T_max = (T/W)*m*g
          => T/m = (T/W)*g*u

        So "per u" acceleration is:
          aT = (T/W)*g

        If constant_Tmax, it depends on m.
        """
        m = max(m, 1e-6)
        if self.params.thrust_mode == "constant_Tmax":
            return self.params.thrust_to_weight * (self.params.m0 / m) * self.g
        return self.params.thrust_to_weight * self.g

    def _vy_profile(self, y: float) -> float:
        """
        A safe desired descent speed as a function of altitude.

        - high altitude: can descend faster
        - low altitude: must descend slowly

        NOTE: this is conservative by design.
        """
        y = max(0.0, float(y))

        # A simple piecewise profile (easy to understand and tune)
        if y > 120.0:
            return -12.0
        if y > 60.0:
            return -10.0
        if y > 25.0:
            return -7.0
        if y > self.gains.alt_flare:
            return -4.0

        # flare region (y <= alt_flare)
        # at y = alt_flare -> about -2.0
        # at y = 0 -> about -0.3
        return -max(0.3, 0.2 * y)

    def _update_phase(self, t: float, x: Tuple[float, ...]) -> None:
        """
        Phase machine with hysteresis.

        We keep it simple:
          - start in BRAKE
          - once fall speed is safe, switch to DESCENT or ALIGN
          - near ground -> FLARE

        ALIGN is used to ensure we do not touch down outside the landing zone.
        """
        px, py, vx, vy, theta, omega, m, u_act, delta_act = x
        half = 0.5 * self.cfg.landing_zone_width

        in_zone = abs(px) <= half

        # Always flare near ground.
        if py <= self.gains.alt_flare:
            if self.phase != "FLARE":
                self.phase = "FLARE"
                self._phase_entry_t = t
            return

        # If we are low AND not in the zone, do ALIGN (hover/slow descend and slide).
        if (py <= self.gains.alt_hold_if_missed) and (not in_zone):
            if self.phase != "ALIGN":
                self.phase = "ALIGN"
                self._phase_entry_t = t
            return

        # BRAKE exits when vertical speed is no longer dangerously negative.
        #
        # Why this rule exists:
        #   Your screenshots show the rocket can start with vy ~ -35 m/s.
        #   With T/W=2, the best upward braking you can get (upright) is about +g,
        #   so we need to spend the first couple of seconds "just braking".
        #
        # We keep BRAKE until:
        #   - we have spent at least a short time braking (>= 0.5 s), and
        #   - the fall speed is above -11 m/s (i.e., much safer).
        if self.phase == "BRAKE":
            if (t - self._phase_entry_t) >= 0.5 and vy >= -11.0:
                self.phase = "DESCENT"
                self._phase_entry_t = t
            return

        # If we are high, stay in DESCENT (with gentle x correction).
        if self.phase not in ["DESCENT", "ALIGN", "FLARE"]:
            self.phase = "DESCENT"
            self._phase_entry_t = t

    def compute_control(self,
                        t: float,
                        x: Tuple[float, ...],
                        dt: float,
                        target_xy: Tuple[float, float] = (0.0, 0.0)
                        ) -> Tuple[float, float, Dict[str, float]]:
        """
        Main API: compute (u_cmd, delta_cmd) given current state.

        Returns:
          u_cmd, delta_cmd, dbg

        dbg is a dictionary of internal signals for plotting/debug.
        """
        dt = max(float(dt), 1e-6)

        px, py, vx, vy, theta, omega, m, u_act, delta_act = x

        # Create internal altitude reference the first time we run.
        # This prevents the classic "v_ref = v_des - k*y" dive-to-death.
        if self.y_ref is None:
            self.y_ref = float(py)

        # Update phase based on current state.
        self._update_phase(t, x)

        # Landing zone
        half = 0.5 * self.cfg.landing_zone_width

        # Zone error: 0 inside the zone, distance to nearest edge outside.
        if px < -half:
            x_zone_error = px + half
        elif px > half:
            x_zone_error = px - half
        else:
            x_zone_error = 0.0

        # ------------------------------------------------------------------
        # 1) Choose desired velocities (vx_des, vy_des) based on the phase
        # ------------------------------------------------------------------

        vy_prof = self._vy_profile(py)

        if self.phase == "BRAKE":
            # BRAKE: reduce fall speed ASAP, keep nearly upright.
            # We do NOT try to aggressively fix x while braking.
            vy_des = max(vy_prof, -8.0)  # never demand super fast descent here
            vx_des = 0.0

        elif self.phase == "ALIGN":
            # ALIGN: do NOT descend quickly if we are not over the pad.
            # We hover or slow descend while sliding sideways.
            vy_des = -0.5

            # Capture law: pull x_zone_error to 0 without overshoot.
            # v_des = -k * error, then clamp.
            vx_des = clamp(-0.25 * x_zone_error, -self.gains.vx_cap_low, self.gains.vx_cap_low)

        elif self.phase == "FLARE":
            # FLARE: very gentle descent, kill horizontal speed.
            vy_des = self._vy_profile(py)
            vx_des = 0.0

        else:
            # DESCENT: keep descending with the safe profile.
            vy_des = vy_prof

            # Gentle x capture even at altitude, but keep it conservative.
            vx_des = clamp(-0.18 * x_zone_error, -self.gains.vx_cap_low, self.gains.vx_cap_low)

        # ------------------------------------------------------------------
        # 2) Velocity tracking -> desired accelerations (ax_cmd, ay_cmd)
        # ------------------------------------------------------------------

        # Simple PD on velocity and (optionally) position.
        # For horizontal we use zone error so we don't chase x=0 too hard.
        ax_cmd = (-self.gains.kx * x_zone_error) + (self.gains.kvx * (vx_des - vx))

        # Vertical: use y_ref instead of ground (prevents dive).
        # We update y_ref to move downward at the desired rate.
        # y_ref_dot = vy_des
        self.y_ref += float(vy_des) * dt

        y_err = (self.y_ref - py)

        if self.phase == "BRAKE":
            ay_cmd = (self.gains.ky * y_err) + (self.gains.kvy_brake * (vy_des - vy))
        else:
            ay_cmd = (self.gains.ky * y_err) + (self.gains.kvy * (vy_des - vy))

        # ------------------------------------------------------------------
        # EMERGENCY BRAKE OVERRIDE (your "brake immediately" request)
        # ------------------------------------------------------------------
        # If the rocket is falling extremely fast, we do something very simple:
        #   - stop trying to translate sideways
        #   - command almost maximum upward acceleration
        #   - keep the thrust vector nearly vertical
        #
        # This is an engineering safety trick.
        # It is not elegant, but it dramatically improves survivability.
        if self.phase == "BRAKE" and vy <= -15.0:
            ax_cmd = 0.0
            ay_cmd = 0.90 * self.g

        # Anti-climb: if we start climbing, reduce thrust to stop it.
        if vy > self.gains.anti_climb_vy and py > 1.0:
            ay_cmd = min(ay_cmd, -0.5)  # push gently downward until vy <= 0

        # Safety clamps on net accelerations (these are net accelerations "ay")
        # Net vertical acceleration ay is limited by rocket physics:
        #   - minimum is about -g (engine off)
        #   - maximum is about +g (full thrust, upright)
        ay_cmd = clamp(ay_cmd, -self.g, +0.95 * self.g)

        # Horizontal acceleration also limited to avoid huge tilt demands.
        ax_cmd = clamp(ax_cmd, -4.0, +4.0)

        # ------------------------------------------------------------------
        # 3) Map desired accelerations -> desired thrust direction + throttle
        # ------------------------------------------------------------------

        # The thrust must provide acceleration:
        #   a_thrust = [ax_cmd, ay_cmd + g]
        # because gravity contributes -g in the dynamics.
        a_thrust_x = ax_cmd
        a_thrust_y = ay_cmd + self.g

        # Thrust must point upward overall.
        a_thrust_y = max(a_thrust_y, 0.2)

        # Desired thrust direction angle phi_ref (angle from +y axis)
        phi_ref = math.atan2(a_thrust_x, a_thrust_y)

        # Tilt limits depend on phase.
        if self.phase == "BRAKE":
            phi_max = deg2rad(self.gains.tilt_max_brake_deg)
        elif self.phase == "ALIGN":
            phi_max = deg2rad(self.gains.tilt_max_align_deg)
        elif self.phase == "FLARE":
            phi_max = deg2rad(self.gains.tilt_max_flare_deg)
        else:
            phi_max = deg2rad(self.gains.tilt_max_descent_deg)

        phi_ref = clamp(phi_ref, -phi_max, +phi_max)

        # Required thrust acceleration magnitude
        a_needed = vec_norm2(a_thrust_x, a_thrust_y)

        # Convert to desired ACTUAL throttle u_act_des.
        # Nominal thrust acceleration per unit throttle
        aT_nom = self._aT_effective(m)

        # If we are in MIT mode, we scale that mapping by our estimated gain.
        # (This is where the MIT parameter actually affects the control.)
        if self.mode == "mit":
            aT_used = aT_nom * max(self.k_thrust_hat, 1e-3)
        else:
            aT_used = aT_nom

        # Convert required acceleration magnitude -> desired throttle (actuator state)
        u_act_des = clamp(a_needed / max(aT_used, 1e-6), 0.0, 1.0)

        # ------------------------------------------------------------------
        # 4) Inner attitude loop -> desired gimbal (delta_act_des)
        # ------------------------------------------------------------------

        # IMPORTANT:
        # In the dynamics, thrust direction is:
        #   phi = theta + delta_act
        # So if we want phi_ref, a good theta reference is:
        #   theta_ref = phi_ref - delta_act
        # (this avoids double-counting delta).
        theta_ref = clamp(phi_ref - delta_act, -deg2rad(35.0), +deg2rad(35.0))

        # We use a simple PD in angular space, but scale by the model gain.
        # omega_dot approx = b * delta_act - d_omega * omega.
        T_now = thrust_magnitude(u_act, m, self.params)
        b_model = (self.params.engine_lever_arm * T_now) / max(self.params.Iyy, 1e-6)
        b_model = max(b_model, 1e-4)

        theta_err = wrap_to_pi(theta - theta_ref)
        omega_err = omega

        # Desired delta_act (actuator state) to produce the needed torque.
        delta_act_des = -(self.gains.k_theta * theta_err + self.gains.k_omega * omega_err) / b_model
        delta_act_des = clamp(delta_act_des, self.params.delta_min, self.params.delta_max)

        # ------------------------------------------------------------------
        # 5) Actuator tracking loop (u_act, delta_act) -> commanded (u_cmd, delta_cmd)
        # ------------------------------------------------------------------

        # First-order actuator lag model in the dynamics:
        #   u_act_dot = (u_cmd - u_act)/tau_u
        # We want u_act to track u_act_des. A standard trick is:
        #   u_act_dot_des = k*(u_act_des - u_act)
        # and then choose:
        #   u_cmd = u_act + tau_u * u_act_dot_des
        u_act_dot_des = self.gains.k_u_act * (u_act_des - u_act)
        u_cmd = u_act + self.params.tau_u * u_act_dot_des
        u_cmd = clamp(u_cmd, self.params.u_min, self.params.u_max)

        # Same idea for delta actuator
        delta_dot_des = self.gains.k_delta_act * (delta_act_des - delta_act)
        delta_cmd = delta_act + self.params.tau_delta * delta_dot_des
        delta_cmd = clamp(delta_cmd, self.params.delta_min, self.params.delta_max)

        # Small command smoothing (prevents twitching / chatter)
        #
        # IMPORTANT:
        #   In BRAKE we want commands to react FAST, so we smooth LESS.
        #   Near FLARE we keep smoothing moderate.
        if self.phase == "BRAKE":
            alpha = 0.75
        elif self.phase == "FLARE":
            alpha = 0.55
        else:
            alpha = 0.35
        u_cmd = (1 - alpha) * self._prev_u_cmd + alpha * u_cmd
        delta_cmd = (1 - alpha) * self._prev_delta_cmd + alpha * delta_cmd
        self._prev_u_cmd = u_cmd
        self._prev_delta_cmd = delta_cmd

        # ------------------------------------------------------------------
        # 6) ADAPTATION (choose between 2 strategies)
        # ------------------------------------------------------------------
        #
        # You asked for a dropdown that lets you switch between:
        #   (A) the "adaptive backstepping style" used in this project, and
        #   (B) an MIT-rule style adaptation.
        #
        # We implement BOTH in a beginner-friendly way.
        #
        # ------------------------------------------------------------------
        # (A) mode == "adaptive_backstepping"
        # ------------------------------------------------------------------
        # We keep two disturbance estimates:
        #     d_hat_x  : estimates a constant horizontal acceleration bias
        #     d_hat_y  : estimates a constant vertical acceleration bias
        #
        # How do we update them?
        #   If vx keeps being bigger than we want (vx > vx_des), that suggests
        #   there is a constant "push" in +x (e.g., wind or modeling error).
        #   So we integrate the velocity error:
        #
        #       d_hat_x_dot = gamma * (vx - vx_des)
        #
        # same for y:
        #
        #       d_hat_y_dot = gamma * (vy - vy_des)
        #
        # This is basically "integral action" (very common in control).
        #
        # Then we nudge the commands slightly using these estimates.
        #
        # ------------------------------------------------------------------
        # (B) mode == "mit"
        # ------------------------------------------------------------------
        # MIT rule is often taught as:
        #   - define a cost J = 0.5 * e^2
        #   - choose an adjustable parameter θ_hat
        #   - update θ_hat in the direction that reduces J:
        #
        #       θ_hat_dot = -γ * ∂J/∂θ_hat = -γ * e * ∂e/∂θ_hat
        #
        # Here we use ONE adjustable parameter:
        #     k_thrust_hat
        #
        # meaning:
        #   "How effective is thrust at producing vertical acceleration?"
        #
        # We estimate vertical acceleration from the measured velocity:
        #     a_y_meas ≈ (vy - vy_prev)/dt
        #
        # and we compare it to our commanded net vertical acceleration ay_cmd.
        #
        # Then we update k_thrust_hat so that the mapping from throttle -> accel
        # becomes more accurate over time.
        #
        # IMPORTANT:
        #   We intentionally keep this MIT adaptation conservative and bounded,
        #   because aggressive parameter adaptation can destabilize systems.
        # ------------------------------------------------------------------

        # Default values used in the debug logs (filled below depending on mode)
        ay_meas = float("nan")
        e_ay = float("nan")

        if self.mode == "adaptive_backstepping":

            # --- disturbance-integrator adaptation (very robust) ---
            gamma = 0.12
            self.d_hat_x = clamp(self.d_hat_x + gamma * (vx - vx_des) * dt, -10.0, +10.0)
            self.d_hat_y = clamp(self.d_hat_y + gamma * (vy - vy_des) * dt, -10.0, +10.0)

            # Apply disturbance estimates by nudging commands slightly.
            # This is intentionally SMALL so we don't destabilize.
            u_cmd = clamp(u_cmd + 0.01 * self.d_hat_y, 0.0, 1.0)
            delta_cmd = clamp(delta_cmd - 0.002 * self.d_hat_x, self.params.delta_min, self.params.delta_max)

        else:
            # --- MIT-rule adaptation of thrust effectiveness ---

            # 1) Estimate vertical acceleration from vy finite difference.
            if self._vy_prev_for_mit is None:
                self._vy_prev_for_mit = float(vy)
            ay_meas = (float(vy) - float(self._vy_prev_for_mit)) / dt
            self._vy_prev_for_mit = float(vy)

            # 2) Error between what we WANTED (ay_cmd) and what we GOT (ay_meas).
            e_ay = float(ay_cmd) - float(ay_meas)

            # 3) Update the estimate.
            #
            # A very conservative MIT-like update:
            #   k_dot = -gamma_k * e_ay  - sigma_k*(k-1)
            #
            # If e_ay > 0 (we didn't accelerate upward enough), we want MORE thrust.
            # That happens if k decreases (because u_act_des = a_needed/(aT*k)).
            gamma_k = 0.08
            sigma_k = 0.03
            k_dot = (-gamma_k * e_ay) - (sigma_k * (self.k_thrust_hat - 1.0))
            self.k_thrust_hat = float(clamp(self.k_thrust_hat + k_dot * dt, 0.60, 1.40))

            # In MIT mode we DO NOT use the disturbance nudges.
            # (This keeps the comparison "clean": only one adaptation mechanism.)
            self.d_hat_x = 0.0
            self.d_hat_y = 0.0

        dbg = {
            "phase": {"BRAKE": 0, "ALIGN": 1, "DESCENT": 2, "FLARE": 3}.get(self.phase, -1),
            # Which controller mode is active (for plotting / debugging)
            # 0 = adaptive_backstepping, 1 = mit
            "mode": 0 if self.mode == "adaptive_backstepping" else 1,
            "k_thrust_hat": float(self.k_thrust_hat),
            "ay_cmd": float(ay_cmd),
            "ay_meas": float(ay_meas),
            "e_ay": float(e_ay),
            "x_zone_error": x_zone_error,
            "vx_des": vx_des,
            "vy_des": vy_des,
            "y_ref": float(self.y_ref),
            "phi_ref": float(phi_ref),
            "theta_ref": float(theta_ref),
            "u_act_des": float(u_act_des),
            "delta_act_des": float(delta_act_des),
            "d_hat_x": float(self.d_hat_x),
            "d_hat_y": float(self.d_hat_y),
        }

        return float(u_cmd), float(delta_cmd), dbg


# =============================================================================
# Plotting utilities (called after End)
# =============================================================================

def plot_log(npz_path: str) -> None:
    """
    Plot various graphs saved in the simulation log.

    The log is created by the GUI when you press End.

    We keep the plots simple and readable:
      - position and velocity
      - attitude
      - commanded vs actual actuator values
      - autopilot phase and key internal signals
    """

    data = np.load(npz_path, allow_pickle=True)

    t = data["t"]
    X = data["X"]
    Ucmd = data["U_cmd"]
    Uappl = data["U_applied"]
    dbg = data["dbg"].item() if "dbg" in data else {}

    px = X[:, 0]
    py = X[:, 1]
    vx = X[:, 2]
    vy = X[:, 3]
    theta = X[:, 4]
    omega = X[:, 5]
    u_act = X[:, 7]
    delta_act = X[:, 8]

    u_cmd = Ucmd[:, 0]
    d_cmd = Ucmd[:, 1]
    u_used = Uappl[:, 0]
    d_used = Uappl[:, 1]

    # --- Figure 1: positions ---
    plt.figure()
    plt.title("Position vs time")
    plt.plot(t, px, label="x (m)")
    plt.plot(t, py, label="y (m)")
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("time (s)")
    plt.ylabel("position")
    plt.legend()
    plt.grid(True)

    # --- Figure 2: velocities ---
    plt.figure()
    plt.title("Velocity vs time")
    plt.plot(t, vx, label="vx (m/s)")
    plt.plot(t, vy, label="vy (m/s)")
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("time (s)")
    plt.ylabel("velocity")
    plt.legend()
    plt.grid(True)

    # --- Figure 3: attitude ---
    plt.figure()
    plt.title("Attitude vs time")
    plt.plot(t, rad2deg(theta), label="theta (deg)")
    plt.plot(t, rad2deg(omega), label="omega (deg/s)")
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("time (s)")
    plt.ylabel("attitude")
    plt.legend()
    plt.grid(True)

    # --- Figure 4: throttle commanded vs applied ---
    plt.figure()
    plt.title("Throttle: commanded vs applied")
    plt.plot(t, u_cmd, label="u_cmd")
    plt.plot(t, u_used, label="u_applied")
    plt.plot(t, u_act, label="u_act (state)")
    plt.xlabel("time (s)")
    plt.ylabel("throttle")
    plt.legend()
    plt.grid(True)

    # --- Figure 5: gimbal commanded vs applied ---
    plt.figure()
    plt.title("Gimbal: commanded vs applied")
    plt.plot(t, rad2deg(d_cmd), label="delta_cmd (deg)")
    plt.plot(t, rad2deg(d_used), label="delta_applied (deg)")
    plt.plot(t, rad2deg(delta_act), label="delta_act (deg, state)")
    plt.xlabel("time (s)")
    plt.ylabel("gimbal (deg)")
    plt.legend()
    plt.grid(True)

    # --- Optional: phase plot if present ---
    if "phase" in dbg:
        plt.figure()
        plt.title("Autopilot phase (0=BRAKE,1=ALIGN,2=DESCENT,3=FLARE)")
        plt.plot(t, dbg["phase"], label="phase")
        plt.xlabel("time (s)")
        plt.ylabel("phase")
        plt.grid(True)

    if "x_zone_error" in dbg:
        plt.figure()
        plt.title("Zone error (x outside pad) vs time")
        plt.plot(t, dbg["x_zone_error"], label="x_zone_error")
        plt.axhline(0.0, linestyle="--")
        plt.xlabel("time (s)")
        plt.ylabel("meters")
        plt.grid(True)


    # -------------------------------------------------------------------------
    # EXTRA PLOTS (you asked for ~3 more graphs)
    # -------------------------------------------------------------------------

    # 6) Desired vs actual velocities (helps you see oscillations / tracking)
    if ("vx_des" in dbg) and ("vy_des" in dbg):
        plt.figure()
        plt.title("Desired vs actual velocities")
        plt.plot(t, X[:, 2], label="vx (actual)")
        plt.plot(t, dbg["vx_des"], label="vx_des (autopilot)")
        plt.plot(t, X[:, 3], label="vy (actual)")
        plt.plot(t, dbg["vy_des"], label="vy_des (autopilot)")
        plt.xlabel("time (s)")
        plt.ylabel("m/s")
        plt.grid(True)
        plt.legend()

    # 7) Thrust direction tracking: phi = theta + delta_act
    #    (If phi_ref exists in dbg, we plot it too)
    phi_actual = X[:, 4] + X[:, 8]
    if ("phi_ref" in dbg):
        plt.figure()
        plt.title("Thrust direction tracking (phi = theta + delta)")
        plt.plot(t, np.degrees(phi_actual), label="phi_actual (deg)")
        plt.plot(t, np.degrees(dbg["phi_ref"]), label="phi_ref (deg)")
        plt.plot(t, np.degrees(X[:, 4]), label="theta (deg)")
        plt.xlabel("time (s)")
        plt.ylabel("degrees")
        plt.grid(True)
        plt.legend()

    # 8) Adaptive quantities (what the adaptive part is doing)
    #
    # In adaptive_backstepping mode:
    #   d_hat_x, d_hat_y integrate velocity errors -> act like disturbance estimates.
    #
    # In MIT mode:
    #   k_thrust_hat is adapted to better match commanded vs measured vertical accel.
    #
    if ("d_hat_x" in dbg) or ("d_hat_y" in dbg) or ("k_thrust_hat" in dbg):
        plt.figure()
        plt.title("Adaptive estimates (disturbance integrator / MIT gain)")
        if "d_hat_x" in dbg:
            plt.plot(t, dbg["d_hat_x"], label="d_hat_x")
        if "d_hat_y" in dbg:
            plt.plot(t, dbg["d_hat_y"], label="d_hat_y")
        if "k_thrust_hat" in dbg:
            plt.plot(t, dbg["k_thrust_hat"], label="k_thrust_hat (MIT)")
        plt.xlabel("time (s)")
        plt.grid(True)
        plt.legend()

    # Optional: show MIT internal signals if present
    if ("ay_cmd" in dbg) and ("ay_meas" in dbg):
        plt.figure()
        plt.title("Vertical acceleration: commanded vs measured (MIT helper plot)")
        plt.plot(t, dbg["ay_cmd"], label="ay_cmd")
        plt.plot(t, dbg["ay_meas"], label="ay_meas (finite diff)")
        plt.xlabel("time (s)")
        plt.ylabel("m/s^2")
        plt.grid(True)
        plt.legend()

    plt.show()


# =============================================================================
# LIVE GUI (autopilot + controls)
# =============================================================================

class RocketAutopilotGUI:
    """
    Tkinter GUI:
      - live animation
      - Start / Stop / Restart / End
      - noise sliders
      - metrics panel (like your screenshot)
      - landing zone markers
      - crash / landed messages

    After you press End:
      - the GUI saves a log to disk
      - the GUI closes
      - the plots automatically open

    This is exactly the workflow you asked for.
    """

    def __init__(self):
        # ---------------------------------------------------------------------
        # Window and styling
        # ---------------------------------------------------------------------
        self.root = tk.Tk()
        self.root.title("2D Rocket Landing (SAFE Autopilot: Brake Immediately)")

        # If you click the window X button, treat it like pressing End.
        # This guarantees the log is saved AND the plots appear.
        self.root.protocol("WM_DELETE_WINDOW", self.end)
        self.root.geometry("1250x800")
        self.root.configure(bg="#ECECF7")

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("TFrame", background="#ECECF7")
        self.style.configure("TLabelframe", background="#ECECF7")
        self.style.configure("TLabelframe.Label", background="#ECECF7", font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabel", background="#ECECF7", font=("Segoe UI", 10))
        self.style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=8)

        # ---------------------------------------------------------------------
        # Physics params + simulator config
        # ---------------------------------------------------------------------
        self.params = RocketParams(
            thrust_mode="hover_normalized",
            thrust_to_weight=2.0,
            use_aero_drag=True,
            use_mass_depletion=True,
            wind_x=0.0,
            wind_y=0.0,
        )

        self.config = SimConfig(
            dt=0.02,
            t_max=60.0,
            landing_zone_width=10.0,
            noise_mu=0.0,
            noise_sigma=0.0,
            input_u_mu=0.0,
            input_u_sigma=0.0,
            input_delta_mu=0.0,
            input_delta_sigma=0.0,
            seed=None,
        )

        self.sim = RocketSimulator(self.params, self.config)

        # ---------------------------------------------------------------------
        # Initial condition (matches your screenshots)
        # ---------------------------------------------------------------------
        px0 = -95.0
        py0 = 160.0
        vx0 = 16.0
        vy0 = -32.0
        theta0 = deg2rad(5.0)
        omega0 = deg2rad(2.0)
        m0 = 1000.0
        u_act0 = 0.0
        delta_act0 = 0.0

        self.x0 = (px0, py0, vx0, vy0, theta0, omega0, m0, u_act0, delta_act0)
        self.sim.reset(self.x0)

        # ---------------------------------------------------------------------
        # Autopilot (you can choose the adaptation method)
        # ---------------------------------------------------------------------
        #
        # You asked for a selection between:
        #   1) Adaptive backstepping-style (the default method in this project)
        #   2) MIT rule adaptation
        #
        # We implement BOTH using the SAME safe flight-phase logic, so you can
        # compare them fairly.
        #
        # The GUI dropdown will call _on_autopilot_mode_change(), which recreates
        # the autopilot object with the chosen mode.
        self.autopilot_mode = tk.StringVar(value="Adaptive Backstepping")
        self.autopilot = SafeBrakeImmediatelyAutopilot(self.params, self.config, mode="adaptive_backstepping")
        self.autopilot.reset()

        # Debug dictionary for plotting
        self.last_dbg: Dict[str, float] = {}

        # Running flag
        self.running = False

        # Log buffers (filled while running)
        self._log_t: List[float] = []
        self._log_X: List[List[float]] = []
        self._log_Ucmd: List[List[float]] = []
        self._log_Uapplied: List[List[float]] = []
        self._log_dbg: Dict[str, List[float]] = {}

        # When End is pressed, we store the path here
        self._saved_log_path: Optional[str] = None

        # ---------------------------------------------------------------------
        # Layout: top info panel, then canvas + control panel
        # ---------------------------------------------------------------------
        info_outer = ttk.Frame(self.root, padding=10)
        info_outer.pack(side=tk.TOP, fill=tk.X)

        info_bg = tk.Frame(info_outer, bg="#F7F7FF", bd=1, relief="solid")
        info_bg.pack(side=tk.TOP, fill=tk.X)

        self.info_var = tk.StringVar(value="")
        self.info_label = tk.Label(
            info_bg,
            textvariable=self.info_var,
            justify=tk.LEFT,
            anchor="nw",
            bg="#F7F7FF",
            fg="#1F1F2E",
            font=("Consolas", 11),
            padx=12,
            pady=8,
        )
        self.info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        main = ttk.Frame(self.root, padding=10)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Canvas
        self.canvas = tk.Canvas(main, bg="#EEF1FF", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Control panel
        ctrl = ttk.Frame(main, padding=10)
        ctrl.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------------------------------------------------------------------
        # Controls: Start/Stop/Restart/End
        # ---------------------------------------------------------------------
        buttons = ttk.Labelframe(ctrl, text="Simulation Controls", padding=10)
        buttons.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(buttons)
        btn_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(btn_frame, text="Start", style="Big.TButton", command=self.start)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", style="Big.TButton", command=self.stop)
        self.restart_btn = ttk.Button(btn_frame, text="Restart", style="Big.TButton", command=self.restart)
        self.end_btn = ttk.Button(btn_frame, text="End", style="Big.TButton", command=self.end)

        self.start_btn.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.stop_btn.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.restart_btn.grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        self.end_btn.grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # ---------------------------------------------------------------------
        # Autopilot label (always on)
        # ---------------------------------------------------------------------
        ap_box = ttk.Labelframe(ctrl, text="Autopilot", padding=10)
        ap_box.pack(fill=tk.X, pady=(0, 10))

        # Mode selection row
        ttk.Label(ap_box, text="Mode:").pack(anchor="w")

        # A readonly dropdown so you can switch between adaptation strategies
        # without editing the code.
        self.mode_combo = ttk.Combobox(
            ap_box,
            textvariable=self.autopilot_mode,
            state="readonly",
            values=[
                "Adaptive Backstepping",   # the default method we used so far
                "MIT Rule",                # alternative adaptation (single-parameter MIT)
            ],
            width=28,
        )
        self.mode_combo.pack(anchor="w", fill=tk.X, pady=(4, 6))
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_autopilot_mode_change)

        # A small readout label (kept separate from the dropdown)
        self.autopilot_readout_var = tk.StringVar(value=self._autopilot_readout_text())
        self.autopilot_readout = ttk.Label(ap_box, textvariable=self.autopilot_readout_var)
        self.autopilot_readout.pack(anchor="w")

        self.applied_label = ttk.Label(ap_box, text="Applied: u=0.00, delta=0.00 deg")
        self.applied_label.pack(anchor="w", pady=(6, 0))

        # ---------------------------------------------------------------------
        # Noise controls
        # ---------------------------------------------------------------------
        noise_box = ttk.Labelframe(ctrl, text="Noise", padding=10)
        noise_box.pack(fill=tk.X, pady=(0, 10))

        self.proc_sigma = tk.DoubleVar(value=0.0)
        ttk.Label(noise_box, text="Process noise sigma (vx, vy, omega)").pack(anchor="w")
        proc_slider = ttk.Scale(noise_box, from_=0.0, to=2.0, variable=self.proc_sigma, command=self._on_noise_change)
        proc_slider.pack(fill=tk.X)

        self.u_sigma = tk.DoubleVar(value=0.0)
        ttk.Label(noise_box, text="Input noise sigma (throttle)").pack(anchor="w", pady=(8, 0))
        u_slider = ttk.Scale(noise_box, from_=0.0, to=0.2, variable=self.u_sigma, command=self._on_noise_change)
        u_slider.pack(fill=tk.X)

        self.d_sigma_deg = tk.DoubleVar(value=0.0)
        ttk.Label(noise_box, text="Input noise sigma (gimbal, deg)").pack(anchor="w", pady=(8, 0))
        d_slider = ttk.Scale(noise_box, from_=0.0, to=5.0, variable=self.d_sigma_deg, command=self._on_noise_change)
        d_slider.pack(fill=tk.X)

        # ---------------------------------------------------------------------
        # Simulation speed controls
        # ---------------------------------------------------------------------
        speed_box = ttk.Labelframe(ctrl, text="Simulation Speed", padding=10)
        speed_box.pack(fill=tk.X, pady=(0, 10))

        self.steps_per_frame = tk.IntVar(value=3)
        ttk.Label(speed_box, text="Steps per frame (higher = faster sim)").pack(anchor="w")
        spf_slider = ttk.Scale(speed_box, from_=1, to=15, value=3, command=self._on_speed_change)
        spf_slider.pack(fill=tk.X)

        self.dt_var = tk.DoubleVar(value=self.config.dt)
        ttk.Label(speed_box, text="dt (seconds)").pack(anchor="w", pady=(8, 0))
        dt_slider = ttk.Scale(speed_box, from_=0.005, to=0.05, variable=self.dt_var, command=self._on_dt_change)
        dt_slider.pack(fill=tk.X)

        # ---------------------------------------------------------------------
        # Canvas mapping / ground
        # ---------------------------------------------------------------------
        self.canvas_w = 1
        self.canvas_h = 1

        # A wider view so the rocket does not "vanish" off-screen.
        self.xmin, self.xmax = -220.0, 220.0
        self.ymin, self.ymax = -10.0, 240.0

        self.scale = 1.0
        self.ground_margin_px = 10
        self.ground_y_canvas = 0.0
        self.x0_canvas = 0.0

        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Start the periodic loop
        self.root.after(20, self._loop)

        # Draw the initial scene
        self._draw_static_ground()
        self._update_info_text()
        self._redraw()

    # -------------------------------------------------------------------------
    # Button callbacks
    # -------------------------------------------------------------------------

    def start(self):
        """Start/resume simulation."""
        if self.sim.status in [STATUS_CRASHED, STATUS_LANDED, STATUS_MISSED, STATUS_TIMEOUT]:
            # If simulation already finished, treat Start like Restart+Start.
            self.restart()

        self.sim.status = STATUS_RUNNING
        self.running = True

    def stop(self):
        """Pause simulation."""
        self.running = False
        if self.sim.status == STATUS_RUNNING:
            self.sim.status = STATUS_PAUSED

    def restart(self):
        """Reset simulation + controller + logs."""
        self.running = False
        self.sim.reset(self.x0)
        self.autopilot = self._make_autopilot_from_mode()
        self.autopilot.reset()
        if hasattr(self, "autopilot_readout_var"):
            self.autopilot_readout_var.set(self._autopilot_readout_text())
        self.last_dbg = {}

        # Clear logs
        self._log_t.clear()
        self._log_X.clear()
        self._log_Ucmd.clear()
        self._log_Uapplied.clear()
        self._log_dbg.clear()

        self._saved_log_path = None

        self._update_info_text()
        self._redraw()

    def end(self):
        """
        End the simulation:
          1) Save a log file (npz)
          2) Close the GUI

        The plots are shown AFTER mainloop returns (see run()).
        """
        self.running = False

        # Save log (if we have at least a few samples)
        if len(self._log_t) > 5:
            self._saved_log_path = self._save_log_to_disk()

        # Close GUI
        self.root.quit()

    # -------------------------------------------------------------------------
    # Slider callbacks
    # -------------------------------------------------------------------------

    def _on_noise_change(self, _evt=None):
        """Update simulator noise from sliders."""
        proc_sig = float(self.proc_sigma.get())
        self.sim.set_process_noise(0.0, proc_sig)

        u_sig = float(self.u_sigma.get())
        d_sig = deg2rad(float(self.d_sigma_deg.get()))
        self.sim.set_input_noise(0.0, u_sig, 0.0, d_sig)

    def _on_dt_change(self, _evt=None):
        """Update dt from slider."""
        self.config.dt = float(self.dt_var.get())

    def _on_speed_change(self, val):
        """Update steps-per-frame from slider."""
        self.steps_per_frame.set(max(1, int(round(float(val)))))


    # -------------------------------------------------------------------------
    # Autopilot mode switching
    # -------------------------------------------------------------------------

    def _autopilot_readout_text(self) -> str:
        """Small helper: build a human-readable autopilot status string."""
        mode = self.autopilot_mode.get()
        if mode == "MIT Rule":
            return "SAFE Autopilot: ON  |  Mode: MIT Rule (thrust gain adaptation)"
        return "SAFE Autopilot: ON  |  Mode: Adaptive Backstepping (disturbance estimate)"

    def _make_autopilot_from_mode(self) -> SafeBrakeImmediatelyAutopilot:
        """
        Factory: create an autopilot instance matching the GUI dropdown.

        We recreate the object (instead of toggling flags) so that:
          - all internal adaptation states reset cleanly
          - the logs clearly show which method was active
        """
        mode_str = self.autopilot_mode.get()
        if mode_str == "MIT Rule":
            return SafeBrakeImmediatelyAutopilot(self.params, self.config, mode="mit")
        return SafeBrakeImmediatelyAutopilot(self.params, self.config, mode="adaptive_backstepping")

    def _on_autopilot_mode_change(self, event=None):
        """GUI callback when you change the dropdown."""
        # Stop the sim (safer), recreate the autopilot, then update labels.
        self.running = False
        self.autopilot = self._make_autopilot_from_mode()
        self.autopilot.reset()

        if hasattr(self, "autopilot_readout_var"):
            self.autopilot_readout_var.set(self._autopilot_readout_text())

    # -------------------------------------------------------------------------
    # Canvas mapping
    # -------------------------------------------------------------------------

    def _on_canvas_resize(self, event):
        """Recompute mapping when canvas is resized."""
        self.canvas_w = max(1, int(event.width))
        self.canvas_h = max(1, int(event.height))

        sx = self.canvas_w / (self.xmax - self.xmin)
        sy = self.canvas_h / (self.ymax - self.ymin)
        self.scale = min(sx, sy)

        self.ground_y_canvas = self.canvas_h - self.ground_margin_px
        self.x0_canvas = self.canvas_w * 0.5

        self._draw_static_ground()

    def world_to_canvas(self, x_m: float, y_m: float) -> Tuple[float, float]:
        """World meters -> canvas pixels."""
        cx = self.x0_canvas + (x_m * self.scale)
        cy = self.ground_y_canvas - (y_m * self.scale)
        return cx, cy

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------

    def _loop(self):
        """Tkinter periodic loop."""
        if self.running and self.sim.status == STATUS_RUNNING:
            for _ in range(self.steps_per_frame.get()):
                u_cmd, delta_cmd, dbg = self.autopilot.compute_control(
                    t=self.sim.t,
                    x=self.sim.x,
                    dt=self.config.dt,
                    target_xy=(0.0, 0.0),
                )
                self.last_dbg = dbg

                self.sim.step(u_cmd, delta_cmd)

                # Log one sample per integration step
                self._append_log_sample(u_cmd, delta_cmd, dbg)

                # Auto-stop if finished
                if self.sim.status != STATUS_RUNNING:
                    self.running = False
                    break

        # Update applied input readout
        self.applied_label.config(
            text=(
                f"Applied (after input-noise): u={self.sim.last_u_applied:.2f}, "
                f"delta={rad2deg(self.sim.last_delta_applied):.2f} deg"
            )
        )

        self._update_info_text()
        self._redraw()

        self.root.after(20, self._loop)

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------

    def _append_log_sample(self, u_cmd: float, delta_cmd: float, dbg: Dict[str, float]) -> None:
        """Append one sample to the in-memory log."""
        self._log_t.append(float(self.sim.t))
        self._log_X.append(list(self.sim.x))
        self._log_Ucmd.append([float(u_cmd), float(delta_cmd)])
        self._log_Uapplied.append([float(self.sim.last_u_applied), float(self.sim.last_delta_applied)])

        # Store debug signals into separate arrays (same length as time)
        for k, v in dbg.items():
            if k not in self._log_dbg:
                self._log_dbg[k] = []
            self._log_dbg[k].append(float(v))

        # Ensure any missing debug keys still align in length (fill with NaN)
        for k in self._log_dbg.keys():
            if len(self._log_dbg[k]) < len(self._log_t):
                self._log_dbg[k].append(float("nan"))

    def _save_log_to_disk(self) -> str:
        """Save an .npz log file into the same folder as these scripts."""
        # Save in the script directory so you can always find it.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"rocket_log_{ts}.npz"
        path = os.path.join(script_dir, filename)

        t = np.asarray(self._log_t, dtype=float)
        X = np.asarray(self._log_X, dtype=float)
        U_cmd = np.asarray(self._log_Ucmd, dtype=float)
        U_applied = np.asarray(self._log_Uapplied, dtype=float)

        # Debug dict saved as object
        np.savez(
            path,
            t=t,
            X=X,
            U_cmd=U_cmd,
            U_applied=U_applied,
            dbg=self._log_dbg,
            final_status=str(self.sim.status),
            landing_zone_width=float(self.config.landing_zone_width),
        )
        return path

    # -------------------------------------------------------------------------
    # Info panel (your screenshot style)
    # -------------------------------------------------------------------------

    def _update_info_text(self) -> None:
        px, py, vx, vy, theta, omega, m, u_act, delta_act = self.sim.x
        theta_deg = rad2deg(theta)
        omega_deg_s = rad2deg(omega)

        text = (
            f"/* Horizontal position */ rocket.x      = {px:8.2f}\n"
            f"/* Horizontal velocity */ rocket.dx     = {vx:8.2f}\n"
            f"/* Vertical position   */ rocket.y      = {py:8.2f}\n"
            f"/* Vertical velocity   */ rocket.dy     = {vy:8.2f}\n"
            f"/* Angle from vertical */ rocket.theta  = {theta_deg:8.2f}\n"
            f"/* Angular velocity    */ rocket.dtheta = {omega_deg_s:8.2f}\n"
            f"/* Simulation time     */ rocket.T      = {self.sim.t:8.2f}\n"
            f"/* Status */              status        = {self.sim.status}\n"
        )
        self.info_var.set(text)

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------

    def _draw_static_ground(self) -> None:
        """Draw sky background, ground line, pad ticks, and landing zone edges."""
        self.canvas.delete("bg")
        self.canvas.delete("ground")

        # Sky
        self.canvas.create_rectangle(0, 0, self.canvas_w, self.canvas_h, fill="#EEF1FF", outline="", tags="bg")
        self.canvas.create_rectangle(0, 0, self.canvas_w, int(self.canvas_h * 0.35), fill="#F7F8FF", outline="", tags="bg")

        # Ground line
        self.canvas.create_line(0, self.ground_y_canvas, self.canvas_w, self.ground_y_canvas, width=4, fill="#1E2A78", tags="ground")

        # Landing zone edges
        half = 0.5 * self.config.landing_zone_width
        xL, _ = self.world_to_canvas(-half, 0.0)
        xR, _ = self.world_to_canvas(+half, 0.0)
        self.canvas.create_line(xL, self.ground_y_canvas, xL, self.ground_y_canvas - 40, width=4, fill="#CC0000", tags="ground")
        self.canvas.create_line(xR, self.ground_y_canvas, xR, self.ground_y_canvas - 40, width=4, fill="#CC0000", tags="ground")

        # Small ticks around pad center
        center_x, _ = self.world_to_canvas(0.0, 0.0)
        for i in range(-10, 11):
            x = center_x + i * 6
            self.canvas.create_line(x, self.ground_y_canvas, x, self.ground_y_canvas - 10, width=2, fill="#1E2A78", tags="ground")

    def _rocket_polygon_world(self) -> List[Tuple[float, float]]:
        """Rocket outline in world coordinates."""
        px, py, vx, vy, theta, omega, m, u_act, delta_act = self.sim.x

        H = 14.0
        W = 3.2

        local = [
            (0.0, +H / 2),
            (+W / 2, +H * 0.25),
            (+W / 2, -H * 0.35),
            (+W * 0.75, -H / 2),
            (0.0, -H * 0.42),
            (-W * 0.75, -H / 2),
            (-W / 2, -H * 0.35),
            (-W / 2, +H * 0.25),
        ]

        dir_x = math.sin(theta)
        dir_y = math.cos(theta)
        perp_x = math.cos(theta)
        perp_y = -math.sin(theta)

        world_pts = []
        for bx, by in local:
            wx = px + bx * perp_x + by * dir_x
            wy = py + bx * perp_y + by * dir_y
            world_pts.append((wx, wy))

        return world_pts

    def _thrust_line_world(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Small red line indicating thrust direction."""
        px, py, vx, vy, theta, omega, m, u_act, delta_act = self.sim.x

        phi = theta + delta_act
        ux = math.sin(phi)
        uy = math.cos(phi)

        # Start near the rocket base
        base_x = px
        base_y = py

        # Line length scaled by current throttle state
        length = 18.0 * (0.2 + 0.8 * clamp(u_act, 0.0, 1.0))

        p1 = (base_x, base_y)
        p2 = (base_x - length * ux, base_y - length * uy)
        return p1, p2

    def _redraw(self) -> None:
        """Redraw rocket + overlays."""
        self.canvas.delete("rocket")
        self.canvas.delete("overlay")

        # Rocket body
        poly = self._rocket_polygon_world()
        pts = []
        for wx, wy in poly:
            cx, cy = self.world_to_canvas(wx, wy)
            pts.extend([cx, cy])

        self.canvas.create_polygon(pts, outline="#1E2A78", fill="", width=3, tags="rocket")

        # Thrust line
        (x1, y1), (x2, y2) = self._thrust_line_world()
        c1 = self.world_to_canvas(x1, y1)
        c2 = self.world_to_canvas(x2, y2)
        self.canvas.create_line(c1[0], c1[1], c2[0], c2[1], width=4, fill="#D31B1B", tags="rocket")

        # Overlays for status
        if self.sim.status == STATUS_CRASHED:
            self.canvas.create_text(self.canvas_w * 0.45, self.canvas_h * 0.45, text="CRASHED!", fill="#CC0000", font=("Segoe UI", 42, "bold"), tags="overlay")
        elif self.sim.status == STATUS_LANDED:
            self.canvas.create_text(self.canvas_w * 0.45, self.canvas_h * 0.45, text="LANDED!", fill="#0A7A0A", font=("Segoe UI", 42, "bold"), tags="overlay")
        elif self.sim.status == STATUS_MISSED:
            self.canvas.create_text(self.canvas_w * 0.45, self.canvas_h * 0.45, text="MISSED PAD!", fill="#CC7A00", font=("Segoe UI", 42, "bold"), tags="overlay")
        elif self.sim.status == STATUS_TIMEOUT:
            self.canvas.create_text(self.canvas_w * 0.45, self.canvas_h * 0.45, text="TIMEOUT!", fill="#444444", font=("Segoe UI", 42, "bold"), tags="overlay")

    # -------------------------------------------------------------------------
    # Run
    # -------------------------------------------------------------------------

    def run(self) -> Optional[str]:
        """
        Run the GUI mainloop.

        Returns:
          saved_log_path (or None if no log was saved).

        IMPORTANT:
          We plot AFTER the GUI closes, not inside the GUI.
        """
        try:
            self.root.mainloop()
        finally:
            # Always destroy the window cleanly
            try:
                self.root.destroy()
            except tk.TclError:
                pass

        return self._saved_log_path


# =============================================================================
# Public entry point used by rocket_main.py
# =============================================================================

def run_everything() -> None:
    """
    Run the full experience you asked for:

      1) Open the live GUI
      2) You press Start/Stop/Restart
      3) You press End
      4) A log is saved
      5) The plots pop up automatically

    This is the only function rocket_main.py needs to call.
    """

    app = RocketAutopilotGUI()
    log_path = app.run()

    if log_path is not None:
        print(f"Log saved to: {log_path}")
        plot_log(log_path)
    else:
        print("No log saved (simulation may not have been started).")
