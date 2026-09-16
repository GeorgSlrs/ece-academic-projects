# Adaptive Control Coursework

A set of simulation assignments and a DC-motor laboratory exploring how controllers update parameters or compensate for uncertain dynamics while tracking a reference. MATLAB studies are complemented by Arduino sketches, measurement records and reports from the laboratory workflow.

## Subprojects

| Folder | Main work |
| --- | --- |
| [HW1](hw1/) | Nonlinear-system stability and Lyapunov analysis using phase portraits, equilibrium searches, attraction-region estimates and decay comparisons. |
| [HW2](hw2/) | Model-reference adaptive control and normalized MIT-rule experiments, with tracking, parameter and error plots. Start with `ACRL_HW2_Ex1.m` and `ACRL_HW2_Ex2.m`. |
| [HW3](hw3/) | Adaptive augmentation of a stepper-motor model using RBF neural-network compensation. `ACRL_HW_3.m` compares sigma/e modification and projection variants. |
| [DC-Motor Laboratory](lab-dc-motor/) | Experimental first-order model identification, MATLAB response analysis, Arduino MIT/MRAC/ADI and robust-adaptive experiments, serial measurements and a public report export. |

## Exploring and reproducing

Each subfolder provides its own file map and setup guide. The simulations require MATLAB; HW3 uses `lyap`, and the laboratory response scripts use `tf`, `step` and `lsim`, requiring the Control System Toolbox.

The Arduino experiments require the laboratory motor, driver, encoder and board configuration described in the sketches. Review those hardware-specific settings before using them. The lab README also records an archival detail: the recovered MIT and MRAC sketch files are byte-identical, so their folder names should not be interpreted as evidence of distinct implementations.

Some code was developed with coding-assistant support. The collection records coursework exposure, experiments and supporting material without claiming independent authorship of every implementation or validated settings for other hardware.
