import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ===============================================================
#  Double pendulum model
#  -------------------------------------------------------------
#  This file provides:
#    - dynamics(x, u)     : continuous-time dynamics  x_dot = f(x, u)
#    - rk4_step(...)      : one Runge-Kutta 4 integration step
#    - simulate(...)      : simulate for some time with chosen control
#    - simple PD control  : stabilizes the pendulum around q_ref
#    - convergence tests  : compare different dt values
#    - animate_double_pendulum(...) : live animation of the motion
#
#  State:
#      x = [q1, q2, q1_dot, q2_dot]^T
#  Input (torques):
#      u = [u1, u2]^T
#
# ===============================================================

# -----------------------------
# Physical / model parameters
# -----------------------------
g  = 9.81   # gravity acceleration [m/s^2]
m1 = 1.0    # mass of first link's point mass [kg]
m2 = 1.0    # mass of second link's point mass [kg]
l1 = 0.5    # length / COM distance of first link [m]
l2 = 0.5    # length / COM distance of second link [m]


def dynamics(x, u):
    """
    Continuous-time dynamics of the double pendulum.

    Parameters
    ----------
    x : array_like, shape (4,)
        State vector [q1, q2, q1_dot, q2_dot].
    u : array_like, shape (2,)
        Input (torques) [u1, u2].

    Returns
    -------
    x_dot : ndarray, shape (4,)
        Time derivative of the state: [q1_dot, q2_dot, q1_ddot, q2_ddot].
    """
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)

    # Unpack state and input
    q1, q2, q1_dot, q2_dot = x
    u1, u2 = u

    q     = np.array([q1, q2])
    q_dot = np.array([q1_dot, q2_dot])

    # ----- Mass / inertia matrix M(q) -----
    # M is a 2x2 matrix that depends on the configuration (angles).
    # M = [[l1^2*m1 + l2^2*m2 + l1^2*m2 + 2*l1*l2*m2*cos(q2),   l2^2*m2 + l1*l2*m2*cos(q2)],
    #      [l2^2*m2 + l1*l2*m2*cos(q2),                        l2^2*m2                   ]]

    M11 = l1**2 * m1 + l1**2 * m2 + l2**2 * m2 + 2.0 * l1 * l2 * m2 * np.cos(q2)
    M12 = l2**2 * m2 + l1 * l2 * m2 * np.cos(q2)
    M21 = M12
    M22 = l2**2 * m2
    M = np.array([[M11, M12],
                  [M21, M22]])

    # ----- Coriolis / centrifugal matrix C(q, q_dot) -----
    # This matrix multiplies q_dot in the dynamics.
    #
    # C = [[-2*q2_dot*l1*l2*m2*sin(q2),   -q2_dot*l1*l2*m2*sin(q2)],
    #      [ q1_dot*l1*l2*m2*sin(q2),     0                       ]]

    C11 = -2.0 * q2_dot * l1 * l2 * m2 * np.sin(q2)
    C12 = -1.0 * q2_dot * l1 * l2 * m2 * np.sin(q2)
    C21 =  1.0 * q1_dot * l1 * l2 * m2 * np.sin(q2)
    C22 =  0.0
    C = np.array([[C11, C12],
                  [C21, C22]])

    # ----- Gravity vector G(q) -----
    # G = [ -g*m1*l1*sin(q1) - g*m2*(l1*sin(q1) + l2*sin(q1+q2)),
    #       -g*m2*l2*sin(q1 + q2)                                ]

    G1 = -g * m1 * l1 * np.sin(q1) - g * m2 * (l1 * np.sin(q1) + l2 * np.sin(q1 + q2))
    G2 = -g * m2 * l2 * np.sin(q1 + q2)
    G = np.array([G1, G2])

    # ----- Solve for q_ddot -----
    # From the homework:
    #   q_ddot = M^{-1} * ( u - C(q,q_dot) * q_dot + G(q) )
    #
    # Instead of computing M^{-1} explicitly, we solve
    #   M * q_ddot = u - C q_dot + G
    # which is numerically better.

    tau = np.array([u1, u2])
    rhs = tau - C @ q_dot + G         # right-hand side
    q_ddot = np.linalg.solve(M, rhs)  # M * q_ddot = rhs

    # ----- Assemble x_dot -----
    # x = [q1, q2, q1_dot, q2_dot]
    # so the derivatives are:
    #   d/dt q1      = q1_dot
    #   d/dt q2      = q2_dot
    #   d/dt q1_dot  = q1_ddot
    #   d/dt q2_dot  = q2_ddot

    x_dot = np.array([q1_dot,
                      q2_dot,
                      q_ddot[0],
                      q_ddot[1]])

    return x_dot


