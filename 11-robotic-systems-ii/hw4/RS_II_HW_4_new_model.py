"""
======================================================================================

WHAT THIS ONE FILE DOES
-----------------------
This script is a *single self-contained* file (no other scripts needed).

It contains:
  (A) The exact double pendulum dynamics from Parts 1-2.
  (B) A Part-2 style trajectory optimization (Hermite-Simpson direct collocation)
      solved by cyipopt, to produce a nominal trajectory (x_bar[k], u_bar[k]).
  (C) A Part-3 Time-Varying LQR (TVLQR) tracking controller built by:
      1) building a discrete-time model f_discrete using RK4
      2) linearizing f_discrete around (x_bar[k], u_bar[k]) -> A_k, B_k
      3) running a finite-horizon Riccati recursion -> K_k
      4) constructing a *smooth* K(t) using kernel regression (Nadaraya-Watson),
         so we don't apply a crude "piecewise constant list of K matrices" directly.



It also includes:
  - A visible slider that controls observation noise sigma_obs
  - Multiple plots that update when you move the slider
  - A Monte-Carlo "success vs noise" curve (computed once at startup)
  - A live animation: "true" vs "nominal at k_ref"


"""

# =========================
# 0) IMPORTS (ONLY THESE)
# =========================

import numpy as np                              
import matplotlib.pyplot as plt                 
from matplotlib.animation import FuncAnimation  
from matplotlib.widgets import Slider           


# ===============================================================
# 1) DOUBLE PENDULUM MODEL 
# ===============================================================

# -----------------------------
# Physical / model parameters
# -----------------------------
motors = [403, 379]  

mass = [0.10548177618443695, 0.076197443620415454]          # [m1, m2]
length = [0.05, 0.05]                                       # [l1, l2] (link lengths for geometry)
com = [0.05, 0.03670036749567022]                           # [r1, r2] (COM distances)
inertia = [0.00046166221821039165, 0.00023702395072092597]  # [I1, I2]
damping = [7.634058385430087e-12, 0.0005106535523065844]    # [b1, b2]
coulomb_fric = [0.00305, 0.0007777]                         # [mu1, mu2]
gravity = 9.81
torque_limit = [0.15, 0.15]                                 # provided (not enforced everywhere; rest of script unchanged)

# Unpack into scalar names used throughout the script
g = float(gravity)

m1 = float(mass[0])
m2 = float(mass[1])

l1 = float(length[0])
l2 = float(length[1])

r1 = float(com[0])
r2 = float(com[1])

I1 = float(inertia[0])
I2 = float(inertia[1])

b1 = float(damping[0])
b2 = float(damping[1])

mu1 = float(coulomb_fric[0])
mu2 = float(coulomb_fric[1])


g_r = 1.0      # gear ratio 
I_r = 0.0      # rotor inertia 


def dynamics(x, u):
    """
    Continuous-time dynamics of the double pendulum.

    State:
        x = [q1, q2, q1_dot, q2_dot]^T
    Input:
        u = [u1, u2]^T

    Returns:
        x_dot = [q1_dot, q2_dot, q1_ddot, q2_ddot]^T

    UPDATED MODEL (matches your screenshot):
        M(q) qdd + C(q,qd) qd + G(q) + F(qd) = tau

    with:
      - M as in your matrix (includes I1,I2, l1^2 m2, and cos(q2) coupling)
      - C as in your matrix (uses l1*m2*r2*sin(q2) coupling)
      - G as in your vector (negative signs exactly as shown)
      - F as in your vector (viscous + coulomb modeled via arctan(100*qd))
    """
    # Convert inputs to numpy arrays (ensures math works even if lists are passed)
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)

    # Unpack state components (angles and angular velocities)
    q1, q2, q1_dot, q2_dot = x

    # Unpack control torques
    u1, u2 = u

    # Bundle angles and velocities into 2-vectors (handy for matrix formulas)
    q     = np.array([q1, q2], dtype=float)
    q_dot = np.array([q1_dot, q2_dot], dtype=float)

    # Handy trig
    s1  = np.sin(q1)
    s2  = np.sin(q2)
    c2  = np.cos(q2)
    s12 = np.sin(q1 + q2)

    # Common coupling scalar that appears everywhere in your new model
    a = l1 * m2 * r2

    # ----- Mass / inertia matrix M(q) (MATCHES YOUR SCREENSHOT) -----
    # M = [[ I1 + I2 + l1^2*m2 + 2*l1*m2*r2*cos(q2) + g_r^2*I_r + I_r,   I2 + l1*m2*r2*cos(q2) ],
    #      [ I2 + l1*m2*r2*cos(q2),                                      I2                         ]]
    M11 = I1 + I2 + (l1**2) * m2 + 2.0 * a * c2 + (g_r**2) * I_r + I_r
    M12 = I2 + a * c2
    M21 = M12
    M22 = I2

    M = np.array([[M11, M12],
                  [M21, M22]], dtype=float)

    # ----- Coriolis / centrifugal matrix C(q, q_dot) (MATCHES YOUR SCREENSHOT) -----
    # C = [[-2*q2_dot*l1*m2*r2*sin(q2),  -q2_dot*l1*m2*r2*sin(q2)],
    #      [ q1_dot*l1*m2*r2*sin(q2),     0                       ]]
    C11 = -2.0 * q2_dot * a * s2
    C12 = -1.0 * q2_dot * a * s2
    C21 =  1.0 * q1_dot * a * s2
    C22 =  0.0

    C = np.array([[C11, C12],
                  [C21, C22]], dtype=float)

    # ----- Gravity vector G(q) (MATCHES YOUR SCREENSHOT; note negative signs) -----
    # G = [ -g*m1*r1*sin(q1) - g*m2*( l1*sin(q1) + r2*sin(q1+q2) ),
    #       -g*m2*r2*sin(q1+q2) ]
    G1 = -g * m1 * r1 * s1 - g * m2 * (l1 * s1 + r2 * s12)
    G2 = -g * m2 * r2 * s12
    G = np.array([G1, G2], dtype=float)

    # ----- Friction term F(q_dot) (MATCHES YOUR SCREENSHOT FORM) -----
    # F = [ b1*q1_dot + mu*atan(100*q1_dot),
    #       b2*q2_dot + mu*atan(100*q2_dot) ]
    # (Your parameter list provides mu1, mu2, so we apply per-joint Coulomb strength.)
    F1 = b1 * q1_dot + mu1 * np.arctan(100.0 * q1_dot)
    F2 = b2 * q2_dot + mu2 * np.arctan(100.0 * q2_dot)
    F = np.array([F1, F2], dtype=float)

    # Compute accelerations from:
    #   M q_ddot + C q_dot + G + F = tau
    # -> M q_ddot = tau - C q_dot - G - F
    tau = np.array([u1, u2], dtype=float)
    rhs = tau - C @ q_dot - G - F

    # Solve linear system for q_ddot without explicitly inverting M
    q_ddot = np.linalg.solve(M, rhs)

    # Assemble state derivative x_dot
    x_dot = np.array([q1_dot, q2_dot, q_ddot[0], q_ddot[1]], dtype=float)
    return x_dot


