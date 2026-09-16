# Robust Control Simulations

Coursework examining feedback control under model limitations, disturbances and measurement noise. The collection includes two team-project browser simulations—a cart–pendulum and a planar dual-rotor vehicle—alongside feedback-design exercises and a robust-control motor laboratory.

## Simulations

| Artifact | What it demonstrates |
| --- | --- |
| [Inverted pendulum](inverted-pendulum/) | A cart–pendulum SISO simulation focused on pendulum-angle stabilization. The accompanying public write-up discusses modelling, controller tuning, force/angle constraints and the prefilter. |
| [Dual_Rotor_Drone_Simulation_v3.html](Dual_Rotor_Drone_Simulation_v3.html) | A six-state planar dual-rotor model with cascaded horizontal, pitch and altitude feedback, rotor-force saturation, adjustable drag, sensor noise and disturbance. The fixed controller uses proportional/derivative gains; its integral gains are zero. |

The dual-rotor artifact integrates the nonlinear model with a forward-Euler step and displays the motion and telemetry on a Canvas. The interactive controls allow qualitative exploration of how the simulated response changes as the environment is varied.

## Homework and motor laboratory

[coursework/](coursework/) contains MATLAB and Python exercises in P/PI/PID and inverse-based feedback design, multivariable analysis, mixed-sensitivity synthesis and uncertainty modelling. Its laboratory folder includes measured DC-motor frequency-response data and robust-controller analysis. The nested README distinguishes Python dependencies from the MATLAB Control System and Robust Control Toolbox requirements.

## Open the artifacts

Open either HTML file in a modern browser; the simulations are self-contained and require no package installation. Read the [inverted-pendulum guide](inverted-pendulum/README.md) for the SISO file names and write-up. `Robust_Control_Team_Project_Presentation.pptx` contains the team presentation.

The course title describes the broader coursework context; the browser demonstrations alone do not establish formal robustness guarantees. This was team work, including coding-assistant-supported implementation, and individual contribution is not claimed for every component.
