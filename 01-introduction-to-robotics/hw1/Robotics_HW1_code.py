import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

cylinder_radius = 2.5
cylinder_height = 25

T_world_box = np.array([
    [0, 1, 0, 50],
    [-1, 0, 0, 50],
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
T_world_cylinder[:3, 3] = [69.50, 9.50, 2.50]

T_manipulated_box = T_world_box.copy()
T_manipulated_cylinder = np.eye(4)
T_manipulated_cylinder[:3, 3] = [50, 50, 45]

def draw_frame(ax, T, label):
    origin = T[:3, 3]
    x_dir = T[:3, 0]
    y_dir = T[:3, 1]
    z_dir = T[:3, 2]
    ax.quiver(*origin, *x_dir, color='r', length=5, arrow_length_ratio=0.1)
    ax.quiver(*origin, *y_dir, color='g', length=5, arrow_length_ratio=0.1)
    ax.quiver(*origin, *z_dir, color='b', length=5, arrow_length_ratio=0.1)
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
        [transformed_corners[j] for j in [0, 1, 2, 3]],
        [transformed_corners[j] for j in [4, 5, 6, 7]],
        [transformed_corners[j] for j in [0, 1, 5, 4]],
        [transformed_corners[j] for j in [2, 3, 7, 6]],
        [transformed_corners[j] for j in [1, 2, 6, 5]],
        [transformed_corners[j] for j in [3, 0, 4, 7]]
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

def draw_cylinder(ax, T, radius=2.5, height=25):
    theta = np.linspace(0, 2 * np.pi, 50)
    z = np.linspace(-height / 2, height / 2, 50)
    theta, z = np.meshgrid(theta, z)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    ones = np.ones(x.shape).flatten()
    points = np.vstack((x.flatten(), y.flatten(), z.flatten(), ones))
    transformed_points = T @ points
    x = transformed_points[0, :].reshape(theta.shape)
    y = transformed_points[1, :].reshape(theta.shape)
    z = transformed_points[2, :].reshape(theta.shape)
    ax.plot_surface(x, y, z, color='orange', alpha=0.6)

fig = plt.figure(figsize=(14, 10))
ax1 = fig.add_subplot(121, projection='3d')
ax1.set_title('Initial Positions')
ax1.set_xlim([0, 100]); ax1.set_ylim([0, 100]); ax1.set_zlim([0, 50])
ax1.set_xlabel('X (cm)'); ax1.set_ylabel('Y (cm)'); ax1.set_zlabel('Z (cm)')
draw_frame(ax1, np.eye(4), 'World Frame')
draw_frame(ax1, T_world_box, 'Box Frame')
draw_box_with_hole(ax1, T_world_box, width=20, height=10, depth=40, hole_radius=5)
draw_frame(ax1, T_world_cylinder, 'Cylinder Frame')
draw_cylinder(ax1, T_world_cylinder, radius=cylinder_radius, height=cylinder_height)

ax2 = fig.add_subplot(122, projection='3d')
ax2.set_title('After Manipulation')
ax2.set_xlim([0, 100]); ax2.set_ylim([0, 100]); ax2.set_zlim([0, 50])
ax2.set_xlabel('X (cm)'); ax2.set_ylabel('Y (cm)'); ax2.set_zlabel('Z (cm)')
draw_frame(ax2, np.eye(4), 'World Frame')
draw_frame(ax2, T_manipulated_box, 'Manipulated Box Frame')
draw_box_with_hole(ax2, T_manipulated_box, width=20, height=10, depth=40, hole_radius=5)
draw_frame(ax2, T_manipulated_cylinder, 'Cylinder Frame')
draw_cylinder(ax2, T_manipulated_cylinder, radius=cylinder_radius, height=cylinder_height)

plt.tight_layout()
plt.show()
