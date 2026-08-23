# Robotic Systems II — HW4

## What this assignment covers
Hardware-oriented continuation of the double-pendulum/TVLQR work. The folder includes a revised physical model, cached nominal/TVLQR trajectories and a `pyCandle` runner for CAN-connected motor hardware.

## Main files
- `RS_II_HW_4_new_model.py` — revised double-pendulum model/simulation.
- `build_tvlqr_cache.py` — generates the TVLQR cache.
- `tvlqr_cache.npz` — precomputed cache.
- `run.py` — hardware runner using `pyCandle`.
- `projection_helper.py` — trajectory/projection helper functions.
- `Report (3).pdf` / `Report.docx` — report.
- `READ_ME.txt` — original setup notes.

## Requirements
The original notes mention:
- Python 3.9 environment
- NumPy
- Matplotlib
- `cyipopt` / Ipopt
- `pyCandleMAB` / `pyCandle`
- WSL/Ubuntu and `usbipd` for the hardware setup

## Typical workflow
For simulation/model work, start with the Python model scripts.

For the hardware-oriented path, the original coursework notes specify:
1. Build/rebuild the cache with `build_tvlqr_cache.py`.
2. Verify the hardware connection and motor IDs.
3. Run `run.py`.

## Hardware caution
`run.py` sends motor torque commands. Do not run it on connected hardware unless the mechanism is secured, torque limits and motor IDs have been verified, and an appropriate emergency-stop/power-disconnect procedure is available.

## Notes
The exact USB/CAN setup is machine-specific; `READ_ME.txt` preserves the original WSL/usbipd commands used during the coursework. This is academic coursework; see the repository-level authorship note for context.
