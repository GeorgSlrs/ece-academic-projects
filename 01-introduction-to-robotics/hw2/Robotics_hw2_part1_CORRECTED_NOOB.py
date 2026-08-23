import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

np.set_printoptions(precision=4, suppress=True)

# -----------------------------
# Functions for robotics computations
# -----------------------------
def hat(vec):
    v = vec.reshape((3,))
    return np.array([
        [0., -v[2], v[1]],
        [v[2], 0., -v[0]],
        [-v[1], v[0], 0.]
    ])

def Adj(R, p):
    Tadj = np.zeros((6, 6))
    Tadj[:3, :3] = R
    Tadj[3:, 3:] = R
    Tadj[3:, :3] = hat(p) @ R
    return Tadj

def adjoint(T):
    R = T[:3, :3]
    p = T[:3, 3]
    return Adj(R, p)

def exp_rotation(p):
    phi = p.reshape((3, 1))
    theta = np.linalg.norm(phi)
    if theta < 1e-12:
        return np.eye(3, 3)
    a = phi / theta
    return (np.eye(3)*np.cos(theta)
            + (1. - np.cos(theta)) * a @ a.T
            + np.sin(theta) * hat(a))

def log_rotation(R):
    theta = np.arccos(max(-1., min(1., (np.trace(R) - 1.) / 2.)))
    if theta < 1e-12:
        return np.zeros((3, 1))
    mat = R - R.T
    r = np.array([mat[2, 1], mat[0, 2], mat[1, 0]]).reshape((3, 1))
    return (theta / (2. * np.sin(theta))) * r

def exp_pose(tau):
    tau = tau.reshape((6,1))
    theta = np.linalg.norm(tau[:3, :])
    R = np.eye(3)
    p = np.zeros((3, 1))

    if not np.isclose(theta, 0.):
        r = tau[:3, :] / theta
        rho = tau[3:, :] / theta
        rh = hat(r)
        R = exp_rotation(tau[:3, :])
        p = (np.eye(3)*theta + (1. - np.cos(theta))*rh
             + (theta - np.sin(theta))*(rh @ rh)) @ rho
    else:
        p = tau[3:, :]
    return np.block([[R, p],
                     [np.zeros((1,3)), 1.]])

def log_pose(T):
    R = T[:3, :3]
    p = T[:3, 3:].reshape((3,1))
    rt = log_rotation(R)
    theta = np.linalg.norm(rt)
    if np.allclose(theta, 0.):
        return np.block([[np.zeros((3, 1))],
                         [p]])
    rh = hat(rt / theta)
    return np.block([[rt],
                     [(1./theta * np.eye(3) - 0.5 * rh
                       + (1./theta - 0.5 / np.tan(theta/2.))*(rh @ rh)) @ p * theta]])

def expm_se3(screw_axis, theta):
    tau = (screw_axis * theta).reshape((6,1))
    return exp_pose(tau)

def matrix_log6(T):
    return log_pose(T)

def forward_kinematics(M, SList, q):
    """Computes the forward kinematics."""
    T = np.eye(4)
    transformations = [T.copy()]
    for i in range(len(q)):
        T = T @ expm_se3(SList[:, i], q[i])
        transformations.append(T.copy())
    T = T @ M
    transformations.append(T.copy())
    return T, transformations

def jacobian_space(SList, q):
    """Computes the space Jacobian."""
    n = len(q)
    Js = np.zeros((6, n))
    T = np.eye(4)
    for i in range(n):
        if i > 0:
            T = T @ expm_se3(SList[:, i-1], q[i-1])
        Ad_T = adjoint(T)
        Js[:, i] = Ad_T @ SList[:, i]
    return Js

# -----------------------------
# Robot parameters and Data
# -----------------------------
M = np.array([
    [1, 0, 0, 8.8],
    [0, -1, 0, 0],
    [0, 0, -1, 92.6],
    [0, 0, 0, 1]
])

data = [
    (1, [0, 0, 1], [0, 0, 0]),
    (2, [0, 1, 0], [0, 0, 33.3]),
    (3, [0, 0, 1], [0, 0, 0]),
    (4, [0, 1, 0], [8.8, 0, 64.9]),
    (5, [0, 0, 1], [0, 0, 0]),
    (6, [0, 1, 0], [0, 0, 103.3]),
    (7, [0, 0, 1], [8.8, 0, 0])
]