def rk4_step(x, u, dt):
    """
    One RK4 integration step: x_{next} = x(t+dt) approx.

    We treat u constant over the small interval dt.

    RK4:
      k1 = f(x, u)
      k2 = f(x + dt/2*k1, u)
      k3 = f(x + dt/2*k2, u)
      k4 = f(x + dt*k3, u)
      x_next = x + dt/6 * (k1 + 2k2 + 2k3 + k4)
    """
    # Ensure numpy types
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)

    # Compute RK4 slopes
    k1 = dynamics(x,               u)
    k2 = dynamics(x + 0.5*dt*k1,   u)
    k3 = dynamics(x + 0.5*dt*k2,   u)
    k4 = dynamics(x + dt*k3,       u)

    # Combine slopes to get next state
    x_next = x + (dt/6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
    return x_next


# ===============================================================
# 2) DISCRETE-TIME MODEL f_discrete (IMPORTANT FOR TVLQR)
# ===============================================================

def f_discrete(xk, uk, dt_nom):
    """
    Discrete-time dynamics map: x_{k+1} = f_discrete(x_k, u_k)

    HOW WE GET IT:
      - We have continuous-time ODE: x_dot = f(x,u)
      - To use discrete-time LQR/TVLQR, we need a discrete map.
      - We define f_discrete by one RK4 step over dt_nom:

            x_{k+1} := RK4_step(x_k, u_k, dt_nom)
    """
    return rk4_step(xk, uk, dt_nom)


# ===============================================================
# 3) PART-2 TRAJECTORY OPTIMIZATION (TO GET x_bar, u_bar)
# ===============================================================

def generate_nominal_with_ipopt():
    """
    Generates a nominal trajectory (x_bar[k], u_bar[k]) using a direct collocation NLP.

    Returns:
      t_nom: shape (N,)
      X_nom: shape (N, 4)
      U_nom: shape (N, 2)
      dt_nom: scalar

    NOTE:
      This requires cyipopt. If cyipopt is not installed, this cannot run.
    """
    # Import cyipopt only here (so the rest of file works even if missing)
    try:
        import cyipopt
    except Exception as e:
        raise RuntimeError(
            "cyipopt is required to generate the nominal inside this script.\n"
            "Install it (e.g., conda-forge) and try again.\n"
            f"Import error was: {e}"
        )

    # ==============
    # NLP SETTINGS
    # ==============

    N = 401              # more knot points
    dt_nom = 0.05           # nominal time step (seconds)
    T = (N - 1) * dt_nom    # nominal horizon (seconds) ~ 12s

    nx = 4                  # state dimension
    nu = 2                  # control dimension

    # Boundary conditions
    xf= np.array([0.0, 0.0, 0.0, 0.0], dtype=float)
    x0 = np.array([-np.pi, 0.0, 0.0, 0.0], dtype=float)

    # ------------------------------------------------------------
    # Torque bounds: use your declared torque_limit (per-joint)
    # ------------------------------------------------------------
    u_min = 3
    u_max = 3
    BIG = 1e20  # large bound for "unbounded" state variables

    # ---------------------------
    # Helper: pack/unpack z
    # ---------------------------

    def pack_z(X, U):
        # Flatten and concatenate into one long vector for Ipopt
        return np.concatenate([X.reshape(-1), U.reshape(-1)])

    def unpack_z(z):
        # Split back into X and U arrays
        X_flat = z[:N * nx]
        U_flat = z[N * nx:]
        X = X_flat.reshape(N, nx)
        U = U_flat.reshape(N, nu)
        return X, U

    # ---------------------------
    # Hermite-Simpson defect
    # ---------------------------

    def hermite_simpson_defect(xk, uk, xk1, uk1, h):
        fk  = dynamics(xk,  uk)
        fk1 = dynamics(xk1, uk1)

        uc = 0.5 * (uk + uk1)
        xc = 0.5 * (xk + xk1) + (h / 8.0) * (fk - fk1)

        fc = dynamics(xc, uc)

        defect = xk1 - xk - (h / 6.0) * (fk + 4.0 * fc + fk1)
        return defect

    # ---------------------------
    # Objective + gradient
    # ---------------------------

    # With small torque bounds, we want VERY smooth controls.
    R = np.diag([3.0, 3.0])  # stronger torque penalty than before
    w_du = 5e-2              # stronger smoothness weight

    def objective_cost(z):
        _, U = unpack_z(z)

        effort = 0.0
        # trapezoidal integral of u^T R u
        for k in range(N - 1):
            uk  = U[k]
            uk1 = U[k + 1]
            effort += (dt_nom / 2.0) * (uk.T @ R @ uk + uk1.T @ R @ uk1)

        smooth = 0.0
        for k in range(N - 1):
            du = U[k + 1] - U[k]
            smooth += du @ du

        return effort + w_du * smooth

    def objective_grad(z):
        _, U = unpack_z(z)
        grad = np.zeros_like(z)

        def u_index(k, j):
            return N * nx + k * nu + j

        # effort gradient
        for k in range(N):
            weight = dt_nom
            if k == 0 or k == N - 1:
                weight = dt_nom / 2.0
            dJ_du = 2.0 * weight * (R @ U[k])
            for j in range(nu):
                grad[u_index(k, j)] += dJ_du[j]

        # smoothness gradient
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

    # ---------------------------
    # Constraints g(z)=0
    # ---------------------------

    def constraints_g(z):
        X, U = unpack_z(z)
        g_list = []
        for k in range(N - 1):
            g_list.append(hermite_simpson_defect(X[k], U[k], X[k + 1], U[k + 1], dt_nom))
        return np.concatenate(g_list)

    # ---------------------------
    # Jacobian sparsity structure
    # ---------------------------

    def jacobian_structure():
        rows = []
        cols = []

        def x_col(k, i):
            return k * nx + i

        def u_col(k, j):
            return N * nx + k * nu + j

        for k in range(N - 1):
            row_base = k * nx

            affected = []

            for i in range(nx):
                affected.append(x_col(k, i))
            for j in range(nu):
                affected.append(u_col(k, j))
            for i in range(nx):
                affected.append(x_col(k + 1, i))
            for j in range(nu):
                affected.append(u_col(k + 1, j))

            for r_local in range(nx):
                r = row_base + r_local
                for c in affected:
                    rows.append(r)
                    cols.append(c)

        return np.array(rows, dtype=int), np.array(cols, dtype=int)

    # ---------------------------
    # Jacobian values via local finite differences
    # ---------------------------

    def jacobian_values_fd(z, eps=1e-7):
        X, U = unpack_z(z)

        # baseline defects
        G0 = np.zeros((N - 1, nx), dtype=float)
        for k in range(N - 1):
            G0[k] = hermite_simpson_defect(X[k], U[k], X[k + 1], U[k + 1], dt_nom)

        row_idx, col_idx = jacobian_structure()
        nnz = row_idx.size

        pos = {(row_idx[p], col_idx[p]): p for p in range(nnz)}
        values = np.zeros(nnz, dtype=float)

        n_vars = N * nx + N * nu

        def var_info(var_index):
            if var_index < N * nx:
                kk = var_index // nx
                ii = var_index % nx
                return ("x", kk, ii)
            else:
                idx2 = var_index - N * nx
                kk = idx2 // nu
                jj = idx2 % nu
                return ("u", kk, jj)

        def affected_intervals(knot_index):
            aff = []
            if 0 <= knot_index - 1 <= N - 2:
                aff.append(knot_index - 1)
            if 0 <= knot_index <= N - 2:
                aff.append(knot_index)
            return aff

        for var in range(n_vars):
            kind, kk, idx = var_info(var)
            aff_ints = affected_intervals(kk)
            if not aff_ints:
                continue

            Xp = X.copy()
            Up = U.copy()

            if kind == "x":
                Xp[kk, idx] += eps
            else:
                Up[kk, idx] += eps

            for interval in aff_ints:
                g0 = G0[interval]
                gp = hermite_simpson_defect(Xp[interval], Up[interval],
                                            Xp[interval + 1], Up[interval + 1], dt_nom)
                dg = (gp - g0) / eps

                row_base = interval * nx
                for r_local in range(nx):
                    r = row_base + r_local
                    c = var
                    p = pos.get((r, c), None)
                    if p is not None:
                        values[p] = dg[r_local]

        return values

    # ---------------------------
    # cyipopt callback object
    # ---------------------------

    class TrajectoryOptNLP:
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

    # ---------------------------
    # Build bounds
    # ---------------------------

    n_vars = N * nx + N * nu
    m_cons = (N - 1) * nx

    lb = -BIG * np.ones(n_vars, dtype=float)
    ub =  BIG * np.ones(n_vars, dtype=float)

    # Fix x0
    for i in range(nx):
        lb[i] = x0[i]
        ub[i] = x0[i]

    # Fix xN
    xN_start = (N - 1) * nx
    for i in range(nx):
        lb[xN_start + i] = xf[i]
        ub[xN_start + i] = xf[i]

    # Control bounds (per joint)
    u_start = N * nx
    for k in range(N):
        for j in range(nu):
            idx = u_start + k * nu + j
            lb[idx] = u_min[j]
            ub[idx] = u_max[j]

    cl = np.zeros(m_cons, dtype=float)
    cu = np.zeros(m_cons, dtype=float)

    # ---------------------------
    # Initial guess 
    # ---------------------------

    # We create a smooth angle ramp 0 -> pi, q2 -> 0, velocities 0,
    # and choose U_init to roughly compensate gravity along that path.
    X_init = np.zeros((N, nx), dtype=float)
    U_init = np.zeros((N, nu), dtype=float)

    for k in range(N):
        alpha = k / (N - 1)

        # smooth ramp
        q1g = (1 - alpha) * x0[0] + alpha * xf[0]
        q2g = 0.0
        X_init[k] = np.array([q1g, q2g, 0.0, 0.0], dtype=float)

        # gravity compensation guess (tau ≈ G(q) for static hold)
        q1 = q1g
        q2 = q2g
        s1  = np.sin(q1)
        s12 = np.sin(q1 + q2)

        # G(q) from your model (already has negative sign convention)
        G1 = -g * m1 * r1 * s1 - g * m2 * (l1 * s1 + r2 * s12)
        G2 = -g * m2 * r2 * s12
        ug = np.array([G1, G2], dtype=float)

        # clamp to realistic bounds
        ug = np.minimum(np.maximum(ug, u_min), u_max)
        U_init[k] = ug

    z0 = pack_z(X_init, U_init)

    # ---------------------------
    # Solve NLP
    # ---------------------------

    nlp = cyipopt.Problem(
        n=n_vars,
        m=m_cons,
        problem_obj=TrajectoryOptNLP(),
        lb=lb, ub=ub,
        cl=cl, cu=cu
    )

    nlp.add_option("print_level", 5)
    nlp.add_option("max_iter", 200)
    nlp.add_option("tol", 1e-6)
    nlp.add_option("hessian_approximation", "limited-memory")

    z_sol, info = nlp.solve(z0)

    X_sol, U_sol = unpack_z(z_sol)
    t_nom = np.linspace(0.0, T, N)

    return t_nom, X_sol, U_sol, dt_nom


def load_or_build_nominal(npz_name="nominal_from_part2.npz"):
    """
    Tries to load nominal trajectory from npz.
    If missing, generates nominal using IPOPT inside this script and saves it.

    Returns:
      t_nom, X_nom, U_nom, dt_nom
    """
    try:
        data = np.load(npz_name)
        t_nom = data["t_nom"]
        X_nom = data["X_nom"]
        U_nom = data["U_nom"]
        dt_nom = float(data["dt_nom"])
        print(f"Loaded nominal from '{npz_name}'.")
        return t_nom, X_nom, U_nom, dt_nom
    except Exception as e:
        print(f"WARNING: Could not load {npz_name}.")
        print(f"Reason: {e}")
        print("Generating nominal INSIDE this script using cyipopt (Part 2 embedded)...")

        t_nom, X_nom, U_nom, dt_nom = generate_nominal_with_ipopt()
        np.savez(npz_name, t_nom=t_nom, X_nom=X_nom, U_nom=U_nom, dt_nom=dt_nom)

        print(f"Saved nominal to '{npz_name}' for future runs.")
        return t_nom, X_nom, U_nom, dt_nom


 # ===============================================================
# 4) LINEARIZATION: compute A_k, B_k of f_discrete (ANALYTIC, NO FD)
# ===============================================================

def continuous_jacobians_analytic(x, u):
    """
    Analytic continuous-time Jacobians of the dynamics:

        x_dot = f(x, u)

    where x = [q1, q2, q1_dot, q2_dot], u = [u1, u2].

    Returns:
        A_c = df/dx  (4x4)
        B_c = df/du  (4x2)

    UPDATED MODEL (matches your screenshot):
        M(q) qdd + C(q,qd) qd + G(q) + F(qd) = tau
      -> qdd = M(q)^{-1} [ tau - C(q,qd) qd - G(q) - F(qd) ]

    and using the identity for y = M^{-1} rhs:
        dy = M^{-1} ( drhs - dM * y )

    so for any scalar parameter p:
        ∂qdd/∂p = M^{-1} ( ∂rhs/∂p - (∂M/∂p) qdd )
    """
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)

    q1, q2, q1_dot, q2_dot = x
    u1, u2 = u

    # Handy trig
    s1  = np.sin(q1)
    c1  = np.cos(q1)
    s2  = np.sin(q2)
    c2  = np.cos(q2)
    s12 = np.sin(q1 + q2)
    c12 = np.cos(q1 + q2)

    # Common coupling scalar from your model
    a = l1 * m2 * r2

    # -----------------------------
    # Rebuild M(q), C(q,qd), G(q), F(qd)
    # (must match dynamics() exactly)
    # -----------------------------
    M11 = I1 + I2 + (l1**2) * m2 + 2.0 * a * c2 + (g_r**2) * I_r + I_r
    M12 = I2 + a * c2
    M21 = M12
    M22 = I2
    M = np.array([[M11, M12],
                  [M21, M22]], dtype=float)

    C11 = -2.0 * q2_dot * a * s2
    C12 = -1.0 * q2_dot * a * s2
    C21 =  1.0 * q1_dot * a * s2
    C22 =  0.0
    C = np.array([[C11, C12],
                  [C21, C22]], dtype=float)

    G1 = -g * m1 * r1 * s1 - g * m2 * (l1 * s1 + r2 * s12)
    G2 = -g * m2 * r2 * s12
    G = np.array([G1, G2], dtype=float)

    F1 = b1 * q1_dot + mu1 * np.arctan(100.0 * q1_dot)
    F2 = b2 * q2_dot + mu2 * np.arctan(100.0 * q2_dot)
    F = np.array([F1, F2], dtype=float)

    qd  = np.array([q1_dot, q2_dot], dtype=float)
    tau = np.array([u1, u2], dtype=float)

    # rhs = tau - C qd - G - F
    rhs = tau - C @ qd - G - F
    qdd = np.linalg.solve(M, rhs)  # nominal acceleration

    # Inverse of M via solve (numerically stable)
    Minv = np.linalg.solve(M, np.eye(2))

    # -----------------------------
    # Derivatives of M wrt q1,q2
    # -----------------------------
    # M depends ONLY on q2 through cos(q2)
    dM_dq1 = np.zeros((2, 2), dtype=float)
    dM_dq2 = np.array([
        [-2.0 * a * s2,  -1.0 * a * s2],
        [-1.0 * a * s2,   0.0]
    ], dtype=float)

    # -----------------------------
    # Derivatives of C wrt q2, q1_dot, q2_dot
    # -----------------------------
    dC_dq2 = np.array([
        [-2.0 * q2_dot * a * c2,  -1.0 * q2_dot * a * c2],
        [ 1.0 * q1_dot * a * c2,   0.0]
    ], dtype=float)

    dC_dq1dot = np.array([
        [0.0, 0.0],
        [a * s2, 0.0]
    ], dtype=float)

    dC_dq2dot = np.array([
        [-2.0 * a * s2,  -1.0 * a * s2],
        [ 0.0,            0.0]
    ], dtype=float)

    # -----------------------------
    # Derivatives of G wrt q1,q2
    # -----------------------------
    dG1_dq1 = -g * m1 * r1 * c1 - g * m2 * (l1 * c1 + r2 * c12)
    dG1_dq2 = -g * m2 * (r2 * c12)
    dG2_dq1 = -g * m2 * r2 * c12
    dG2_dq2 = -g * m2 * r2 * c12

    dG_dq1 = np.array([dG1_dq1, dG2_dq1], dtype=float)
    dG_dq2 = np.array([dG1_dq2, dG2_dq2], dtype=float)

    # -----------------------------
    # Derivatives of F wrt q1_dot, q2_dot
    # -----------------------------
    # d/dx atan(100x) = 100 / (1 + (100x)^2)
    dF1_dq1dot = b1 + mu1 * (100.0 / (1.0 + (100.0 * q1_dot) ** 2))
    dF2_dq2dot = b2 + mu2 * (100.0 / (1.0 + (100.0 * q2_dot) ** 2))

    dF_dq1dot = np.array([dF1_dq1dot, 0.0], dtype=float)
    dF_dq2dot = np.array([0.0, dF2_dq2dot], dtype=float)

    # -----------------------------
    # Build drhs/d(state components)
    # rhs = tau - C(q,qd) qd - G(q) - F(qd)
    # -----------------------------
    # wrt q1: only -G contributes
    drhs_dq1 = -dG_dq1

    # wrt q2: -(dC/dq2) qd  - dG/dq2
    drhs_dq2 = -(dC_dq2 @ qd) - dG_dq2

    # wrt q1_dot:
    # d[-C qd]/d(q1_dot) = -(dC/dq1_dot) qd - C[:,0]
    # and -F adds -dF/d(q1_dot)
    drhs_dq1dot = -(dC_dq1dot @ qd) - C[:, 0] - dF_dq1dot

    # wrt q2_dot similarly + friction term on joint 2
    drhs_dq2dot = -(dC_dq2dot @ qd) - C[:, 1] - dF_dq2dot

    # -----------------------------
    # Convert drhs -> dqdd via:
    #   dqdd = M^{-1} ( drhs - dM * qdd )
    # -----------------------------
    dqdd_dq1    = np.linalg.solve(M, drhs_dq1    - dM_dq1 @ qdd)
    dqdd_dq2    = np.linalg.solve(M, drhs_dq2    - dM_dq2 @ qdd)
    dqdd_dq1dot = np.linalg.solve(M, drhs_dq1dot - np.zeros((2, 2)) @ qdd)
    dqdd_dq2dot = np.linalg.solve(M, drhs_dq2dot - np.zeros((2, 2)) @ qdd)

    # -----------------------------
    # Assemble continuous-time Jacobians
    # x_dot = [q1_dot, q2_dot, qdd1, qdd2]
    # -----------------------------
    A_c = np.zeros((4, 4), dtype=float)
    B_c = np.zeros((4, 2), dtype=float)

    # dq1_dot/dx
    A_c[0, 2] = 1.0
    # dq2_dot/dx
    A_c[1, 3] = 1.0

    # qdd rows
    A_c[2:, 0] = dqdd_dq1
    A_c[2:, 1] = dqdd_dq2
    A_c[2:, 2] = dqdd_dq1dot
    A_c[2:, 3] = dqdd_dq2dot

    # df/du: only accelerations depend on u, and ∂qdd/∂u = M^{-1}
    B_c[2:, :] = Minv

    return A_c, B_c


