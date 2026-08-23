"""
Trajectory Optimization  using a cubic-splines formulation
(Hermite–Simpson / cubic Hermite spline direct collocation), solved with cyipopt (Ipopt).

    x = [q1, q2, dq1, dq2]  in R^4
    u = [u1, u2]           in R^2

    qdd = inv(M(q)) * ( u - C(q,dq)*dq + G(q) )

  with:
    g = 9.81
    m1 = m2 = 1 kg
    l1 = l2 = 0.5 m

WHAT THIS SCRIPT DOES (HIGH LEVEL):
  1) Creates decision variables at N knot points:
       {x_k, u_k} for k=0..N-1
  2) Enforces dynamics between knots via Hermite–Simpson "defect" constraints.
     This corresponds to a *cubic Hermite spline* representation of x(t).
  3) Minimizes a cost (control effort + smoothness).
  4) Solves the resulting nonlinear program (NLP) with Ipopt via cyipopt.
  5) Visualizes the resulting trajectory.
"""

import numpy as np
import cyipopt
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation


# =========================================================
# 1) TIME GRID / PROBLEM DATA 
# =========================================================

N = 101                 # number of knot points
dt = 0.05               # timestep (seconds)
T = (N - 1) * dt        # total time 

# State dimension and control dimension 
nx = 4                  # x = [q1, q2, dq1, dq2]
nu = 2                  # u = [u1, u2]

# Boundary conditions from the assignment screenshot:
x0 = np.array([0.0, 0.0, 0.0, 0.0])
xf = np.array([np.pi, 0.0, 0.0, 0.0])

# Control bounds from the assignment screenshot:
u_min = -10.0
u_max =  10.0

# Ipopt requires finite bounds. We'll use a huge number to represent "unbounded".
BIG = 1e20


# =========================================================
# 2) DOUBLE PENDULUM DYNAMICS f(x,u) EXACTLY AS IN HANDOUT
# =========================================================

# Fixed constants EXACTLY as given:
g  = 9.81
m1 = 1.0
m2 = 1.0
l1 = 0.5
l2 = 0.5


def dynamics_f(x, u):
    """
    Implements the continuous-time dynamics xdot = f(x,u) EXACTLY as in your PDF.

    STATE:
      x = [q1, q2, dq1, dq2]^T

    CONTROL:
      u = [u1, u2]^T

    HANDOUT EQUATIONS:
      Define q = [q1, q2]^T, dq = [dq1, dq2]^T

      qdd = inv(M(q)) * ( u - C(q,dq)*dq + G(q) )

      xdot = [ dq1, dq2, qdd1, qdd2 ]^T

    where M, C, G are EXACTLY the ones shown in the screenshot.
    """
    # --- unpack state and control for readability ---
    q1, q2, dq1, dq2 = x
    u1, u2 = u

    # Helpful trig terms (appear in M,C,G)
    c2 = np.cos(q2)
    s2 = np.sin(q2)

    # =====================================================
    # Build M(q) EXACTLY:
    #
    # M = [ l1^2 m1 + l2^2 m2 + l1^2 m2 + 2 l1 m2 l2 cos(q2)      l2^2 m2 + l1 m2 l2 cos(q2) ]
    #     [ l2^2 m2 + l1 m2 l2 cos(q2)                           l2^2 m2                  ]
    # =====================================================
    M11 = (l1**2)*m1 + (l2**2)*m2 + (l1**2)*m2 + 2*l1*m2*l2*c2
    M12 = (l2**2)*m2 + l1*m2*l2*c2
    M21 = M12
    M22 = (l2**2)*m2

    M = np.array([[M11, M12],
                  [M21, M22]])

    # =====================================================
    # Build C(q,dq) EXACTLY:
    #
    # C = [ -2 dq2 l1 m2 l2 sin(q2)      -dq2 l1 m2 l2 sin(q2) ]
    #     [  dq1 l1 m2 l2 sin(q2)         0                   ]
    #
    # Then the handout uses the term: C(q,dq) * dq
    # =====================================================
    C11 = -2.0 * dq2 * l1 * m2 * l2 * s2
    C12 = -1.0 * dq2 * l1 * m2 * l2 * s2
    C21 =  1.0 * dq1 * l1 * m2 * l2 * s2
    C22 =  0.0

    C = np.array([[C11, C12],
                  [C21, C22]])

    dq = np.array([dq1, dq2])

    # =====================================================
    # Build G(q) EXACTLY:
    #
    # G = [ -g m1 l1 sin(q1) - g m2 ( l1 sin(q1) + l2 sin(q1+q2) ) ]
    #     [ -g m2 l2 sin(q1+q2)                                     ]
    # =====================================================
    G1 = -g*m1*l1*np.sin(q1) - g*m2*(l1*np.sin(q1) + l2*np.sin(q1 + q2))
    G2 = -g*m2*l2*np.sin(q1 + q2)
    G  = np.array([G1, G2])

    # Control vector
    uvec = np.array([u1, u2])

    # =====================================================
    # Compute qdd from:
    #   qdd = inv(M) * ( u - C*dq + G )
    # =====================================================
    forces = uvec - (C @ dq) + G
    qdd = np.linalg.solve(M, forces)

    # =====================================================
    # Assemble state derivative:
    #   xdot = [dq1, dq2, qdd1, qdd2]
    # =====================================================
    xdot = np.array([dq1, dq2, qdd[0], qdd[1]])
    return xdot


