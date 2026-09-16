import numpy as np
import numpy.linalg as la

# Define M
M = np.array([[1.0,  0.0],
              [10.0, 10.0]])

# SVD of M
U, S, VT = la.svd(M)
u1, v1 = U[:,0], VT.T[:,0]
sigma1 = S[0]

# Full‐block perturbation Δ* = (v1 u1^T)/σ1
Delta_full = np.outer(v1, u1) / sigma1
mu_full = sigma1
delta_full_sigma = la.svd(Delta_full, compute_uv=False)[0]
det_full = la.det(np.eye(2) - M @ Delta_full)

# Diagonal‐block perturbation Δ* = diag(0, 0.1)
Delta_diag = np.diag([0.0, 0.1])
mu_diag = 1.0 / max(abs(np.diag(Delta_diag)))
delta_diag_sigma = max(abs(np.diag(Delta_diag)))
det_diag = la.det(np.eye(2) - M @ Delta_diag)

print("Full block:")
print(f"  μ_full           = {mu_full:.6f}")
print(f"  σ̄(Δ_full)       = {delta_full_sigma:.6f}")
print(f"  det(I - M Δ_full)= {det_full:.2e}")

print("\nDiagonal block:")
print(f"  μ_diag           = {mu_diag:.6f}")
print(f"  σ̄(Δ_diag)       = {delta_diag_sigma:.6f}")
print(f"  det(I - M Δ_diag)= {det_diag:.2e}")
