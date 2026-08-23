import numpy as np
from robot_definitions import get_robot_links, get_robot_joints, get_active_joints
from utils import (
    compute_se3_transform,
    adjoint,
    skew,
    compute_spatial_inertia_matrix,
    twist_to_matrix,
    matrix_exp6,
)

class Dynamics:
    def __init__(self, kinematics):
        """
        A "closed-form" approach to compute M(q), c(q,q_dot), g(q), etc.
        """
        self.kinematics = kinematics
        self.links = get_robot_links()
        self.joints = get_robot_joints()
        self.active_joints = get_active_joints(self.joints)
        self.n_joints = len(self.active_joints)
        
        # 1) transform inertias from CoM -> body frames
        self.transform_inertias()
        
        # 2) build G_all = block diagonal of all link spatial inertias
        self.G_all = self.build_G_all()

    def transform_inertias(self):
        """
        For each link i, transform inertia from CoM to the link's 'body frame':
        G_i^i = [Ad_{T_{b->i}}]^T * G_i^b * [Ad_{T_{b->i}}].
        """
        for i in range(1, 1 + self.n_joints):
            link = self.links[i]
            if link.mass < 1e-12:
                link.G_link = np.zeros((6, 6))
                continue
            # G about CoM
            G_com = compute_spatial_inertia_matrix(
                link.mass, link.inertia_3x3_com, np.zeros(3)
            )
            # T_{b->i} is a translation by -com
            T_b2i = compute_se3_transform([0, 0, 0], -link.com)
            Ad_b2i = adjoint(T_b2i)
            G_i = Ad_b2i.T @ G_com @ Ad_b2i
            link.G_link = G_i

    def build_G_all(self):
        """
        Build block diagonal: G_all = diag(G_link1, G_link2, ..., G_linkN).
        """
        blocks = []
        for i in range(1, 1 + self.n_joints):
            blocks.append(self.links[i].G_link)

        G_all = np.block([
            [blocks[i] if i == j else np.zeros((6, 6))
             for j in range(self.n_joints)]
            for i in range(self.n_joints)
        ])
        return G_all

    def build_A_all(self, q):
        """
        A_all is 6n x 6n, with each 6x6 block containing
        the screw axis for that joint.
        """
        A_all = np.zeros((6*self.n_joints, 6*self.n_joints))
        for i in range(self.n_joints):
            S_i = self.kinematics.S_list[i].reshape((6, 1))
            # M_i = home transform of joint i
            joint_i = self.active_joints[i]
            T_i = compute_se3_transform(
                joint_i.home_transform['rpy'],
                joint_i.home_transform['xyz']
            )
            Ad_Mi_inv = adjoint(np.linalg.inv(T_i))
            A_i_6x1 = Ad_Mi_inv @ S_i  # 6x1

            row = i*6
            col = i*6
            block_6x6 = np.zeros((6, 6))
            block_6x6[:, 0] = A_i_6x1.flatten()
            A_all[row:row+6, col:col+6] = block_6x6
        return A_all

    def build_W(self, q):
        """
        W(q) is a 6n x 6n matrix with Ad_{T_{i+1,i}} blocks on the subdiagonal.
        """
        W = np.zeros((6*self.n_joints, 6*self.n_joints))
        for i in range(self.n_joints - 1):
            # T_i: transform from base to link i
            T_i = np.eye(4)
            for j in range(i+1):
                S_j = self.kinematics.S_list[j]
                theta_j = q[j]
                T_i = T_i @ matrix_exp6(twist_to_matrix(S_j), theta_j)

                # also multiply the link's home transform
                joint_j = self.active_joints[j]
                T_fixed_j = compute_se3_transform(
                    joint_j.home_transform['rpy'],
                    joint_j.home_transform['xyz']
                )
                T_i = T_i @ T_fixed_j

            joint_ip1 = self.active_joints[i+1]
            T_i_to_ip1 = compute_se3_transform(
                joint_ip1.home_transform['rpy'],
                joint_ip1.home_transform['xyz']
            )
            Ad_sub = adjoint(T_i_to_ip1)
            
            row = (i+1)*6
            col = i*6
            W[row:row+6, col:col+6] = Ad_sub
        return W

    def build_L(self, q):
        """
        L(q) = (I - W(q))^-1.
        """
        size = 6*self.n_joints
        W_ = self.build_W(q)
        I_ = np.eye(size)
        try:
            L_ = np.linalg.inv(I_ - W_)
        except np.linalg.LinAlgError:
            L_ = np.linalg.pinv(I_ - W_)
        return L_

    def convert_qdot_to_6n(self, q_dot):
        """
        Expand q_dot (n,) into 6n x 1 by placing each q_dot[i]
        in the top row of its 6x1 chunk.
        """
        x = np.zeros((6*self.n_joints, 1))
        for i in range(self.n_joints):
            x[i*6] = q_dot[i]
        return x

    def compute_V_all(self, q, q_dot):
        """
        V_all = L(q)*[A_all * q_dot + V_base], for a fixed base => V_base=0.
        """
        A_all = self.build_A_all(q)
        L_ = self.build_L(q)
        big = A_all @ self.convert_qdot_to_6n(q_dot)
        V_all = L_ @ big
        return V_all.flatten()

    def compute_ad(self, big_6n):
        """
        Build block diag of ad([w,v]) for each 6-vector chunk.
        """
        n = self.n_joints
        vec = big_6n.reshape(-1)
        ad_mat = np.zeros((6*n, 6*n))
        for i in range(n):
            w = vec[6*i : 6*i+3]
            v = vec[6*i+3 : 6*i+6]
            w_sk = skew(w)
            v_sk = skew(v)
            block = np.block([
                [w_sk,            np.zeros((3, 3))],
                [v_sk,            w_sk            ]
            ])
            ad_mat[6*i : 6*i+6, 6*i : 6*i+6] = block
        return ad_mat

    def build_ad_vector(self, V):
        """
        Same as compute_ad, but if V is shape (6n,)
        or (6n,1). Just a convenience method.
        """
        if V.ndim == 1:
            V = V.reshape(-1, 1)
        return self.compute_ad(V)

    def compute_mass_matrix(self, q):
    
        A_all = self.build_A_all(q)
        L_ = self.build_L(q)
        big_6n = A_all.T @ L_.T @ self.G_all @ L_ @ A_all
        N = self.n_joints
        M = big_6n[:N, :N]
        return M

    def compute_coriolis(self, q, q_dot):
        """
        c(q,q_dot) = partial expression for demonstration.
        """
        A_all = self.build_A_all(q)
        L_ = self.build_L(q)
        W_ = self.build_W(q)

        # build 6n vector of A_all*q_dot
        big_qdot_6n = self.convert_qdot_to_6n(q_dot)
        ad_Aqdot = self.compute_ad(big_qdot_6n)

        V_all = self.compute_V_all(q, q_dot)
        ad_V_all = self.build_ad_vector(V_all)

        # minimal partial:
        left = self.G_all @ L_ @ (ad_Aqdot @ W_)
        mid = left @ L_ @ A_all @ big_qdot_6n
        c_6n = -A_all.T @ L_.T @ mid

        # pick out first n
        N = self.n_joints
        c = c_6n[:N].flatten()
        return c

    def compute_gravity(self, q):
        """
        g(q) = A_all^T * L(q)^T * G_all * L(q) * V_base_dot
        with V_base_dot = [0,0,-9.81,0,0,0,...].
        """
        A_all = self.build_A_all(q)
        L_ = self.build_L(q)

        V_base_dot = np.zeros((6*self.n_joints, 1))
        for i in range(self.n_joints):
            V_base_dot[i*6 + 2] = -9.81

        big_6n = A_all.T @ L_.T @ self.G_all @ L_ @ V_base_dot
        N = self.n_joints
        g = big_6n[:N].flatten()
        return g
