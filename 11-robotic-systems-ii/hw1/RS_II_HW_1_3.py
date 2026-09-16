
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, Slider

# --------------------------- QP SOLVER ---------------------------

def nullspace_via_svd(A, tol=None):
    M, N = A.shape
    if M == 0:
        return np.eye(N)
    U, S, Vt = np.linalg.svd(A, full_matrices=True)
    if tol is None:
        tol = max(A.shape) * (np.max(S) if S.size else 0.0) * np.finfo(float).eps
    rank = int(np.sum(S > tol))
    return Vt[rank:].T  # (N, N-rank)

def particular_solution_eq(A, b, tol=1e-10):
    if A.shape[0] == 0:
        return np.zeros(A.shape[1])
    x_p, *_ = np.linalg.lstsq(A, b, rcond=None)
    if np.linalg.norm(A @ x_p - b) > tol:
        raise ValueError("Equalities A x = b appear inconsistent.")
    return x_p

def project_nonnegative(v):
    return np.maximum(v, 0.0)

def spd_solve(H, rhs):
    # Try Cholesky; if it fails (nearly singular / not SPD), add tiny ridge and solve
    try:
        R = np.linalg.cholesky(H)
        return np.linalg.solve(R, np.linalg.solve(R.T, rhs))
    except np.linalg.LinAlgError:
        return np.linalg.solve(H + 1e-10*np.eye(H.shape[0]), rhs)

def phase1_hinge_check(C, d, iters=200, step=1e-1, backtrack=0.5, tol=1e-8):
    """
    Feasibility probe for Cz <= d by minimizing 0.5||(Cz - d)_+||^2 via gradient descent with backtracking.
    Robust init so J0 is always defined (no UnboundLocalError).
    """
    P, N = C.shape
    z = np.zeros(N)
    r = C @ z - d
    J0 = 0.5 * np.dot(np.maximum(r, 0.0), np.maximum(r, 0.0))
    for _ in range(iters):
        pos = (r > 0.0).astype(float)
        grad = C.T @ (pos * r)
        gnorm = np.linalg.norm(grad)
        if gnorm < tol or J0 < tol:
            break
        t = step
        while True:
            z_new = z - t*grad
            r_new = C @ z_new - d
            J_new = 0.5 * np.dot(np.maximum(r_new, 0.0), np.maximum(r_new, 0.0))
            if J_new <= J0 - 1e-4*t*gnorm**2 or t < 1e-12:
                z, r, J0 = z_new, r_new, J_new
                break
            t *= backtrack
    return z, float(J0)

