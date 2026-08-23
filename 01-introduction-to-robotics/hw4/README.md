# Introduction to Robotics — HW4

## What this assignment covers
A modular rigid-body dynamics and task-space control simulation. The implementation combines robot definitions, kinematics, dynamics, PID task-space control, numerical simulation and 3D visualization.

## Main files
- `main.py` — primary entry point.
- `kinematics.py` — robot kinematics.
- `dynamics.py` — rigid-body dynamics.
- `controller.py` — `TaskSpaceControllerPID`.
- `simulator.py` — simulation loop.
- `visualization.py` — plots and animation.
- `robot_definitions.py`, `utils.py` — robot parameters and math helpers.
- `Intro_Robotics_HW4_Report_v4.pdf` — report.
- `requirements.txt.txt` — pinned Python dependencies.

## Requirements
The supplied requirements file pins:
- NumPy 1.24.4
- SciPy 1.11.1
- Matplotlib 3.7.2

## Install
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r .\requirements.txt.txt
```

## Run
```powershell
py .\main.py
```

## Expected output
A convergence/error plot followed by an animation of the simulated robot.

## Notes
Run from this folder so the local module imports resolve correctly. This is academic coursework; see the repository-level authorship note for context.
