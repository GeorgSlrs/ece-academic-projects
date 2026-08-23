# kinematics.py

import numpy as np
from helpers import matrix_exp6, se3, adjoint

def forward_kinematics_POE(S_list, thetas, M):
    """
    Computes the forward kinematics using the Product of Exponentials (POE).
    S_list: shape (6, N) -> each column is a screw axis [w_x, w_y, w_z, v_x, v_y, v_z].
    thetas: shape (N,) -> joint angles
    M:      4x4 matrix -> end-effector home configuration
    """
    T = np.eye(4)
    N = S_list.shape[1]
    for i in range(N):
        exp_i = matrix_exp6(se3(S_list[:,i] * thetas[i]))
        T = T @ exp_i
    T = T @ M
    return T

def geometric_jacobian_POE(S_list, thetas, M):
    """
    Computes the Body Jacobian (Geometric Jacobian in the body frame) using POE.
    J_b = [Ad_{(e^{-[S1]*theta1} ... e^{-[SN]*thetaN} M)^-1} * S1, 
           ...
          Ad_{(e^{-[SN]*thetaN} M)^-1} * SN ]
    """
    N = S_list.shape[1]
    J_b = np.zeros((6, N))
    T = M.copy()

    # Compute the transformation from base to end-effector
    for i in range(N-1, -1, -1):
        S = S_list[:, i]
        Ad_T = adjoint(np.linalg.inv(T))
        J_b[:, i] = Ad_T @ S
        T = matrix_exp6(-se3(S * thetas[i])) @ T

    return J_b