SList = np.zeros((6, 7))
for idx, (n, r_i, q_i) in enumerate(data):
    r_i = np.array(r_i)
    q_i = np.array(q_i)
    rho_i = -np.cross(r_i, q_i)
    S_i = np.concatenate((r_i, rho_i))
    SList[:, idx] = S_i

# Initial joint angles (all zeros)
q_initial = np.zeros(7)

# Target transformation matrix T_wd
T_wd = np.array([
    [1, 0, 0, 69.50],
    [0, 1, 0, 9.50],
    [0, 0, 1, 2.50],
    [0, 0, 0, 1]
])

# Inverse Kinematics Iteration
max_iterations = 2000
epsilon = 1e-5
q_k = q_initial.copy()
a = 0.1  # Step size

joint_angles_history = [q_k.copy()]  # Store the joint angles for plotting

for iteration in range(max_iterations):
    T_wb, transformations = forward_kinematics(M, SList, q_k)
    T_err = T_wd @ np.linalg.inv(T_wb)
    V_w = matrix_log6(T_err)
    norm_V_w = np.linalg.norm(V_w)
    if norm_V_w < epsilon:
        print(f"Converged in {iteration} iterations")
        break
    
    J_w = jacobian_space(SList, q_k)
    damping = 1e-6
    J_w_pinv = J_w.T @ np.linalg.inv(J_w @ J_w.T + damping * np.eye(6))
    
    delta_q = (J_w_pinv @ V_w).flatten()
    q_k = q_k + a * delta_q
    joint_angles_history.append(q_k.copy())

print("\nFinal joint angles q_k (radians):")
print(np.round(q_k, 4))

q_k_deg = np.degrees(q_k)
q_k_deg = (q_k_deg + 180) % 360 - 180
print("\nFinal joint angles q_k (degrees):")
print(np.round(q_k_deg, 2))

T_final, transformations_final = forward_kinematics(M, SList, q_k)
print("\nFinal transformation matrix T_wb:")
print(T_final)
print("\nDesired transformation matrix T_wd:")
print(T_wd)

# Visualization code
def draw_frame(ax, T, label='', length=5):
    origin = T[:3, 3]
    x_dir = T[:3, 0]
    y_dir = T[:3, 1]
    z_dir = T[:3, 2]
    ax.quiver(*origin, *(x_dir * length), color='r', arrow_length_ratio=0.1)
    ax.quiver(*origin, *(y_dir * length), color='g', arrow_length_ratio=0.1)
    ax.quiver(*origin, *(z_dir * length), color='b', arrow_length_ratio=0.1)
    if label:
        ax.text(*origin, label, color='black')

def draw_box_with_hole(ax, T, width=40, height=20, depth=20, hole_radius=5):
    box_corners = np.array([
        [-width / 2, -depth / 2, 0, 1],
        [width / 2, -depth / 2, 0, 1],
        [width / 2, depth / 2, 0, 1],
        [-width / 2, depth / 2, 0, 1],
        [-width / 2, -depth / 2, height, 1],
        [width / 2, -depth / 2, height, 1],
        [width / 2, depth / 2, height, 1],
        [-width / 2, depth / 2, height, 1]
    ])

    transformed_corners = (T @ box_corners.T).T[:, :3]
    faces = [
        [transformed_corners[j] for j in [0, 1, 2, 3]],  # Bottom
        [transformed_corners[j] for j in [4, 5, 6, 7]],  # Top
        [transformed_corners[j] for j in [0, 1, 5, 4]],  # Front
        [transformed_corners[j] for j in [2, 3, 7, 6]],  # Back
        [transformed_corners[j] for j in [1, 2, 6, 5]],  # Right
        [transformed_corners[j] for j in [3, 0, 4, 7]]   # Left
    ]

    ax.add_collection3d(Poly3DCollection(faces, color='red', alpha=0.3, edgecolor='k'))

    z = np.linspace(0, height, 50)
    theta = np.linspace(0, 2 * np.pi, 50)
    theta, z = np.meshgrid(theta, z)
    x = hole_radius * np.cos(theta)
    y = hole_radius * np.sin(theta)
    ones = np.ones(x.shape).flatten()
    hole_points = np.vstack((x.flatten(), y.flatten(), z.flatten(), ones))
    transformed_hole_points = T @ hole_points
    x_hole = transformed_hole_points[0, :].reshape(x.shape)
    y_hole = transformed_hole_points[1, :].reshape(y.shape)
    z_hole = transformed_hole_points[2, :].reshape(z.shape)

    ax.plot_surface(x_hole, y_hole, z_hole, color='blue', alpha=0.6)

