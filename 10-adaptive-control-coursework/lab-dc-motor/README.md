# Adaptive-Control DC-Motor Laboratory

## What this project contains
Hardware-oriented coursework for an adaptive-control laboratory using a DC motor, motor driver, Arduino, encoder feedback and experimentally identified first-order plant models. The recovered material includes identification scripts, serial/measurement data, Arduino controller sketches and a sanitized text export of the laboratory report.

## Folder map
- `identification/transfer_get.m` — fits positive/negative PWM steady-state data and records the identified first-order models.
- `identification/adaptive_control_lab_1_1_responses.m` — plots measured fits and simulated step/sine/ramp responses of the identified models.
- `controllers/mit/mit.ino` — recovered MIT-rule Arduino sketch.
- `controllers/mrac/Mrac.ino` — recovered file from the MRAC folder. In the recovered Drive snapshot this file is byte-identical to `mit.ino`; both are preserved to reflect the original coursework archive rather than silently rewriting history.
- `controllers/adi/sketch_dec10a.ino` — adaptive dynamic-inversion (ADI) implementation.
- `controllers/robust-adaptive/sketch_dec17a.ino` — ADI/direct-MRAC experiment with dead-zone, normalization, leakage and projection-style robustifying options.
- `controllers/vector-mrac/sketch_jan15a.ino` — position-oriented vector MRAC experiment with encoder state, reference-model states, normalized adaptation, dead-zone and leakage.
- `measurements/meas_get.ipynb` — measurement/Arduino CLI notebook; a user-specific absolute Windows path was replaced by a relative project path before publication.
- `measurements/out.txt.gz`, `measurements/out_MIT.txt.gz` — losslessly compressed copies of the recovered raw serial-output logs. Decompress with `gzip -d` / 7-Zip when needed.
- `report/Adaptive_Control_Lab_Report_public.md` — sanitized text export of the original Word report.

## Requirements
### MATLAB identification/simulation
- MATLAB
- Control System Toolbox is required by `tf`, `step` and `lsim` in `adaptive_control_lab_1_1_responses.m`.

### Arduino experiments
- Arduino-compatible board and Arduino toolchain
- Motor driver and encoder-equipped DC-motor laboratory hardware matching the pin assignments in each sketch
- Serial connection for measurements/logging

### Notebook
The notebook uses Python serial/subprocess tooling to interact with the Arduino toolchain. Review its port, board and project-path settings before running it.

## Safety / reproducibility
The Arduino sketches drive physical motor hardware. Verify pin assignments, voltage/PWM limits, motor direction and emergency power-off before connecting hardware. The numerical parameters and saturation limits are coursework-specific and should not be assumed safe for another setup.

## Authorship note
This is coursework material recovered from the original project files. Some code in this repository was developed with coding-assistant support; inclusion does not claim independent authorship of every line.
