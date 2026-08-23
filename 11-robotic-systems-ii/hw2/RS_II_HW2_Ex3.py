import numpy as np
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Try to import proxsuite for MPC QP solving.
# If not available, we will only run the LQR controller.
try:
    import proxsuite
    HAS_PROX = True
except Exception:
    HAS_PROX = False

# ---------------- Physical params ----------------
g   = 9.81   # gravity [m/s^2]
m   = 1.0    # mass [kg]
J   = 0.05   # moment of inertia [kg m^2]
kx  = 0.3    # drag coefficient in body x
ky  = 0.3    # drag coefficient in body y
kth = 0.02   # rotational viscous damping
L   = 0.5    # length of the body drawn in the animation

# Actuator limits (thrust and torque)
T_MIN = 0.5 * m * g
T_MAX = 1.5 * m * g
TAU_MIN, TAU_MAX = -0.5, 0.5

# State and input dimensions
N, M = 6, 2  # state: (X, Y, theta, Xdot, Ydot, thetadot), input: (T, tau)


# ---------------- Helpers ----------------
def Rot(th):
    """2D rotation matrix for angle th (world <-> body)."""
    c, s = np.cos(th), np.sin(th)
    return np.array([[c, -s],
                     [s,  c]])


# Nonlinear plant with PHYSICAL rotational damping:
#   J * thdd = tau - k_th * thd   -> thdd = (tau - kth * thd) / J
def dynamics(x, u):
    """
    Nonlinear continuous-time dynamics of the planar quadrotor.

    x = [X, Y, theta, Xdot, Ydot, thetadot]
    u = [T, tau]
    """
    X, Y, th, Xd, Yd, thd = x
    T, tau = u

    # body-frame velocity v_body = R^T * [Xdot, Ydot]
    v_body = Rot(th).T @ np.array([Xd, Yd])
    vx, vy = v_body

    # quadratic drag in body frame: ~ v * |v|
    fx = -kx * vx * abs(vx)
    fy = -ky * vy * abs(vy)

    # translation (in world coordinates)
    Xdd = (-np.sin(th) * (T + fy) + np.cos(th) * fx) / m
    Ydd = ( np.cos(th) * (T + fy) + np.sin(th) * fx) / m - g

    # rotation (including viscous damping)
    thdd = (tau - kth * thd) / J

    # return state derivative
    return np.array([Xd, Yd, thd, Xdd, Ydd, thdd])


def rk4(x, u, dt):
    """
    Runge-Kutta 4th order integrator for one step.

    Integrates the continuous dynamics over one time step dt,
    assuming u is constant over that time.
    """
    k1 = dynamics(x, u)
    k2 = dynamics(x + 0.5 * dt * k1, u)
    k3 = dynamics(x + 0.5 * dt * k2, u)
    k4 = dynamics(x + dt * k3,  u)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


# ---------------- Linearization & discretization ----------------
def linearize_ct():
    """
    Linearize the dynamics around hover (x=0, y=?, theta=0, v=0, T=mg, tau=0).

    Returns continuous-time A, B matrices such that:
        xdot = A x + B u
    in deviation variables around the equilibrium.
    """
    A = np.array([
        [0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0,-g, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0,-kth/J],  # thdd = (tau - kth*thd)/J  => ∂thdd/∂thd = -kth/J
    ], float)

    B = np.array([
        [0,   0],
        [0,   0],
        [0,   0],
        [0,   0],
        [1/m, 0],
        [0, 1/J],
    ], float)
    return A, B


def discretize_euler(A, B, dt):
    """
    Simple forward-Euler discretization of continuous linear model:
      x_{k+1} ≈ (I + dt*A)x_k + dt*B u_k
    """
    Ad = np.eye(N) + dt * A
    Bd = dt * B
    return Ad, Bd


# ---------------- DLQR (infinite horizon) ----------------
def dlqr_inf(Ad, Bd, Q, R, tol=1e-10, itmax=10000):
    """
    Infinite-horizon discrete-time LQR via Riccati iteration.

    Ad, Bd : discrete-time model
    Q, R   : state and input cost matrices

    Returns:
      P : Riccati solution
      K : feedback gain such that u = u_ref - K (x - x_ref)
    """
    P = Q.copy()
    for _ in range(itmax):
        S = R + Bd.T @ P @ Bd
        K = np.linalg.solve(S, Bd.T @ P @ Ad)
        Pn = Q + Ad.T @ P @ (Ad - Bd @ K)
        if np.linalg.norm(Pn - P, ord='fro') < tol:
            P = Pn
            break
        P = Pn
    K = np.linalg.solve(R + Bd.T @ P @ Bd, Bd.T @ P @ Ad)
    return P, K