def linearize_discrete_fd(x_bar, u_bar, dt_nom, eps=1e-6):
    """
    Analytic linearization of the discrete RK4 map:
        x_{k+1} = f_discrete(x_k, u_k)

    We want:
        A = df_discrete/dx evaluated at (x_bar, u_bar)
        B = df_discrete/du evaluated at (x_bar, u_bar)

   
    Dimensions:
        x in R^4, u in R^2
        A is 4x4, B is 4x2
    """
    x_bar = np.asarray(x_bar, dtype=float)
    u_bar = np.asarray(u_bar, dtype=float)

    nx = x_bar.size
    nu = u_bar.size

    I = np.eye(nx, dtype=float)
    dt = float(dt_nom)

    # -----------------------------
    # RK4 stages (same as rk4_step)
    # -----------------------------
    x1 = x_bar
    k1 = dynamics(x1, u_bar)
    A1, B1 = continuous_jacobians_analytic(x1, u_bar)

    # Sensitivities of k1
    dk1_dx = A1
    dk1_du = B1

    # Stage 2
    x2 = x_bar + 0.5 * dt * k1
    dx2_dx = I + 0.5 * dt * dk1_dx
    dx2_du =      0.5 * dt * dk1_du

    k2 = dynamics(x2, u_bar)
    A2, B2 = continuous_jacobians_analytic(x2, u_bar)

    dk2_dx = A2 @ dx2_dx
    dk2_du = A2 @ dx2_du + B2

    # Stage 3
    x3 = x_bar + 0.5 * dt * k2
    dx3_dx = I + 0.5 * dt * dk2_dx
    dx3_du =      0.5 * dt * dk2_du

    k3 = dynamics(x3, u_bar)
    A3, B3 = continuous_jacobians_analytic(x3, u_bar)

    dk3_dx = A3 @ dx3_dx
    dk3_du = A3 @ dx3_du + B3

    # Stage 4
    x4 = x_bar + dt * k3
    dx4_dx = I + dt * dk3_dx
    dx4_du =     dt * dk3_du

    k4 = dynamics(x4, u_bar)
    A4, B4 = continuous_jacobians_analytic(x4, u_bar)

    dk4_dx = A4 @ dx4_dx
    dk4_du = A4 @ dx4_du + B4

    # Final RK4 combine:
    # x_next = x + dt/6 * (k1 + 2k2 + 2k3 + k4)
    A = I + (dt / 6.0) * (dk1_dx + 2.0 * dk2_dx + 2.0 * dk3_dx + dk4_dx)
    B =      (dt / 6.0) * (dk1_du + 2.0 * dk2_du + 2.0 * dk3_du + dk4_du)

    return A, B


