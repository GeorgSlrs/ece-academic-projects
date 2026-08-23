# helpers.py

import numpy as np

def skew_3d(omega):
    """
    Returns the 3x3 skew-symmetric matrix (hat operator) of a 3D vector omega.
    So that skew_3d(omega) * v = omega x v for any v.
    """
    return np.array([
        [0,        -omega[2],  omega[1]],
        [omega[2],  0,        -omega[0]],
        [-omega[1], omega[0],  0       ]
    ], dtype=float)

def se3(vec6):
    """
    Given a 6D vector [omega_x, omega_y, omega_z, v_x, v_y, v_z],
    return the corresponding 4x4 se(3) matrix:
        [ [omega_hat],  v ]
        [     0     ,  0 ]
    """
    omega = vec6[0:3]
    v     = vec6[3:6]
    mat = np.zeros((4,4), dtype=float)
    mat[0:3, 0:3] = skew_3d(omega)
    mat[0:3, 3]   = v
    return mat

def adjoint(T):
    """
    Compute the 6x6 Adjoint representation of the transformation matrix T in SE(3).
    T = [ R  p ]
        [ 0  1 ]
    Then
    Ad_T = [ R        0 ]
            [ p_hat*R R ].
    """
    R = T[0:3, 0:3]
    p = T[0:3, 3]
    p_hat = skew_3d(p)
    Ad = np.block([
        [R,             np.zeros((3,3))],
        [p_hat @ R,     R              ]
    ])
    return Ad

def matrix_exp6(se3_mat):
    """
    Exponential map from se(3) to SE(3).
    This uses the standard Rodrigues formula approach.
    """
    # Extract angular part
    omega_mat = se3_mat[0:3, 0:3]
    v = se3_mat[0:3, 3]

    # Check if near-zero rotation
    if np.linalg.norm(omega_mat, 'fro') < 1e-8:
        # No real rotation, translation only
        T = np.eye(4)
        T[0:3, 3] = v
        return T

    # Extract the angle from the rotation part
    omega = np.array([omega_mat[2,1], omega_mat[0,2], omega_mat[1,0]])  # inverse hat
    theta = np.linalg.norm(omega)

    # Normalize the axis
    if abs(theta) < 1e-12:
        # This is a very small rotation
        T = np.eye(4)
        T[0:3, 3] = v
        return T

    w_hat = omega_mat / theta
    R = (
        np.eye(3)
        + np.sin(theta) * w_hat
        + (1 - np.cos(theta)) * (w_hat @ w_hat)
    )
    G = (
        np.eye(3)
        + ((1 - np.cos(theta))/theta) * w_hat
        + ((theta - np.sin(theta))/ (theta**2)) * (w_hat @ w_hat)
    )
    T = np.eye(4)
    T[0:3, 0:3] = R
    T[0:3, 3]   = G @ v
    return T

def matrix_log6(T):
    """
    Log map from SE(3) to se(3). 
    This returns the 4x4 se(3) matrix whose exponential is T.
    """
    R = T[0:3, 0:3]
    p = T[0:3, 3]

    # If R is close to identity, no rotation
    if np.linalg.norm(R - np.eye(3)) < 1e-9:
        se3_mat = np.zeros((4,4))
        se3_mat[0:3, 3] = p
        return se3_mat

    # Otherwise, extract angle from rotation
    # For rotation matrix R, angle = arccos((trace(R) - 1)/2)
    acos_input = 0.5*(np.trace(R) - 1)
    # Numerically clamp to -1..1
    acos_input = max(min(acos_input, 1.0), -1.0)
    theta = np.arccos(acos_input)

    # For numeric stability if theta is ~0 or ~pi
    if abs(theta) < 1e-9:
        # Rotation is almost 0
        se3_mat = np.zeros((4,4))
        se3_mat[0:3, 3] = p
        return se3_mat

    w_hat = (theta/(2*np.sin(theta))) * (R - R.T)
    omega = np.array([ w_hat[2,1], w_hat[0,2], w_hat[1,0] ])

    # Now compute the translation part via formula
    w_hat_n = w_hat / theta    # normalized skew
    G_inv = (
        np.eye(3)
        - 0.5 * w_hat
        + (1.0/theta - 0.5 * (1/np.tan(theta/2))) * (w_hat_n @ w_hat_n)
    )
    v = G_inv @ p

    se3_mat = np.zeros((4,4))
    se3_mat[0:3, 0:3] = w_hat
    se3_mat[0:3, 3]   = v
    return se3_mat

def rotation_matrix_to_euler(R):
    """
    Convert a 3x3 rotation matrix R into ZYX Euler angles [roll, pitch, yaw].
    Returns angles in radians.
    """
    sy = np.sqrt(R[0,0]**2 + R[1,0]**2)
    singular = sy < 1e-6

    if not singular:
        roll  = np.arctan2(R[2,1], R[2,2])
        pitch = np.arctan2(-R[2,0], sy)
        yaw   = np.arctan2(R[1,0], R[0,0])
    else:
        roll  = np.arctan2(-R[1,2], R[1,1])
        pitch = np.arctan2(-R[2,0], sy)
        yaw   = 0

    return np.array([roll, pitch, yaw])

def euler_to_rotation_matrix(euler):
    """
    Convert ZYX Euler angles to a rotation matrix.
    euler: [roll, pitch, yaw] in radians
    """
    roll, pitch, yaw = euler

    Rx = np.array([
        [1,          0,           0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll),  np.cos(roll)]
    ])

    Ry = np.array([
        [ np.cos(pitch), 0, np.sin(pitch)],
        [             0, 1,            0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [         0,            0, 1]
    ])

    R = Rz @ Ry @ Rx
    return R