# ---------------- Drag-aware feedforward ----------------
def theta_from_drag(ax, ay, xd, yd, theta0=None, iters=6):
    """
    Given desired accelerations ax, ay and velocities xd, yd in world frame,
    find the angle theta so that the horizontal forces balance with drag.

    Solve g(theta) = 0 for theta:
      g(theta) = (cos θ Fx + sin θ Fy) - fx(theta) = 0
      Fx = m*ax, Fy = m*(ay+g),
      fx(theta) = -kx * vx|vx|,   vx = cos θ xd + sin θ yd.

    We use a simple 1D Newton iteration (very fast).
    """
    Fx = m * ax
    Fy = m * (ay + g)  # use global g

    # initial guess: no-drag solution (simple arctan-based guess)
    th = float(theta0 if theta0 is not None else np.arctan2(-ax, ay + g))

    for _ in range(iters):
        c, s = np.cos(th), np.sin(th)
        vx = c * xd + s * yd
        dvx_dth = -s * xd + c * yd
        fx = -kx * vx * abs(vx)
        dfx_dth = -kx * 2.0 * abs(vx) * dvx_dth

        # residual and its derivative
        eq  = (c * Fx + s * Fy) - fx
        deq = (-s * Fx + c * Fy) - dfx_dth
        th -= eq / (deq + 1e-8)  # Newton step (denominator protected from 0)

    return float(th)


def T_closed_form_given_theta(theta, ax, ay, xd, yd):
    """
    Given theta, ax, ay, xd, yd, solve analytically for thrust T.

    T(theta) = -fy(theta) + (-sin θ Fx + cos θ Fy)
    where
      fy(theta) = -ky * vy|vy|,
      vy = -sin θ xd + cos θ yd
    """
    Fx = m * ax
    Fy = m * (ay + g)
    s, c = np.sin(theta), np.cos(theta)
    vy = -s * xd + c * yd
    fy = -ky * vy * abs(vy)
    T  = -fy + (-s * Fx + c * Fy)
    # Clip to actuator limits
    return float(np.clip(T, T_MIN, T_MAX))


def ff_from_acc_with_drag(ax, ay, xd, yd, theta_prev=None):
    """
    Drag-aware feedforward: given desired ax, ay, xd, yd,
    return reference attitude theta_ref and thrust T_ref that
    best realize those accelerations under drag.
    """
    th_ref = theta_from_drag(ax, ay, xd, yd, theta0=theta_prev)
    T_ref  = T_closed_form_given_theta(th_ref, ax, ay, xd, yd)
    return th_ref, T_ref


# ---------------- Reference generator (circle) ----------------
def path_circle_with_drag(t, dt_ref=0.05, xc=0.5, yc=0.6, R=0.4, w=0.4, theta_prev=None):
    """
    Reference generator: a circular path in (x,y) with radius R and angular speed w.

    For time t, it returns:
      xref(t) = [x, y, theta_ref, xdot, ydot, thetadot_ref]
      uref(t) = [T_ref, tau_ref]
    including drag-aware feedforward for T and theta.
    """
    # reference position / velocity / acceleration in world frame
    x  = xc + R * np.cos(w * t)
    y  = yc + R * np.sin(w * t)
    xd = -R * w * np.sin(w * t)
    yd =  R * w * np.cos(w * t)
    ax = -R * w * w * np.cos(w * t)
    ay = -R * w * w * np.sin(w * t)

    # drag-aware theta, T
    th_ref, T_ref = ff_from_acc_with_drag(ax, ay, xd, yd, theta_prev=theta_prev)

    # numeric theta_dot via central difference for tau_ref = kth * theta_dot_ref
    t_eps = 1e-3
    tp = t + t_eps
    tm = t - t_eps

    xd_p = -R * w * np.sin(w * tp)
    yd_p =  R * w * np.cos(w * tp)
    xd_m = -R * w * np.sin(w * tm)
    yd_m =  R * w * np.cos(w * tm)

    th_plus, _  = ff_from_acc_with_drag(ax, ay, xd_p, yd_p, theta_prev=th_ref)
    th_minus, _ = ff_from_acc_with_drag(ax, ay, xd_m, yd_m, theta_prev=th_ref)
    thd_ref = (th_plus - th_minus) / (2 * t_eps)

    # reference torque so theta_ddot_ref = 0: tau_ref = kth * theta_dot_ref
    tau_ref = kth * thd_ref

    xref = np.array([x, y, th_ref, xd, yd, thd_ref])
    uref = np.array([T_ref, tau_ref])
    return xref, uref


