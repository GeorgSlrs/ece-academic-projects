# Robotic Systems II Coursework

Four assignments study control of nonlinear robotic systems, moving from hopper integration and constrained optimization to planar quadrotor simulations, double-pendulum trajectory optimization and a hardware-oriented tracking workflow. Reports, saved animations and trajectory caches document the coursework alongside the Python source.

## Subprojects

| Folder | System and methods | Starting point |
| --- | --- | --- |
| [HW1](hw1/) | One-mass hopper simulation, numerical integration comparisons, equality-constrained QP reduction and QP-based control. | `RS_II_HW_1_1.py`, `RS_II_HW_1_2.py`, `RS_II_HW_1_3.py` |
| [HW2](hw2/) | Planar quadrotor control: PD-style feedback, LQR/MPC comparisons and parameter/region scans. | `RS_II_HW2_Ex1.py`, `RS_II_HW2_Ex2.py`, `RS_II_HW2_Ex3.py` |
| [HW3](hw3/) | Nonlinear double-pendulum modelling, direct-collocation trajectory optimization with Ipopt, and TVLQR tracking/noise experiments. | `RS_II_HW_3_1.py` through `RS_II_HW_3_3.py` |
| [HW4](hw4/) | Revised physical model, nominal trajectory/TVLQR cache generation and a pyCandle/CAN motor runner. | `RS_II_HW_4_new_model.py`, `build_tvlqr_cache.py`; hardware workflow in the folder README |

## Environment

Use the instructions and dependency files inside each homework folder. HW1 uses NumPy and Matplotlib. HW2 lists NumPy, Matplotlib, ProxSuite and Pillow and includes a Dockerfile. The double-pendulum optimization work uses `cyipopt` with a compatible Ipopt installation. HW4 additionally depends on the original pyCandle/CAN hardware environment and cached trajectories.

`hw4/run.py` sends commands to physical motors; it is not a simulation entry point. Its motor IDs, connections and torque settings belong to the original laboratory setup.

Some implementation work used coding-assistant support. These are preserved coursework studies, with no claim of sole authorship of every line or of portability to a different robot without adaptation.
