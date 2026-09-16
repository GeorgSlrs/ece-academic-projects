# Adaptive Rocket Landing Control

A final-project simulation of a planar rocket descending toward a landing pad using bounded throttle and engine-gimbal commands. The project combines a nine-state dynamics model, numerical integration, adaptive-controller experiments and a live desktop interface for observing the descent and its touchdown outcome.

## Model and controller

The state includes position, velocity, tilt, angular rate, mass, actual throttle and actual gimbal angle. The dynamics model includes actuator lag and configurable effects such as mass depletion and drag. The simulator adds RK4 integration, process/input noise and touchdown classification.

The autopilot uses an early-braking strategy with two selectable educational adaptation modes: a backstepping-inspired controller with disturbance-bias estimates and an MIT-rule-style estimate of thrust effectiveness. These are simulation experiments rather than flight-qualified guidance algorithms.

## Files

- [rocket_main.py](rocket_main.py) — application entry point.
- [rocket_dynamics.py](rocket_dynamics.py) — parameters and state-derivative equations.
- [rocket_simulator.py](rocket_simulator.py) — controller, simulator, Tkinter interface, logging and plots.
- `rocket_log_*.npz` — saved simulation logs from the coursework.
- `REPORT_ADAPTIVE_CONTROL_FINAL_PROJECT (1).pdf`, the DOCX report and `ADAPTIVE_CONTROL_PRESENTATION.pptx` — project discussion.

## Run

Use Python 3 with NumPy, Matplotlib and Tk/Tkinter support. From this folder:

```bash
python rocket_main.py
```

The interface provides Start, Stop, Restart and End controls. Ending a run saves a new `.npz` log and opens the diagnostic plots. The original logs are examples of past runs, not a new performance evaluation.

This is academic project work with coding-assistant-supported development; the archive does not claim independent authorship of every implementation detail.