def rk4_step(x, u, dt):
    """
    One Runge-Kutta 4th-order (RK4) integration step.

    x_next ≈ x(t + dt) given x(t) and constant input u in [t, t+dt].

    Parameters
    ----------
    x : array_like, shape (4,)
        Current state.
    u : array_like, shape (2,)
        Constant input during this step.
    dt : float
        Time step [s].

    Returns
    -------
    x_next : ndarray, shape (4,)
        Approximation of the state at t + dt.
    """
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)

    # Standard RK4 scheme:
    # k1 = f(x, u)
    # k2 = f(x + dt/2 * k1, u)
    # k3 = f(x + dt/2 * k2, u)
    # k4 = f(x + dt   * k3, u)
    # x_next = x + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

    k1 = dynamics(x,               u)
    k2 = dynamics(x + 0.5*dt*k1,   u)
    k3 = dynamics(x + 0.5*dt*k2,   u)
    k4 = dynamics(x + dt*k3,       u)

    x_next = x + (dt/6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
    return x_next


def simulate(x0, T, dt, control_fn):
    """
    Simulate the system forward in time using RK4 and a control law.

    Parameters
    ----------
    x0 : array_like, shape (4,)
        Initial state at t = 0.
    T : float
        Total simulation time [s].
    dt : float
        Time step [s].
    control_fn : callable
        control_fn(t, x) -> u (size 2).

    Returns
    -------
    t_grid : ndarray, shape (N+1,)
        Time instants from 0 to T.
    x_traj : ndarray, shape (N+1, 4)
        State trajectory.
    """
    x0 = np.asarray(x0, dtype=float)
    N = int(np.round(T / dt))
    t_grid = np.linspace(0.0, N*dt, N+1)
    x_traj = np.zeros((N+1, 4))
    x_traj[0] = x0
    x = x0.copy()

    for k in range(N):
        t = t_grid[k]
        u = control_fn(t, x)
        x = rk4_step(x, u, dt)

        # ------------- SAFETY CHECK -------------
        # If the state norm becomes ridiculously large, it usually
        # means numerical divergence (e.g., too large dt, bad gains).
        # We stop the simulation early and fill the rest with NaNs,
        # instead of letting it overflow and produce inf/nan warnings.
        if np.linalg.norm(x) > 1e3:
            print(f"WARNING: state blew up at t={t:.3f} s, dt={dt}")
            x_traj[k+1:] = np.nan
            break

        x_traj[k+1] = x

    return t_grid, x_traj


# ===============================================================
#  Simple PD controller
# ===============================================================

def make_pd_controller(q_ref, Kp, Kd):
    """
    Create a PD control law u = Kp*(q_ref - q) + Kd*(0 - q_dot).

    Parameters
    ----------
    q_ref : array_like, shape (2,)
        Desired joint angles [q1_ref, q2_ref].
    Kp : array_like, shape (2,) or (2,2)
        Proportional gains (diagonal or full matrix).
    Kd : array_like, shape (2,) or (2,2)
        Derivative gains.

    Returns
    -------
    control_fn : callable
        Function(t, x) -> u that can be passed to simulate().
    """
    q_ref = np.asarray(q_ref, dtype=float)
    Kp = np.asarray(Kp, dtype=float)
    Kd = np.asarray(Kd, dtype=float)

    def control_fn(t, x):
        q     = x[:2]        # [q1, q2]
        q_dot = x[2:]        # [q1_dot, q2_dot]

        # Position error and velocity error
        e_q   = q_ref - q
        e_dq  = -q_dot       # want q_dot -> 0

        # If Kp, Kd are given as vectors, treat them as diagonal matrices.
        if Kp.ndim == 1:
            u_p = Kp * e_q
        else:
            u_p = Kp @ e_q

        if Kd.ndim == 1:
            u_d = Kd * e_dq
        else:
            u_d = Kd @ e_dq

        u = u_p + u_d

        # *** TORQUE SATURATION ***
        # To avoid huge torques that can make the integration blow up,
        # we clip the control input to a reasonable range.
        u_max = 50.0  # [N·m]   <-- you can tune this if needed
        u = np.clip(u, -u_max, u_max)

        return u

    return control_fn


def zero_control(t, x):
    """Zero torque control (used sometimes for checks)."""
    return np.zeros(2)


# ===============================================================
#  Energy (for optional checks)
# ===============================================================

def total_energy(x):
    """
    Compute total mechanical energy (kinetic + potential).

    Useful to check that with zero control and reasonably small dt
    the energy is nearly conserved (no damping in the model).
    """
    q1, q2, q1_dot, q2_dot = x
    q     = np.array([q1, q2])
    q_dot = np.array([q1_dot, q2_dot])

    # Rebuild mass matrix (same as in dynamics)
    M11 = l1**2 * m1 + l1**2 * m2 + l2**2 * m2 + 2.0 * l1 * l2 * m2 * np.cos(q2)
    M12 = l2**2 * m2 + l1 * l2 * m2 * np.cos(q2)
    M21 = M12
    M22 = l2**2 * m2
    M = np.array([[M11, M12],
                  [M21, M22]])

    kinetic = 0.5 * q_dot @ (M @ q_dot)

    # Positions of masses (same as in animation)
    x1 = l1 * np.sin(q1)
    y1 = -l1 * np.cos(q1)
    theta2 = q1 + q2
    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 - l2 * np.cos(theta2)

    potential = m1 * g * y1 + m2 * g * y2

    return kinetic + potential


# ===============================================================
#  Convergence / integration-quality tests
# ===============================================================

def convergence_experiment(x0, T, dt_list, control_fn, q_ref):
    """
    Run simulations with different dt values and compare:

      - tracking error vs time
      - RMS tracking error vs dt
      - max state error vs dt (vs a fine reference)

    Parameters
    ----------
    x0 : array_like, (4,)
    T : float
    dt_list : list of float
        Time steps to test (e.g. [0.05, 0.02, 0.01, 0.005]).
    control_fn : callable
        PD control law (or any control).
    q_ref : array_like, (2,)
        Desired joint angles (for tracking error).

    Returns
    -------
    results : dict
        Contains per-dt trajectories and error metrics.
    """
    q_ref = np.asarray(q_ref)

    # Sort dt's from largest to smallest (just for nicer plotting)
    dt_list = sorted(dt_list, reverse=True)

    # Use a very small dt as "reference" solution
    # This is our "reference trajectory" x_ref(t) that approximates
    # the true continuous-time solution.
    dt_ref = min(dt_list) / 2.0
    t_ref, x_ref = simulate(x0, T, dt_ref, control_fn)

    results = {
        "dt_list": dt_list,
        "dt_ref": dt_ref,
        "t_ref": t_ref,
        "x_ref": x_ref,
        "per_dt": []  # list of dicts with info for each dt
    }

    for dt in dt_list:
        t, x = simulate(x0, T, dt, control_fn)

        # Indices to sample reference trajectory at coarse time grid.
        # Because dt is (approximately) a multiple of dt_ref, t / dt_ref
        # is (almost) integer, so we round to nearest index.
        idx = np.round(t / dt_ref).astype(int)
        idx = np.clip(idx, 0, len(t_ref)-1)   # safety clipping
        x_ref_samp = x_ref[idx]

        # State difference vs reference trajectory
        diff_state = x - x_ref_samp
        max_state_err = np.max(np.abs(diff_state))

        # Tracking error for angles only (q1, q2)
        q      = x[:, :2]
        e_q    = q - q_ref  # (N+1, 2)
        e_norm = np.linalg.norm(e_q, axis=1)  # ||error|| at each time
        rms_tracking = np.sqrt(np.mean(e_norm**2))

        results["per_dt"].append({
            "dt": dt,
            "t": t,
            "x": x,
            "e_norm": e_norm,
            "rms_tracking": rms_tracking,
            "max_state_err_vs_ref": max_state_err
        })

    return results


# ===============================================================
#  Animation
# ===============================================================

def animate_double_pendulum(t_grid, x_traj, dt):
    """
    Live animation of the double pendulum motion.
    """
    q1 = x_traj[:, 0]
    q2 = x_traj[:, 1]

    # Base position
    x0, y0 = 0.0, 0.0

    # First link tip
    x1 = l1 * np.sin(q1)
    y1 = -l1 * np.cos(q1)

    # Second link tip
    theta2 = q1 + q2
    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 - l2 * np.cos(theta2)

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    max_len = l1 + l2
    ax.set_xlim(-1.2 * max_len, 1.2 * max_len)
    ax.set_ylim(-1.2 * max_len, 0.6 * max_len)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Double Pendulum with PD Control")

    line, = ax.plot([], [], 'o-', lw=2)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    def init():
        line.set_data([], [])
        time_text.set_text('')
        return line, time_text

    def update(frame):
        this_x = [x0, x1[frame], x2[frame]]
        this_y = [y0, y1[frame], y2[frame]]
        line.set_data(this_x, this_y)
        time_text.set_text(f"t = {t_grid[frame]:.2f} s")
        return line, time_text

    anim = FuncAnimation(fig, update,
                         frames=len(t_grid),
                         init_func=init,
                         blit=True,
                         interval=dt * 1000)
    plt.show()
    return anim


# ===============================================================
#  Main demo
# ===============================================================
if __name__ == "__main__":
    # -----------------------------------------------------------
    # 1) Choose initial state (not exactly at equilibrium)
    # -----------------------------------------------------------
    x0 = np.array([
        0.6,   # q1 [rad]
        -0.3,  # q2 [rad]
        0.0,   # q1_dot
        0.0    # q2_dot
    ])

    # Desired configuration for PD controller:
    # bottom equilibrium  q1 = 0, q2 = 0  (both links straight down)
    q_ref = np.array([0.0, 0.0])

    # PD gains (diagonal)
    # These are softer now so that the pendulum swings more before settling.
    Kp = np.array([15.0, 10.0])   # proportional gains for joints 1, 2
    Kd = np.array([3.0,  2.0])    # derivative gains

    pd_control = make_pd_controller(q_ref, Kp, Kd)

    # -----------------------------------------------------------
    # 2) Quick equilibrium check at downward configuration
    # -----------------------------------------------------------
    x_eq = np.array([0.0, 0.0, 0.0, 0.0])
    f_eq = dynamics(x_eq, np.zeros(2))
    print("f(x_eq, 0) =", f_eq, " (should be ~0)")

    # -----------------------------------------------------------
    # 3) Simulate with a "good" dt and animate
    # -----------------------------------------------------------
    # Longer simulation time so we can see it swing and then settle.
    T_sim = 15.0
    dt_sim = 0.01

    t_grid, x_traj = simulate(x0, T_sim, dt_sim, pd_control)
    animate_double_pendulum(t_grid, x_traj, dt_sim)

    # -----------------------------------------------------------
    # 4) Convergence tests for different dt's
    # -----------------------------------------------------------
    # We keep a range of dt values, from coarse to fine.
    # With the softer PD gains and torque saturation, these
    # should not blow up and will show convergence.
    dt_list = [0.05, 0.02, 0.01, 0.005]

    results = convergence_experiment(x0, T=4.0,   # slightly shorter horizon
                                     dt_list=dt_list,
                                     control_fn=pd_control,
                                     q_ref=q_ref)

    # ---- Plot tracking error vs time for each dt ----
    plt.figure()
    for info in results["per_dt"]:
        dt = info["dt"]
        t  = info["t"]
        e_norm = info["e_norm"]
        plt.plot(t, e_norm, label=f"dt={dt}")
    plt.xlabel("t [s]")
    plt.ylabel("||q - q_ref|| [rad]")
    plt.title("Tracking error vs time for different dt")
    plt.grid(True)
    plt.legend()

    # ---- Plot RMS tracking error vs dt ----
    plt.figure()
    dts = []
    rms_vals = []
    max_errs = []
    for info in results["per_dt"]:
        dts.append(info["dt"])
        rms_vals.append(info["rms_tracking"])
        max_errs.append(info["max_state_err_vs_ref"])

    dts = np.array(dts)
    rms_vals = np.array(rms_vals)
    max_errs = np.array(max_errs)

    plt.loglog(dts, rms_vals, 'o-')
    plt.xlabel("dt [s]")
    plt.ylabel("RMS tracking error [rad]")
    plt.title("RMS tracking error vs dt (convergence)")
    plt.grid(True, which="both")

    # ---- Plot max state error vs dt compared to fine reference ----
    plt.figure()
    plt.loglog(dts, max_errs, 's-')
    plt.xlabel("dt [s]")
    plt.ylabel("max |x(dt) - x_ref|")
    plt.title("Max state error vs dt (vs fine reference)")
    plt.grid(True, which="both")

    plt.show()
