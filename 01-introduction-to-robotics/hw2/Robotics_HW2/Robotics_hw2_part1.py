import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

np.set_printoptions(precision=4, suppress=True)

# Functions for robotics computations
def hat(vec):
    v = vec.reshape((3,))
    return np.array([
        [0., -v[2], v[1]],
        [v[2], 0., -v[0]],
        [-v[1], v[0], 0.]
    ])

def adjoint(T):
    """Computes the adjoint representation of a transformation matrix."""
    R = T[:3, :3]  # Rotation part
    p = T[:3, 3]   # Position part
    p_hat = hat(p)
    Ad_T = np.zeros((6,6))
    Ad_T[:3, :3] = R
    Ad_T[3:, 3:] = R
    Ad_T[3:, :3] = p_hat @ R
    return Ad_T

def exp_rotation(phi):
    theta = np.linalg.norm(phi)
    if theta < 1e-12:
        return np.eye(3)
    a = phi / theta
    return (
        np.cos(theta) * np.eye(3)
        + (1 - np.cos(theta)) * np.outer(a, a)
        + np.sin(theta) * hat(a)
    )

def log_rotation(R):
    acos_input = (np.trace(R) - 1.0) / 2.0
    theta = np.arccos(np.clip(acos_input, -1.0, 1.0))
    if theta < 1e-12:
        return np.zeros(3)
    else:
        omega_hat = (R - R.T) / (2 * np.sin(theta))
        omega = np.array([omega_hat[2,1], omega_hat[0,2], omega_hat[1,0]]) * theta
        return omega

def exp_pose(tau):
    omega = tau[:3]
    v = tau[3:]
    theta = np.linalg.norm(omega)
    if theta < 1e-12:
        R = np.eye(3)
        p = v
    else:
        omega_hat = hat(omega / theta)
        R = exp_rotation(omega)
        G = (
            np.eye(3) * theta
            + (1 - np.cos(theta)) * omega_hat
            + (theta - np.sin(theta)) * omega_hat @ omega_hat
        )
        p = G @ (v / theta)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p.flatten()
    return T

def log_pose(T):
    R = T[:3, :3]
    p = T[:3, 3]
    omega = log_rotation(R)
    theta = np.linalg.norm(omega)
    if theta < 1e-12:
        v = p
    else:
        omega_hat = hat(omega / theta)
        G_inv = (
            (1.0 / theta) * np.eye(3)
            - 0.5 * omega_hat
            + (1 / theta - 0.5 / np.tan(theta / 2)) * omega_hat @ omega_hat
        )
        v = G_inv @ p
    return np.concatenate((omega, v))

def expm_se3(screw_axis, theta):
    tau = screw_axis * theta
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

# Robot parameters 
M = np.array([
    [-1, 0, 0, 8.8],
    [0, 1, 0, 0],
    [0, 0, -1, 92.6],
    [0, 0, 0, 1]
])

# 'Corrected' data for r_i and q_i
data = [
    # n,    r_i,           q_i
    (1, [0, 0, 1], [0, 0, 0]), 
    (2, [0, 1, 0], [0, 0, 33.3]),
    (3, [0, 0, 1], [0, 0, 0]),
    (4, [0, 1, 0], [8.8, 0, 64.9]),
    (5, [0, 0, 1], [0, 0, 0]),
    (6, [0, 1, 0], [0, 0, 103.3]),
    (7, [0, 0, 1], [8.8, 0, 0])
]

# Compute screw axes S_i
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

# Inverse kinematics iteration
max_iterations = 2000
epsilon = 1e-5
q_k = q_initial.copy()
a = 0.1  # Step size

# Store joint angles for convergence plot
joint_angles_history = [q_k.copy()]

for iteration in range(max_iterations):
    # Forward kinematics to get current end-effector pose
    T_wb, transformations = forward_kinematics(M, SList, q_k)
    
    # Compute error transformation
    T_err = T_wd @ np.linalg.inv(T_wb)
    
    # Compute the twist (error in world frame)
    V_w = matrix_log6(T_err)
    norm_V_w = np.linalg.norm(V_w)
    if norm_V_w < epsilon:
        print(f"Converged in {iteration} iterations")
        break
    
    # Compute space Jacobian
    J_w = jacobian_space(SList, q_k)
    
    # Compute pseudoinverse of Jacobian with damping for stability
    damping = 1e-6
    # Corrected computation of pseudoinverse
    J_w_pinv = J_w.T @ np.linalg.inv(J_w @ J_w.T + damping * np.eye(6))
    
    # Update joint variables
    delta_q = J_w_pinv @ V_w
    q_k = q_k + a * delta_q  # Apply step size 'a'
    joint_angles_history.append(q_k.copy())

