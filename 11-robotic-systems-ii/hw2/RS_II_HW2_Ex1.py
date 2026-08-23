import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ----------------------------
# USER SETTINGS (defaults)
# ----------------------------
DT    = 0.01   # time step [s]
TF    = 8.0    # final time [s]
YREF  = 1.0    # altitude target [m]
XREF  = 0.0    # horizontal target [m]
KPX   = 1.2    # x PD gains
KDX   = 0.7
KPY   = 10.0   # y PD gains
KDY   = 6.0
KPTH  = 12.0   # attitude PD gains
KDTH  = 3.0
XCTL  = True   # enable horizontal control

def _env_float(name, default):
    v = os.getenv(name)
    try:
        return float(v) if v is not None else default
    except Exception:
        return default

def _env_bool(name, default):
    v = os.getenv(name)
    if v is None: return default
    v = str(v).strip().lower()
    if v in ("1","true","t","yes","y","on"): return True
    if v in ("0","false","f","no","n","off"): return False
    return default

# override from environment if provided
DT   = _env_float("DT", DT)
TF   = _env_float("TF", TF)
YREF = _env_float("YREF", YREF)
XREF = _env_float("XREF", XREF)
KPX  = _env_float("KPX", KPX)
KDX  = _env_float("KDX", KDX)
KPY  = _env_float("KPY", KPY)
KDY  = _env_float("KDY", KDY)
KPTH = _env_float("KPTH", KPTH)
KDTH = _env_float("KDTH", KDTH)
XCTL = _env_bool ("XCTL", XCTL)

# ----------------------------
# Physical parameters
# ----------------------------
g   = 9.81
m   = 1.0
J   = 0.05
kx  = 0.3
ky  = 0.3
kth = 0.02

T_min = 0.5*m*g
T_max = 1.5*m*g
tau_min = -0.5
tau_max =  0.5

def clamp(val, vmin, vmax):
    return np.minimum(np.maximum(val, vmin), vmax)

def world_to_body_vel(xdot, ydot, theta):
    c, s = np.cos(theta), np.sin(theta)
    vx =  c * xdot + s * ydot
    vy = -s * ydot + c * xdot  
    return vx, vy

def dynamics(x, u):
    x = np.asarray(x).reshape(-1)
    u = np.asarray(u).reshape(-1)
    X, Y, th, Xd, Yd, thd = x
    T, tau = u

    # input saturation (safety)
    T   = clamp(T,   T_min, T_max)
    tau = clamp(tau, tau_min, tau_max)

    # velocities in body frame for drag
    vx, vy = world_to_body_vel(Xd, Yd, th)

    # drag forces and angular damping
    fx  = -kx * vx * abs(vx)
    fy  = -ky * vy * abs(vy)
    fth = -kth * thd

    # rotation terms
    c, s = np.cos(th), np.sin(th)

    # translational and rotational accelerations
    Xdd  = ( -s * (T + fy) + c * fx ) / m
    Ydd  = (  c * (T + fy) + s * fx ) / m - g
    thdd = (tau - fth) / J

    return np.array([Xd, Yd, thd, Xdd, Ydd, thdd])

def rk4_step(x, u, dt):
    k1 = dynamics(x, u)
    k2 = dynamics(x + 0.5*dt*k1, u)
    k3 = dynamics(x + 0.5*dt*k2, u)
    k4 = dynamics(x + dt*k3,     u)
    return x + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def simulate(x0, u_fn, tf=8.0, dt=0.01):
    N = int(np.floor(tf/dt)) + 1
    t = np.linspace(0.0, tf, N)
    X = np.zeros((N, 6))
    U = np.zeros((N, 2))

    X[0] = np.asarray(x0).reshape(-1)
    for k in range(N-1):
        uk = np.asarray(u_fn(t[k], X[k])).reshape(-1)
        U[k] = uk
        X[k+1] = rk4_step(X[k], uk, dt)

    # hold last control value
    U[-1] = U[-2]
    return t, X, U

# ----------------------------
# Controllers
# ----------------------------
def pd_hover_controller_y(y_ref=1.0, kp_y=10.0, kd_y=6.0):
    mg_val = m*g
    def u_y(x):
        _, y, _, _, yd, _ = x
        # T = mg + m * (PD correction)
        T_cmd = mg_val + (-kp_y*(y - y_ref) - kd_y*yd) * m
        return T_cmd
    return u_y

