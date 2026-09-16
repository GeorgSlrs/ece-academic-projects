"""
Robust QP Solver (NumPy only) with:
  a) Equality elimination (nullspace reduction): x = x_p + N z
  b) Phase-I feasibility check on inequalities after elimination
  c) Primal–Dual Augmented Lagrangian (with slacks) on reduced problem
  d)  Damped slack, ridge-stabilized x-step, over-relaxed duals, adaptive rho
  e) Clear convergence report

QP in original variables x:
  minimize  1/2 x^T Q x + q^T x
  s.t.      A x = b
            C x <= d
We convert to z-variables by eliminating A x = b.

"""

import numpy as np


# ========= small linear algebra helpers =========

def nullspace_via_svd(A, tol=None):
    """
    Compute an orthonormal basis N for the nullspace of A (rows M x N).
    Returns N with shape (N, r), so that A @ N = 0 and columns of N are orthonormal.
    If A has full row rank and M < N, r = N - rank(A). If M=0, return identity.

    tol: threshold on singular values considered 'zero'.
    """
    M, N = A.shape
    if M == 0:
        return np.eye(N)  # nothing to eliminate; nullspace is all of R^N
    U, S, Vt = np.linalg.svd(A, full_matrices=True)
    if tol is None:
        tol = max(A.shape) * np.max(S) * np.finfo(float).eps
    rank = np.sum(S > tol)
    # Right singular vectors (rows of Vt). Nullspace is spanned by the last N - rank columns.
    Nmat = Vt[rank:].T  # shape (N, N-rank)
    return Nmat 

def particular_solution_eq(A, b, tol=1e-10):
    """
    Compute a particular solution x_p to A x = b using least-squares
    and verify consistency: ||A x_p - b||_2 <= tol.
    Raises ValueError if the equality system looks inconsistent.
    """
    if A.shape[0] == 0:
        return np.zeros(A.shape[1])
    x_p, residuals, rank, svals = np.linalg.lstsq(A, b, rcond=None)
    r = A @ x_p - b
    if np.linalg.norm(r, 2) > tol:
        raise ValueError("Equalities A x = b appear inconsistent: ||A x_p - b|| too large.")
    return x_p


def project_nonnegative(v):
    """Projection Π_{>=0}(v): clip negatives to zero, elementwise."""
    return np.maximum(v, 0.0)


def spd_solve(H, rhs):
    """
    Solve H x = rhs assuming H should be SPD.
    Try Cholesky; if it fails (near-indefinite numerics), add a tiny ridge and solve.
    """
    try:
        R = np.linalg.cholesky(H)
        y = np.linalg.solve(R.T, rhs)
        x = np.linalg.solve(R, y)
        return x
    except np.linalg.LinAlgError:
        eps = 1e-10
        return np.linalg.solve(H + eps*np.eye(H.shape[0]), rhs)


# ========= Phase-I feasibility (inequalities only) =========

def phase1_hinge_check(C, d, iters=200, step=1e-1, backtrack=0.5, tol=1e-8):
    """
        J(z) = 0.5 * ||(C z - d)_+||_2^2, 
    If min J ~ 0, likely feasible; if it stalls high, inequalities likely infeasible.

    Returns (z_hat, J_final).
    """
    P, N = C.shape
    z = np.zeros(N)
    for _ in range(iters):
        r = C @ z - d               # residuals
        pos = (r > 0).astype(float) # active mask for hinge
        grad = C.T @ (pos * r)      # gradient of 0.5||(r)_+||^2
        gnorm = np.linalg.norm(grad, 2)
        if gnorm < tol:
            break
        # backtracking steps
        t = step
        J0 = 0.5 * np.dot(np.maximum(r, 0.0), np.maximum(r, 0.0))
        while True:
            z_new = z - t * grad
            r_new = C @ z_new - d
            J_new = 0.5 * np.dot(np.maximum(r_new, 0.0), np.maximum(r_new, 0.0))
            if J_new <= J0 - 1e-4 * t * gnorm**2 or t < 1e-12:
                z, J0 = z_new, J_new
                break
            t *= backtrack
        if J0 < tol:
            break
    return z, J0
# ========= Robust ALM on reduced (inequality-only) problem =========

