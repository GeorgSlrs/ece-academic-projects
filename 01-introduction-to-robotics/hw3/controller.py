# controller.py

import numpy as np

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