def alm_inequalities_only(Qz, qz, Cz, dz,
                          rho=1.0, max_iter=3000, eps_feas=1e-6, eps_stat=1e-6,
                          beta=0.8, delta=1e-8, alpha=1.7,
                          rho_adjust_period=5, rho_balance_ratio=10.0,
                          rho_growth=2.0, rho_shrink=0.5, rho_min=1e-6, rho_max=1e10,
                          use_relative_stop=True, verbose=False):
    """
    Minimize 1/2 z^T Qz z + qz^T z  s.t. Cz z <= dz
    ALM with slacks s>=0: Cz z + s = dz.
    Tricks: damped slack (beta), ridge (delta), over-relaxed duals (alpha), adaptive rho.
    """
    N = Qz.shape[0]; P = Cz.shape[0]
    z = np.zeros(N)
    s = project_nonnegative(dz - Cz @ z)
    mu = np.zeros(P)
    CT = Cz.T
    z_prev = z.copy()
    converged = False

    for k in range(max_iter):
        # (1) damped slack
        s_uncon = dz - Cz @ z - mu / max(rho, 1e-30)
        s = project_nonnegative(beta*s_uncon + (1-beta)*s)

        # (2) z-step
        H = Qz + rho*(CT @ Cz) + delta*np.eye(N)
        rhs = -qz - CT @ (mu - rho*(dz - s))
        z_prev[:] = z
        z = spd_solve(H, rhs)

        # (3) dual ascent (over-relax z)
        z_bar = alpha*z + (1-alpha)*z_prev if alpha != 1.0 else z
        mu = project_nonnegative(mu + rho*(Cz @ z_bar + s - dz))

        # (4) residuals
        r_ineq = np.linalg.norm(Cz @ z + s - dz, np.inf)
        r_stat = np.linalg.norm(Qz @ z + qz + CT @ mu, np.inf)

        abs_ok = (r_ineq <= eps_feas) and (r_stat <= eps_stat)
        if use_relative_stop:
            r_ineq_rel = r_ineq / (1.0 + np.linalg.norm(dz, np.inf))
            scale_stat = 1.0 + max(np.linalg.norm(qz, np.inf), np.linalg.norm(Qz @ z, np.inf))
            r_stat_rel = r_stat / scale_stat
            rel_ok = (r_ineq_rel <= 10*eps_feas) and (r_stat_rel <= 10*eps_stat)
        else:
            rel_ok = True

        if abs_ok and rel_ok:
            converged = True
            break

        # (5) adaptive rho
        if rho_adjust_period and ((k+1) % rho_adjust_period == 0):
            rp, rd = r_ineq, r_stat
            rho_new = rho
            if rp > rho_balance_ratio * rd:
                rho_new = min(rho * rho_growth, rho_max)
            elif rd > rho_balance_ratio * rp:
                rho_new = max(rho * rho_shrink, rho_min)
            if rho_new != rho:
                mu = project_nonnegative(mu * min(1.0, np.sqrt(rho_new / rho)))
                rho = rho_new

        if verbose:
            print(f"[it {k:4d}] r_ineq={r_ineq:.3e} r_stat={r_stat:.3e} rho={rho:.1e}")

    report = {
        'converged': converged,
        'iters': k + 1,
        'rho_final': rho,
        'r_ineq': float(r_ineq),
        'r_stat': float(r_stat),
        'r_comp': float(np.linalg.norm(mu*s, np.inf)) if P else 0.0
    }
    return {'z': z, 's': s, 'mu': mu, 'rho': rho, 'iters': k + 1, 'history': {}, 'report': report}

def solve_qp_with_elimination(Q, q, A=None, b=None, C=None, d=None,
                              rho=1.0, max_iter=3000, eps_feas=1e-6, eps_stat=1e-6,
                              beta=0.8, delta=1e-8, alpha=1.7,
                              rho_adjust_period=5, rho_balance_ratio=10.0,
                              rho_growth=2.0, rho_shrink=0.5, rho_min=1e-6, rho_max=1e10,
                              use_relative_stop=True, verbose=False,
                              do_phase1=False, phase1_tol=1e-8):
    Q = np.asarray(Q, float); q = np.asarray(q, float).reshape(-1); n = Q.shape[0]
    if A is None or b is None: A = np.zeros((0,n)); b = np.zeros(0)
    else: A = np.asarray(A,float); b = np.asarray(b,float).reshape(-1)
    if C is None or d is None: C = np.zeros((0,n)); d = np.zeros(0)
    else: C = np.asarray(C,float); d = np.asarray(d,float).reshape(-1)

    x_p = particular_solution_eq(A, b, 1e-10)
    N = nullspace_via_svd(A); rdim = N.shape[1]

    if rdim == 0:
        viol = C @ x_p - d
        if np.max(viol) <= 1e-8:
            return {'x': x_p, 's': project_nonnegative(d - C @ x_p), 'mu': None,
                    'rho': rho, 'iters': 0, 'history': {}, 'report':
                    {'converged': True, 'iters': 0, 'rho_final': rho, 'r_eq': 0.0,
                     'r_ineq': float(np.max(np.abs(viol + np.maximum(viol,0.0)))),
                     'r_pr': float(np.max(np.maximum(viol,0.0))),
                     'r_stat': float(np.linalg.norm(Q @ x_p + q, np.inf)),
                     'r_comp': 0.0}}
        raise ValueError("Equalities fix x uniquely but inequalities are violated ⇒ infeasible.")

    # Reduced problem
    Qz = N.T @ Q @ N
    qz = N.T @ (Q @ x_p + q)
    Cz = C @ N
    dz = d - C @ x_p

    if do_phase1 and Cz.shape[0] > 0:
        _, J_feas = phase1_hinge_check(Cz, dz, iters=300, step=1e-1, backtrack=0.5, tol=phase1_tol)
        if J_feas > 1e-6:
            print("[Phase-I] Warning: hinge loss ~", J_feas)

    rz = alm_inequalities_only(Qz, qz, Cz, dz, rho, max_iter, eps_feas, eps_stat,
                               beta, delta, alpha, rho_adjust_period, rho_balance_ratio,
                               rho_growth, rho_shrink, rho_min, rho_max, use_relative_stop, verbose)
    z = rz['z']; x = x_p + N @ z
    s = project_nonnegative(d - C @ x)
    return {'x': x, 's': s, 'mu': rz['mu'], 'rho': rz['rho'],
            'iters': rz['iters'], 'history': rz['history'], 'report': rz['report']}

