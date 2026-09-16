"""
one_mass_hopper_live.py — NumPy + Matplotlib only
Live simulator for the one-mass hopper (stance phase) — NO gravity compensation.

State:
  X = [x, y, xd, yd]^T
Inputs:
  u = [f, tau]^T
    - f   : axial force along leg [N]
    - tau : torque about the foot [N·m]  (torque → tangential force via tau/r)

Geometry:
  r  = sqrt(x^2 + y^2)
  r_hat = [x, y]/r
  t_hat = [-r_y, r_x]
  R = [ r_hat  t_hat ] = [[r_x, -r_y],[r_y, r_x]]

Dynamics (translation; torque produces tangential force tau/r):
  [xddot; yddot] = (1/m) R [ f ; tau / r ] - [0; g]

Controller (PD in world frame, NO gravity compensation):
  a_des = Kp (p* - p) + Kd (0 - v)
  F_des = m * a_des                 # NO +[0, g]
  F_par  = r_hat · F_des            [N]
  F_perp = t_hat · F_des            [N]
  f   = F_par                       [N]
  tau = F_perp * r                  [N·m]

Notes:
- Initial state X0 = [0, 1, 0, 0]^T (position (0,1), zero velocities).
"""

import math
from time import perf_counter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider

# ---------------- Parameters ----------------
g = 9.81     # gravity [m/s^2]
m = 5.0      # mass [kg]
r_eps = 1e-9 # avoid divide-by-zero at the origin

# Initial state 
X0 = np.array([0.0, 1.0, 0.0, 0.0], dtype=float)   # [x, y, xd, yd]

#target position so it actually moves
GOAL = np.array([0.25, 1.20], dtype=float)         # [x*, y*], desired velocity = 0

DT_DEFAULT = 0.01


F_MAX_N     = 900.0   # axial force [N]
TAU_MAX_NM  = 300.0   # torque [N·m]

# ---------------- Helpers ----------------
def leg_frame(x: float, y: float):
    """Return r_hat=(rx,ry), t_hat=(tx,ty), and radius r."""
    r = math.hypot(x, y)
    if r < r_eps:
        r = r_eps
    rx, ry = x / r, y / r
    tx, ty = -ry, rx
    return (rx, ry), (tx, ty), r

# ---------------- Continuous dynamics ----------------
def dynamics(X: np.ndarray, u: np.ndarray) -> np.ndarray:
    """
    X = [x,y,xd,yd], u = [f, tau] with tau in N·m.
    Tangential force Ft = tau / r.
    """
    x, y, xd, yd = X
    f, tau = u
    (rx, ry), (tx, ty), r = leg_frame(x, y)
    Ft = tau / r
    ax = (rx * f + tx * Ft) / m
    ay = (ry * f + ty * Ft) / m - g
    return np.array([xd, yd, ax, ay], dtype=float)

# ---------------- Integrators ----------------
def euler_step(X, u, dt):                 # 1st order
    return X + dt * dynamics(X, u)

def semi_implicit_step(X, u, dt):         # 1st order, symplectic
    x, y, xd, yd = X
    k = dynamics(X, u)  # [xd, yd, ax, ay]
    xd2 = xd + dt * k[2]
    yd2 = yd + dt * k[3]
    x2  = x  + dt * xd2
    y2  = y  + dt * yd2
    return np.array([x2, y2, xd2, yd2], dtype=float)

def midpoint_step(X, u, dt):              # 2nd order (RK2)
    Xm = X + 0.5 * dt * dynamics(X, u)
    return X + dt * dynamics(Xm, u)

def rk4_step(X, u, dt):                   # 4th order
    k1 = dynamics(X, u)
    k2 = dynamics(X + 0.5*dt*k1, u)
    k3 = dynamics(X + 0.5*dt*k2, u)
    k4 = dynamics(X + dt*k3, u)
    return X + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

STEP_FNS = {
    "Euler": euler_step,
    "Semi-Implicit": semi_implicit_step,
    "Midpoint": midpoint_step,
    "RK4": rk4_step,
}

