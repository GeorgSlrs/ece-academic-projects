import numpy as np

class Simulator:
    def __init__(self, dynamics, controller, dt):
        self.dynamics = dynamics
        self.controller = controller
        self.dt = dt
    
    def compute_desired_trajectory(self, t, amplitude, frequency, base_pos=np.zeros(3)):
        """
        x_des(t) = base_pos + amplitude * sin(2π f t)
        x'_des(t) = 2π f * amplitude * cos(2π f t)
        """
        pos_des = base_pos + amplitude * np.sin(2*np.pi*frequency*t)
        vel_des = (2*np.pi*frequency) * amplitude * np.cos(2*np.pi*frequency*t)
        return pos_des, vel_des
    
    def simulate(self, q_init, q_dot_init, duration,
                 amplitude, frequency, base_pos=np.zeros(3)):
        a = 0.1;
        n_steps = int(duration / self.dt)
        q = q_init.copy()
        q_dot = q_dot_init.copy()
        
        history_t = []
        history_q = []
        history_q_dot = []
        history_ee = []
        history_ee_des = []
        
        for step in range(n_steps):
            t = step * self.dt
            pos_des, vel_des = self.compute_desired_trajectory(t, amplitude, frequency, base_pos)
            
            # IMPORTANT: pass dt to the controller
            tau = self.controller.compute_control_torque(q, q_dot, pos_des, vel_des, self.dt)
            
            # Compute M, c, g
            M = self.dynamics.compute_mass_matrix(q)
            c = self.dynamics.compute_coriolis(q, q_dot)
            g = self.dynamics.compute_gravity(q)
            
            # Forward dynamics
            rhs = tau - c - g
            try:
                q_ddot = np.linalg.solve(M, rhs)
            except np.linalg.LinAlgError:
                q_ddot = np.linalg.pinv(M) @ rhs
            
            # Euler integration
            q_dot += a*q_ddot * self.dt
            q += q_dot * self.dt
            
            # Record
            history_t.append(t)
            history_q.append(q.copy())
            history_q_dot.append(q_dot.copy())
            
            # End-effector actual
            T_ee = self.dynamics.kinematics.forward_kinematics(q)
            ee_pos = T_ee[:3, 3]
            history_ee.append(ee_pos.copy())

            # Desired
            history_ee_des.append(pos_des.copy())
            
            if step % 50 == 0:
                print(f"Step {step}/{n_steps}, t={t:.2f}, q={q}")
        
        return history_t, history_q, history_q_dot, history_ee, history_ee_des