# =========================================================
# 3) CUBIC SPLINES FORMULATION (HERMITE–SIMPSON DEFECT)
# =========================================================

def hermite_simpson_defect(xk, uk, xk1, uk1, h):
    """
    This function creates the dynamics constraint between knot k and k+1
    using Hermite–Simpson collocation.

    KEY IDEA:
      - The state trajectory x(t) on [t_k, t_{k+1}] is represented as a cubic Hermite spline.
      - That spline is defined by (xk, xk1) and endpoint derivatives (fk, fk1),
        where fk = f(xk,uk), fk1 = f(xk1,uk1).
      - We enforce the dynamics at the midpoint as well, giving a very accurate transcription.

    Standard Hermite–Simpson construction:
      fk  = f(xk,  uk)
      fk1 = f(xk1, uk1)

      uc  = (uk + uk1)/2          (piecewise linear control)
      xc  = 0.5*(xk + xk1) + h/8*(fk - fk1)   (midpoint state from cubic Hermite)

      fc  = f(xc, uc)

    Then the defect (must equal 0 for feasibility):
      defect = xk1 - xk - h/6 * ( fk + 4*fc + fk1 )

    If defect == 0, then the discrete points are consistent with a cubic spline
    that satisfies the dynamics well over the interval.
    """
    fk  = dynamics_f(xk,  uk)
    fk1 = dynamics_f(xk1, uk1)

    uc = 0.5 * (uk + uk1)
    xc = 0.5 * (xk + xk1) + (h / 8.0) * (fk - fk1)

    fc = dynamics_f(xc, uc)

    defect = xk1 - xk - (h / 6.0) * (fk + 4.0 * fc + fk1)
    return defect


# =========================================================
# 4) PACK / UNPACK DECISION VECTOR z = [X_flat, U_flat]
# =========================================================

def pack_z(X, U):
    """
    Pack state and control trajectories into a single decision vector z.

    X: shape (N, nx)  -> states at all knot points
    U: shape (N, nu)  -> controls at all knot points

    z: shape (N*nx + N*nu, )
    """
    return np.concatenate([X.reshape(-1), U.reshape(-1)])


def unpack_z(z):
    """
    Inverse of pack_z:
      z -> (X, U)
    """
    X_flat = z[:N * nx]
    U_flat = z[N * nx:]
    X = X_flat.reshape(N, nx)
    U = U_flat.reshape(N, nu)
    return X, U


# =========================================================
# 5) OBJECTIVE FUNCTION (COST) + ITS GRADIENT
# =========================================================

def objective_cost(z, R=np.diag([1.0, 1.0]), w_du=1e-2):
    """
    A common "appropriate" cost for this assignment is:

      J = integral_0^T  u(t)^T R u(t) dt   +   w_du * sum ||u_{k+1} - u_k||^2

    Why these terms?
      - u^T R u penalizes large torques (effort).
      - ||u_{k+1}-u_k||^2 penalizes rapid changes (smoothness).

    DISCRETIZATION:
      - We approximate the integral using the trapezoidal rule:
          sum_{k=0}^{N-2} (h/2) [ u_k^T R u_k + u_{k+1}^T R u_{k+1} ]
    """
    _, U = unpack_z(z)

    # --- effort term (trapezoidal quadrature) ---
    effort = 0.0
    for k in range(N - 1):
        uk  = U[k]
        uk1 = U[k + 1]
        effort += (dt / 2.0) * (uk.T @ R @ uk + uk1.T @ R @ uk1)

    # --- smoothness term ---
    smooth = 0.0
    for k in range(N - 1):
        du = U[k + 1] - U[k]
        smooth += du @ du

    return effort + w_du * smooth


