import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

class Visualization:
    def __init__(self, kinematics, dt):
        self.kinematics = kinematics
        self.dt = dt
    
    def animate(self, history_q, history_ee):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim([-0.5, 0.5])
        ax.set_ylim([-0.5, 0.5])
        ax.set_zlim([0, 1.0])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Robot Simulation')
        
        line_robot, = ax.plot([], [], [], 'bo-', lw=2, label='Links')
        line_ee, = ax.plot([], [], [], 'r-', lw=1, label='EE Path')
        
        ee_path_x, ee_path_y, ee_path_z = [], [], []
        
        def init():
            line_robot.set_data([], [])
            line_robot.set_3d_properties([])
            line_ee.set_data([], [])
            line_ee.set_3d_properties([])
            return line_robot, line_ee
        
        def update(frame):
            q = history_q[frame]
            
            from utils import matrix_exp6, twist_to_matrix, compute_se3_transform
            
            positions = [np.array([0.0, 0.0, 0.0])]
            T = np.eye(4)
            for i in range(self.kinematics.n_joints):
                S_i = self.kinematics.S_list[i]
                theta_i = q[i]
                dT = matrix_exp6(twist_to_matrix(S_i), theta_i)
                T = T @ dT
                j_i = self.kinematics.active_joints[i]
                T_fixed = compute_se3_transform(
                    j_i.home_transform['rpy'],
                    j_i.home_transform['xyz']
                )
                T_link = T @ T_fixed
                positions.append(T_link[:3, 3])
            
            arr_pos = np.array(positions)
            line_robot.set_data(arr_pos[:,0], arr_pos[:,1])
            line_robot.set_3d_properties(arr_pos[:,2])
            
            ee_pos = arr_pos[-1]
            ee_path_x.append(ee_pos[0])
            ee_path_y.append(ee_pos[1])
            ee_path_z.append(ee_pos[2])
            line_ee.set_data(ee_path_x, ee_path_y)
            line_ee.set_3d_properties(ee_path_z)
            
            return line_robot, line_ee
        
        ani = animation.FuncAnimation(
            fig, update, frames=len(history_q),
            init_func=init, blit=False, interval=200
        )
        ax.legend()
        plt.show()
    
    def plot_convergence(self, history_t, history_ee, history_ee_des):
        arr_ee = np.array(history_ee)
        arr_ee_des = np.array(history_ee_des)
        errors = arr_ee_des - arr_ee
        norms = np.linalg.norm(errors, axis=1)
        
        plt.figure()
        plt.plot(history_t, norms, 'b-', label='||p_des - p||')
        plt.xlabel('Time (s)')
        plt.ylabel('Position Error Norm (m)')
        plt.title('End-Effector Convergence')
        plt.grid(True)
        plt.legend()
        plt.show()
