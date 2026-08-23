import numpy as np

class TaskSpaceControllerPID:
    def __init__(self, kinematics, dynamics, Kp, Kd, Ki):
        """
        PID control in task space.
        """
        self.kinematics = kinematics
        self.dynamics = dynamics
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki

        # Integral of position error
        self.integral_pos_error = np.zeros(3)

    def compute_control_torque(self, q, q_dot, desired_pos, desired_vel, dt):
        """
        tau = J_lin^T * [ Kp*pos_err + Kd*vel_err + Ki*∫pos_err ]
        """
        # 1. Current end-effector position
        T_ee = self.kinematics.forward_kinematics(q)
        current_pos = T_ee[:3, 3]

        # 2. Position error
        pos_err = desired_pos - current_pos

        # 3. Linear Jacobian
        J = self.kinematics.compute_jacobian(q)
        J_lin = J[:3, :]

        # 4. End-effector linear velocity
        v_current = J_lin @ q_dot
        vel_err = desired_vel - v_current

        # 5. Update integral
        self.integral_pos_error += pos_err * dt

        # 6. Task-space force
        F_task = (self.Kp @ pos_err) \
                 + (self.Kd @ vel_err) \
                 + (self.Ki @ self.integral_pos_error)

        # 7. Map to joint torques
        tau = J_lin.T @ F_task
        return tau
