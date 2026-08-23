import numpy as np
from scipy.linalg import expm
from scipy.spatial.transform import Rotation as R

def skew(v):
    return np.array([
        [0,     -v[2],  v[1]],
        [v[2],   0,    -v[0]],
        [-v[1],  v[0],  0   ]
    ])

def adjoint(T):
    R_ = T[:3, :3]
    p = T[:3, 3]
    p_sk = skew(p)
    top = np.hstack((R_, np.zeros((3,3))))
    bot = np.hstack((p_sk @ R_, R_))
    return np.vstack((top, bot))

def twist_to_matrix(S):
    w = S[:3]
    v = S[3:]
    mat = np.zeros((4,4))
    mat[:3,:3] = skew(w)
    mat[:3,3] = v
    return mat

def matrix_exp6(S_mat, theta):
    w_mat = S_mat[:3,:3]
    v = S_mat[:3,3]
    norm_w = np.linalg.norm(w_mat, ord='fro')
    
    if norm_w < 1e-12:
        # pure translation
        T = np.eye(4)
        T[:3,3] = v * theta
        return T
    else:
        R_ = expm(w_mat * theta)
        w = np.array([w_mat[2,1], w_mat[0,2], w_mat[1,0]])
        w_sk = skew(w)
        I3 = np.eye(3)
        
        # V = I*theta + (1 - cos(theta))*w^ + (theta - sin(theta))* (w^2)
        V = (I3*theta
             + (1 - np.cos(theta))*w_sk
             + (theta - np.sin(theta))*(w_sk @ w_sk))
        p = V @ v
        T = np.eye(4)
        T[:3,:3] = R_
        T[:3,3] = p
        return T

def compute_se3_transform(rpy, xyz):
    rot = R.from_euler('xyz', rpy).as_matrix()
    T = np.eye(4)
    T[:3,:3] = rot
    T[:3,3] = xyz
    return T

def compute_spatial_inertia_matrix(mass, I3, com):
    r_sk = skew(com)
    upper_left = I3 + mass * (r_sk @ r_sk.T)
    upper_right = mass * r_sk
    lower_left = -mass * r_sk
    lower_right = mass * np.eye(3)
    G = np.block([
        [upper_left, upper_right],
        [lower_left, lower_right]
    ])
    return G