# ---------------------------  setup ---------------------------

g = 9.81
m = 5.0

# Sinusoidal references
Ax, fx, phix, xoff = 0.35, 0.25, 0.0, 0.00
Ay, fy, phiy, yoff = 0.20, 0.50, np.pi/2, 1.00

# PD gains (initial values; can be changed live by sliders)
Kp_x, Kd_x = 40.0, 12.0
Kp_y, Kd_y = 60.0, 18.0

# Weights in the QP cost
w_ax, w_ay  = 50.0, 50.0
w_f,  w_tau = 1e-4, 1e-4

# Bounds
a_max_x = 25.0; a_max_y = 25.0
f_min, f_max     = 0.0, 500.0
tau_min, tau_max = -200.0, 200.0

# Sim horizon (dt will be adjustable)
dt, T = 0.01, 12.0
K = int(np.round(T/dt))

x0 = np.array([0.0, 1.0, 0.0, 0.0])
PERTURB = 0.0

# ---------- references and feed-forward ----------
two_pi = 2*np.pi
def ref_xy(t):
    xref  = xoff + Ax*np.sin(two_pi*fx*t + phix)
    vxref = Ax*(two_pi*fx)*np.cos(two_pi*fx*t + phix)
    axref = -Ax*(two_pi*fx)**2*np.sin(two_pi*fx*t + phix)
    yref  = yoff + Ay*np.sin(two_pi*fy*t + phiy)
    vyref = Ay*(two_pi*fy)*np.cos(two_pi*fy*t + phiy)
    ayref = -Ay*(two_pi*fy)**2*np.sin(two_pi*fy*t + phiy)
    return xref, vxref, axref, yref, vyref, ayref

def pd_accel_targets(x_state, t):
    x, y, vx, vy = x_state
    xr, vxr, axr, yr, vyr, ayr = ref_xy(t)
    # Use the (possibly live-updated) global gains
    ax_des = axr + Kp_x*(xr - x) + Kd_x*(vxr - vx)
    ay_des = ayr + Kp_y*(yr - y) + Kd_y*(vyr - vy)
    return np.array([ax_des, ay_des])

def unit_r(x_pos, y_pos, eps=1e-12):
    L = np.hypot(x_pos, y_pos)
    if L < eps:
        return np.array([1.0, 0.0])  # arbitrary when at origin
    return np.array([x_pos/L, y_pos/L])