print("\nFinal joint angles q_k (radians):")
print(np.round(q_k, 4))

# Convert joint angles to degrees and wrap within [-180, 180]
q_k_deg = np.degrees(q_k)
q_k_deg = (q_k_deg + 180) % 360 - 180
print("\nFinal joint angles q_k (degrees):")
print(np.round(q_k_deg, 2))

# Verify results with forward kinematics
T_final, transformations_final = forward_kinematics(M, SList, q_k)
print("\nFinal transformation matrix T_wb:")
print(T_final)
print("\nDesired transformation matrix T_wd:")
print(T_wd)

# Visualization code

# Define the plotting functions
def draw_frame(ax, T, label):
    origin = T[:3, 3]
    x_dir = T[:3, 0]
    y_dir = T[:3, 1]
    z_dir = T[:3, 2]
    length = 5  # Adjust as needed
    ax.quiver(*origin, *(x_dir * length), color='r', arrow_length_ratio=0.1)
    ax.quiver(*origin, *(y_dir * length), color='g', arrow_length_ratio=0.1)
    ax.quiver(*origin, *(z_dir * length), color='b', arrow_length_ratio=0.1)
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

    # Transform the corners to the box frame
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

    # Transform the cylindrical hole coordinates
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

def draw_robot(ax, transformations, color='grey', label_prefix=''):
    """Draws the robot manipulator based on joint transformations."""
    for i, T in enumerate(transformations):
        if i > 0:
            p_prev = transformations[i - 1][:3, 3]
            p_curr = T[:3, 3]
            ax.plot([p_prev[0], p_curr[0]], [p_prev[1], p_curr[1]], [p_prev[2], p_curr[2]], color=color)
        # Optionally, you can label each frame
        # draw_frame(ax, T, f"{label_prefix}Frame {i}")

# Transformation matrices
cylinder_radius = 2.5  
cylinder_height = 25

T_world_box = np.array([
    [0, 1, 0, 50],   
    [1, 0, 0, 50],
    [0, 0, 1, 10],
    [0, 0, 0, 1]
])

# Rotation of -90 degrees about the y-axis to align cylinder's local z-axis along the world x-axis
theta = np.deg2rad(-90)
cos_theta = np.cos(theta)
sin_theta = np.sin(theta)
R_y_neg90 = np.array([
    [cos_theta, 0, sin_theta],
    [0, 1, 0],
    [-sin_theta, 0, cos_theta]
])

# Position of the cylinder (desired position)
T_world_cylinder = np.eye(4)
T_world_cylinder[:3, :3] = R_y_neg90
T_world_cylinder[:3, 3] = T_wd[:3, 3]  # Use the desired position

# Plotting the frames
fig = plt.figure(figsize=(12, 8))

# Plot final configuration
ax1 = fig.add_subplot(111, projection='3d')
ax1.set_title("Final Configuration")
ax1.set_xlim([0, 100])
ax1.set_ylim([0, 100])
ax1.set_zlim([0, 50])
ax1.set_xlabel("X (cm)")
ax1.set_ylabel("Y (cm)")
ax1.set_zlabel("Z (cm)")
draw_frame(ax1, np.eye(4), "World Frame")
draw_frame(ax1, T_world_box, "Box Frame")
draw_box_with_hole(ax1, T_world_box, width=20, height=10, depth=40, hole_radius=5)
draw_frame(ax1, T_world_cylinder, "Cylinder Frame")
draw_cylinder(ax1, T_world_cylinder, radius=cylinder_radius, height=cylinder_height)
# Removed drawing of the robot manipulator
# draw_robot(ax1, transformations_final, color='blue', label_prefix='')

plt.tight_layout()
plt.show()

# -------------------------------
# Convergence Plot
# -------------------------------

# Convert joint angles history to a NumPy array for easier indexing
joint_angles_history = np.array(joint_angles_history)

# Convert joint angles to degrees and wrap within [-180, 180]
joint_angles_history_deg = np.degrees(joint_angles_history)
joint_angles_history_deg = (joint_angles_history_deg + 180) % 360 - 180

# Plotting the convergence of joint angles
plt.figure(figsize=(10, 6))
for i in range(joint_angles_history_deg.shape[1]):
    plt.plot(joint_angles_history_deg[:, i], label=f"Joint {i+1}")
plt.title("Convergence of Joint Angles")
plt.xlabel("Iteration")
plt.ylabel("Joint Angle (degrees)")
plt.legend()
plt.grid(True)
plt.show()

