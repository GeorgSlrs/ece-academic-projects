# Impulse-Voltage Measurement Analysis

MATLAB analysis of oscilloscope voltage/time traces from the electrical-measurements laboratory.

## Contents

- `electrical_mes/tek00000.csv` through `tek00019.csv`: two-column oscilloscope traces.
- `electrical_mes/graph_electrical_mes.m` and `graph2.m`: plotting and waveform analysis.

## Running the coursework

Use MATLAB with this `measurement-analysis` directory as the current folder. Add the script directory to the path with `addpath('electrical_mes')`, then call `graph_electrical_mes`; its relative data path is `electrical_mes`. The alternative `graph2.m` retains an absolute path from the original computer and requires its `folder_path` to be adapted locally before use.

## Archive notes

Preserved as coursework; full execution and numerical results have not been revalidated.

These are laboratory measurement data, not personal records.