def alm_inequalities_only(Qz, qz, Cz, dz,
                          rho=1.0, max_iter=3000, eps_feas=1e-6, eps_stat=1e-6,
                          beta=0.8, delta=1e-8, alpha=1.7,
                          rho_adjust_period=5, rho_balance_ratio=10.0,
                          rho_growth=2.0, rho_shrink=0.5, rho_min=1e-6, rho_max=1e10,
                          use_relative_stop=True, verbose=False):
    """
    Solve: minimize 1/2 z^T Qz z + qz^T z  s.t. Cz z <= dz
    using ALM with slacks (s>=0: Cz z + s = dz). No equalities here.

    Returns dict with z, s, mu, rho, iters, converged, history, report.
    """
    N = Qz.shape[0]
    P = Cz.shape[0]
    assert Qz.shape == (N, N) and qz.shape == (N,)
    assert Cz.shape[1] == N and dz.shape == (P,)

    z = np.zeros(N)
    s = project_nonnegative(dz - Cz @ z)  # s^0
    mu = np.zeros(P)

    CT = Cz.T

    hist = {'r_ineq': [], 'r_pr': [], 'r_stat': [], 'r_ineq_rel': [], 'r_stat_rel': [], 'rho': []}
    converged = False
    z_prev = z.copy()

    for k in range(max_iter):
        # (1) damped slack
        s_uncon = dz - Cz @ z - mu / max(rho, 1e-30)
        s = project_nonnegative(beta * s_uncon + (1 - beta) * s)

        # (2) z-step: (Qz + ρ C^T C + δI) z = -qz - C^T(μ - ρ(dz - s))
        H = Qz + rho * (CT @ Cz) + delta * np.eye(N)
        rhs = -qz - CT @ (mu - rho * (dz - s))
        z_prev[:] = z
        z = spd_solve(H, rhs)

        # (3) dual ascent with over-relaxation
        z_bar = alpha * z + (1 - alpha) * z_prev if alpha != 1.0 else z
        mu = project_nonnegative(mu + rho * (Cz @ z_bar + s - dz))

        # (4) residuals
        r_ineq = np.linalg.norm(Cz @ z + s - dz, np.inf)
        grad_z = Qz @ z + qz + CT @ mu
        r_stat = np.linalg.norm(grad_z, np.inf)

        r_ineq_rel = r_ineq / (1.0 + np.linalg.norm(dz, np.inf))
        scale_stat = 1.0 + max(np.linalg.norm(qz, np.inf), np.linalg.norm(Qz @ z, np.inf))
        r_stat_rel = r_stat / scale_stat

        hist['r_ineq'].append(r_ineq); hist['r_pr'].append(r_ineq)
        hist['r_stat'].append(r_stat); hist['r_ineq_rel'].append(r_ineq_rel)
        hist['r_stat_rel'].append(r_stat_rel); hist['rho'].append(rho)

        if verbose:
            print(f"[it {k:4d}] r_ineq={r_ineq:.3e} r_stat={r_stat:.3e} rho={rho:.1e}")

        # stopping
        abs_ok = (r_ineq <= eps_feas) and (r_stat <= eps_stat)
        rel_ok = (r_ineq_rel <= 10*eps_feas) and (r_stat_rel <= 10*eps_stat) if use_relative_stop else True
        if abs_ok and rel_ok:
            converged = True
            break

        # adaptive rho
        if rho_adjust_period and ((k + 1) % rho_adjust_period == 0):
            rp, rd = r_ineq, r_stat
            rho_new = rho
            if rp > rho_balance_ratio * rd:
                rho_new = min(rho * rho_growth, rho_max)
            elif rd > rho_balance_ratio * rp:
                rho_new = max(rho * rho_shrink, rho_min)
            if rho_new != rho:
                scale = min(1.0, np.sqrt(rho_new / rho))
                mu = project_nonnegative(mu * scale)
                rho = rho_new

    report = {
        'converged': converged,
        'iters': k + 1,
        'rho_final': rho,
        'r_ineq': hist['r_ineq'][-1] if hist['r_ineq'] else 0.0,
        'r_stat': hist['r_stat'][-1] if hist['r_stat'] else 0.0,
        'r_ineq_rel': hist['r_ineq_rel'][-1] if hist['r_ineq_rel'] else 0.0,
        'r_stat_rel': hist['r_stat_rel'][-1] if hist['r_stat_rel'] else 0.0,
        'r_comp': np.linalg.norm(mu * s, np.inf) if P else 0.0
    }

    return {'z': z, 's': s, 'mu': mu, 'rho': rho, 'iters': k + 1,
            'history': hist, 'report': report}