# ---------- QP per-step ----------
def solve_one_step_qp(x_state, t, qp_verbose=False):
    rx, ry = unit_r(x_state[0], x_state[1])

    # Quadratic cost on [ax, ay, f, tau]
    Q = np.diag([w_ax, w_ay, w_f, w_tau])

    a_des = pd_accel_targets(x_state, t)
    q = np.array([-w_ax*a_des[0], -w_ay*a_des[1], 0.0, 0.0])

    # Linear dynamics equalities:
    # m*[ax, ay]^T = f*[rx,ry]^T + tau*[-ry, rx]^T + [0, -m g]^T
    Aeq = np.array([[1.0, 0.0, -(rx/m),  (ry/m)],
                    [0.0, 1.0, -(ry/m), -(rx/m)]])
    beq = np.array([0.0, -g])

    # Box constraints as inequalities: C z <= d
    rows, rhs = [], []
    rows += [[0,0, 1,0],[0,0,-1,0]];             rhs += [f_max, -f_min]
    rows += [[0,0, 0,1],[0,0, 0,-1]];            rhs += [tau_max, -tau_min]
    if a_max_x is not None: rows += [[ 1,0,0,0],[-1,0,0,0]]; rhs += [a_max_x, a_max_x]
    if a_max_y is not None: rows += [[0, 1,0,0],[0,-1,0,0]]; rhs += [a_max_y, a_max_y]
    C = np.asarray(rows,float); d = np.asarray(rhs,float)

    res = solve_qp_with_elimination(Q, q, Aeq, beq, C, d,
                                    rho=1.0, max_iter=4000, eps_feas=1e-8, eps_stat=1e-8,
                                    beta=0.8, delta=1e-8, alpha=1.7,
                                    rho_adjust_period=5, rho_balance_ratio=10.0,
                                    rho_growth=2.0, rho_shrink=0.5,
                                    verbose=qp_verbose, do_phase1=False)  # realtime: skip Phase-I
    return res["x"], res  # x = [ax, ay, f, tau]

# --------------------------- Integrators ---------------------------

def f_rhs(s, a):
    x,y,vx,vy = s; axc,ayc = a
    return np.array([vx, vy, axc, ayc])

def step_euler(s, a, h):
    return s + h*f_rhs(s,a)

def step_semi_implicit(s, a, h):
    x,y,vx,vy = s; axc,ayc = a
    vx1, vy1 = vx+axc*h, vy+ayc*h
    return np.array([x+vx1*h, y+vy1*h, vx1, vy1])

def step_midpoint(s, a, h):
    k1=f_rhs(s,a); k2=f_rhs(s+0.5*h*k1,a)
    return s + h*k2

def step_rk4(s, a, h):
    k1=f_rhs(s,a)
    k2=f_rhs(s+0.5*h*k1,a)
    k3=f_rhs(s+0.5*h*k2,a)
    k4=f_rhs(s+h*k3,a)
    return s + (h/6.0)*(k1+2*k2+2*k3+k4)

INTEGRATORS = {"Euler":step_euler, "Semi-Implicit":step_semi_implicit, "Midpoint":step_midpoint, "RK4":step_rk4}

MAX_COMPARE_STEPS = 6000       # hard cap on steps during compare
DECIMATE_TARGET_POINTS = 2000  # reduce points per curve if very dense

def simulate_batch_from(state0, t0, methods, dt_use, steps):
    """Run all integrators offline from (state0,t0) for 'steps' with same dt/gains."""
    results = {}
    for name in methods:
        s = state0.copy()
        t = t0
        hist = np.empty((steps, 9))  # (t, x, y, vx, vy, ax, ay, f, tau)
        for k in range(steps):
            z,_ = solve_one_step_qp(s, t)
            axc, ayc, f, tau = z
            s = INTEGRATORS[name](s, np.array([axc,ayc]), dt_use)
            t += dt_use
            hist[k] = (t, s[0], s[1], s[2], s[3], axc, ayc, f, tau)
        results[name] = hist
    return results