# ===============================================================
# 5) DISCRETE-TIME TVLQR (finite horizon) via Riccati recursion
# ===============================================================

def tvlqr_discrete(A_list, B_list, Q, R, Qf):
    """
    Finite-horizon discrete-time TVLQR.

    We assume linearized error dynamics:
        dx_{k+1} = A_k dx_k + B_k du_k

    and quadratic cost:
        sum_{k=0}^{N-2} ( dx_k^T Q dx_k + du_k^T R du_k ) + dx_{N-1}^T Qf dx_{N-1}

    Output:
      K_list: list of feedback gains K_k (each is 2x4)
      P_list: list of Riccati matrices P_k (each is 4x4)

    IMPORTANT:
      The control law in tracking form will be:
        u_k = u_bar[k] - K_k (x_k - x_bar[k])
    """
    N = len(A_list) + 1

    P_list = [None] * N
    K_list = [None] * (N - 1)

    # Terminal condition
    P_list[N - 1] = Qf.copy()

    # Backward recursion
    for k in reversed(range(N - 1)):
        Ak = A_list[k]
        Bk = B_list[k]
        Pn = P_list[k + 1]

        S = R + Bk.T @ Pn @ Bk
        Kk = np.linalg.solve(S, (Bk.T @ Pn @ Ak))

        Pk = Q + Ak.T @ Pn @ Ak - Ak.T @ Pn @ Bk @ Kk

        K_list[k] = Kk
        P_list[k] = Pk

    return K_list, P_list


