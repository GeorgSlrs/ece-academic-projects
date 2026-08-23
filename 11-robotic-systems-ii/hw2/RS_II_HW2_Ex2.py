import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ===== physical parameters =====
g, m, J = 9.81, 1.0, 0.05
kx, ky, kth = 0.3, 0.3, 0.02

# input limits
T_min, T_max = 0.5 * m * g, 1.5 * m * g
tau_min, tau_max = -0.5, 0.5

# sample time & duration (spec requires dt=0.05)
DT, TF = 0.05, 8.0

# hover location (equilibrium position)
HOVER_X, HOVER_Y = 0.0, 1.0

# ======= LIGHT NOISE for the regular simulation (not used in evaluation) =======
RNG_SEED = 7
OBS_NOISE_STD = np.array([0.02, 0.02, np.deg2rad(2.0), 0.05, 0.05, 0.06])
PROC_NOISE_STD = np.array([0.15, 0.15, 0.25])   # [ax, ay, athdd]
INIT_NOISE_STD = np.array([0.04, 0.04, np.deg2rad(3.0), 0.07, 0.07, 0.08])
ADD_OBS_NOISE = True
ADD_PROC_NOISE = True


# ---------------- helpers ----------------
def clamp(val, vmin, vmax):
    """Clamp a scalar or array between vmin and vmax."""
    return np.minimum(np.maximum(val, vmin), vmax)


def world_to_body_vel(xdot, ydot, theta):
    """Convert world-frame velocity (Xdot, Ydot) to body-frame components (vx, vy)."""
    c, s = np.cos(theta), np.sin(theta)
    vx = c * xdot + s * ydot
    vy = -s * xdot + c * ydot
    return vx, vy


# ---------------- nonlinear plant (with clamping + optional proc noise) ----------------
def dynamics(x, u, proc_noise=None):
    """
    Nonlinear continuous-time dynamics of the planar quadrotor.

    x = [X, Y, theta, Xdot, Ydot, thetadot]
    u = [T, tau]
    """
    x = np.asarray(x).reshape(-1)
    u = np.asarray(u).reshape(-1)
    X, Y, th, Xd, Yd, thd = x
    T, tau = u

    # clamp inputs (the plant enforces limits)
    T = clamp(T, T_min, T_max)
    tau = clamp(tau, tau_min, tau_max)

    # body-frame drag
    vx, vy = world_to_body_vel(Xd, Yd, th)
    fx = -kx * vx * abs(vx)
    fy = -ky * vy * abs(vy)
    fth = -kth * thd

    c, s = np.cos(th), np.sin(th)
    Xdd = (-s * (T + fy) + c * fx) / m
    Ydd = (c * (T + fy) + s * fx) / m - g
    thdd = (tau - fth) / J

    # optional process noise on accelerations
    if proc_noise is not None:
        Xdd += proc_noise[0]
        Ydd += proc_noise[1]
        thdd += proc_noise[2]

    return np.array([Xd, Yd, thd, Xdd, Ydd, thdd])


def rk4(x, u, dt, proc_noise=None):
    """
    4th-order Runge-Kutta step.
    Process noise (if provided) is held constant over the sample (ZOH disturbance).
    """
    k1 = dynamics(x, u, proc_noise)
    k2 = dynamics(x + 0.5 * dt * k1, u, proc_noise)
    k3 = dynamics(x + 0.5 * dt * k2, u, proc_noise)
    k4 = dynamics(x + dt * k3, u, proc_noise)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


# ---------------- hover (equilibrium) ----------------
def hover_point(xstar=HOVER_X, ystar=HOVER_Y):
    """
    Hover equilibrium around which we linearize:
    X = xstar, Y = ystar, theta = 0, all velocities = 0,
    input T = mg, tau = 0.
    """
    x_bar = np.array([xstar, ystar, 0, 0, 0, 0], float)
    u_bar = np.array([m * g, 0.0], float)
    return x_bar, u_bar


# ---------------- linearize (continuous) then discretize ----------------
def linearize_at_hover():
    """
    Continuous-time linearization of the nonlinear dynamics at hover.

    xdot = Ac (x - x_bar) + Bc (u - u_bar)
    """
    Ac = np.array([
        [0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, -g, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, kth / J],   # ∂θ̈/∂θ̇ (note: positive here matches plant sign)
    ], float)

    Bc = np.array([
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [1 / m, 0],   # ∂ÿ/∂T
        [0, 1 / J],   # ∂θ̈/∂τ
    ], float)

    return Ac, Bc


def discretize_euler(Ac, Bc, dt):
    """
    Simple forward-Euler discretization of the continuous linear model.

    x_{k+1} = Ad x_k + Bd u_k  with sample time dt.
    """
    Ad = np.eye(6) + dt * Ac
    Bd = dt * Bc
    return Ad, Bd


