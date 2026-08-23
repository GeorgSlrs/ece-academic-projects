# trajectory.py

import numpy as np
from helpers import rotation_matrix_to_euler, euler_to_rotation_matrix

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