# ---------------- MPC blocks (optional) ----------------
def build_mpc_qp_interleaved(Ad, Bd, H, Q, R, Pterm,
                             x1, xref_seq, uref_seq, u_lb, u_ub):
    """
    z = [u1, x2, u2, x3, ..., uH, x_{H+1}].
    H      : horizon length
    Q, R   : stage costs
    Pterm  : terminal cost
    x1     : current state
    xref_seq, uref_seq : reference trajectories of length H+1 and H.
    """
    n, m = Ad.shape[0], Bd.shape[1]
    stride = m + n
    nz = H * stride
    Hmat = np.zeros((nz, nz))
    gvec = np.zeros(nz)

    def iu(k):     
        off = (k - 1) * stride
        return slice(off, off + m)

    def ix(kp1):   
        k = kp1 - 1
        off = (k - 1) * stride + m
        return slice(off, off + n)

    # Quadratic + linear cost on controls
    for k in range(1, H+1):
        s = iu(k)
        Hmat[s, s] += R
        gvec[s]    += -R @ uref_seq[k-1]

    # Quadratic + linear cost on states (except x1 which is fixed)
    for k in range(2, H+1):
        s = ix(k)
        Hmat[s, s] += Q
        gvec[s]    += -Q @ xref_seq[k-1]

    # Terminal cost on x_{H+1}
    sT = ix(H+1)
    Hmat[sT, sT] += Pterm
    gvec[sT]     += -Pterm @ xref_seq[H]

    # Dynamics constraints: x_{k+1} = Ad x_k + Bd u_k
    meq = H * n
    Aeq = np.zeros((meq, nz))
    beq = np.zeros(meq)

    # First: x2 = Ad * x1 + Bd * u1
    rows = slice(0, n)
    Aeq[rows, ix(2)] += np.eye(n)
    Aeq[rows, iu(1)] += -Bd
    beq[rows] = Ad @ x1

    # Then for k = 2..H: x_{k+1} = Ad x_k + Bd u_k
    for k in range(2, H+1):
        r = slice((k-1)*n, k*n)
        Aeq[r, ix(k+1)] += np.eye(n)
        Aeq[r, ix(k)]   += -Ad
        Aeq[r, iu(k)]   += -Bd

    # Input box constraints: u_lb <= u_k <= u_ub
    C = np.zeros((H*m, nz))
    l = np.zeros(H*m)
    u = np.zeros(H*m)
    for k in range(1, H+1):
        r = slice((k-1)*m, k*m)
        C[r, iu(k)] = np.eye(m)
        l[r] = u_lb
        u[r] = u_ub

    return Hmat, gvec, Aeq, beq, C, l, u


def mpc_step_interleaved(x_now, Ad, Bd, Q, R, Pterm, H, dt,
                         u_lb, u_ub, ref_fn):
    """
    One MPC step:
    - Build a local reference over horizon H (xref_seq, uref_seq)
    - Build and solve QP to get optimal sequence
    - Return first control input u1.
    """
    # Build reference sequences of length H+1 (states) and H (inputs)
    xref_seq = []
    uref_seq = []
    theta_seed = None
    for i in range(H+1):
        xr, ur = ref_fn(i * dt, theta_prev=theta_seed)
        theta_seed = xr[2]
        xref_seq.append(xr)
        if i < H:
            uref_seq.append(ur)
    xref_seq = np.stack(xref_seq, axis=0)
    uref_seq = np.stack(uref_seq, axis=0)

    # Build QP
    Hmat, gvec, Aeq, beq, C, l, u = build_mpc_qp_interleaved(
        Ad, Bd, H, Q, R, Pterm, x_now, xref_seq, uref_seq, u_lb, u_ub
    )

    n   = Hmat.shape[0]
    neq = Aeq.shape[0]
    nin = C.shape[0]

    qp = proxsuite.proxqp.dense.QP(n, neq, nin)
    qp.init(Hmat, gvec, Aeq, beq, C, l, u)
    qp.solve()

    if qp.results.info.status != proxsuite.proxqp.QPSolverOutput.PROXQP_SOLVED:
        raise RuntimeError(f"proxqp failed: {qp.results.info}")

    # Optimal stacked decision z, take first control u1
    z = qp.results.x
    u1 = z[:M]
    return u1, xref_seq[0], uref_seq[0]