# ---------------- DLQR (infinite horizon via Riccati iteration) ----------------
def dlqr(Ad, Bd, Q, R, tol=1e-10, itmax=10000):
    """
    Discrete-time LQR via Riccati iteration.

    Returns:
        P : solution of the DARE
        K : feedback gain (u = u_bar - K (x - x_bar))
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


# ---------------- simulate nonlinear plant with DLQR (+ optional noise) ----------------
def simulate_dlqr(K, x_bar, u_bar, dt=DT, tf=TF, x0=None, rng=None):
    """
    Simulate the nonlinear plant under the DLQR controller.

    K     : LQR gain matrix (2x6)
    x_bar : equilibrium state
    u_bar : equilibrium input
    """
    N = int(np.round(tf / dt))
    X = np.zeros((N + 1, 6))
    U = np.zeros((N, 2))
    X[0] = x_bar if x0 is None else x0

    for k in range(N):
        # measurement noise to the controller
        if (rng is not None) and ADD_OBS_NOISE:
            x_meas = X[k] + rng.normal(0.0, OBS_NOISE_STD)
        else:
            x_meas = X[k]

        # LQR state feedback around hover
        e = x_meas - x_bar
        u_raw = u_bar - K @ e   # DLQR control (plant clamps)

        # process noise this sample (held fixed through RK4 stages)
        proc = rng.normal(0.0, PROC_NOISE_STD) if ((rng is not None) and ADD_PROC_NOISE) else None

        U[k] = u_raw
        X[k + 1] = rk4(X[k], u_raw, dt, proc_noise=proc)

    t = np.arange(N + 1) * dt
    return t, X, U


# ---------------- robust animation ----------------
def animate_xy(t, X, x_bar, L=0.8, pad=0.6, title="Planar quadrotor"):
    """
    Simple 2D animation of the quadrotor motion in the (x, y) plane.
    """
    xmin, xmax = X[:, 0].min(), X[:, 0].max()
    ymin, ymax = X[:, 1].min(), X[:, 1].max()

    if xmax - xmin < 1e-3:
        cx = 0.5 * (xmin + xmax)
        xmin, xmax = cx - pad, cx + pad
    else:
        xmin, xmax = xmin - 0.2, xmax + 0.2

    if ymax - ymin < 1e-3:
        cy = 0.5 * (ymin + ymax)
        ymin, ymax = cy - pad, cy + pad
    else:
        ymin, ymax = min(0.0, ymin - 0.2), ymax + 0.2

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(title)
    ax.axhline(0.0, lw=1, alpha=0.3)

    body_line, = ax.plot([], [], lw=3, c='C0')
    left, = ax.plot([], [], 'ko', ms=6)
    right, = ax.plot([], [], 'ko', ms=6)
    path_line, = ax.plot([], [], lw=1, c='C1', alpha=0.7)
    target, = ax.plot([x_bar[0]], [x_bar[1]], 'r+', ms=12, mew=2)

    def endpoints(x, y, th):
        ex = np.array([np.cos(th), np.sin(th)])
        pL = np.array([x, y]) - 0.5 * L * ex
        pR = np.array([x, y]) + 0.5 * L * ex
        return pL, pR

    def init():
        x, y, th = X[0, 0], X[0, 1], X[0, 2]
        pL, pR = endpoints(x, y, th)
        body_line.set_data([pL[0], pR[0]], [pL[1], pR[1]])
        left.set_data([pL[0]], [pL[1]])
        right.set_data([pR[0]], [pR[1]])
        path_line.set_data([x], [y])
        return body_line, left, right, path_line, target

    def update(k):
        x, y, th = X[k, 0], X[k, 1], X[k, 2]
        pL, pR = endpoints(x, y, th)
        body_line.set_data([pL[0], pR[0]], [pL[1], pR[1]])
        left.set_data([pL[0]], [pL[1]])
        right.set_data([pR[0]], [pR[1]])
        path_line.set_data(X[:k + 1, 0], X[:k + 1, 1])
        ax.set_title(f"{title}  |  t={t[k]:.2f}s")
        return body_line, left, right, path_line, target

    anim = FuncAnimation(
        fig, update, init_func=init,
        frames=len(t), interval=1000 * (t[1] - t[0]),
        blit=False
    )
    return anim


# ---------------- success test (for "how far" evaluation) ----------------
def success_run(K, x_bar, u_bar, x0, dt=DT, tf=TF,
                eps_pos=0.06, eps_ang=0.07, eps_vel=0.12, max_sat_frac=0.5):
    """
    Deterministic evaluation: NO NOISE here.
    Success if final errors are small, no tumble, and not mostly saturated.
    """
    t, X, U = simulate_dlqr(K, x_bar, u_bar, dt, tf, x0=x0, rng=None)  # <- no noise

    e = X - x_bar
    ef = e[-1]

    ok_pos = (abs(ef[0]) < eps_pos) and (abs(ef[1]) < eps_pos)
    ok_ang = abs(ef[2]) < eps_ang
    ok_vel = (abs(ef[3]) < eps_vel) and (abs(ef[4]) < eps_vel) and (abs(ef[5]) < eps_vel)
    ok_angle_bound = np.all(np.abs(X[:, 2]) < np.pi / 2)

    # fraction of time the *commanded* inputs exceed limits (i.e., would be clamped)
    sat_T = np.mean((np.clip(U[:, 0], T_min, T_max) - U[:, 0]) != 0.0)
    sat_tau = np.mean((np.clip(U[:, 1], tau_min, tau_max) - U[:, 1]) != 0.0)
    ok_sat = (sat_T <= max_sat_frac) and (sat_tau <= max_sat_frac)

    return ok_pos and ok_ang and ok_vel and ok_angle_bound and ok_sat


def max_radius_along_dir(K, x_bar, u_bar, d, r_hi=2.0, tol=1e-3):
    """
    Binary search on the radius r along direction d so that success_run()==True.

    We search for the largest r such that the controller still succeeds
    from initial condition x0 = x_bar + r * d_hat.
    """
    d = d / (np.linalg.norm(d) + 1e-12)

    # Ensure r=0 succeeds (sanity)
    if not success_run(K, x_bar, u_bar, x_bar):
        return 0.0

    lo, hi = 0.0, 1e-3
    while hi < r_hi and success_run(K, x_bar, u_bar, x_bar + hi * d):
        lo, hi = hi, hi * 2.0

    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if success_run(K, x_bar, u_bar, x_bar + mid * d):
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break

    return lo


# =============================== main ===============================
if __name__ == "__main__":
    # 1) equilibrium and design model
    rng = np.random.default_rng(RNG_SEED)
    x_bar, u_bar = hover_point()
    Ac, Bc = linearize_at_hover()
    Ad, Bd = discretize_euler(Ac, Bc, DT)

    # 2) DLQR weights and gain
    Q = np.diag([5, 5, 10, 1, 3, 1])
    R = np.diag([2e-2, 1e-2])
    P, K = dlqr(Ad, Bd, Q, R)
    print("DLQR gain K (2x6):\n", K)

    # 3) slightly noisy initial condition for the regular demo sim
    x0 = x_bar + rng.normal(0.0, INIT_NOISE_STD)
    print("Initial perturbation (demo):", x0 - x_bar)

    # 4) simulate the nonlinear plant (with mild noise for realism)
    t, X, U = simulate_dlqr(K, x_bar, u_bar, dt=DT, tf=TF, x0=x0, rng=rng)

    # 5) time plots
    fig, axs = plt.subplots(2, 1, figsize=(7, 6), sharex=False)

    axs[0].plot(t, X[:, 0], label='x')
    axs[0].plot(t, X[:, 1], label='y')
    axs[0].axhline(x_bar[0], ls='--', c='k')
    axs[0].axhline(x_bar[1], ls='--', c='k')
    axs[0].set_ylabel('pos [m]')
    axs[0].legend()

    axs[1].plot(t[:-1], U[:, 0], label='T')
    axs[1].plot(t[:-1], U[:, 1], label='tau')
    axs[1].axhline(T_min, ls='--', c='k')
    axs[1].axhline(T_max, ls='--', c='k')
    axs[1].axhline(tau_min, ls='--', c='k')
    axs[1].axhline(tau_max, ls='--', c='k')
    axs[1].set_ylabel('inputs')
    axs[1].set_xlabel('time [s]')
    axs[1].legend()

    fig.tight_layout()

    # 6) robust animation — keep a reference and show afterwards
    anim = animate_xy(t, X, x_bar, title="DLQR about hover (demo with mild noise)")
    plt.show()

    # 7) Evaluate "how far" LQR works (deterministic, NO NOISE)
    dirs = {
        "x":       np.array([1, 0, 0, 0, 0, 0]),
        "y":       np.array([0, 1, 0, 0, 0, 0]),
        "theta":   np.array([0, 0, 1, 0, 0, 0]),
        "xdot":    np.array([0, 0, 0, 1, 0, 0]),
        "ydot":    np.array([0, 0, 0, 0, 1, 0]),
        "thetadot":np.array([0, 0, 0, 0, 0, 1]),
    }

    print("\nMax admissible initial error magnitude per direction (binary search, NO NOISE):")
    radii = {}
    for name, d in dirs.items():
        r = max_radius_along_dir(K, x_bar, u_bar, d, r_hi=2.0, tol=1e-3)
        radii[name] = r
        print(f"  {name:9s}: r* ≈ {r:.4f}")

    # bar plot
    plt.figure(figsize=(7, 3))
    plt.bar(list(radii.keys()), list(radii.values()))
    plt.ylabel("max |Δ along direction|")
    plt.title("How far from linearization (empirical LQR region, NO NOISE)")
    plt.show()