def pd_theta_controller(kp_th=12.0, kd_th=3.0, theta_ref_fn=None):
    if theta_ref_fn is None:
        theta_ref_fn = lambda x, T: 0.0
    def u_theta(x, T):
        th  = x[2]
        thd = x[5]
        th_ref = float(theta_ref_fn(x, T))
        tau_cmd = -kp_th*(th - th_ref) - kd_th*thd
        return tau_cmd
    return u_theta

def theta_ref_from_x_pd(x_ref=0.0, kp_x=1.2, kd_x=0.7, theta_limit=0.6):
    def fn(x, T):
        x_pos, _, _, xdot, _, _ = x
        # desired horizontal acceleration from PD on x
        ax_des = -kp_x*(x_pos - x_ref) - kd_x*xdot
        # avoid division by zero
        T_eff = max(float(T), 1e-3)
        # approximate relation: ax ≈ -(T/m)*theta  -> theta ≈ -m*ax/T
        th_ref = -m*ax_des / T_eff
        return np.clip(th_ref, -theta_limit, theta_limit)
    return fn

def make_controller(use_x_control=True, **kwargs):
    y_ref = kwargs.get("y_ref", 1.0)
    kp_y  = kwargs.get("kp_y", 10.0)
    kd_y  = kwargs.get("kd_y", 6.0)

    kp_th = kwargs.get("kp_th", 12.0)
    kd_th = kwargs.get("kd_th", 3.0)

    x_ref = kwargs.get("x_ref", 0.0)
    kp_x  = kwargs.get("kp_x", 1.2)
    kd_x  = kwargs.get("kd_x", 0.7)

    uy = pd_hover_controller_y(y_ref=y_ref, kp_y=kp_y, kd_y=kd_y)
    if use_x_control:
        th_ref_fn = theta_ref_from_x_pd(x_ref=x_ref, kp_x=kp_x, kd_x=kd_x)
    else:
        # no x control -> desire level attitude
        th_ref_fn = lambda x, T: 0.0

    uth = pd_theta_controller(kp_th=kp_th, kd_th=kd_th, theta_ref_fn=th_ref_fn)

    def u_fn(t, x):
        # altitude controller
        T_cmd   = uy(x)
        # attitude controller
        tau_cmd = uth(x, T_cmd)

        # CLAMP both T and tau here so U stores the applied inputs
        T_cmd   = clamp(T_cmd,   T_min, T_max)
        tau_cmd = clamp(tau_cmd, tau_min, tau_max)

        return np.array([T_cmd, tau_cmd])

    return u_fn

# ----------------------------
# Plotting + checks + animation
# ----------------------------
def plot_all(t, X, U, y_ref, x_ref):
    # XY trajectory
    plt.figure()
    plt.plot(X[:,0], X[:,1], label="trajectory")
    plt.scatter([X[0,0]],[X[0,1]], label="start")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title("XY trajectory")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.legend()
    plt.show()

    # Altitude tracking
    plt.figure()
    plt.plot(t, X[:,1], label="y")
    plt.plot(t, np.ones_like(t)*y_ref, linestyle="--", label="y_ref")
    plt.xlabel("time [s]")
    plt.ylabel("altitude [m]")
    plt.title("Altitude tracking")
    plt.legend()
    plt.show()

    # X tracking over time
    plt.figure()
    plt.plot(t, X[:,0], label="x")
    plt.plot(t, np.ones_like(t)*x_ref, linestyle="--", label="x_ref")
    plt.xlabel("time [s]")
    plt.ylabel("x position [m]")
    plt.title("Horizontal position tracking")
    plt.legend()
    plt.show()

    # Attitude (pitch)
    plt.figure()
    plt.plot(t, X[:,2])
    plt.xlabel("time [s]")
    plt.ylabel("theta [rad]")
    plt.title("Attitude (pitch)")
    plt.show()

    # Thrust and bounds
    plt.figure()
    plt.plot(t, U[:,0], label="T [N]")
    plt.plot(t, np.ones_like(t)*T_min, linestyle="--", label="T_min")
    plt.plot(t, np.ones_like(t)*T_max, linestyle="--", label="T_max")
    plt.xlabel("time [s]")
    plt.ylabel("thrust / bounds")
    plt.title("Input thrust and bounds")
    plt.legend()
    plt.show()

    # Torque tau over time (now guaranteed in [-0.5, 0.5])
    plt.figure()
    plt.plot(t, U[:,1], label="tau")
    plt.axhline(tau_min, linestyle="--", label="tau_min")
    plt.axhline(tau_max, linestyle="--", label="tau_max")
    plt.xlabel("time [s]")
    plt.ylabel("tau [N·m]")
    plt.title("Torque input tau over time")
    plt.legend()
    plt.show()