# ===============================================================
# 6) "SMOOTH" K(t) using Kernel Regression
# ===============================================================

def gaussian_kernel(z):
    """Simple Gaussian kernel K(z) = exp(-0.5 z^2)."""
    return np.exp(-0.5 * z * z)


def smooth_gain_kernel_regression(t_query, t_samples, K_samples, bandwidth):
    """
    Kernel regression  to get a smooth K(t_query).

    We treat K as a vector in R^(nu*nx). We flatten each matrix K_k to a vector.

    Formula:
      K(t) = sum_i w_i(t) K_i / sum_i w_i(t),
      with weights w_i(t) = exp( -0.5 * ((t - t_i)/h)^2 ).
    """
    t_samples = np.asarray(t_samples, dtype=float)

    # Flatten all K matrices into vectors so we can average them
    K_flat = np.array([K.reshape(-1) for K in K_samples], dtype=float)

    # Compute normalized distance to each sample time
    z = (t_query - t_samples) / float(bandwidth)

    # Compute weights with Gaussian kernel
    w = gaussian_kernel(z)

    # Avoid division by zero
    w_sum = np.sum(w) + 1e-12

    # Weighted average
    K_avg_flat = (w[:, None] * K_flat).sum(axis=0) / w_sum

    # Reshape back to matrix
    nu_nx = K_samples[0].shape
    return K_avg_flat.reshape(nu_nx)


def make_smooth_K_of_t(t_nom, K_list, dt_nom):
    """
    Build a callable K_of_t(t) that returns a smooth gain matrix K(t).
    """
    t_samples = t_nom[:-1]
    h = 2.0 * dt_nom

    def K_of_t(t):
        if t <= t_samples[0]:
            return K_list[0]
        if t >= t_samples[-1]:
            return K_list[-1]
        return smooth_gain_kernel_regression(t, t_samples, K_list, bandwidth=h)

    return K_of_t


# ===============================================================
# 7) PROJECTION ("progress chooser") utilities
# ===============================================================

def weighted_state_distance(x, X_nom, W):
    """
    Compute weighted distance from x to each X_nom[k]:
       d_k^2 = (x - X_nom[k])^T W (x - X_nom[k])
    """
    dx = X_nom - x[None, :]
    d2 = np.einsum("ni,ij,nj->n", dx, W, dx)
    return d2


def pick_progress_farthest_inside_tube(x, X_nom, W, tube_radius):
    """
    Projection progress rule ("farthest inside the tube"):

    1) compute distance of x to each nominal knot
    2) pick the LARGEST index that is inside the tube
    3) if none are inside -> pick closest knot

    Returns:
      k_ref (int), dist_to_ref (float)
    """
    d2 = weighted_state_distance(x, X_nom, W)
    d = np.sqrt(np.maximum(d2, 0.0))

    inside = np.where(d <= tube_radius)[0]
    if inside.size > 0:
        k_ref = int(inside[-1])
    else:
        k_ref = int(np.argmin(d))

    return k_ref, float(d[k_ref])


# ===============================================================
# 8) CLOSED-LOOP SIMULATION (PROJ TVLQR) WITH OBSERVATION NOISE
# ===============================================================

def total_energy_true(x):
    """
    Rough mechanical energy (kinetic + potential) of the true system.
    """
    q1, q2, q1d, q2d = x

    a = l1 * m2 * r2
    c2 = np.cos(q2)

    # New-model M(q)
    M11 = I1 + I2 + (l1**2) * m2 + 2.0 * a * c2 + (g_r**2) * I_r + I_r
    M12 = I2 + a * c2
    M22 = I2
    M = np.array([[M11, M12],
                  [M12, M22]], dtype=float)

    qd = np.array([q1d, q2d], dtype=float)
    T = 0.5 * (qd.T @ M @ qd)

    # Heights of COMs (consistent with your gravity vector form)
    y1 = r1 * np.cos(q1)
    y2 = l1 * np.cos(q1) + r2 * np.cos(q1 + q2)
    V = m1 * g * y1 + m2 * g * y2

    return float(T + V)


