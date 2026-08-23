"""
build_tvlqr_cache.py
====================
Run this ONCE on your laptop to generate:
  - nominal_from_part2.npz (if missing, via your module)
  - tvlqr_cache.npz        (always generated/overwritten)

Then the hardware runner will ONLY LOAD tvlqr_cache.npz (fast + reliable).

Folder expectation:
  C:\\Users\\georg\\Desktop\\ergasia4 contains:
    - RS_II_HW_4_new_model.py
    - (optional) nominal_from_part2.npz
    - this script
"""

import os
import importlib
import importlib.util
import numpy as np


# -------------------------
# Settings
# -------------------------
SIM_MODULE_NAME = "RS_II_HW_4_new_model"

NOMINAL_FILE = "nominal_from_part2.npz"
CACHE_FILE   = "tvlqr_cache.npz"

# LQR weights (use the same ones you want on hardware)
Q  = np.diag([50.0, 50.0, 2.0, 2.0])
R  = np.diag([0.8, 0.8])
Qf = np.diag([200.0, 200.0, 10.0, 10.0])

FD_EPS = 1e-6


def import_sim_module(module_name: str):
    """Import by module name; if that fails, import by file path in this folder."""
    try:
        return importlib.import_module(module_name)
    except Exception as e1:
        fname = module_name + ".py"
        here = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.join(here, fname)
        if not os.path.exists(fpath):
            raise RuntimeError(
                f"Failed normal import '{module_name}'. Also missing file:\n  {fpath}\n\n"
                f"Normal import error:\n  {e1}"
            )
        spec = importlib.util.spec_from_file_location(module_name, fpath)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not build import spec for:\n  {fpath}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


# ============================================================
# ADDED: helpers to compute a terminal equilibrium LQR
# ============================================================

def estimate_tau_equilibrium_via_dynamics(sim, x_eq):
    """
    ADDED:
    Estimate the torque tau_eq that makes qdd = 0 at a given pose (x_eq, with qd=0)
    using only sim.dynamics(), without needing access to M,G explicitly.

    dynamics: qdd = Minv * (tau - other)   where other = Cqd + G + F
    For qd=0, other is the torque needed to hold equilibrium.

    We can recover Minv columns by probing with tau=[1,0] and tau=[0,1]:
      qdd0  = dynamics(x, [0,0])[2:]
      qdd_e1= dynamics(x, [1,0])[2:] = Minv*e1 + qdd0  -> col1 = qdd_e1 - qdd0
      qdd_e2= dynamics(x, [0,1])[2:] = Minv*e2 + qdd0  -> col2 = qdd_e2 - qdd0

    Then qdd0 = -Minv * other  -> other = -Minv^{-1} qdd0
    """
    x_eq = np.asarray(x_eq, dtype=float).copy()
    x_eq[2:] = 0.0  # enforce qd=0 for equilibrium holding

    qdd0  = np.asarray(sim.dynamics(x_eq, np.array([0.0, 0.0]))[2:], dtype=float)
    qdd_e1 = np.asarray(sim.dynamics(x_eq, np.array([1.0, 0.0]))[2:], dtype=float)
    qdd_e2 = np.asarray(sim.dynamics(x_eq, np.array([0.0, 1.0]))[2:], dtype=float)

    col1 = qdd_e1 - qdd0
    col2 = qdd_e2 - qdd0
    Minv = np.column_stack([col1, col2])  # 2x2

    # other = -Minv^{-1} qdd0
    other = -np.linalg.solve(Minv, qdd0)
    tau_eq = other
    return tau_eq


def dlqr_iterative(A, B, Qlqr, Rlqr, max_iter=5000, tol=1e-12):
    """
    ADDED:
    Solve the discrete-time infinite-horizon LQR (DARE) by fixed-point iteration.

    Returns:
      K, P
    """
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Qlqr = np.asarray(Qlqr, dtype=float)
    Rlqr = np.asarray(Rlqr, dtype=float)

    P = Qlqr.copy()
    for _ in range(max_iter):
        S = Rlqr + B.T @ P @ B
        K = np.linalg.solve(S, (B.T @ P @ A))
        P_new = Qlqr + A.T @ P @ A - A.T @ P @ B @ K
        if np.max(np.abs(P_new - P)) < tol:
            P = P_new
            break
        P = P_new

    # final K
    S = Rlqr + B.T @ P @ B
    K = np.linalg.solve(S, (B.T @ P @ A))
    return K, P


def main():
    print(f"[INFO] Importing module: {SIM_MODULE_NAME}")
    sim = import_sim_module(SIM_MODULE_NAME)

    required = [
        "load_or_build_nominal",
        "linearize_discrete_fd",
        "tvlqr_discrete",
    ]
    for name in required:
        if not hasattr(sim, name):
            raise RuntimeError(f"[ERROR] Module missing required function: {name}")

    print(f"[INFO] Loading/building nominal: {NOMINAL_FILE}")
    t_nom, X_nom, U_nom, dt_nom = sim.load_or_build_nominal(NOMINAL_FILE)

    print("[INFO] Linearizing along nominal (finite-diff)...")
    A_list, B_list = [], []
    for k in range(len(t_nom) - 1):
        Ak, Bk = sim.linearize_discrete_fd(X_nom[k], U_nom[k], dt_nom, eps=FD_EPS)
        A_list.append(Ak)
        B_list.append(Bk)

    print("[INFO] Running discrete TVLQR Riccati recursion...")
    K_list, P_list = sim.tvlqr_discrete(A_list, B_list, Q, R, Qf)

    # Make K_list a clean ndarray for saving
    K_arr = np.stack(K_list, axis=0)  # shape: (N-1, 2, 4)

    # ============================================================
    # ADDED: terminal equilibrium hold data
    # ============================================================
    print("[INFO] Computing terminal equilibrium hold data (x_goal, tau_eq, K_eq)...")

    x_goal = np.asarray(X_nom[-1], dtype=float).copy()
    x_goal[2:] = 0.0  # force goal velocity = 0

    # Estimate torque that holds this equilibrium in the model
    tau_eq = estimate_tau_equilibrium_via_dynamics(sim, x_goal)

    # Linearize discrete model at equilibrium and compute infinite-horizon DLQR
    Aeq, Beq = sim.linearize_discrete_fd(x_goal, tau_eq, dt_nom, eps=FD_EPS)

    # You can tune these separately from the tracking weights if you want.
    Q_hold = np.diag([200.0, 200.0, 10.0, 10.0])
    R_hold = np.diag([1.0, 1.0])

    K_eq, P_eq = dlqr_iterative(Aeq, Beq, Q_hold, R_hold)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILE)
    np.savez(
        out_path,
        t_nom=t_nom,
        X_nom=X_nom,
        U_nom=U_nom,
        dt_nom=np.array(dt_nom, dtype=float),
        K_list=K_arr,

        # ADDED fields:
        x_goal=x_goal,
        tau_eq=tau_eq,
        K_eq=K_eq,
    )

    print("\n[SUCCESS] Wrote TVLQR cache:")
    print(f"  {out_path}")
    print("  Contents: t_nom, X_nom, U_nom, dt_nom, K_list")
    print("  ADDED: x_goal, tau_eq, K_eq")


if __name__ == "__main__":
    main()