def rk4_convergence_check(x0, u_fn, tf=2.0, dt_ref=0.002, dt_list=(0.04, 0.02, 0.01, 0.005)):
    _, X_ref, _ = simulate(x0, u_fn, tf=tf, dt=dt_ref)
    x_ref_end = X_ref[-1]

    dts, errs = [], []
    for dt in dt_list:
        _, Xc, _ = simulate(x0, u_fn, tf=tf, dt=dt)
        dts.append(dt)
        errs.append(np.linalg.norm(Xc[-1] - x_ref_end))

    plt.figure()
    plt.loglog(dts, errs, marker='o')
    plt.gca().invert_xaxis()
    plt.xlabel("time step dt [s] (log)")
    plt.ylabel("final-state error vs reference (log)")
    plt.title("RK4 step-halving convergence")
    plt.show()

def animate_quadrotor(t, X, L=0.8, trail_len=120):
    margin = 0.8
    xmin, xmax = X[:,0].min() - margin, X[:,0].max() + margin
    ymin, ymax = min(0.0, X[:,1].min()) - margin, X[:,1].max() + margin

    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Planar quadrotor – animation")

    body_line,  = ax.plot([], [], linewidth=3)
    rotor_left,  = ax.plot([], [], marker='o')
    rotor_right, = ax.plot([], [], marker='o')
    thrust_line, = ax.plot([], [], linestyle='-')
    trail_line,  = ax.plot([], [])
    ax.axhline(0.0, linewidth=1)

    def update(k):
        x, y, th = X[k,0], X[k,1], X[k,2]
        c, s = np.cos(th), np.sin(th)
        ex = np.array([ c, s])
        ey = np.array([-s, c])

        pc = np.array([x, y])
        pL = pc - 0.5*L*ex
        pR = pc + 0.5*L*ex

        body_line.set_data([pL[0], pR[0]], [pL[1], pR[1]])
        rotor_left.set_data( [pL[0]],[pL[1]] )
        rotor_right.set_data([pR[0]],[pR[1]] )

        tip = pc + 0.4*ey
        thrust_line.set_data([pc[0], tip[0]], [pc[1], tip[1]])

        i0 = max(0, k-trail_len)
        trail_line.set_data(X[i0:k+1,0], X[i0:k+1,1])

        return body_line, rotor_left, rotor_right, thrust_line, trail_line

    anim = FuncAnimation(fig, update, frames=len(t), interval=20, blit=True)
    plt.show()
    return anim

# ----------------------------
# Run with current settings
# ----------------------------
if __name__ == "__main__":
    print(f"[CONFIG] dt={DT}, tf={TF}, yref={YREF}, xref={XREF}, xctl={XCTL}")
    print(f"[GAINS ] kpx={KPX}, kdx={KDX}, kpy={KPY}, kdy={KDY}, kp_th={KPTH}, kd_th={KDTH}")

    # initial state: [X, Y, theta, Xdot, Ydot, thetadot]
    x0 = np.array([0.0, 0.0, 0.25, 0.0, 0.0, 0.0])

    u_fn = make_controller(use_x_control=XCTL,
                           y_ref=YREF, kp_y=KPY, kd_y=KDY,
                           kp_th=KPTH, kd_th=KDTH,
                           x_ref=XREF, kp_x=KPX, kd_x=KDX)

    t, X, U = simulate(x0, u_fn, tf=TF, dt=DT)

    print("Final state:", X[-1])
    print("Final input [T, tau]:", U[-1])
    print("Tau range during simulation: min =", np.min(U[:,1]), "max =", np.max(U[:,1]))

    plot_all(t, X, U, YREF, XREF)
    rk4_convergence_check(x0, u_fn)
    animate_quadrotor(t, X)
