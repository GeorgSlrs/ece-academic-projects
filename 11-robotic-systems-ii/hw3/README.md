# Robotic Systems II — HW3

## What this assignment covers
Double-pendulum control and trajectory optimization. The three parts cover the nonlinear model, Hermite-Simpson/cubic-spline direct collocation using Ipopt, and TVLQR tracking with noise/Monte-Carlo visualization.

## Main files
- `RS_II_HW_3_1.py` — nonlinear double-pendulum simulation/control work.
- `RS_II_HW_3_2.py` — trajectory optimization with `cyipopt`.
- `RS_II_HW_3_3.py` — nominal trajectory + TVLQR tracking/noise experiments.
- `RS_II_HW_3_Report_v2.pdf` — report.
- `requirements.txt.txt` — dependencies.

## Requirements
The supplied requirements file lists:
- NumPy
- Matplotlib
- cyipopt

`cyipopt` also requires an Ipopt installation compatible with your operating system/Python environment.

## Install
Create a virtual environment, then install the dependencies. For environments where Ipopt is already available:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install numpy matplotlib cyipopt
```

If `cyipopt` installation fails, install Ipopt through a suitable Conda/system package first.

## Run
```powershell
py .\RS_II_HW_3_1.py
py .\RS_II_HW_3_2.py
py .\RS_II_HW_3_3.py
```

## Notes
Optimization can take noticeably longer than the basic simulation. This is academic coursework; see the repository-level authorship note for context.