# ---------------- Simulation & metrics ----------------
def simulate(controller="lqr", H=16, Tfinal=20.0, dt=0.05,
             noise_std=0.0, x_init=None):
    """
    Simulate the nonlinear quadrotor with either LQR or MPC.
    controller : "lqr" or "mpc"
    H          : horizon (only used by MPC)
    Tfinal     : total simulated time
    dt         : time step (controller + integrator)
    noise_std  : measurement noise std for the state
    x_init     : initial state; if None, a default tilted state is used.
    """
    steps = int(Tfinal / dt)

    # nonlinear plant initial state
    if x_init is None:
        # default: slightly tilted about hover
        x = np.array([0.0, 0.0, np.deg2rad(10.0), 0.0, 0.0, 0.0])
    else:
        x = np.array(x_init, dtype=float)

    # discrete linear model for LQR/MPC design
    A, B = linearize_ct()
    Ad, Bd = discretize_euler(A, B, dt)

    # LQR weights (also used as MPC stage weights)
    Q = np.diag([5, 5, 10, 1, 3, 1])
    Rw = np.diag([2e-2, 1e-2])
    Pterm, K = dlqr_inf(Ad, Bd, Q, Rw)

    # reference path function (drag-aware feedforward)
    def ref_fn(t, theta_prev=None):
        return path_circle_with_drag(t, dt_ref=dt, theta_prev=theta_prev)

    theta_seed = x[2]
    traj, ref_traj, ctrls = [], [], []
    sat_count = 0  # how many time steps hit actuator saturation

    for k in range(steps):
        t = k * dt
        xr, ur = ref_fn(t, theta_prev=theta_seed)
        theta_seed = xr[2]

        if controller == "lqr":
            # Add measurement noise to state (if noise_std>0)
            e = (x + noise_std * np.random.randn(N)) - xr
            # LQR feedback around reference
            u = ur - K @ e
        elif controller == "mpc" and HAS_PROX:
            # MPC with receding horizon
            u, xr_unused, ur_unused = mpc_step_interleaved(
                x + noise_std * np.random.randn(N),
                Ad, Bd, Q, Rw, Pterm, H, dt,
                np.array([T_MIN, TAU_MIN]),
                np.array([T_MAX, TAU_MAX]),
                lambda tau, theta_prev=None: ref_fn(t + tau, theta_prev=theta_prev)
            )
        else:
            raise ValueError("controller must be 'lqr' or 'mpc' (and proxsuite installed)")

        # clamp inputs (apply actuator limits in the plant)
        u = np.array([np.clip(u[0], T_MIN, T_MAX),
                      np.clip(u[1], TAU_MIN, TAU_MAX)])
        sat_count += int((u[0] in (T_MIN, T_MAX)) or (u[1] in (TAU_MIN, TAU_MAX)))

        # propagate nonlinear dynamics
        x = rk4(x, u, dt)
        traj.append(x.copy())
        ref_traj.append(xr.copy())
        ctrls.append(u.copy())

    return (np.array(traj), np.array(ref_traj), np.array(ctrls),
            sat_count, K, Pterm, Ad, Bd, Q, Rw)


def metrics(traj, ref_traj, ctrls, dt):
    """
    Compute some scalar performance metrics:
      - RMS position error,
      - max |theta|,
      - total control effort.
    """
    e = traj - ref_traj
    xy_rms = np.sqrt(np.mean(np.sum(e[:, :2]**2, axis=1)))
    th_max = np.rad2deg(np.max(np.abs(traj[:, 2])))
    effort = np.sum(np.sum(ctrls**2, axis=1)) * dt
    return dict(xy_rms=xy_rms, theta_max_deg=th_max, effort=effort)