def objective_grad(z, R=np.diag([1.0, 1.0]), w_du=1e-2):
    """
    Analytic gradient of the objective.

    Notes:
      - The objective depends ONLY on U (controls), not directly on X.
      - So gradient entries for X are all 0.
    """
    _, U = unpack_z(z)
    grad = np.zeros_like(z)

    # Helper to locate control component in the packed vector z
    def u_index(k, j):
        return N * nx + k * nu + j

    # ---- gradient of the effort term ----
    # Trapezoid weights: endpoints get dt/2, interior get dt
    for k in range(N):
        weight = dt
        if k == 0 or k == N - 1:
            weight = dt / 2.0

        # d/du (u^T R u) = 2 R u (for symmetric R)
        dJ_du = 2.0 * weight * (R @ U[k])

        for j in range(nu):
            grad[u_index(k, j)] += dJ_du[j]

    # ---- gradient of the smoothness term: sum ||u_{k+1}-u_k||^2 ----
    for k in range(N):
        if k == 0:
            dS = 2.0 * (U[0] - U[1])
        elif k == N - 1:
            dS = 2.0 * (U[N - 1] - U[N - 2])
        else:
            dS = 2.0 * (2.0 * U[k] - U[k - 1] - U[k + 1])

        for j in range(nu):
            grad[u_index(k, j)] += w_du * dS[j]

    return grad


# =========================================================
# 6) CONSTRAINTS g(z) = 0 (ALL HERMITE–SIMPSON DEFECTS)
# =========================================================

def constraints_g(z):
    """
    Stack all Hermite–Simpson defect constraints into one vector g(z).

    There are (N-1) intervals and each interval produces nx equations.
    So total number of equality constraints is:
      m = (N-1)*nx
    """
    X, U = unpack_z(z)

    g_list = []
    for k in range(N - 1):
        defect = hermite_simpson_defect(X[k], U[k], X[k + 1], U[k + 1], dt)
        g_list.append(defect)

    return np.concatenate(g_list)


# =========================================================
# 7) JACOBIAN SPARSITY PATTERN + FINITE-DIFFERENCE VALUES
# =========================================================

def jacobian_structure():
    """
    Return (rows, cols) indices of the nonzero Jacobian entries dg/dz.

    IMPORTANT SPARSITY FACT:
      Constraint block for interval k depends only on:
        X[k], U[k], X[k+1], U[k+1]
      So each constraint row is connected to only those variables.

    This sparsity pattern makes Ipopt much faster.
    """
    rows = []
    cols = []

    def x_col(k, i):
        return k * nx + i

    def u_col(k, j):
        return N * nx + k * nu + j

    for k in range(N - 1):
        row_base = k * nx

        affected_cols = []

        # X[k]
        for i in range(nx):
            affected_cols.append(x_col(k, i))

        # U[k]
        for j in range(nu):
            affected_cols.append(u_col(k, j))

        # X[k+1]
        for i in range(nx):
            affected_cols.append(x_col(k + 1, i))

        # U[k+1]
        for j in range(nu):
            affected_cols.append(u_col(k + 1, j))

        # Full connection between the nx constraint rows and affected cols
        for r_local in range(nx):
            r = row_base + r_local
            for c in affected_cols:
                rows.append(r)
                cols.append(c)

    return np.array(rows, dtype=int), np.array(cols, dtype=int)


