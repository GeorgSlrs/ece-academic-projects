# visualization.py

import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from helpers import adjoint, matrix_exp6, se3
import matplotlib.pyplot as plt

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
    from kinematics import forward_kinematics_POE
    from helpers import matrix_exp6, se3
    
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