def draw_cylinder(ax, T, radius=2.5, height=25, color='orange'):
    theta = np.linspace(0, 2 * np.pi, 50)
    z = np.linspace(-height / 2, height / 2, 50)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x = radius * np.cos(theta_grid)
    y = radius * np.sin(theta_grid)
    ones = np.ones(x.shape).flatten()
    points = np.vstack((x.flatten(), y.flatten(), z_grid.flatten(), ones))
    transformed_points = T @ points
    x_transformed = transformed_points[0, :].reshape(theta_grid.shape)
    y_transformed = transformed_points[1, :].reshape(theta_grid.shape)
    z_transformed = transformed_points[2, :].reshape(theta_grid.shape)
    ax.plot_surface(x_transformed, y_transformed, z_transformed, color=color, alpha=0.6)

def draw_robot(ax, transformations, color='grey'):
    """Draws the robot manipulator based on joint transformations."""
    for i, T in enumerate(transformations):
        if i > 0:
            p_prev = transformations[i - 1][:3, 3]
            p_curr = T[:3, 3]
            ax.plot([p_prev[0], p_curr[0]],
                    [p_prev[1], p_curr[1]],
                    [p_prev[2], p_curr[2]], color=color)
        # Draw coordinate frames for each joint
        draw_frame(ax, T, label=f'F{i}')

# Transformation matrices
cylinder_radius = 2.5  
cylinder_height = 25

T_world_box = np.array([
    [0, 1, 0, 50],
    [1, 0, 0, 50],
    [0, 0, 1, 10],
    [0, 0, 0, 1]
])

theta = np.deg2rad(-90)
cos_theta = np.cos(theta)
sin_theta = np.sin(theta)
R_y_neg90 = np.array([
    [cos_theta, 0, sin_theta],
    [0, 1, 0],
    [-sin_theta, 0, cos_theta]
])

T_world_cylinder = np.eye(4)
T_world_cylinder[:3, :3] = R_y_neg90
T_world_cylinder[:3, 3] = T_wd[:3, 3]

# Plot final configuration
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("Final Configuration After IK Convergence")
ax.set_xlim([0, 100])
ax.set_ylim([0, 100])
ax.set_zlim([0, 50])
ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
ax.set_zlabel("Z (cm)")

draw_frame(ax, np.eye(4), "World")
draw_frame(ax, T_world_box, "Box")
draw_box_with_hole(ax, T_world_box, width=20, height=10, depth=40, hole_radius=5)
draw_frame(ax, T_world_cylinder, "Cylinder")
draw_cylinder(ax, T_world_cylinder, radius=cylinder_radius, height=cylinder_height)

# Draw the robot in the final configuration
draw_robot(ax, transformations_final, color='grey')

plt.tight_layout()
plt.show()

# -------------------------------
# Convergence Plot
# -------------------------------
joint_angles_history = np.array(joint_angles_history)

# Convert joint angles to degrees and wrap within [-180, 180]
joint_angles_history_deg = np.degrees(joint_angles_history)
joint_angles_history_deg = (joint_angles_history_deg + 180) % 360 - 180

plt.figure(figsize=(10, 6))
for i in range(joint_angles_history_deg.shape[1]):
    plt.plot(joint_angles_history_deg[:, i], label=f"Joint {i+1}")
plt.title("Convergence of Joint Angles")
plt.xlabel("Iteration")
plt.ylabel("Joint Angle (degrees)")
plt.legend()
plt.grid(True)
plt.show()