def jacobian_values_fd(z, eps=1e-7):
    """
    Compute Jacobian values using finite differences (NumPy-only, no JAX).

    SPEED / LOGIC TRICK:
      A variable at knot k only affects at most TWO interval constraints:
        - interval (k-1)
        - interval k
      So we do local recomputation instead of recomputing all constraints each time.
    """
    X, U = unpack_z(z)

    # Baseline defects for all intervals:
    G0 = np.zeros((N - 1, nx))
    for k in range(N - 1):
        G0[k, :] = hermite_simpson_defect(X[k], U[k], X[k + 1], U[k + 1], dt)

    row_idx, col_idx = jacobian_structure()
    nnz = row_idx.size

    # Map (row, col) -> position index in values vector
    pos = {(row_idx[p], col_idx[p]): p for p in range(nnz)}
    values = np.zeros(nnz)

    n_vars = N * nx + N * nu

    def var_info(var_index):
        """
        Decode variable index in packed z:
          If < N*nx -> it's a state component X[k,i]
          Else      -> it's a control component U[k,j]
        """
        if var_index < N * nx:
            k = var_index // nx
            i = var_index % nx
            return ("x", k, i)
        else:
            idx2 = var_index - N * nx
            k = idx2 // nu
            j = idx2 % nu
            return ("u", k, j)

    def affected_intervals(k):
        """
        Knot k affects:
          interval k-1 (if valid)
          interval k   (if valid)
        """
        aff = []
        if 0 <= k - 1 <= N - 2:
            aff.append(k - 1)
        if 0 <= k <= N - 2:
            aff.append(k)
        return aff

    # Loop through all variables, finite-difference only the local constraint blocks
    for var in range(n_vars):
        kind, k, idx = var_info(var)
        aff_ints = affected_intervals(k)
        if not aff_ints:
            continue

        # Perturb copies
        Xp = X.copy()
        Up = U.copy()

        if kind == "x":
            Xp[k, idx] += eps
        else:
            Up[k, idx] += eps

        # Recompute only affected intervals
        for interval in aff_ints:
            g0 = G0[interval, :]
            gp = hermite_simpson_defect(Xp[interval], Up[interval],
                                        Xp[interval + 1], Up[interval + 1], dt)

            dg = (gp - g0) / eps  # finite diff for nx rows

            row_base = interval * nx
            for r_local in range(nx):
                r = row_base + r_local
                c = var
                p = pos.get((r, c), None)
                if p is not None:
                    values[p] = dg[r_local]

    return values


# =========================================================
# 8) cyipopt CALLBACK CLASS
# =========================================================

class TrajectoryOptNLP:
    """
    cyipopt expects an object that provides:
      - objective(z)
      - gradient(z)
      - constraints(z)
      - jacobianstructure()
      - jacobian(z)

    We'll use Ipopt's limited-memory Hessian approximation, so we don't provide Hessians.
    """
    def objective(self, z):
        return objective_cost(z)

    def gradient(self, z):
        return objective_grad(z)

    def constraints(self, z):
        return constraints_g(z)

    def jacobianstructure(self):
        return jacobian_structure()

    def jacobian(self, z):
        return jacobian_values_fd(z)


# =========================================================
# 9) BUILD VARIABLE BOUNDS + CONSTRAINT BOUNDS
# =========================================================

n_vars = N * nx + N * nu
m_cons = (N - 1) * nx

# Variable bounds (lb <= z <= ub)
lb = -BIG * np.ones(n_vars)
ub =  BIG * np.ones(n_vars)

# ---- Fix x0 by setting bounds equal ----
for i in range(nx):
    lb[i] = x0[i]
    ub[i] = x0[i]

# ---- Fix x_{N-1} (final state) by setting bounds equal ----
xN_start = (N - 1) * nx
for i in range(nx):
    lb[xN_start + i] = xf[i]
    ub[xN_start + i] = xf[i]

# ---- Apply control bounds for all knots ----
u_start = N * nx
for k in range(N):
    for j in range(nu):
        idx = u_start + k * nu + j
        lb[idx] = u_min
        ub[idx] = u_max

# Constraints are equality: g(z) = 0
cl = np.zeros(m_cons)
cu = np.zeros(m_cons)


# =========================================================
# 10) INITIAL GUESS (IMPORTANT FOR NLP SOLVERS)
# =========================================================

# Good simple guess:
#  - linearly interpolate states between x0 and xf
#  - zero controls
X_init = np.zeros((N, nx))
U_init = np.zeros((N, nu))

for k in range(N):
    alpha = k / (N - 1)
    X_init[k, :] = (1 - alpha) * x0 + alpha * xf

z0 = pack_z(X_init, U_init)


# =========================================================
# 11) CREATE IPOPT PROBLEM AND SOLVE
# =========================================================