# ========= High-level solve: eliminate equalities, then solve in z =========

def solve_qp_with_elimination(Q, q, A=None, b=None, C=None, d=None,
                              # ALM knobs
                              rho=1.0, max_iter=3000, eps_feas=1e-6, eps_stat=1e-6,
                              beta=0.8, delta=1e-8, alpha=1.7,
                              rho_adjust_period=5, rho_balance_ratio=10.0,
                              rho_growth=2.0, rho_shrink=0.5, rho_min=1e-6, rho_max=1e10,
                              use_relative_stop=True, verbose=False,
                              # Phase I settings
                              do_phase1=True, phase1_tol=1e-8):
    """
    Main entry:
      1) Check/solve Ax=b. If inconsistent -> raise with a clear message.
      2) Build nullspace basis N and particular solution x_p.
      3) Reduce QP to z-space:
           Qz = N^T Q N,   qz = N^T (Q x_p + q)
           Cz = C N,       dz = d - C x_p
      4) Optional Phase-I test on Cz z <= dz.
      5) Run robust ALM (inequalities only) on z.
      6) Map back x = x_p + N z.

    Returns dict with x,s,lam=None,mu (ineq multipliers mapped), etc., plus a convergence report.
    """
    # Shapes and safe defaults
    Q = np.asarray(Q, float); q = np.asarray(q, float).reshape(-1)
    Nvars = Q.shape[0]
    assert Q.shape == (Nvars, Nvars) and q.shape == (Nvars,)

    if A is None or b is None:
        A = np.zeros((0, Nvars), float); b = np.zeros((0,), float)
    else:
        A = np.asarray(A, float); b = np.asarray(b, float).reshape(-1)
        assert A.shape[1] == Nvars and A.shape[0] == b.shape[0]

    if C is None or d is None:
        C = np.zeros((0, Nvars), float); d = np.zeros((0,), float)
    else:
        C = np.asarray(C, float); d = np.asarray(d, float).reshape(-1)
        assert C.shape[1] == Nvars and C.shape[0] == d.shape[0]

    # (1) Particular solution for Ax=b (or detect inconsistency)
    x_p = particular_solution_eq(A, b, tol=1e-10)

    # (2) Nullspace basis N (columns) for A
    Nmat = nullspace_via_svd(A)
    rdim = Nmat.shape[1]  # reduced dimension (could be 0)

    # If no degrees of freedom left (rdim == 0), x is fixed = x_p.
    if rdim == 0:
        # Just check inequalities feasibility with that x_p
        viol = C @ x_p - d
        if np.max(viol) <= 1e-8:
            # Trivial solution
            report = {
                'converged': True,
                'iters': 0,
                'rho_final': rho,
                'r_eq': 0.0,
                'r_ineq': float(np.max(np.abs(viol + np.maximum(viol, 0.0)))),  # zero if feasible
                'r_pr': float(np.max(np.maximum(viol, 0.0))),
                'r_stat': float(np.linalg.norm(Q @ x_p + q + A.T @ np.zeros_like(b) + C.T @ np.zeros(C.shape[0]), np.inf)),
                'note': "No free variables after eliminating equalities; x = x_p."
            }
            return {'x': x_p, 's': project_nonnegative(d - C @ x_p),
                    'lam': None, 'mu': None, 'rho': rho, 'iters': 0,
                    'history': {}, 'report': report}
        else:
            raise ValueError("Equalities fix x uniquely but inequalities are violated ⇒ infeasible.")

    # (3) Reduced QP in z
    # Objective: 1/2 (x_p+N z)^T Q (x_p+N z) + q^T (x_p+N z) = const + 1/2 z^T Qz z + qz^T z
    Qz = Nmat.T @ Q @ Nmat
    qz = Nmat.T @ (Q @ x_p + q)

    # Inequalities: C (x_p + N z) <= d  ⇒  (C N) z <= d - C x_p
    Cz = C @ Nmat
    dz = d - C @ x_p

    # (4) Optional Phase-I feasibility check (catches hopeless cases early)
    if do_phase1 and Cz.shape[0] > 0:
        _, J_feas = phase1_hinge_check(Cz, dz, iters=300, step=1e-1, backtrack=0.5, tol=phase1_tol)
        if J_feas > 1e-6:
            print("[Phase-I] Warning: Inequalities may be infeasible under Ax=b; "
                  f"hinge loss ~ {J_feas:.3e} (cannot drive to ~0).")

    # (5) Solve reduced problem with robust ALM (ineq only)
    res_z = alm_inequalities_only(Qz, qz, Cz, dz,
                                  rho=rho, max_iter=max_iter, eps_feas=eps_feas, eps_stat=eps_stat,
                                  beta=beta, delta=delta, alpha=alpha,
                                  rho_adjust_period=rho_adjust_period, rho_balance_ratio=rho_balance_ratio,
                                  rho_growth=rho_growth, rho_shrink=rho_shrink, rho_min=rho_min, rho_max=rho_max,
                                  use_relative_stop=use_relative_stop, verbose=verbose)

    z = res_z['z']
    x = x_p + Nmat @ z  # map back to original variables

    # Build a convergence report in x-space for clarity
    r_eq = np.linalg.norm(A @ x - b, np.inf) if A.shape[0] else 0.0
    s = project_nonnegative(d - C @ x)
    r_ineq = np.linalg.norm(C @ x + s - d, np.inf) if C.shape[0] else 0.0
    r_pr = max(r_eq, r_ineq)
    r_stat = np.linalg.norm(Q @ x + q + A.T @ np.zeros(A.shape[0]) + C.T @ res_z['mu'], np.inf) if C.shape[0] else \
             np.linalg.norm(Q @ x + q, np.inf)

    report = {
        'converged': res_z['report']['converged'],
        'iters': res_z['report']['iters'],
        'rho_final': res_z['report']['rho_final'],
        'r_eq': r_eq,
        'r_ineq': r_ineq,
        'r_pr': r_pr,
        'r_stat': r_stat,
        'r_comp': res_z['report']['r_comp']
    }

    return {'x': x, 's': s, 'lam': None, 'mu': res_z['mu'], 'rho': res_z['rho'],
            'iters': res_z['iters'], 'history': res_z['history'], 'report': report}


