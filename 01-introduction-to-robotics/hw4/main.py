import numpy as np
import matplotlib.pyplot as plt

from kinematics import Kinematics
from dynamics import Dynamics
from controller import TaskSpaceControllerPID  # <-- IMPORTANT: correct import
from simulator import Simulator
from visualization import Visualization

def main():
    # 1. Simulation parameters
    duration = 5.0
    dt = 0.01
    amplitude = np.array([0.2, 0.2, 0.2])  # sinusoid amplitude (m)
    frequency = 0.25                      # frequency (Hz)
    base_pos = np.array([0.0, 0.0, 0.0])

    # 2. Build kinematics & dynamics
    kin = Kinematics()
    dyn = Dynamics(kin)

    # 3. PID gains for task-space control
    Kp = np.diag([50, 50, 50])
    Kd = np.diag([10, 10, 10])
    Ki = np.diag([2, 2, 2])   # optional integral gains

    # 4. Create the PID controller
    #    (Previously you had 'TaskSpaceController', but the class is named 'TaskSpaceControllerPID')
    ctrl = TaskSpaceControllerPID(kin, dyn, Kp, Kd, Ki)

    # 5. Create the simulator
    sim = Simulator(dyn, ctrl, dt)

    # 6. Initial states
    q_init = np.zeros(kin.n_joints)
    q_dot_init = np.zeros(kin.n_joints)

    print("Starting simulation...")
    history_t, history_q, history_q_dot, history_ee, history_ee_des = sim.simulate(
        q_init, q_dot_init, duration, amplitude, frequency, base_pos
    )
    print("Simulation completed.")

    # 7. Plot the end-effector error norm
    viz = Visualization(kin, dt)
    viz.plot_convergence(history_t, history_ee, history_ee_des)

    # 8. Animate
    viz.animate(history_q, history_ee)

if __name__ == "__main__":
    main()
