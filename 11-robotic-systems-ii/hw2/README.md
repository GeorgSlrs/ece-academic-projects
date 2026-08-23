# Robotic Systems II — HW2

## What this assignment covers
Control studies for a planar quadrotor model, including PD-style control, LQR/MPC comparisons, parameter/region scans and animated simulation results.

## Main files
- `RS_II_HW2_Ex1.py`, `RS_II_HW2_Ex2.py`, `RS_II_HW2_Ex3.py` — three exercise implementations.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — container setup used for the coursework.
- `RS_II_HW_2_REPORT.pdf` — report.
- `quad_*.gif`, `quad_LQR_vs_MPC_*.png`, `region_scan_theta_H24.png` — saved results/animations.

## Requirements
The supplied requirements file lists:
- NumPy
- Matplotlib
- ProxSuite
- Pillow

## Install
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r .\requirements.txt
```

## Run
```powershell
py .\RS_II_HW2_Ex1.py
py .\RS_II_HW2_Ex2.py
py .\RS_II_HW2_Ex3.py
```

The exercises are independent; you do not have to run all three every time.

## Notes
This is simulation coursework. See the repository-level authorship note for context.
