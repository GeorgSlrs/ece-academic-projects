import numpy as np
from robot_definitions import get_robot_links, get_robot_joints, get_active_joints
from utils import compute_se3_transform, twist_to_matrix, matrix_exp6, adjoint, skew

class Kinematics:
    def __init__(self):
        self.links = get_robot_links()
        self.joints = get_robot_joints()
        self.active_joints = get_active_joints(self.joints)
        self.n_joints = len(self.active_joints)
        
        self.S_list = []
        self.define_screw_axes()
    
    def define_screw_axes(self):
        for i, joint in enumerate(self.active_joints):
            w = joint.axis
            pivot = np.array(joint.home_transform['xyz'])
            S_local = np.hstack([w, -np.cross(w, pivot)])
            
            M_i = compute_se3_transform(
                joint.home_transform['rpy'],
                joint.home_transform['xyz']
            )
            Ad_inv = adjoint(np.linalg.inv(M_i))
            S_space = Ad_inv @ S_local
            
            self.S_list.append(S_space)
    
    def forward_kinematics(self, q):
        T = np.eye(4)
        for i in range(self.n_joints):
            S_i = self.S_list[i]
            theta_i = q[i]
            T = T @ matrix_exp6(twist_to_matrix(S_i), theta_i)
        
        # multiply transform from last joint to link_5
        last_joint = self.joints[-1]
        T_fixed = compute_se3_transform(
            last_joint.home_transform['rpy'],
            last_joint.home_transform['xyz']
        )
        T = T @ T_fixed
        return T
    
    def compute_jacobian(self, q):
        J = np.zeros((6, self.n_joints))
        T_current = np.eye(4)
        for i in range(self.n_joints):
            J[:, i] = adjoint(T_current) @ self.S_list[i]
            dT = matrix_exp6(twist_to_matrix(self.S_list[i]), q[i])
            T_current = T_current @ dT
        return J