def simulate_closed_loop_proj_tvlqr_with_noise(
    x0, T, dt_sim, dt_ctrl,
    t_nom, X_nom, U_nom, K_of_t,
    Wproj, tube_radius, u_clip,
    sigma_obs, seed=0
):
    """
    Closed-loop simulation where:

      - True state x evolves with RK4 steps of dt_sim.
      - Controller updates every dt_ctrl (ZOH between updates).
      - Controller sees a noisy measurement at control update times:
            x_hat = x_true + noise,   noise ~ N(0, sigma_obs^2 I)
      - PROJECTION chooses k_ref based on x_hat:
            k_ref = farthest nominal index inside a tube around x_hat
      - Control law:
            u = u_bar[k_ref] - K(t_ref) ( x_hat - x_bar[k_ref] )
        where t_ref = t_nom[k_ref] and K(t_ref) is from kernel regression.

    Returns:
      t_grid, x_true_traj, x_hat_traj, u_traj,
      k_ref_hist, dist_hist, sat_frac_hist, energy_hist
    """
    rng = np.random.default_rng(seed)

    x0 = np.asarray(x0, dtype=float)
    N = int(np.round(T / dt_sim))
    t_grid = np.linspace(0.0, N*dt_sim, N+1)

    x_true = x0.copy()

    x_true_traj = np.zeros((N+1, 4), dtype=float)
    x_hat_traj  = np.zeros((N+1, 4), dtype=float)
    u_traj      = np.zeros((N+1, 2), dtype=float)

    k_ref_hist  = np.zeros(N+1, dtype=int)
    dist_hist   = np.zeros(N+1, dtype=float)

    sat_frac_hist = np.zeros(N+1, dtype=float)
    energy_hist   = np.zeros(N+1, dtype=float)

    x_true_traj[0] = x_true
    energy_hist[0] = total_energy_true(x_true)

    u_hold = np.zeros(2, dtype=float)
    x_hat = x_true.copy()
    next_ctrl_time = 0.0

    k_ref, d_ref = pick_progress_farthest_inside_tube(x_hat, X_nom, Wproj, tube_radius)
    k_ref_hist[0] = k_ref
    dist_hist[0]  = d_ref
    x_hat_traj[0] = x_hat

    for k in range(N):
        t = t_grid[k]

        # -------------------------------------------------------
        # Controller update (every dt_ctrl seconds)
        # -------------------------------------------------------
        if t >= next_ctrl_time - 1e-12:
            # New noisy observation at control update time
            x_hat = x_true + rng.normal(0.0, sigma_obs, size=4)

            # Projection: pick which nominal knot we should track
            k_ref, d_ref = pick_progress_farthest_inside_tube(x_hat, X_nom, Wproj, tube_radius)

            # Reference values at that knot
            x_bar = X_nom[k_ref]
            u_bar = U_nom[k_ref]
            t_ref = t_nom[k_ref]

            # Smooth gain at that (reference) time
            Kt = K_of_t(t_ref)

            # TVLQR tracking control
            u = u_bar - Kt @ (x_hat - x_bar)

            # Torque clipping (very important: matches assignment bounds)
            u = np.clip(u, -u_clip, u_clip)

            # Hold this control until next ctrl update
            u_hold = u

            next_ctrl_time += dt_ctrl

        # -------------------------------------------------------
        # True system evolution with RK4 at dt_sim
        # (controller is ZOH between dt_ctrl updates)
        # -------------------------------------------------------
        x_true = rk4_step(x_true, u_hold, dt_sim)

        # Safety guard against blow-up
        if np.linalg.norm(x_true) > 1e3 or np.any(~np.isfinite(x_true)):
            x_true_traj[k+1:] = np.nan
            x_hat_traj[k+1:]  = np.nan
            u_traj[k+1:]      = np.nan
            k_ref_hist[k+1:]  = k_ref_hist[k]
            dist_hist[k+1:]   = dist_hist[k]
            sat_frac_hist[k+1:] = sat_frac_hist[k]
            energy_hist[k+1:]   = energy_hist[k]
            break

        x_true_traj[k+1] = x_true
        x_hat_traj[k+1]  = x_hat
        u_traj[k]        = u_hold

        k_ref_hist[k+1] = k_ref

        # Distance logged based on TRUE state vs chosen nominal (easier to interpret)
        dx_true = x_true - X_nom[k_ref]
        dist_hist[k+1] = float(np.sqrt(dx_true.T @ Wproj @ dx_true))

        # Saturation fraction:
        sat1 = (abs(u_hold[0]) >= (u_clip - 1e-9))
        sat2 = (abs(u_hold[1]) >= (u_clip - 1e-9))
        sat_frac_hist[k+1] = 0.5*float(sat1) + 0.5*float(sat2)

        # Energy diagnostic
        energy_hist[k+1] = total_energy_true(x_true)

    u_traj[-1] = u_traj[-2]
    return (t_grid, x_true_traj, x_hat_traj, u_traj,
            k_ref_hist, dist_hist, sat_frac_hist, energy_hist)


def success_metric(x_true_traj, X_nom, angle_tol=0.25, vel_tol=0.5):
    """
    Decide if the run is "successful" (simple criterion).
    """
    if np.any(np.isnan(x_true_traj)):
        return False

    x_final = x_true_traj[-1]
    x_goal  = X_nom[-1]

    q_err  = np.linalg.norm(x_final[:2] - x_goal[:2])
    dq_err = np.linalg.norm(x_final[2:] - x_goal[2:])

    return (q_err <= angle_tol) and (dq_err <= vel_tol)


def estimate_break_noise_curve(
    x0, T, dt_sim, dt_ctrl,
    t_nom, X_nom, U_nom, K_of_t,
    Wproj, tube_radius, u_clip,
    sigma_grid, n_trials=8, seed0=0
):
    """
    For each sigma in sigma_grid:
      run n_trials Monte-Carlo simulations with different random seeds
      compute success rate
    """
    rates = []
    for i, sigma in enumerate(sigma_grid):
        ok = 0
        for tr in range(n_trials):
            seed = seed0 + 1000*i + tr
            t, x_true, x_hat, u, kref, dist, sat, E = simulate_closed_loop_proj_tvlqr_with_noise(
                x0, T, dt_sim, dt_ctrl,
                t_nom, X_nom, U_nom, K_of_t,
                Wproj, tube_radius, u_clip,
                sigma_obs=sigma, seed=seed
            )
            if success_metric(x_true, X_nom):
                ok += 1
        rates.append(ok / float(n_trials))
    return np.array(rates, dtype=float)


# ===============================================================
# 9) SIMPLE GEOMETRY FOR ANIMATION (pendulum in x-y)
# ===============================================================

def angles_to_points(q1, q2):
    """
    Convert angles (q1,q2) into 2D link endpoints for plotting.

    NOTE:
      Geometry uses link lengths (l1, l2). Your new model uses COM distances (r1, r2)
      for dynamics/gravity, but the animation is still drawn as a 2-link arm with full lengths.
    """
    x0, y0 = 0.0, 0.0
    x1 = l1 * np.sin(q1)
    y1 = l1 * np.cos(q1)
    x2 = x1 + l2 * np.sin(q1 + q2)
    y2 = y1 + l2 * np.cos(q1 + q2)
    return (x0, y0), (x1, y1), (x2, y2)


# ===============================================================
# 10) MAIN
# ===============================================================

