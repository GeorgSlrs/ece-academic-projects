import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.linalg import inv

###############################################################################
#                           HELPER FUNCTIONS
###############################################################################

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

###############################################################################
#                       FORWARD KINEMATICS & JACOBIAN
###############################################################################

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
        S = S_list[:, i].reshape((6,1))
        J_b[:, i] = adjoint(np.linalg.inv(T)) @ S.flatten()
        T = matrix_exp6(-se3(S.flatten() * thetas[i])) @ T

    return J_b

###############################################################################
#                           TRAJECTORY GENERATION
###############################################################################

class TrajectoryGenerator:
    """
    A cubic-spline-based trajectory generator in SE(3).
    Generates separate cubic splines for position and Euler angles.
    """

    def __init__(self, T_total):
        self.T_total = T_total  # duration of each trajectory segment

    def generate_trajectory(self, T_start, T_goal, Vs_start=np.zeros(6), Vg_goal=np.zeros(6)):
        """
        Returns two functions:
          pos_func(t) -> R^3,  orientation_func(t) -> Euler angles in R^3
        that define desired position & orientation over time 0 <= t <= T_total.
        
        Vs_start: initial twist vector (6,)
        Vg_goal: final twist vector (6,)
        """
        # Extract start and goal positions
        p_start = T_start[:3, 3]
        p_goal  = T_goal[:3, 3]

        # Convert start & goal rotations to Euler angles
        e_start = rotation_matrix_to_euler(T_start[:3, :3])
        e_goal  = rotation_matrix_to_euler(T_goal[:3, :3])

        # Build the cubic polynomial coefficients for each position axis
        A_pos = []
        for i in range(3):
            # Using boundary conditions:
            # pos(0) = p_start[i], pos(T) = p_goal[i],
            # pos'(0) = Vs_start[i + 3], pos'(T) = Vg_goal[i + 3]
            a0 = p_start[i]
            a1 = Vs_start[i + 3]
            a2 = (3*(p_goal[i] - p_start[i]) - (2*Vs_start[i + 3] + Vg_goal[i + 3])*self.T_total) / (self.T_total**2)
            a3 = (-2*(p_goal[i] - p_start[i]) + (Vs_start[i + 3] + Vg_goal[i + 3])*self.T_total) / (self.T_total**3)
            A_pos.append((a0, a1, a2, a3))

        # Build the cubic polynomial coefficients for each orientation axis (Euler angles)
        A_ori = []
        for i in range(3):
            a0 = e_start[i]
            a1 = Vs_start[i]  # angular velocity components
            a2 = (3*(e_goal[i] - e_start[i]) - (2*Vs_start[i] + Vg_goal[i])*self.T_total) / (self.T_total**2)
            a3 = (-2*(e_goal[i] - e_start[i]) + (Vs_start[i] + Vg_goal[i])*self.T_total) / (self.T_total**3)
            A_ori.append((a0, a1, a2, a3))

        # Define the position trajectory function
        def pos_traj(t):
            if t < 0: 
                t = 0
            if t > self.T_total: 
                t = self.T_total
            pos = np.array([0.0, 0.0, 0.0])
            for i, (a0, a1, a2, a3) in enumerate(A_pos):
                pos[i] = a0 + a1*t + a2*(t**2) + a3*(t**3)
            return pos

        # Define the orientation trajectory function
        def ori_traj(t):
            if t < 0:
                t = 0
            if t > self.T_total:
                t = self.T_total
            euler = np.array([0.0, 0.0, 0.0])
            for i, (a0, a1, a2, a3) in enumerate(A_ori):
                euler[i] = a0 + a1*t + a2*(t**2) + a3*(t**3)
            return euler

        return pos_traj, ori_traj

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

###############################################################################
#                               PI CONTROLLER
###############################################################################

class PIController:
    """
    PI controller for 6D task-space error X_e in the body frame.
    V = Kp * X_e + Ki * integral(X_e dt)
    """
    def __init__(self, Kp, Ki, integral_limit=None):
        self.Kp = Kp
        self.Ki = Ki
        self.integral_error = np.zeros((6,1))
        self.integral_limit = integral_limit  # Optional: limit for integral windup

    def compute_control(self, error_6x1, dt):
        """
        error_6x1: shape (6,1)
        dt: scalar time step
        returns: V (6,1)
        """
        # Accumulate integral
        self.integral_error += error_6x1 * dt

        # Anti-windup: Clamp the integral term if limits are set
        if self.integral_limit is not None:
            self.integral_error = np.clip(self.integral_error, -self.integral_limit, self.integral_limit)

        # Compute control law
        V = self.Kp @ error_6x1 + self.Ki @ self.integral_error
        return V