# ---------- Animation helpers ----------
def body_line(x, y, th):
    """Compute the two endpoints of the quadrotor 'body' segment for plotting."""
    p1 = np.array([x, y]) + 0.5 * L * np.array([np.cos(th), np.sin(th)])
    p2 = np.array([x, y]) - 0.5 * L * np.array([np.cos(th), np.sin(th)])
    return np.vstack([p1, p2])


def animate(traj, ref_traj, dt, save_path="quad_drag_ff.gif", show=False,
            label="quad", color="C0"):
    """
    Create a GIF animation of a single run (either LQR or MPC)
    showing the quadrotor and the reference path.
    """
    xmin = min(traj[:, 0].min(), ref_traj[:, 0].min()) - 0.8
    xmax = max(traj[:, 0].max(), ref_traj[:, 0].max()) + 0.8
    ymin = min(traj[:, 1].min(), ref_traj[:, 1].min()) - 0.8
    ymax = max(traj[:, 1].max(), ref_traj[:, 1].max()) + 0.8

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ref_line, = ax.plot([], [], 'k--', lw=1, label='ref')
    body_line_plot, = ax.plot([], [], '-', lw=3, color=color, label=label)
    trail, = ax.plot([], [], ':', lw=1, color=color, alpha=0.7, label=label + " path")
    ax.legend()

    Kf = min(len(traj), len(ref_traj))

    def update(i):
        ref_line.set_data(ref_traj[:i, 0], ref_traj[:i, 1])
        bl = body_line(traj[i, 0], traj[i, 1], traj[i, 2])
        body_line_plot.set_data(bl[:, 0], bl[:, 1])
        trail.set_data(traj[:i, 0], traj[:i, 1])
        ax.set_title(f"t = {i*dt:.2f}s")
        return ref_line, body_line_plot, trail

    ani = FuncAnimation(fig, update, frames=Kf, interval=1000 * dt, blit=True)
    writer = PillowWriter(fps=max(1, int(round(1.0 / dt))))
    ani.save(save_path, writer=writer)
    if show:
        plt.show()
    plt.close(fig)
    print(f"Saved animation to {save_path}")


def animate_compare(trajL, trajM, ref_traj, dt,
                    save_path="quad_LQR_vs_MPC.gif", show=False):
    """
    Create a GIF animation showing LQR and MPC trajectories together,
    overlaid on the same reference path.
    """
    xmin = min(trajL[:, 0].min(), trajM[:, 0].min(), ref_traj[:, 0].min()) - 0.8
    xmax = max(trajL[:, 0].max(), trajM[:, 0].max(), ref_traj[:, 0].max()) + 0.8
    ymin = min(trajL[:, 1].min(), trajM[:, 1].min(), ref_traj[:, 1].min()) - 0.8
    ymax = max(trajL[:, 1].max(), trajM[:, 1].max(), ref_traj[:, 1].max()) + 0.8

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

    ref_line, = ax.plot([], [], 'k--', lw=1, label='ref')
    bodyL, = ax.plot([], [], '-', lw=3, color='C0', label='LQR')
    trailL, = ax.plot([], [], ':', lw=1, color='C0', alpha=0.7)
    bodyM, = ax.plot([], [], '-', lw=3, color='C1', label='MPC')
    trailM, = ax.plot([], [], ':', lw=1, color='C1', alpha=0.7)

    ax.legend()

    Kf = min(len(trajL), len(trajM), len(ref_traj))

    def update(i):
        ref_line.set_data(ref_traj[:i, 0], ref_traj[:i, 1])

        blL = body_line(trajL[i, 0], trajL[i, 1], trajL[i, 2])
        bodyL.set_data(blL[:, 0], blL[:, 1])
        trailL.set_data(trajL[:i, 0], trajL[:i, 1])

        blM = body_line(trajM[i, 0], trajM[i, 1], trajM[i, 2])
        bodyM.set_data(blM[:, 0], blM[:, 1])
        trailM.set_data(trajM[:i, 0], trajM[:i, 1])

        ax.set_title(f"LQR vs MPC   t = {i*dt:.2f}s")
        return ref_line, bodyL, trailL, bodyM, trailM

    ani = FuncAnimation(fig, update, frames=Kf, interval=1000 * dt, blit=True)
    writer = PillowWriter(fps=max(1, int(round(1.0 / dt))))
    ani.save(save_path, writer=writer)
    if show:
        plt.show()
    plt.close(fig)
    print(f"Saved combined animation to {save_path}")