problem_obj = TrajectoryOptNLP()

nlp = cyipopt.Problem(
    n=n_vars,
    m=m_cons,
    problem_obj=problem_obj,
    lb=lb, ub=ub,
    cl=cl, cu=cu
)

# Ipopt options (tune if needed)
nlp.add_option("print_level", 5)
nlp.add_option("max_iter", 2000)
nlp.add_option("tol", 1e-6)

# Use quasi-Newton approximation (we didn't implement Hessians)
nlp.add_option("hessian_approximation", "limited-memory")

# Solve the NLP
z_sol, info = nlp.solve(z0)

print("\n=== IPOPT STATUS ===")
print("status:", info.get("status"))
print("objective:", info.get("obj_val"))

# Unpack solution into trajectories
X_sol, U_sol = unpack_z(z_sol)

# EXTRA (useful sanity prints):
# - max defect: should be near 0 if dynamics constraints are satisfied well
# - max |u|: should be <= 10 because of bounds
g_sol = constraints_g(z_sol)
print("max |defect|:", np.max(np.abs(g_sol)))
print("max |u|:", np.max(np.abs(U_sol)))


# =========================================================
# 12) OPTIONAL: SMOOTH RECONSTRUCTION FOR PLOTTING (CUBIC HERMITE)
# =========================================================

def hermite_spline_eval(xk, fk, xk1, fk1, h, s):
    """
    Evaluate cubic Hermite spline on interval [k, k+1] at normalized time s in [0,1].

    Formula (vector-valued):
      x(s) = h00(s) xk + h10(s) (h fk) + h01(s) xk1 + h11(s) (h fk1)

    where fk  = f(xk,uk)  is derivative at left endpoint
          fk1 = f(xk1,uk1) is derivative at right endpoint
    """
    h00 = 2*s**3 - 3*s**2 + 1
    h10 = s**3 - 2*s**2 + s
    h01 = -2*s**3 + 3*s**2
    h11 = s**3 - s**2
    return h00*xk + h10*(h*fk) + h01*xk1 + h11*(h*fk1)


# Dense time grid for prettier plots
M = 1000
t_fine = np.linspace(0.0, T, M)
X_fine = np.zeros((M, nx))
U_fine = np.zeros((M, nu))

for idx_t, t in enumerate(t_fine):
    k = int(np.floor(t / dt))
    if k >= N - 1:
        k = N - 2

    t0 = k * dt
    s = (t - t0) / dt

    xk  = X_sol[k]
    xk1 = X_sol[k + 1]
    uk  = U_sol[k]
    uk1 = U_sol[k + 1]

    fk  = dynamics_f(xk,  uk)
    fk1 = dynamics_f(xk1, uk1)

    # Smooth cubic state
    X_fine[idx_t] = hermite_spline_eval(xk, fk, xk1, fk1, dt, s)

    # Simple piecewise-linear control interpolation
    U_fine[idx_t] = (1 - s) * uk + s * uk1


# =========================================================
# 13) VISUALIZATION
# =========================================================


plt.close("all")

print("Creating 5 figures: angles, velocities, controls, XY end-effector path, and LIVE animation...")

# Figure 1: angles vs time
plt.figure(1)
plt.plot(t_fine, X_fine[:, 0], label="q1(t)")
plt.plot(t_fine, X_fine[:, 1], label="q2(t)")
plt.xlabel("time [s]")
plt.ylabel("angle [rad]")
plt.title("Figure 1: Double pendulum angles (smooth cubic Hermite reconstruction)")
plt.grid(True)
plt.legend()

# Figure 2: angular velocities vs time
plt.figure(2)
plt.plot(t_fine, X_fine[:, 2], label="dq1(t)")
plt.plot(t_fine, X_fine[:, 3], label="dq2(t)")
plt.xlabel("time [s]")
plt.ylabel("angular velocity [rad/s]")
plt.title("Figure 2: Double pendulum velocities (smooth cubic Hermite reconstruction)")
plt.grid(True)
plt.legend()

# Figure 3: controls vs time
plt.figure(3)
plt.plot(t_fine, U_fine[:, 0], label="u1(t)")
plt.plot(t_fine, U_fine[:, 1], label="u2(t)")
plt.xlabel("time [s]")
plt.ylabel("torque [Nm]")
plt.title("Figure 3: Control inputs (piecewise linear interpolation)")
plt.grid(True)
plt.legend()

