# Introduction to Robotics — HW3

## What this assignment covers
Robot kinematics, trajectory generation and feedback control in simulation. The folder contains both a larger single-file version and a modular implementation with controller, kinematics, trajectory, simulator and visualization modules.

## Main files
- `Robotics_hw3_part1.py` — self-contained/large implementation.
- `simulator.py` — modular simulation entry point and integration logic.
- `controller.py` — PI feedback controller.
- `kinematics.py` — forward kinematics and geometric Jacobian routines.
- `trajectory.py` — desired trajectory generation.
- `helpers.py` — SE(3) utilities.
- `visualization.py` — plotting/animation.
- `Intro_Robotics_HW3_Report.pdf` — report.
- `requirements.txt.txt` — dependency list.

## Requirements
The supplied requirements file contains:
- NumPy
- Matplotlib
- SciPy

## Install
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r .\requirements.txt.txt
```

## Run
The self-contained coursework script can be started with:

```powershell
py .\Robotics_hw3_part1.py
```

The modular files are also useful for inspecting the controller/kinematics structure separately.

## Expected output
Plots and an animation of the simulated robot/trajectory tracking.

## Notes
This is academic coursework; see the repository-level authorship note for context.