def compute_metrics(H):
    """Simple metrics for a history array H."""
    t = H[:,0]; x = H[:,1]; y = H[:,2]
    xr = np.array([ref_xy(tt)[0] for tt in t])
    yr = np.array([ref_xy(tt)[3] for tt in t])
    ex, ey = xr - x, yr - y
    rmse_x = np.sqrt(np.mean(ex**2))
    rmse_y = np.sqrt(np.mean(ey**2))
    max_ex = np.max(np.abs(ex))
    max_ey = np.max(np.abs(ey))
    u_energy = np.trapz(H[:,7]**2 + H[:,8]**2, t)  # ∫(f^2+tau^2) dt
    return dict(rmse_x=rmse_x, rmse_y=rmse_y, max_ex=max_ex, max_ey=max_ey, effort=u_energy)

def decimate(H, target_points=DECIMATE_TARGET_POINTS):
    """Reduce number of plotted points for speed; keep endpoints."""
    n = H.shape[0]
    if n <= target_points:
        return H
    step = int(np.ceil(n / target_points))
    return H[::step]

# --------------------------- Simulator ---------------------------

class QPSim:
    def __init__(self, dt, K):
        self.dt, self.K = dt, K
        self.reset()
    def reset(self):
        self.t=0.0; self.k=0; self.state=x0.copy()
        if PERTURB: self.state += np.array([0,0,PERTURB,PERTURB])
        self.hist=[]
    def step(self, method_name):
        z,_ = solve_one_step_qp(self.state, self.t); axc,ayc,f,tau = z
        self.state = INTEGRATORS[method_name](self.state, np.array([axc,ayc]), self.dt)
        self.t += self.dt; self.k += 1; self.hist.append((self.t,*self.state,axc,ayc,f,tau))
        return self.state, z
    def simulate_offline(self, method_name):
        self.reset()
        for _ in range(self.K):
            self.step(method_name)
        return np.array(self.hist)

# --------------------------- Visualization with dt + gain sliders ---------------------------