# ---------------- PD controller ----------------
def controller_pd_no_gc(
    X: np.ndarray,
    pos_ref=GOAL,
    kp: float = 200.0,
    kd: float = 40.0,
) -> np.ndarray:
    """
    a_des = Kp (p* - p) + Kd (0 - v)
    F_des = m * a_des                  
    f   = (r_hat · F_des)              [N]
    tau = (t_hat · F_des) * r          [N·m]
    """
    x, y, xd, yd = X
    p = np.array([x, y])
    v = np.array([xd, yd])

    a_des = kp*(pos_ref - p) + kd*(0.0 - v)
    F_des = m * a_des                                   # world force [N]

    (rx, ry), (tx, ty), r = leg_frame(x, y)
    F_par  = F_des[0]*rx + F_des[1]*ry                  # [N]
    F_perp = F_des[0]*tx + F_des[1]*ty                  # [N]

    f   = F_par
    tau = F_perp * r                                    # [N·m]

    # Separate saturations
    f   = max(-F_MAX_N,     min(F_MAX_N,     float(f)))
    tau = max(-TAU_MAX_NM,  min(TAU_MAX_NM,  float(tau)))
    return np.array([f, tau], dtype=float)

# ---------------- Batch simulator (for Compare) ----------------
def simulate(method="RK4", T=6.0, dt=DT_DEFAULT,
             X0_=X0.copy(), kp=200.0, kd=40.0, pos_ref=GOAL):
    step = STEP_FNS[method]
    N = int(T/dt) + 1
    t = np.linspace(0.0, T, N)
    X_hist = np.zeros((N,4))
    U_hist = np.zeros((N,2))
    X = X0_.astype(float).copy()
    tic = perf_counter()
    for k in range(N):
        u = controller_pd_no_gc(X, pos_ref=pos_ref, kp=kp, kd=kd)
        X_hist[k] = X
        U_hist[k] = u
        if k < N-1:
            X = step(X, u, dt)
            # ground clamp
            if X[1] < 0.0:
                X[1] = 0.0
                if X[3] < 0.0:
                    X[3] = 0.0
    elapsed = perf_counter() - tic
    return t, X_hist, U_hist, elapsed

# ---------------- Live UI ----------------
plt.rcParams["toolbar"] = "None"
fig = plt.figure(figsize=(9.2, 7.2))
ax = fig.add_axes([0.08, 0.25, 0.62, 0.7])
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.2, 1.8)
ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
ax.grid(True, alpha=0.3)
ax.set_title("One-mass hopper (select integrator, then Start)")

# ground, goal, leg, mass
ax.plot([-2, 2], [0, 0], "k-", lw=2)
ax.plot([GOAL[0]], [GOAL[1]], marker="x", color="k", ms=10)  # goal marker
X = X0.copy()
leg_line, = ax.plot([0, X[0]], [0, X[1]], "-", lw=3)
mass_dot, = ax.plot([X[0]], [X[1]], "o", ms=12)

# info text
txt = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top", family="monospace")

# widgets
ax_radio = fig.add_axes([0.75, 0.66, 0.20, 0.14])
radio = RadioButtons(ax_radio, labels=list(STEP_FNS.keys()), active=3)

ax_dt = fig.add_axes([0.75, 0.61, 0.20, 0.03])
s_dt = Slider(ax_dt, "Δt [s]", 0.001, 0.05, valinit=DT_DEFAULT)

# wide gain ranges to test “no-controller” too
ax_kp = fig.add_axes([0.75, 0.56, 0.20, 0.03])
s_kp = Slider(ax_kp, "Kp", 0.0, 500.0, valinit=200.0)

ax_kd = fig.add_axes([0.75, 0.51, 0.20, 0.03])
s_kd = Slider(ax_kd, "Kd", 0.0, 500.0, valinit=40.0)

ax_start = fig.add_axes([0.75, 0.44, 0.09, 0.05]); btn_start = Button(ax_start, "Start")
ax_stop  = fig.add_axes([0.86, 0.44, 0.09, 0.05]); btn_stop  = Button(ax_stop,  "Stop")
ax_step  = fig.add_axes([0.75, 0.37, 0.09, 0.05]); btn_step  = Button(ax_step,  "Step")
ax_reset = fig.add_axes([0.86, 0.37, 0.09, 0.05]); btn_reset = Button(ax_reset, "Reset")
ax_cmp   = fig.add_axes([0.75, 0.30, 0.20, 0.05]); btn_cmp   = Button(ax_cmp,   "Compare Methods")
ax_quit  = fig.add_axes([0.75, 0.23, 0.20, 0.05]); btn_quit  = Button(ax_quit,  "End / Close")

running = False
method_label = "RK4"
t_live = 0.0

def update_graphics():
    leg_line.set_data([0, X[0]], [0, X[1]])
    mass_dot.set_data([X[0]], [X[1]])
    txt.set_text(
        f"method: {method_label}\n"
        f"t = {t_live:5.2f} s\n"
        f"x = {X[0]: .3f}  y = {X[1]: .3f}\n"
        f"xd= {X[2]: .3f}  yd= {X[3]: .3f}"
    )
    fig.canvas.draw_idle()