# =========================================================
# Figure 4 (NEW): "trajectory" in XY space (end-effector path)
# =========================================================
# For a double pendulum, a very intuitive visualization of the trajectory is the
# path traced by the tip of the second link (end-effector) in the plane.
#
# Using forward kinematics (common convention):
#   x1 = l1*sin(q1),         y1 = -l1*cos(q1)
#   x2 = x1 + l2*sin(q1+q2), y2 = y1 - l2*cos(q1+q2)
#
# NOTE: If your course defines angles from a different axis, this plot may be
# rotated/flipped — but it still shows the motion path clearly.

q1_traj = X_fine[:, 0]
q2_traj = X_fine[:, 1]

x1 = l1 * np.sin(q1_traj)
y1 = -l1 * np.cos(q1_traj)

x2 = x1 + l2 * np.sin(q1_traj + q2_traj)
y2 = y1 - l2 * np.cos(q1_traj + q2_traj)

plt.figure(4)
plt.plot(x2, y2, label="end-effector path (link-2 tip)")
plt.scatter([x2[0]], [y2[0]], marker="o", label="start")
plt.scatter([x2[-1]], [y2[-1]], marker="x", label="end")
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.title("Figure 4: Resulting trajectory in XY space (end-effector path)")
plt.grid(True)
plt.axis("equal")  # keep aspect ratio so the path shape is not distorted
plt.legend()

# =========================================================
# Figure 5 (NEW): LIVE ANIMATION of the double pendulum
# =========================================================
# We animate the two links in the plane using the same forward kinematics:
#   Joint 0 is at (0,0)
#   Joint 1 is at (x1,y1)
#   Tip (end effector) is at (x2,y2)

fig5, ax5 = plt.subplots(num=5)
ax5.set_title("Figure 5: Live animation of the double pendulum (optimal trajectory)")
ax5.set_xlabel("x [m]")
ax5.set_ylabel("y [m]")
ax5.grid(True)
ax5.set_aspect("equal", adjustable="box")

# Plot limits: maximum reach is l1+l2
reach = l1 + l2
ax5.set_xlim(-reach - 0.1, reach + 0.1)
ax5.set_ylim(-reach - 0.1, reach + 0.1)

# Line objects for links and a trace of the tip
link_line, = ax5.plot([], [], linewidth=3, label="links")
tip_trace, = ax5.plot([], [], linewidth=1, label="tip trace")
time_text = ax5.text(0.02, 0.95, "", transform=ax5.transAxes)

ax5.legend(loc="upper right")

# Store trace points
trace_x = []
trace_y = []

# To keep animation smooth on slower machines, you can skip frames:
frame_skip = 2  # show every 2nd point of the dense grid

def init_anim():
    """Initialize animation artists."""
    link_line.set_data([], [])
    tip_trace.set_data([], [])
    time_text.set_text("")
    trace_x.clear()
    trace_y.clear()
    return link_line, tip_trace, time_text

def update_anim(frame_idx):
    """
    Update function called by FuncAnimation.
    frame_idx is an index into the animation frames.
    """
    i = frame_idx * frame_skip
    if i >= M:
        i = M - 1

    q1 = X_fine[i, 0]
    q2 = X_fine[i, 1]

    # Forward kinematics
    x1 = l1 * np.sin(q1)
    y1 = -l1 * np.cos(q1)
    x2 = x1 + l2 * np.sin(q1 + q2)
    y2 = y1 - l2 * np.cos(q1 + q2)

    # Links: (0,0) -> (x1,y1) -> (x2,y2)
    link_line.set_data([0.0, x1, x2], [0.0, y1, y2])

    # Trace tip
    trace_x.append(x2)
    trace_y.append(y2)
    tip_trace.set_data(trace_x, trace_y)

    # Time display
    time_text.set_text(f"t = {t_fine[i]:.2f} s")

    return link_line, tip_trace, time_text

# Number of animation frames
n_frames = int(np.ceil(M / frame_skip))

# interval is in milliseconds
anim = FuncAnimation(
    fig5,
    update_anim,
    frames=n_frames,
    init_func=init_anim,
    interval=dt * 1000 * frame_skip,  # approx real-time
    blit=True
)

plt.show()
