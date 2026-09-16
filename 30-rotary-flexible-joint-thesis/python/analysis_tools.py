# analysis_tools.py (FULL)
from __future__ import annotations
import numpy as np
from typing import Tuple


def linearize_finite_diff(f, x0: np.ndarray, u0: np.ndarray,
                          eps_x: float = 1e-6, eps_u: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
    """
    Finite-difference linearization.

    We want:
      xdot = f(x,u)
    Linearization around (x0,u0):
      xdot ≈ f(x0,u0) + A (x-x0) + B (u-u0)

    where:
      A = ∂f/∂x |(x0,u0)
      B = ∂f/∂u |(x0,u0)

    We approximate partial derivatives with symmetric differences:
      ∂f/∂x_i ≈ (f(x0+eps*e_i,u0) - f(x0-eps*e_i,u0)) / (2 eps)
    """
    x0 = np.asarray(x0, float).copy()
    u0 = np.asarray(u0, float).copy()
    n = x0.size
    m = u0.size

    f0 = np.asarray(f(x0, u0), float).reshape(-1)
    if f0.size != n:
        raise ValueError("f(x,u) must return vector same length as x")

    A = np.zeros((n, n), float)
    B = np.zeros((n, m), float)

    for i in range(n):
        dx = np.zeros(n); dx[i] = eps_x
        fp = np.asarray(f(x0 + dx, u0), float).reshape(-1)
        fm = np.asarray(f(x0 - dx, u0), float).reshape(-1)
        A[:, i] = (fp - fm) / (2.0 * eps_x)

    for j in range(m):
        du = np.zeros(m); du[j] = eps_u
        fp = np.asarray(f(x0, u0 + du), float).reshape(-1)
        fm = np.asarray(f(x0, u0 - du), float).reshape(-1)
        B[:, j] = (fp - fm) / (2.0 * eps_u)

    return A, B


def _expm(A: np.ndarray) -> np.ndarray:
    """
    Matrix exponential exp(A).
    We try SciPy if installed; otherwise we do a simple scaling+squaring Taylor fallback.
    """
    A = np.asarray(A, float)
    try:
        from scipy.linalg import expm  # type: ignore
        return expm(A)
    except Exception:
        n = A.shape[0]
        I = np.eye(n)
        normA = np.linalg.norm(A, ord=1)
        s = 0 if normA == 0 else max(0, int(np.ceil(np.log2(normA))))
        As = A / (2.0**s)

        K = 20
        X = I.copy()
        term = I.copy()
        for k in range(1, K+1):
            term = term @ As / float(k)
            X = X + term

        for _ in range(s):
            X = X @ X
        return X


def c2d_zoh(A: np.ndarray, B: np.ndarray, Ts: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Exact Zero-Order Hold discretization using block matrix exponential:

      M = [A B;
           0 0]

      exp(M Ts) = [Ad Bd;
                   0  I]

    """
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    n = A.shape[0]
    m = B.shape[1]

    M = np.zeros((n+m, n+m), float)
    M[:n, :n] = A
    M[:n, n:] = B

    E = _expm(M * float(Ts))
    Ad = E[:n, :n]
    Bd = E[:n, n:]
    return Ad, Bd


def freqresp_ss(A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray, w: np.ndarray) -> np.ndarray:
    """
    SISO frequency response:
      G(jw) = C (jwI - A)^-1 B + D
    """
    A = np.asarray(A, float)
    B = np.asarray(B, float).reshape(-1, 1)
    C = np.asarray(C, float).reshape(1, -1)
    D = float(np.asarray(D).reshape(()))

    n = A.shape[0]
    I = np.eye(n)
    G = np.zeros_like(w, dtype=complex)

    for k, wk in enumerate(w):
        X = np.linalg.solve(1j*wk*I - A, B)
        G[k] = (C @ X).item() + D
    return G


def poles(A: np.ndarray) -> np.ndarray:
    return np.linalg.eigvals(np.asarray(A, float))


def damping_from_poles(lam: np.ndarray):
    lam = np.asarray(lam, complex)
    sigma = np.real(lam)
    omega = np.imag(lam)
    wn = np.sqrt(sigma**2 + omega**2)
    zeta = np.zeros_like(wn)
    mask = wn > 1e-12
    zeta[mask] = -sigma[mask] / wn[mask]
    return wn, zeta


def ctrb(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Controllability matrix:
      [B, AB, A^2B, ..., A^(n-1)B]
    """
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    n = A.shape[0]
    blocks = [B]
    Ak = np.eye(n)
    for _ in range(1, n):
        Ak = Ak @ A
        blocks.append(Ak @ B)
    return np.concatenate(blocks, axis=1)


def obsv(A: np.ndarray, C: np.ndarray) -> np.ndarray:
    """
    Observability matrix:
      [C; CA; CA^2; ...; CA^(n-1)]
    """
    A = np.asarray(A, float)
    C = np.asarray(C, float)
    n = A.shape[0]
    blocks = [C]
    Ak = np.eye(n)
    for _ in range(1, n):
        Ak = Ak @ A
        blocks.append(C @ Ak)
    return np.concatenate(blocks, axis=0)


def root_locus_output_feedback(A: np.ndarray, B: np.ndarray, C: np.ndarray, k_list: np.ndarray) -> np.ndarray:
    """
    Simple root locus for output feedback u=-k*y, y=Cx, input matrix B:
      Acl = A - B*k*C
    """
    A = np.asarray(A, float)
    B = np.asarray(B, float).reshape(-1, 1)
    C = np.asarray(C, float).reshape(1, -1)
    n = A.shape[0]

    poles_k = np.zeros((len(k_list), n), dtype=complex)
    for i, k in enumerate(k_list):
        Acl = A - (B * float(k)) @ C
        poles_k[i, :] = np.linalg.eigvals(Acl)
    return poles_k


def solve_dare_iter(Ad: np.ndarray, Bd: np.ndarray, Q: np.ndarray, R: np.ndarray,
                    max_iter: int = 5000, tol: float = 1e-10) -> np.ndarray:
    """
    Very simple iterative DARE solver (for teaching/visualization).
    For serious work, use SciPy's solve_discrete_are if available.
    """
    Ad = np.asarray(Ad, float)
    Bd = np.asarray(Bd, float)
    Q = np.asarray(Q, float)
    R = np.asarray(R, float)

    P = Q.copy()
    for _ in range(max_iter):
        S = R + Bd.T @ P @ Bd
        K = np.linalg.solve(S, Bd.T @ P @ Ad)
        Pn = Ad.T @ P @ Ad - Ad.T @ P @ Bd @ K + Q
        if np.linalg.norm(Pn - P, ord="fro") < tol * (1 + np.linalg.norm(P, ord="fro")):
            P = Pn
            break
        P = Pn
    return 0.5 * (P + P.T)


def dlqr(Ad: np.ndarray, Bd: np.ndarray, Q: np.ndarray, R: np.ndarray):
    """
    Discrete LQR:
      minimize sum x^T Q x + u^T R u
      x_{k+1} = Ad x_k + Bd u_k
    """
    P = solve_dare_iter(Ad, Bd, Q, R)
    S = R + Bd.T @ P @ Bd
    K = np.linalg.solve(S, Bd.T @ P @ Ad)
    eigs = np.linalg.eigvals(Ad - Bd @ K)
    return K, P, eigs


def dkalman_gain(Ad: np.ndarray, Cd: np.ndarray, Qn: np.ndarray, Rn: np.ndarray,
                 max_iter: int = 5000, tol: float = 1e-10) -> np.ndarray:
    """
    Steady-state discrete Kalman filter gain via iteration.
    """
    Ad = np.asarray(Ad, float)
    Cd = np.asarray(Cd, float)
    Qn = np.asarray(Qn, float)
    Rn = np.asarray(Rn, float)

    P = Qn.copy()
    for _ in range(max_iter):
        S = Cd @ P @ Cd.T + Rn
        L = (Ad @ P @ Cd.T) @ np.linalg.inv(S)
        Pn = Ad @ P @ Ad.T - L @ S @ L.T + Qn
        if np.linalg.norm(Pn - P, ord="fro") < tol * (1 + np.linalg.norm(P, ord="fro")):
            P = Pn
            break
        P = Pn

    S = Cd @ P @ Cd.T + Rn
    L = (Ad @ P @ Cd.T) @ np.linalg.inv(S)
    return L