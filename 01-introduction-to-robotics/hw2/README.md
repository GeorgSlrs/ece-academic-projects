# Introduction to Robotics — HW2

## What this assignment covers
Screw-theory / SE(3) robotics calculations, including exponential and logarithmic maps, adjoint transformations, forward kinematics and related 3D visualization.

## Main files
- `Robotics_hw2_part1.py` — main Part 1 implementation.
- `Robotics_hw2_part2.py` — Part 2 implementation.
- `Robotics_hw2_part1_v2.py` and similarly named files — intermediate/revised coursework versions retained for transparency.
- `Robotics_report_hw2_v2.pdf` — final report copy.
- `Figure_1.png`, `Figure_2.png` — result figures.

## Requirements
- Python 3
- NumPy
- Matplotlib

## Install
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install numpy matplotlib
```

## Run
Start with the final/revised scripts:

```powershell
py .\Robotics_hw2_part1_v2.py
py .\Robotics_hw2_part2.py
```

If reproducing the coursework exactly, compare the outputs with the report because several historical revisions are preserved.

## Notes
The duplicate/revision files are intentional historical artifacts, not separate projects. This is academic coursework; see the repository-level authorship note for context.