###############################################################################
#                           DRAWING / VISUALIZATION
###############################################################################

def draw_frame(ax, T, label):
    """
    Draws a coordinate frame (x, y, z axes) based on the transformation matrix T.
    """
    origin = T[:3, 3]
    x_dir = T[:3, 0]
    y_dir = T[:3, 1]
    z_dir = T[:3, 2]
    
    length = 5.0  # length for the quivers
    ax.quiver(*origin, *x_dir, color='r', length=length, arrow_length_ratio=0.2)
    ax.quiver(*origin, *y_dir, color='g', length=length, arrow_length_ratio=0.2)
    ax.quiver(*origin, *z_dir, color='b', length=length, arrow_length_ratio=0.2)
    
    ax.text(*origin, f" {label}", color='black', fontsize=10)

def draw_box_with_hole(ax, T, width=20, height=20, depth=40, hole_radius=5):
    """
    Draws a rectangular box (cuboid) with a cylindrical hole.
    T is 4x4 transform in the world frame for the box.
    """
    # Define corners in local box frame
    box_corners = np.array([
        [-width/2, -depth/2, 0,       1],
        [ width/2, -depth/2, 0,       1],
        [ width/2,  depth/2, 0,       1],
        [-width/2,  depth/2, 0,       1],
        [-width/2, -depth/2, height,  1],
        [ width/2, -depth/2, height,  1],
        [ width/2,  depth/2, height,  1],
        [-width/2,  depth/2, height,  1]
    ])
    
    # Transform corners to world frame
    box_corners_world = (T @ box_corners.T).T[:, :3]
    
    # Define faces
    faces = [
        [box_corners_world[j] for j in [0, 1, 2, 3]],  # Bottom face
        [box_corners_world[j] for j in [4, 5, 6, 7]],  # Top face
        [box_corners_world[j] for j in [0, 1, 5, 4]],  # Front face
        [box_corners_world[j] for j in [2, 3, 7, 6]],  # Back face
        [box_corners_world[j] for j in [1, 2, 6, 5]],  # Right face
        [box_corners_world[j] for j in [3, 0, 4, 7]]   # Left face
    ]
    
    box_poly = Poly3DCollection(faces, color='red', alpha=0.3, edgecolor='k')
    ax.add_collection3d(box_poly)
    
    # Cylindrical hole
    z_vals = np.linspace(0, height, 50)
    theta_vals = np.linspace(0, 2*np.pi, 50)
    theta_vals, z_vals = np.meshgrid(theta_vals, z_vals)
    
    x_hole_local = hole_radius * np.cos(theta_vals)
    y_hole_local = hole_radius * np.sin(theta_vals)
    
    ones = np.ones(x_hole_local.size)
    hole_points_local = np.vstack((x_hole_local.ravel(), y_hole_local.ravel(), z_vals.ravel(), ones))
    hole_points_world = T @ hole_points_local
    
    x_hole = hole_points_world[0,:].reshape(x_hole_local.shape)
    y_hole = hole_points_world[1,:].reshape(y_hole_local.shape)
    z_hole = hole_points_world[2,:].reshape(z_vals.shape)
    
    ax.plot_surface(x_hole, y_hole, z_hole, color='blue', alpha=0.6)

def draw_cylinder(ax, T, radius=2.5, height=25):
    """
    Draws a cylinder aligned with the local z-axis, then transformed by T.
    """
    theta_vals = np.linspace(0, 2*np.pi, 50)
    z_vals = np.linspace(-height/2, height/2, 50)
    theta_vals, z_vals = np.meshgrid(theta_vals, z_vals)
    
    x_local = radius * np.cos(theta_vals)
    y_local = radius * np.sin(theta_vals)
    
    ones = np.ones(x_local.size)
    cylinder_local = np.vstack((x_local.ravel(), y_local.ravel(), z_vals.ravel(), ones))
    cylinder_world = T @ cylinder_local
    
    x_world = cylinder_world[0,:].reshape(x_local.shape)
    y_world = cylinder_world[1,:].reshape(y_local.shape)
    z_world = cylinder_world[2,:].reshape(z_vals.shape)
    
    ax.plot_surface(x_world, y_world, z_world, color='orange', alpha=0.6)