if __name__ == "__main__":
    # -----------------------------------------------------------
    # (A) Load nominal or build it INSIDE THE SCRIPT
    # -----------------------------------------------------------
    t_nom, X_nom, U_nom, dt_nom = load_or_build_nominal("nominal_from_part2.npz")
    T_nom = float(t_nom[-1])

    # -----------------------------------------------------------
    # (B) Build A_k, B_k by linearizing f_discrete at each nominal point
    # -----------------------------------------------------------
    A_list = []
    B_list = []
    for k in range(len(t_nom) - 1):
        A_k, B_k = linearize_discrete_fd(X_nom[k], U_nom[k], dt_nom, eps=1e-6)
        A_list.append(A_k)
        B_list.append(B_k)

    # -----------------------------------------------------------
    # (C) Choose LQR weights (tune if needed)
    # -----------------------------------------------------------
    Q  = np.diag([50.0, 50.0, 2.0, 2.0])
    R  = np.diag([0.8, 0.8])          # slightly larger R -> less aggressive torques
    Qf = np.diag([200.0, 200.0, 10.0, 10.0])

    # -----------------------------------------------------------
    # (D) TVLQR recursion to get discrete gains K_k
    # -----------------------------------------------------------
    K_list, P_list = tvlqr_discrete(A_list, B_list, Q, R, Qf)

    # -----------------------------------------------------------
    # (E) Smooth gain K(t) using kernel regression
    # -----------------------------------------------------------
    K_of_t = make_smooth_K_of_t(t_nom, K_list, dt_nom)

    # -----------------------------------------------------------
    # (F) Projection settings (only controller we use)
    # -----------------------------------------------------------
    Wproj = np.diag([4.0, 4.0, 0.5, 0.5])
    tube_radius = 0.6
    u_clip = 10.0

    # -----------------------------------------------------------
    # (G) Simulation settings
    # -----------------------------------------------------------
    dt_sim  = 0.01     # integration step (small for smooth physics)
    dt_ctrl = dt_nom   # controller update period = nominal step (sensible + stable)
    T_sim   = T_nom

    x0 = np.array([0.2, -0.2, 0.0, 0.0], dtype=float)

    # Initial observation noise sigma (slider will change this)
    sigma0 = 0.00

    # -----------------------------------------------------------
    # (H) Helper: run one simulation
    # -----------------------------------------------------------
    sim_data = {}

    def run_one_sim(sigma, seed=1):
        return simulate_closed_loop_proj_tvlqr_with_noise(
            x0, T_sim, dt_sim, dt_ctrl,
            t_nom, X_nom, U_nom, K_of_t,
            Wproj, tube_radius, u_clip,
            sigma_obs=sigma, seed=seed
        )

    (t_grid, x_true, x_hat, u_traj,
     k_ref_hist, dist_hist, sat_frac_hist, energy_hist) = run_one_sim(sigma0, seed=1)

    sim_data["t"] = t_grid
    sim_data["x_true"] = x_true
    sim_data["u"] = u_traj
    sim_data["kref"] = k_ref_hist
    sim_data["dist"] = dist_hist
    sim_data["sat"] = sat_frac_hist
    sim_data["E"] = energy_hist

    # -----------------------------------------------------------
    # (I) Monte-Carlo success curve (computed ONCE, not on slider)
    # -----------------------------------------------------------
    sigma_grid = np.linspace(0.0, 1.0, 11)
    success_rates = estimate_break_noise_curve(
        x0, T_sim, dt_sim, dt_ctrl,
        t_nom, X_nom, U_nom, K_of_t,
        Wproj, tube_radius, u_clip,
        sigma_grid, n_trials=8, seed0=10
    )

    # ===========================================================
    # (J) PLOTTING: one big figure with a clearly visible slider
    # ===========================================================

    plt.close("all")

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # IMPORTANT: make extra space for the slider (bottom=0.28 gives it room)
    plt.subplots_adjust(bottom=0.28, wspace=0.25, hspace=0.30)

    ax_angles = axs[0, 0]
    ax_ctrl   = axs[0, 1]
    ax_err    = axs[1, 0]
    ax_proj   = axs[1, 1]

    # ---- Angles plot ----
    ax_angles.set_title("Angles vs time (true vs nominal)")
    ax_angles.set_xlabel("t [s]")
    ax_angles.set_ylabel("angle [rad]")
    ax_angles.grid(True)

    ax_angles.plot(t_nom, X_nom[:, 0], "k--", linewidth=2, label="q1_nom")
    ax_angles.plot(t_nom, X_nom[:, 1], "k:",  linewidth=2, label="q2_nom")

    line_q1_true, = ax_angles.plot(sim_data["t"], sim_data["x_true"][:, 0], label="q1_true")
    line_q2_true, = ax_angles.plot(sim_data["t"], sim_data["x_true"][:, 1], label="q2_true")
    ax_angles.legend(loc="best")

    # ---- Controls plot ----
    ax_ctrl.set_title("Controls vs time (u1,u2) - PROJ TVLQR")
    ax_ctrl.set_xlabel("t [s]")
    ax_ctrl.set_ylabel("torque [Nm]")
    ax_ctrl.grid(True)

    ax_ctrl.plot(t_nom, U_nom[:, 0], "k--", linewidth=2, label="u1_nom")
    ax_ctrl.plot(t_nom, U_nom[:, 1], "k:",  linewidth=2, label="u2_nom")

    line_u1, = ax_ctrl.plot(sim_data["t"], sim_data["u"][:, 0], label="u1_applied")
    line_u2, = ax_ctrl.plot(sim_data["t"], sim_data["u"][:, 1], label="u2_applied")
    ax_ctrl.legend(loc="best")

    # ---- Error norms plot ----
    ax_err.set_title("Tracking error norms vs time (true - selected reference)")
    ax_err.set_xlabel("t [s]")
    ax_err.set_ylabel("error norm")
    ax_err.grid(True)

    e = np.zeros_like(sim_data["x_true"])
    for i in range(sim_data["t"].size):
        kref_i = sim_data["kref"][i]
        e[i] = sim_data["x_true"][i] - X_nom[kref_i]

    e_q  = np.linalg.norm(e[:, :2], axis=1)
    e_dq = np.linalg.norm(e[:, 2:], axis=1)
    e_all = np.linalg.norm(e, axis=1)

    line_eq,   = ax_err.plot(sim_data["t"], e_q,   label="||e_q|| (angles)")
    line_edq,  = ax_err.plot(sim_data["t"], e_dq,  label="||e_dq|| (velocities)")
    line_eall, = ax_err.plot(sim_data["t"], e_all, label="||e|| (full)")
    ax_err.legend(loc="best")

    # ---- Projection behavior plot ----
    ax_proj.set_title("Projection behavior: k_ref(t) and dist to chosen knot")
    ax_proj.set_xlabel("t [s]")
    ax_proj.set_ylabel("k_ref")
    ax_proj.grid(True)

    # Left axis: k_ref(t) (purple)
    line_kref, = ax_proj.plot(
        sim_data["t"], sim_data["kref"],
        linewidth=2.0, color="tab:purple", label="k_ref(t)"
    )

    # Right axis: distance (green) + tube radius (red dashed)
    ax_proj_r = ax_proj.twinx()
    ax_proj_r.set_ylabel("distance")

    line_dist, = ax_proj_r.plot(
        sim_data["t"], sim_data["dist"],
        linewidth=2.0, color="tab:green", label="dist to chosen knot"
    )

    tube_line = ax_proj_r.axhline(
        tube_radius, linestyle="--", linewidth=2.0, color="tab:red", label="tube radius"
    )

    # Combined legend
    lines_left, labels_left = ax_proj.get_legend_handles_labels()
    lines_right, labels_right = ax_proj_r.get_legend_handles_labels()
    ax_proj.legend(lines_left + lines_right, labels_left + labels_right, loc="upper left")

    # ---- Slider axis (VISIBLE) ----
    # We place it in the free space we created with bottom=0.28.
    ax_sigma = fig.add_axes([0.15, 0.12, 0.70, 0.05])
    slider_sigma = Slider(ax_sigma, "sigma_obs", 0.0, 1.0, valinit=sigma0, valstep=0.02)

    # ===========================================================
    # (K) Extra figure: success curve
    # ===========================================================

    fig_mc, ax_mc = plt.subplots(figsize=(7, 4))
    ax_mc.set_title("Success rate vs observation noise sigma (Monte-Carlo) - PROJ TVLQR")
    ax_mc.set_xlabel("sigma_obs")
    ax_mc.set_ylabel("success rate")
    ax_mc.grid(True)
    ax_mc.plot(sigma_grid, success_rates, "o-", label="success rate")
    ax_mc.set_ylim(-0.05, 1.05)
    ax_mc.legend(loc="best")

    vline_sigma = ax_mc.axvline(sigma0, linestyle="--", linewidth=2.0, color="tab:blue")

    # ===========================================================
    # (L) Extra figure: energy + saturation
    # ===========================================================

    fig_diag, axs_diag = plt.subplots(2, 1, figsize=(7, 6))
    plt.subplots_adjust(hspace=0.35)

    ax_E = axs_diag[0]
    ax_sat = axs_diag[1]

    ax_E.set_title("Total energy vs time (true)")
    ax_E.set_xlabel("t [s]")
    ax_E.set_ylabel("Energy (arb.)")
    ax_E.grid(True)
    line_E, = ax_E.plot(sim_data["t"], sim_data["E"], label="E_true")
    ax_E.legend(loc="best")

    ax_sat.set_title("Saturation fraction vs time (0, 0.5, 1.0)")
    ax_sat.set_xlabel("t [s]")
    ax_sat.set_ylabel("sat_frac")
    ax_sat.grid(True)
    line_sat, = ax_sat.plot(sim_data["t"], sim_data["sat"], label="sat_frac")
    ax_sat.set_ylim(-0.05, 1.05)
    ax_sat.legend(loc="best")

    # ===========================================================
    # (M) Live animation: true vs nominal at k_ref
    # ===========================================================

    fig_anim, ax_anim = plt.subplots(figsize=(6, 6))
    ax_anim.set_title("Live animation (true vs nominal at k_ref)")
    ax_anim.set_xlabel("x")
    ax_anim.set_ylabel("y")
    ax_anim.grid(True)
    ax_anim.set_aspect("equal", adjustable="box")
    ax_anim.set_xlim(-1.1, 1.1)
    ax_anim.set_ylim(-1.1, 1.1)

    line_true, = ax_anim.plot([], [], linewidth=4, label="true")
    line_nom,  = ax_anim.plot([], [], "--", linewidth=3, label="nominal at k_ref")
    ax_anim.legend(loc="upper right")

    def anim_init():
        line_true.set_data([], [])
        line_nom.set_data([], [])
        return line_true, line_nom

    def anim_update(frame):
        # Clamp frame
        frame = int(np.clip(frame, 0, sim_data["t"].size - 1))

        q1t = sim_data["x_true"][frame, 0]
        q2t = sim_data["x_true"][frame, 1]

        kref = sim_data["kref"][frame]
        q1n = X_nom[kref, 0]
        q2n = X_nom[kref, 1]

        (x0p, y0p), (x1t, y1t), (x2t, y2t) = angles_to_points(q1t, q2t)
        (_, _),     (x1n, y1n), (x2n, y2n) = angles_to_points(q1n, q2n)

        line_true.set_data([x0p, x1t, x2t], [y0p, y1t, y2t])
        line_nom.set_data([x0p, x1n, x2n], [y0p, y1n, y2n])

        return line_true, line_nom


    def frame_generator():
        """
        Infinite frame generator:
          0,1,2,...,N-1,0,1,2,... forever
        This is robust and keeps animation alive.
        """
        k = 0
        while True:
            yield k
            k += 1
            if k >= sim_data["t"].size:
                k = 0

    anim = FuncAnimation(
        fig_anim,
        anim_update,
        init_func=anim_init,
        frames=frame_generator(),     # <-- iterator (GOOD)
        interval=20,
        blit=False,                   # safer for Tkinter (avoids "blank animation" issues)
        cache_frame_data=False,       # avoids unbounded caching warnings
        save_count=sim_data["t"].size # also avoids warnings
    )

    # ===========================================================
    # (N) Slider callback: rerun simulation + update all plots
    # ===========================================================

    def on_slider_change(val):
        sigma = float(slider_sigma.val)

        (t_grid2, x_true2, x_hat2, u2,
         k_ref2, dist2, sat2, E2) = run_one_sim(sigma, seed=1)

        sim_data["t"] = t_grid2
        sim_data["x_true"] = x_true2
        sim_data["u"] = u2
        sim_data["kref"] = k_ref2
        sim_data["dist"] = dist2
        sim_data["sat"] = sat2
        sim_data["E"] = E2

        # Update angles
        line_q1_true.set_data(t_grid2, x_true2[:, 0])
        line_q2_true.set_data(t_grid2, x_true2[:, 1])
        ax_angles.relim()
        ax_angles.autoscale_view()

        # Update controls
        line_u1.set_data(t_grid2, u2[:, 0])
        line_u2.set_data(t_grid2, u2[:, 1])
        ax_ctrl.relim()
        ax_ctrl.autoscale_view()

        # Update errors
        e2 = np.zeros_like(x_true2)
        for i in range(t_grid2.size):
            kk = k_ref2[i]
            e2[i] = x_true2[i] - X_nom[kk]
        e_q2 = np.linalg.norm(e2[:, :2], axis=1)
        e_dq2 = np.linalg.norm(e2[:, 2:], axis=1)
        e_all2 = np.linalg.norm(e2, axis=1)

        line_eq.set_data(t_grid2, e_q2)
        line_edq.set_data(t_grid2, e_dq2)
        line_eall.set_data(t_grid2, e_all2)
        ax_err.relim()
        ax_err.autoscale_view()

        # Update projection diagnostics
        line_kref.set_data(t_grid2, k_ref2)
        line_dist.set_data(t_grid2, dist2)
        tube_line.set_ydata([tube_radius, tube_radius])

        ax_proj.relim()
        ax_proj.autoscale_view()
        ax_proj_r.relim()
        ax_proj_r.autoscale_view()

        # Update MC sigma marker
        vline_sigma.set_xdata([sigma, sigma])

        # Update energy + saturation
        line_E.set_data(t_grid2, E2)
        ax_E.relim()
        ax_E.autoscale_view()

        line_sat.set_data(t_grid2, sat2)
        ax_sat.relim()
        ax_sat.autoscale_view()

        # Redraw
        fig.canvas.draw_idle()
        fig_mc.canvas.draw_idle()
        fig_diag.canvas.draw_idle()
        fig_anim.canvas.draw_idle()

    slider_sigma.on_changed(on_slider_change)

    # Show all windows
    plt.show()