def step_once():
    """One simulation step: control  -> integrate -> clamp -> redraw"""
    global X, t_live
    dt = float(s_dt.val)
    kp = float(s_kp.val); kd = float(s_kd.val)
    u = controller_pd_no_gc(X, pos_ref=GOAL, kp=kp, kd=kd)
    Xn = STEP_FNS[method_label](X, u, dt)
    # ground clamp
    if Xn[1] < 0.0:
        Xn[1] = 0.0
        if Xn[3] < 0.0:
            Xn[3] = 0.0
    X[:] = Xn
    t_live += dt
    update_graphics()

def on_start(_):  # Start
    global running
    running = True

def on_stop(_):   # Stop
    global running
    running = False

def on_step(_):   # Single step
    global running
    running = False
    step_once()

def on_reset(_):  # Reset to initial state
    global X, t_live, running
    running = False
    X[:] = X0
    t_live = 0.0
    update_graphics()

def on_quit(_):   # Close window
    plt.close(fig)

def on_method(label):
    global method_label
    method_label = label

btn_start.on_clicked(on_start)
btn_stop.on_clicked(on_stop)
btn_step.on_clicked(on_step)
btn_reset.on_clicked(on_reset)
btn_quit.on_clicked(on_quit)
radio.on_clicked(on_method)

# Timer callback: "one integration step, then draw"
timer = fig.canvas.new_timer(interval=20)  # ~50 FPS
def on_timer(_):
    if running:
        step_once()
timer.add_callback(on_timer, None)
timer.start()

update_graphics()

# ---------------- Comparison button behavior ----------------
def compare_methods(_=None):
    methods = list(STEP_FNS.keys())
    dt = float(s_dt.val)
    kp = float(s_kp.val); kd = float(s_kd.val)
    T = 6.0
    comp = {}
    for mth in methods:
        t, Xh, Uh, elapsed = simulate(method=mth, T=T, dt=dt, X0_=X0, kp=kp, kd=kd, pos_ref=GOAL)
        comp[mth] = (t, Xh, Uh, elapsed)

    # Error vs time (distance to GOAL) 
    plt.figure()
    for mth in methods:
        t, Xh, _, _ = comp[mth]
        err = np.linalg.norm(Xh[:, :2] - GOAL[None, :], axis=1)
        plt.plot(t, err, label=mth)
    plt.xlabel("time [s]"); plt.ylabel("‖p - goal‖ [m]")
    plt.title("Position error vs time (no gravity compensation)")
    plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    # Position components
    plt.figure()
    for mth in methods:
        t, Xh, _, _ = comp[mth]
        plt.plot(t, Xh[:, 0], label=f"x(t) - {mth}")
        plt.plot(t, Xh[:, 1], linestyle="--", label=f"y(t) - {mth}")
    plt.xlabel("time [s]"); plt.ylabel("position [m]"); plt.title("Position trajectories")
    plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    # xy trajectory
    plt.figure()
    for mth in methods:
        _, Xh, _, _ = comp[mth]
        plt.plot(Xh[:, 0], Xh[:, 1], label=mth)
    plt.scatter([GOAL[0]], [GOAL[1]], marker="x", color="k")
    plt.axhline(0.0, color="k", linewidth=1)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.xlabel("x [m]"); plt.ylabel("y [m]"); plt.title("xy trajectory")
    plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    # Inputs (note units)
    plt.figure()
    for mth in methods:
        t, _, Uh, _ = comp[mth]
        plt.plot(t, Uh[:, 0], label=f"f – {mth}")
    plt.xlabel("time [s]"); plt.ylabel("f [N]"); plt.title("Axial force f(t)")
    plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    plt.figure()
    for mth in methods:
        t, _, Uh, _ = comp[mth]
        plt.plot(t, Uh[:, 1], label=f"tau – {mth}")
    plt.xlabel("time [s]"); plt.ylabel("tau [N·m]"); plt.title("Torque τ(t)")
    plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    # Console summary
    for mth in methods:
        t, Xh, _, elapsed = comp[mth]
        final_err = float(np.linalg.norm(Xh[-1, :2] - GOAL))
        print(f"{mth:>14s} | final |p-goal| = {final_err:8.5f} m | time = {elapsed*1e3:7.2f} ms (dt={dt})")

btn_cmp.on_clicked(compare_methods)

# Keyboard shortcuts
def on_key(event):
    global running
    if event.key == " ":
        running = not running
    elif event.key in ("r", "R"):
        on_reset(None)
    elif event.key in ("s", "S"):
        on_step(None)
fig.canvas.mpl_connect("key_press_event", on_key)

plt.show()