def run_anim():
    sim = QPSim(dt, K); method={"name":"RK4"}

    fig = plt.figure(figsize=(12,6))
    ax_anim = plt.subplot2grid((2,3),(0,0),colspan=2,rowspan=2)
    ax_xy   = plt.subplot2grid((2,3),(0,2))
    ax_u    = plt.subplot2grid((2,3),(1,2))

    ax_anim.axhline(0,color="k",lw=1)
    ax_anim.set_xlim(-1.2,1.2); ax_anim.set_ylim(-0.2,1.8); ax_anim.set_aspect("equal")
    ax_anim.set_title("QP-controlled mass (Start/Stop/Reset; choose integrator)")
    (trail_line,) = ax_anim.plot([],[],lw=1.5)
    mass = plt.Circle((x0[0],x0[1]),0.05,fc="C0",ec="k"); ax_anim.add_patch(mass)

    ax_xy.set_title("positions vs refs"); ax_xy.set_xlabel("time [s]"); ax_xy.set_ylabel("x,y [m]")
    line_x, = ax_xy.plot([],[],label="x"); line_y, = ax_xy.plot([],[],label="y")
    refx,   = ax_xy.plot([],[],"--",label="x_ref"); refy, = ax_xy.plot([],[],"--",label="y_ref")
    ax_xy.legend(loc="upper right"); ax_xy.grid(True)

    ax_u.set_title("inputs"); ax_u.set_xlabel("time [s]"); ax_u.set_ylabel("f [N], tau [Nm]")
    line_f, = ax_u.plot([],[],label="f"); line_ta, = ax_u.plot([],[],label="tau")
    ax_u.legend(loc="upper right"); ax_u.grid(True)

    # Buttons & radio
    ax_start=plt.axes([0.10,0.92,0.08,0.05]); ax_stop=plt.axes([0.20,0.92,0.08,0.05])
    ax_reset=plt.axes([0.30,0.92,0.08,0.05]); ax_comp=plt.axes([0.40,0.92,0.12,0.05])
    ax_radio=plt.axes([0.86,0.58,0.12,0.20])
    btn_start=Button(ax_start,"Start"); btn_stop=Button(ax_stop,"Stop")
    btn_reset=Button(ax_reset,"Reset"); btn_comp=Button(ax_comp,"Compare")
    radio=RadioButtons(ax_radio, list(INTEGRATORS.keys()),
                       active=list(INTEGRATORS.keys()).index(method["name"]))

    # dt slider
    ax_dt = plt.axes([0.86, 0.52, 0.12, 0.03])
    s_dt  = Slider(ax_dt, 'dt', 0.002, 0.05, valinit=sim.dt, valstep=0.001)

    # --- gain sliders (live) ---
    ax_kpx = plt.axes([0.10, 0.03, 0.20, 0.03])
    ax_kdx = plt.axes([0.10, 0.00, 0.20, 0.03])
    ax_kpy = plt.axes([0.40, 0.03, 0.20, 0.03])
    ax_kdy = plt.axes([0.40, 0.00, 0.20, 0.03])
    s_kpx = Slider(ax_kpx, 'Kp_x', 0.0, 150.0, valinit=Kp_x, valstep=0.5)
    s_kdx = Slider(ax_kdx, 'Kd_x', 0.0,  60.0, valinit=Kd_x, valstep=0.5)
    s_kpy = Slider(ax_kpy, 'Kp_y', 0.0, 200.0, valinit=Kp_y, valstep=0.5)
    s_kdy = Slider(ax_kdy, 'Kd_y', 0.0,  80.0, valinit=Kd_y, valstep=0.5)

    running={"flag":False}; trail={"x":[], "y":[]}

    def on_start(_): running["flag"]=True
    def on_stop(_):  running["flag"]=False
    def on_reset(_):
        running["flag"]=False; sim.reset(); trail["x"].clear(); trail["y"].clear()
        line_x.set_data([],[]); line_y.set_data([],[]); refx.set_data([],[]); refy.set_data([],[])
        line_f.set_data([],[]);  line_ta.set_data([],[]); trail_line.set_data([],[])
        mass.center=(x0[0],x0[1]); fig.canvas.draw_idle()
    def on_radio(lbl): method["name"]=lbl; on_reset(None)

    
    def on_compare(_):
        # Pause animation so we don't contend for 'sim'
        was_running = running["flag"]; running["flag"] = False

        # Snapshot current state/time and current sliders/gains
        state_snapshot = sim.state.copy()
        t_snapshot = sim.t
        dt_use = sim.dt
        steps = min(sim.K - sim.k, MAX_COMPARE_STEPS)
        if steps <= 5:
            # too short: extend to full horizon from scratch for fairer look
            state_snapshot = x0.copy(); t_snapshot = 0.0; steps = min(sim.K, MAX_COMPARE_STEPS)

        methods = list(INTEGRATORS.keys())

        # Batch run (no side-effects on the live sim)
        results = simulate_batch_from(state_snapshot, t_snapshot, methods, dt_use, steps)

        # Compute metrics
        metrics = {name: compute_metrics(H) for name, H in results.items()}

        # Plot
        fig2, axs = plt.subplots(1, 2, figsize=(12, 4))
        ax_traj, ax_time = axs

        # (a) x–y trajectories
        for name in methods:
            H = decimate(results[name])
            ax_traj.plot(H[:,1], H[:,2], label=name)
        ax_traj.set_title("Trajectories (x vs y)")
        ax_traj.set_xlabel("x [m]"); ax_traj.set_ylabel("y [m]"); ax_traj.grid(True)
        ax_traj.legend()

        # (b) time-series: refs + positions + errors
        # choose one method as reference for time stamps (all share same dt/length)
        H0 = decimate(results[methods[0]])
        t = H0[:,0]
        xr = np.array([ref_xy(tt)[0] for tt in t])
        yr = np.array([ref_xy(tt)[3] for tt in t])
        ax_time.plot(t, xr, '--', label='x_ref')
        ax_time.plot(t, yr, '--', label='y_ref')
        for name in methods:
            H = decimate(results[name])
            ax_time.plot(t, H[:,1], label=f'x ({name})', alpha=0.9)
            ax_time.plot(t, H[:,2], label=f'y ({name})', alpha=0.9)
        ax_time.set_title("Signals (x,y) vs refs")
        ax_time.set_xlabel("time [s]"); ax_time.set_ylabel("[m]"); ax_time.grid(True)
        ax_time.legend(ncol=2, fontsize=8)

        # Add a small text box with metrics
        txt = []
        for name in methods:
            m = metrics[name]
            txt.append(f"{name}: RMSE(x)={m['rmse_x']:.3f}, RMSE(y)={m['rmse_y']:.3f}, "
                       f"max|ex|={m['max_ex']:.3f}, max|ey|={m['max_ey']:.3f}, "
                       f"∫(f²+τ²)dt={m['effort']:.2f}")
        fig2.text(0.5, 0.02, "\n".join(txt), ha='center', va='bottom', fontsize=9)

        fig2.tight_layout(rect=[0,0.05,1,1])
        fig2.show()

        # Restore run state (do not reset sim; user continues from where they paused)
        running["flag"] = was_running

    def on_dt(val):
        new_dt = float(val)
        sim.dt = new_dt
        sim.K  = int(np.round(T / new_dt))
        on_reset(None)

    # Live update handlers for gains — no reset needed; next step uses them
    def on_kpx(val):
        global Kp_x; Kp_x = float(val)
    def on_kdx(val):
        global Kd_x; Kd_x = float(val)
    def on_kpy(val):
        global Kp_y; Kp_y = float(val)
    def on_kdy(val):
        global Kd_y; Kd_y = float(val)

    btn_start.on_clicked(on_start); btn_stop.on_clicked(on_stop)
    btn_reset.on_clicked(on_reset); btn_comp.on_clicked(on_compare)
    radio.on_clicked(on_radio)
    s_dt.on_changed(on_dt)
    s_kpx.on_changed(on_kpx); s_kdx.on_changed(on_kdx)
    s_kpy.on_changed(on_kpy); s_kdy.on_changed(on_kdy)

    def animate(_):
        if not running["flag"] or sim.k >= sim.K:
            return trail_line, mass, line_x, line_y, refx, refy, line_f, line_ta
        state, z = sim.step(method["name"])
        x,y,_,_ = state; axc,ayc,f,tau = z
        trail["x"].append(x); trail["y"].append(y); trail_line.set_data(trail["x"], trail["y"])
        mass.center=(x,y)
        H=np.array(sim.hist); t=H[:,0]
        line_x.set_data(t,H[:,1]); line_y.set_data(t,H[:,2])
        line_f.set_data(t,H[:,7]); line_ta.set_data(t,H[:,8])
        xr=[ref_xy(tt)[0] for tt in t]; yr=[ref_xy(tt)[3] for tt in t]
        refx.set_data(t,xr); refy.set_data(t,yr)
        ax_xy.relim(); ax_xy.autoscale_view(); ax_u.relim(); ax_u.autoscale_view()
        return trail_line, mass, line_x, line_y, refx, refy, line_f, line_ta

    # keep a reference and bound caching (suppresses warnings)
    anim = FuncAnimation(fig, animate, interval=max(15,int(1000*sim.dt)),
                         cache_frame_data=False, save_count=sim.K)
    plt.show()

# --------------------------- Main ---------------------------
if __name__ == "__main__":
    print("Section 3 – all-in-one. Choose integrator, then Start. Adjust dt and gains live.")
    run_anim()