def draw_robot(ax, joint_angles, S_list, M_robot, color='green'):
    """
    Draws the robot based on current joint angles using forward kinematics.
    """
    T = np.eye(4)
    points = [T[:3, 3]]
    
    for i in range(len(joint_angles)):
        S = S_list[:, i]
        se3_mat = se3(S * joint_angles[i])
        T = T @ matrix_exp6(se3_mat)
        points.append(T[:3, 3])
    
    # Final end-effector
    T = T @ M_robot
    points.append(T[:3, 3])
    
    points = np.array(points)
    
    ax.plot(points[:,0], points[:,1], points[:,2], color=color, linewidth=2)
    ax.scatter(points[:,0], points[:,1], points[:,2], color='red', s=50)

def draw_robot_joints(ax, joint_positions):
    """
    Draws static reference positions of (named) joints.
    """
    joint_names = list(joint_positions.keys())
    for i in range(len(joint_names) - 1):
        start = joint_positions[joint_names[i]]
        end   = joint_positions[joint_names[i + 1]]
        ax.plot([start[0], end[0]],
                [start[1], end[1]],
                [start[2], end[2]],
                'k-', linewidth=2)
        ax.scatter(*start, color='red', s=50)
        ax.text(*start, f"{joint_names[i]}", color='black', fontsize=8)
    
    last_joint_name = joint_names[-1]
    last_joint = joint_positions[last_joint_name]
    ax.scatter(*last_joint, color='blue', s=70, label="End Effector")
    ax.text(*last_joint, f"{last_joint_name}", color='black', fontsize=8)

###############################################################################
#                             MAIN SIMULATION
###############################################################################