# ================ Tiny demo =================
if __name__ == "__main__":
    # Variables x in R^3
    Q = np.array([[10.0,  2.0,  0.0],
                  [ 2.0,  5.0,  1.0],
                  [ 0.0,  1.0,  3.0]])
    q = np.array([-1.0, -2.0, -1.5])

    # Equalities: sum(x) = 1  and  x1 - x3 = 0.2  (full-row-rank 2x3)
    A = np.array([[1.0, 1.0, 1.0],
                  [1.0, 0.0, -1.0]])
    b = np.array([1.0, 0.2])

    # Inequalities: x >= 0, and  x1 + 2 x2 + x3 <= 1.3
    C_nonneg = -np.eye(3)
    d_nonneg = np.zeros(3)
    C_extra  = np.array([[1.0, 2.0, 1.0]])
    d_extra  = np.array([1.3])
    C = np.vstack([C_nonneg, C_extra])
    d = np.hstack([d_nonneg, d_extra])

    res = solve_qp_with_elimination(
        Q, q, A, b, C, d,
        rho=1.0, max_iter=4000, eps_feas=1e-8, eps_stat=1e-8,
        beta=0.8, delta=1e-8, alpha=1.7,
        rho_adjust_period=5, rho_balance_ratio=10.0,
        rho_growth=2.0, rho_shrink=0.5,
        verbose=False, do_phase1=True
    )

    # -----  convergence report -----
    rep = res['report']
    print("\n=== Convergence Report ===")
    print(f"Converged    : {rep['converged']}")
    print(f"Iters        : {rep['iters']}")
    print(f"Final rho    : {rep['rho_final']:.3e}")
    print(f"r_eq (abs)   : {rep['r_eq']:.3e}")
    print(f"r_ineq (abs) : {rep['r_ineq']:.3e}")
    print(f"r_pr (abs)   : {rep['r_pr']:.3e}")
    print(f"r_stat (abs) : {rep['r_stat']:.3e}")
    print(f"r_comp (abs) : {rep['r_comp']:.3e}")

    print("\n=== Solution ===")
    print("x* =", res['x'])
    print("s* =", res['s'])
