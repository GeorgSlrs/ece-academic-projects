# Rotary Flexible Joint Thesis

Diploma-thesis simulation code and working documentation for a motor-driven rotary flexible joint (RFJ). The current Python implementation tracks the link/load angle `phi`, with joint twist `alpha = theta - phi`. The MATLAB scripts preserve an earlier prototype that tracks the motor angle `theta`.

This is a research and coursework archive. The documents are working drafts; the code does not establish experimental validation or guaranteed closed-loop stability.

## Contents

- `python/`: nonlinear plant, sampled-data simulation, seven controller modes, interactive controls and 3D playback, analysis plots, and performance metrics.
- `matlab/`: earlier MATLAB/Simulink model builders and analysis scripts. See its README for known parameter-name inconsistencies.
- `docs/Diploma_Thesis_v2.docx`: mathematical-model working draft.
- `docs/RFJ_Controllers_Phi_Tracking_Detailed_GR_v4.docx`: Greek controller-design documentation for the current phi-tracking implementation.
- `docs/identification_rotary_flexible_joint.docx`: Greek identification and experimental-planning guide.

## Python model and methods

The five-state plant uses `[theta, phi, dtheta, dphi, i]` and motor voltage as its input. It includes motor electrical dynamics, torsional spring and damping, optional cubic spring stiffness, smooth Coulomb friction, and configurable parameter uncertainty. The simulator integrates with RK4 and updates the controller with a zero-order hold.

Controller modes in `run_all.py` are `pid`, `smc`, `mit`, `lqr`, `lqg`, `hinf`, and `mrac`. Measurement and command models include encoder quantization, noise, bias, random-walk drift, dropout/hold, command delay, driver deadzone and voltage saturation. Disturbance options include sinusoidal or pulse load torque.

Analysis covers time traces, twist, motor current and torque, frequency response, Nyquist plots, root locus, continuous and discrete poles, energy, and controller diagnostics. Metrics include IAE/ITAE and RMS phi error, RMS/maximum twist, RMS voltage, and saturation ratio.

## Dependencies and entry points

Use a Python environment with NumPy and Matplotlib. SciPy supplies the matrix exponential when available. H-infinity synthesis additionally uses `control` and `slycot`. The preserved `python/requirements.txt` is an unpinned historical dependency list, not a verified environment lock.

From `python/`:

```sh
python run_all.py                     # GUI is the default
python run_all.py --nogui --mode pid --T 5 --noAnim
python run_all.py --nogui --mode lqr --analysis --noAnim
python run_all.py --nogui --mode hinf --noAnim
```

Use `--nogui` for command-line operation. Without it, controller and analysis options are bypassed by the GUI launch. Parameters are collected in `rfj_params.py`; additional noise settings are exposed by `simulate_L2`.

## Validation and known limitations

All 14 Python source files passed syntax parsing. A short 0.5-second smoke check with Python 3.13.11, NumPy 2.4.2, SciPy 1.17.1 and python-control 0.10.2 produced finite state trajectories for PID, SMC, MIT and LQR. This was an execution check, not a control-performance evaluation.

The original code is preserved with the following observed limitations:

- Metrics call `numpy.trapz`, which is unavailable in the checked NumPy 2.4.2 environment; the command-line path therefore fails when it prints metrics.
- LQG and MRAC encounter array-to-scalar conversion errors in debug values in `controllers.py` under that environment.
- Default H-infinity synthesis failed with a Slycot rank-condition error during the smoke check.
- GUI operation, full analysis plotting, and MATLAB execution were not validated during archiving.

Generated Simulink models, simulation caches, plot output, temporary Office files, superseded document drafts, and third-party manuals/papers are omitted. The MATLAB builders are retained so the model structure remains inspectable without generated artifacts.