def main():
    """
    Main function to run the simulation and visualize
    the robot performing a grasp and release on a cylinder
    over a box with a hole.
    """
    # 1. Define Robot Kinematics
    def compute_screw_axis(r, q):
        """
        S = [r; - r x q]
        where r is the axis of rotation (unit vector) and q is a point on that axis.
        """
        v = -np.cross(r, q)
        return np.concatenate((r, v))

    # Define the 6 screw axes for the robot (6-DOF)
    # Example values; adjust based on your specific robot
    r1 = np.array([0, 0, 1])
    q1 = np.array([0, 0, 0])
    S1 = compute_screw_axis(r1, q1)
    
    r2 = np.array([0, 1, 0])
    q2 = np.array([0, 0, 33.3])
    S2 = compute_screw_axis(r2, q2)
    
    r3 = np.array([0, 0, 1])
    q3 = np.array([0, 0, 0])
    S3 = compute_screw_axis(r3, q3)
    
    r4 = np.array([0, 1, 0])
    q4 = np.array([8.8, 0, 64.9])
    S4 = compute_screw_axis(r4, q4)
    
    r5 = np.array([0, 0, 1])
    q5 = np.array([0, 0, 0])
    S5 = compute_screw_axis(r5, q5)
    
    r6 = np.array([0, 1, 0])
    q6 = np.array([0, 0, 103.3])
    S6 = compute_screw_axis(r6, q6)
    
    # Combine into one array
    S_list = np.column_stack((S1, S2, S3, S4, S5, S6))  # Shape: (6,6)
    
    # End-effector home configuration
    M_robot = np.array([
        [1, 0, 0, 50],
        [0, 1, 0, 50],
        [0, 0, 1, 45],
        [0, 0, 0,  1]
    ])
    
    # 2. Define Box & Cylinder transforms
    # Transformation matrices
    T_world_box = np.array([
        [0, 1, 0, 50],   
        [-1, 0, 0, 50],
        [0, 0, 1, 10],
        [0, 0, 0, 1]
    ])
    
    # Updated Ts1 as per user specification
    Ts1 = np.array([
        [np.sqrt(2)/2, np.sqrt(2)/2, 0, 0],
        [-np.sqrt(2)/2, np.sqrt(2)/2, 0, 10.3],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    # Grasp pose transformation (Tg1) as per user specification
    Tg1 = np.array([
        [1, 0, 0, 69.50],
        [0, 1, 0, 9.50],
        [0, 0, 1, 2.50],
        [0, 0, 0, 1    ]
    ])
    
    # Release pose transformation (Tg2) as per user specification (unchanged)
    Tg2 = np.array([
        [0, 0, -1, 50],
        [0, 1,  0, 50],
        [1, 0,  0, 45],
        [0, 0,  0, 1 ]
    ])
    
    # Starting transformation for second trajectory (Ts2 is correct)
    Ts2 = Tg1.copy()
    
    # Define starting and goal twist vectors (all zeros)
    Vs1 = np.zeros(6)    # Initial twist vector (at Ts1)
    Vg1 = np.zeros(6)    # Goal twist vector (at Tg1)
    Vs2 = np.zeros(6)    # Initial twist vector for second trajectory (at Tg1)
    Vg2 = np.zeros(6)    # Goal twist vector (at Tg2)
    
    # 3. Trajectory Generation
    T_total = 10.0  # Duration for each trajectory segment in seconds
    traj_gen = TrajectoryGenerator(T_total)
    
    # Trajectory 1: Move from Ts1 to Tg1 (Grasp)
    pos_traj1, ori_traj1 = traj_gen.generate_trajectory(Ts1, Tg1, Vs_start=Vs1, Vg_goal=Vg1)
    
    # Trajectory 2: Move from Tg1 to Tg2 (Release)
    pos_traj2, ori_traj2 = traj_gen.generate_trajectory(Tg1, Tg2, Vs_start=Vs2, Vg_goal=Vg2)
    
    # 4. PI Controller Setup
    Kp = 4.0  * np.eye(6)   # Proportional gain
    Ki = 0.04 * np.eye(6)   # Integral gain
    controller = PIController(Kp, Ki, integral_limit=10.0)  # Added integral limit for anti-windup
    
    # 5. Simulation Loop
    a = 0.1                  # Scaling factor for Euler integration
    dt = 0.1                 # Time step
    num_steps = int(2 * T_total / dt)  # Total simulation time (grasp + release)
    
    # Initialize joint angles (6-DOF robot)
    thetal = np.zeros(6)
    
    # History for joint angles and end-effector poses
    joint_history = [thetal.copy()]
    T_history = [forward_kinematics_POE(S_list, thetal, M_robot)]
    T_cylinder_history = [Ts1.copy()]  # Initial cylinder pose
    
    # Convergence logging
    error_norm_history = []  # Store ||X_e|| over time
    time_history = []        # Corresponding time stamps
    
    # Grasping state
    is_grasped = False
    
    # Cylinder's initial transformation
    T_cylinder = Ts1.copy()
    
    # To store the rigid attach offset when grasped
    T_offset_cylinder = np.eye(4)
    
    # Define joint_positions for visualization (static reference)
    joint_positions_visual = {
        "Joint 0": np.array([0,   0,   0   ]),
        "Joint 1": np.array([0,   0,  33.3]),
        "Joint 2": np.array([0,   0,  64.9]),
        "Joint 3": np.array([0,   0, 103.3]),
        "Joint 4": np.array([8.8, 0, 103.3]),
        "Joint 5": np.array([8.8, 0,  93.3]),
        "Joint 6": np.array([8.8, 0,  84.5]),
    }
    
    def get_trajectory_and_time(t):
        """
        Determines which trajectory to follow based on current time t.
        Returns the position and orientation functions along with adjusted time.
        """
        if t < T_total:
            return pos_traj1, ori_traj1, t
        else:
            return pos_traj2, ori_traj2, t - T_total

    def compute_desired_twist(pos_traj, ori_traj, t, dt):
        """
        Computes the desired twist (linear and angular velocities) from the trajectory.
        Uses numerical differentiation (finite differences).
        """
        # Current desired position and orientation
        p_current = pos_traj(t)
        e_current = ori_traj(t)
        
        # Next desired position and orientation
        p_next = pos_traj(t + dt)
        e_next = ori_traj(t + dt)
        
        # Linear velocity (finite difference)
        dp_dt = (p_next - p_current) / dt
        
        # Angular velocity (finite difference)
        de_dt = (e_next - e_current) / dt
        
        # Wrap angular velocities to [-pi, pi] to avoid discontinuities
        de_dt = (de_dt + np.pi) % (2 * np.pi) - np.pi
        
        # Combine into twist
        Vd = np.hstack((de_dt, dp_dt)).reshape((6,1))
        return Vd

    # Damped Pseudoinverse Function
    def damped_pseudoinverse(J, damping_factor=0.01):
        """
        Computes the damped pseudoinverse of matrix J.
        J_pinv = J^T (J J^T + lambda^2 I)^-1
        where lambda is the damping factor.
        """
        lambda_sq = damping_factor**2
        JT = J.T
        return JT @ inv(J @ JT + lambda_sq * np.eye(6))

    for step in range(1, num_steps + 1):
        t = step * dt
        
        # Determine which trajectory to follow
        pos_func, ori_func, local_t = get_trajectory_and_time(t)
        p_d = pos_func(local_t)
        e_d = ori_func(local_t)
        R_d = euler_to_rotation_matrix(e_d)
        
        T_d = np.eye(4)
        T_d[:3, :3] = R_d
        T_d[:3, 3] = p_d
        
        # Current end-effector pose
        T_current = forward_kinematics_POE(S_list, thetal, M_robot)
        
        # Compute error transform T_err = T_current^-1 * T_d
        T_err = np.linalg.inv(T_current) @ T_d
        
        # Log map to se(3)
        V_se3 = matrix_log6(T_err)
        
        # Extract twist coordinates X_e
        X_e = np.array([
            V_se3[2,1],
            V_se3[0,2],
            V_se3[1,0],
            V_se3[0,3],
            V_se3[1,3],
            V_se3[2,3]
        ]).reshape((6,1))
        
        # Log the norm of the error for convergence plot
        error_norm = np.linalg.norm(X_e)
        error_norm_history.append(error_norm)
        time_history.append(t)
        
        # Print the error norm
        print(f"Step {step}, Time {t:.2f}s, Error Norm ||X_e|| = {error_norm:.4f}")
        
        # Compute the control twist from the PI controller
        V_PI = controller.compute_control(X_e, dt)
        
        # Compute body Jacobian
        J_b = geometric_jacobian_POE(S_list, thetal, M_robot)
        
        # Compute joint velocities using damped pseudoinverse
        J_pinv = damped_pseudoinverse(J_b, damping_factor=0.01)  # Adjust damping_factor as needed
        q_dot = J_pinv @ V_PI  # Shape: (6,1)
        
        # Update joint angles using Euler integration with scaling factor a
        thetal += a * q_dot.flatten() * dt  # q_{k+1} = q_k + a * q_dot * dt
        
        # Update history
        joint_history.append(thetal.copy())
        T_current_new = forward_kinematics_POE(S_list, thetal, M_robot)
        T_history.append(T_current_new)
        
        # Check if close enough to grasp the cylinder
        distance_to_grasp = np.linalg.norm(T_current_new[:3, 3] - Tg1[:3, 3])
        if (not is_grasped) and (distance_to_grasp < 1.0):
            is_grasped = True
            print(f"*** Grasped the cylinder at t={t:.2f}s ***")
            # Compute the offset to maintain rigid attachment
            # T_offset = T_current^-1 * T_cylinder
            T_offset_cylinder = np.linalg.inv(T_current_new) @ T_cylinder
    
        # If grasped, update the cylinder's pose to follow the end-effector
        if is_grasped:
            T_cylinder = T_current_new @ T_offset_cylinder
    
        # Check if it's time to release the cylinder
        distance_to_release = np.linalg.norm(T_current_new[:3, 3] - Tg2[:3, 3])
        if is_grasped and (t >= T_total) and (distance_to_release < 1.0):
            is_grasped = False
            T_cylinder = Tg2.copy()
            print(f"*** Released the cylinder at t={t:.2f}s ***")
    
        T_cylinder_history.append(T_cylinder.copy())
    
    # 6. Visualization and Animation
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    def animate_robot(i):
        """
        Animation function to update the robot's position and the cylinder's position.
        """
        ax.clear()
        ax.set_title("Robot: Grasp and Release with Cylinder")
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 100])
        ax.set_zlim([0, 120])
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        
        # Draw world frame
        draw_frame(ax, np.eye(4), "World Frame")
        
        # Draw box
        draw_frame(ax, T_world_box, "Box Frame")
        draw_box_with_hole(ax, T_world_box, width=20, height=20, depth=40, hole_radius=5)
        
        # Draw cylinder
        T_cyl_i = T_cylinder_history[i]
        draw_frame(ax, T_cyl_i, "Cylinder Frame")
        draw_cylinder(ax, T_cyl_i, radius=2.5, height=25)
        
        # Draw robot
        thetal_i = joint_history[i]
        draw_robot(ax, thetal_i, S_list, M_robot, color='green')
        
        # Draw static robot joints for reference
        draw_robot_joints(ax, joint_positions_visual)
        
        if i == 0:
            ax.legend()
        
        # Set viewing angle for better visualization
        ax.view_init(elev=20., azim=-60)
    
    ani = FuncAnimation(
        fig, 
        animate_robot, 
        frames=len(joint_history),
        interval=100,  # in milliseconds
        repeat=False
    )
    
    plt.show()
    
    #######################################################
    # 7. Convergence Curves (Plot the norm of X_e over time)
    #######################################################
    
    plt.figure(figsize=(8, 6))
    plt.plot(time_history, error_norm_history, 'b-', linewidth=2)
    plt.xlabel("Time [s]")
    plt.ylabel("Task-Space Error Norm ||X_e||")
    plt.title("Convergence of End-Effector Task-Space Error")
    plt.grid(True)
    plt.show()

# Run the simulation if this script is executed
if __name__ == "__main__":
    main()

