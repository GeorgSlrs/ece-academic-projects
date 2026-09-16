# Introduction to Robotics Coursework

Four Python assignments trace the path from coordinate geometry to simulated robot control: representing rigid-body poses, computing manipulator kinematics, following a desired trajectory, and adding rigid-body dynamics to the control loop. Reports and saved figures accompany the implementations.

## Assignments

| Folder | Focus | Starting point |
| --- | --- | --- |
| [HW1](hw1/) | Homogeneous transformations, reference frames and 3D object geometry | `Robotics_HW1_code.py` |
| [HW2](hw2/) | SE(3) exponential/logarithmic maps, adjoint transformations and screw-theory forward kinematics | `Robotics_hw2_part1_v2.py`, `Robotics_hw2_part2.py` |
| [HW3](hw3/) | Geometric Jacobians, trajectory generation and PI feedback in simulation | `Robotics_hw3_part1.py`; modular controller/kinematics/trajectory files |
| [HW4](hw4/) | Mass, Coriolis and gravity terms with task-space PID control | `main.py` |

## Exploring the work

Start with the README and report inside the assignment of interest. HW1–HW2 use NumPy and Matplotlib; HW3–HW4 also list SciPy. The later folders include dependency files named `requirements.txt.txt`. Run scripts from their own homework directories so local imports resolve.

The scripts produce plots or animations of the simulated geometry and motion. Historical revisions are retained, especially in HW2 and HW3, so the reports provide useful context when comparing versions.

This is academic coursework, including some coding-assistant-supported development. The collection documents the exercises and their implementations without claiming sole authorship of every line or validation on physical robots.
