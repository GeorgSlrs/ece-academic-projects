# simulator.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from controller import PIController
from kinematics import forward_kinematics_POE, geometric_jacobian_POE
from trajectory import TrajectoryGenerator
from visualization import (
    draw_frame,
    draw_box_with_hole,
    draw_cylinder,
    draw_robot,
    draw_robot_joints
)
from helpers import adjoint, matrix_log6, euler_to_rotation_matrix

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
        return JT @ np.linalg.inv(J @ JT + lambda_sq * np.eye(6))

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