# ---------- Comparison plots ----------
def plot_comparisons(trajL, refL, uL, trajM, refM, uM, dt,
                     prefix="quad_LQR_vs_MPC"):
    """
    Generate a set of PNG plots comparing LQR and MPC:
      - trajectories vs reference,
      - XY path,
      - theta vs time,
      - controls vs time,
      - position error norm.
    """
    tL = np.arange(trajL.shape[0]) * dt
    tM = np.arange(trajM.shape[0]) * dt
    tU_L = np.arange(uL.shape[0]) * dt
    tU_M = np.arange(uM.shape[0]) * dt

    # States vs reference (x, y, theta)
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(7, 8))
    axx, axy, axth = axes

    # x
    axx.plot(tL, refL[:, 0], 'k--', label="ref")
    axx.plot(tL, trajL[:, 0], 'C0-', label="LQR")
    axx.plot(tM, trajM[:, 0], 'C1-', label="MPC")
    axx.set_ylabel("x [m]")
    axx.grid(True, alpha=0.3)
    axx.legend()

    # y
    axy.plot(tL, refL[:, 1], 'k--', label="ref")
    axy.plot(tL, trajL[:, 1], 'C0-', label="LQR")
    axy.plot(tM, trajM[:, 1], 'C1-', label="MPC")
    axy.set_ylabel("y [m]")
    axy.grid(True, alpha=0.3)

    # theta (rad)
    axth.plot(tL, refL[:, 2], 'k--', label="ref")
    axth.plot(tL, trajL[:, 2], 'C0-', label="LQR")
    axth.plot(tM, trajM[:, 2], 'C1-', label="MPC")
    axth.set_ylabel("theta [rad]")
    axth.set_xlabel("time [s]")
    axth.grid(True, alpha=0.3)

    fig.suptitle("States vs reference")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(prefix + "_states_vs_reference.png", dpi=150, bbox_inches='tight')
    plt.close(fig)

    # XY paths
    fig, ax = plt.subplots()
    ax.plot(refL[:, 0], refL[:, 1], 'k--', label="ref")
    ax.plot(trajL[:, 0], trajL[:, 1], 'C0-', label="LQR")
    ax.plot(trajM[:, 0], trajM[:, 1], 'C1-', label="MPC")
    ax.set_aspect('equal')
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("XY path: LQR vs MPC")
    ax.legend()
    fig.savefig(prefix + "_xy.png", dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Theta vs time (deg)
    fig, ax = plt.subplots()
    ax.plot(tL, np.rad2deg(refL[:, 2]), 'k--', label="theta_ref [deg]")
    ax.plot(tL, np.rad2deg(trajL[:, 2]), 'C0-', label="theta_LQR [deg]")
    ax.plot(tM, np.rad2deg(trajM[:, 2]), 'C1-', label="theta_MPC [deg]")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("theta [deg]")
    ax.set_title("Theta: LQR vs MPC")
    ax.legend()
    fig.savefig(prefix + "_theta.png", dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Controls vs time
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(7, 6))
    axT, axTau = axes

    axT.plot(tU_L, uL[:, 0], 'C0-', label="T_LQR")
    axT.plot(tU_M, uM[:, 0], 'C1-', label="T_MPC")
    axT.set_ylabel("T [N]")
    axT.set_title("Thrust")
    axT.legend()
    axT.grid(True, alpha=0.3)

    axTau.plot(tU_L, uL[:, 1], 'C0-', label="tau_LQR")
    axTau.plot(tU_M, uM[:, 1], 'C1-', label="tau_MPC")
    axTau.set_xlabel("t [s]")
    axTau.set_ylabel("tau [Nm]")
    axTau.set_title("Torque")
    axTau.legend()
    axTau.grid(True, alpha=0.3)

    fig.suptitle("Controls: LQR vs MPC")
    fig.tight_layout()
    fig.savefig(prefix + "_controls.png", dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Position error norm
    eL = trajL - refL
    eM = trajM - refM
    pos_err_L = np.sqrt(eL[:, 0]**2 + eL[:, 1]**2)
    pos_err_M = np.sqrt(eM[:, 0]**2 + eM[:, 1]**2)

    fig, ax = plt.subplots()
    ax.plot(tL, pos_err_L, 'C0-', label="||e_pos|| LQR")
    ax.plot(tM, pos_err_M, 'C1-', label="||e_pos|| MPC")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("position error [m]")
    ax.set_title("Position tracking error norm")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(prefix + "_error_pos.png", dpi=150, bbox_inches='tight')
    plt.close(fig)


# ---------- Region-of-attraction style tools (full state x) ----------
def _simulate_and_final_error(controller, H, r, dt, Tscan,
                              x0, dir_vec):
    """
    Simulate from x_init = x0 + r * d_hat (full 6D state),
    and return final full-state error norm ||x(T) - x_ref(T)||_2.
    """
    d = np.array(dir_vec, dtype=float)
    d_norm = np.linalg.norm(d)
    if d_norm == 0:
        raise ValueError("dir_vec must be nonzero")
    d_hat = d / d_norm

    x_init = x0 + r * d_hat
    traj, ref, u, *_ = simulate(controller, H=H, dt=dt,
                                Tfinal=Tscan, x_init=x_init)
    if not np.all(np.isfinite(traj)):
        return np.inf
    e = traj - ref
    return np.linalg.norm(e[-1, :])


def estimate_max_r(controller, H, dt, Tscan, x0, dir_vec,
                   r_start=0.05, r_limit=3.0, eps=5):
    """
    Estimate a 'max radius' r along a direction dir_vec such that
    the controller still 'works':

    - Increase r until the final error exceeds eps or we hit r_limit,
      then use bisection to refine the largest r that still gives error <= eps.
    """
    err0 = _simulate_and_final_error(controller, H, 0.0, dt, Tscan, x0, dir_vec)
    if not np.isfinite(err0) or err0 > eps:
        return 0.0

    r_low = 0.0
    r_high = r_start

    # Exponential growth phase
    while True:
        err = _simulate_and_final_error(controller, H, r_high, dt, Tscan, x0, dir_vec)
        if (not np.isfinite(err)) or (err > eps) or (r_high >= r_limit):
            break
        r_low = r_high
        r_high *= 2.0

    # Bisection refinement
    for _ in range(20):
        mid = 0.5 * (r_low + r_high)
        err = _simulate_and_final_error(controller, H, mid, dt, Tscan, x0, dir_vec)
        if np.isfinite(err) and err <= eps:
            r_low = mid
        else:
            r_high = mid

    return r_low


def scan_r_and_plot(controllers, H, dt, Tscan, x0, dir_vec,
                    r_max=2.0, Nr=25,
                    filename="region_scan.png"):
    """
    For a fixed direction in x-space, scan r in [0, r_max] and plot
    final full-state error for each selected controller.

    This gives a 'slice' of how far from a nominal state x0 each controller
    can start before performance degrades significantly.
    """
    d = np.array(dir_vec, dtype=float)
    d_norm = np.linalg.norm(d)
    if d_norm == 0:
        raise ValueError("dir_vec must be nonzero")
    d_hat = d / d_norm

    r_vals = np.linspace(0.0, r_max, Nr)
    fig, ax = plt.subplots()

    for ctrl in controllers:
        if ctrl == "mpc" and not HAS_PROX:
            continue
        errs = []
        for r in r_vals:
            err = _simulate_and_final_error(ctrl, H, r, dt, Tscan, x0, d_hat)
            errs.append(err)
        ax.plot(r_vals, errs, marker='o', label=ctrl.upper())

    ax.set_xlabel("r = ||x(0) - x0|| along chosen direction")
    ax.set_ylabel("final state error ||x(T) - x_ref(T)||")
    ax.set_title(f"Region scan along direction (H={H})")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------- Run example ----------------
if __name__ == "__main__":
    dt = 0.05

    # 1) LQR with drag-aware feedforward (nominal run)
    trajL, refL, uL, satL, K, P, Ad, Bd, Q, R = simulate("lqr", H=16, dt=dt)
    mL = metrics(trajL, refL, uL, dt)
    print("[LQR] xy_RMS=%.3f  theta_max=%.1fdeg  effort=%.1f  sat=%d" %
          (mL['xy_rms'], mL['theta_max_deg'], mL['effort'], satL))
    print("DLQR gain K:\n", K)

    # Save animation of LQR run
    animate(trajL, refL, dt, save_path="quad_LQR.gif", show=False,
            label="LQR", color="C0")

    if HAS_PROX:
        # 2) MPC nominal run (H=24)
        trajM, refM, uM, satM, *_ = simulate("mpc", H=24, dt=dt)
        mM = metrics(trajM, refM, uM, dt)
        print("[MPC] xy_RMS=%.3f  theta_max=%.1fdeg  effort=%.1f  sat=%d" %
              (mM['xy_rms'], mM['theta_max_deg'], mM['effort'], satM))

        # Save animation of MPC run
        animate(trajM, refM, dt, save_path="quad_MPC.gif", show=False,
                label="MPC", color="C1")

        # Combined animation (same world frame)
        animate_compare(trajL, trajM, refL, dt,
                        save_path="quad_LQR_vs_MPC.gif", show=False)

        # Comparison plots (states, controls, errors)
        plot_comparisons(trajL, refL, uL, trajM, refM, uM, dt,
                         prefix="quad_LQR_vs_MPC")

        # Save scalar metrics to a text file
        with open("quad_LQR_vs_MPC_metrics.txt", "w") as f:
            f.write("LQR metrics:\n")
            for k, v in mL.items():
                f.write(f"  {k}: {v}\n")
            f.write(f"  sat_count: {satL}\n\n")
            f.write("MPC metrics:\n")
            for k, v in mM.items():
                f.write(f"  {k}: {v}\n")
            f.write(f"  sat_count: {satM}\n")
    else:
        print("proxsuite not available: only LQR run, MPC/compare disabled.")

    # 3) Region-of-attraction style analysis around a nominal state x0
    # Base state x0 = reference state at t=0 (full 6D state)
    x_ref0, _ = path_circle_with_drag(0.0, dt_ref=dt)
    x0 = x_ref0.copy()

    # Directions in state space (basis directions + "all ones")
    dir_list = [
        ("x",        np.array([1., 0., 0., 0., 0., 0.])),
        ("y",        np.array([0., 1., 0., 0., 0., 0.])),
        ("theta",    np.array([0., 0., 1., 0., 0., 0.])),
        ("xdot",     np.array([0., 0., 0., 1., 0., 0.])),
        ("ydot",     np.array([0., 0., 0., 0., 1., 0.])),
        ("thetadot", np.array([0., 0., 0., 0., 0., 1.])),
        ("all",      np.array([1., 1., 1., 1., 1., 1.])),
    ]

    Tscan = 10.0
    H_list = [8, 16, 24, 32]

    print("\n=== Approximate max radius r along several directions (full 6D state) ===")
    print("r is the magnitude of the initial deviation x(0) - x0 along that direction.\n")

    for H in H_list:
        print(f"--- Prediction horizon H = {H} ---")
        for name, d in dir_list:
            # LQR r_max
            rL = estimate_max_r("lqr", H, dt, Tscan, x0, d,
                                r_start=0.1, r_limit=3.0, eps=5.0)
            line = f"  Dir={name:8s}  LQR r_max ≈ {rL:6.3f}"

            if name in ("theta", "thetadot"):
                line += f" rad (~{np.rad2deg(rL):5.1f} deg)"
            elif name in ("x", "y"):
                line += " m"
            elif name in ("xdot", "ydot"):
                line += " m/s"
            else:
                line += " (state units)"
            print(line)

            # MPC r_max (if available)
            if HAS_PROX:
                rM = estimate_max_r("mpc", H, dt, Tscan, x0, d,
                                    r_start=0.1, r_limit=3.0, eps=5.0)
                lineM = f"              MPC r_max ≈ {rM:6.3f}"
                if name in ("theta", "thetadot"):
                    lineM += f" rad (~{np.rad2deg(rM):5.1f} deg)"
                elif name in ("x", "y"):
                    lineM += " m"
                elif name in ("xdot", "ydot"):
                    lineM += " m/s"
                else:
                    lineM += " (state units)"
                print(lineM)
        print()

    # 4) Example graph: final error vs r along theta direction for one H
    dir_theta = np.array([0., 0., 1., 0., 0., 0.])
    if HAS_PROX:
        H_graph = 24
        scan_r_and_plot(["lqr", "mpc"], H_graph, dt, Tscan,
                        x0, dir_theta,
                        r_max=np.deg2rad(80.0), Nr=25,
                        filename="region_scan_theta_H24.png")
    else:
        H_graph = 16
        scan_r_and_plot(["lqr"], H_graph, dt, Tscan,
                        x0, dir_theta,
                        r_max=np.deg2rad(80.0), Nr=25,
                        filename="region_scan_theta_H16_LQR_only.png")
