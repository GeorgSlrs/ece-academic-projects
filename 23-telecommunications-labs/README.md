# Telecommunications Laboratory

MATLAB laboratory exercises for signal generation, time/frequency-domain analysis, analog modulation, and digital ASK, FSK, and BPSK modulation/demodulation.

## Contents

- `lab1/`: introductory signal exercises and supplied/generated input arrays.
- `lab2/`: signal-analysis exercise.
- `lab4/`: carrier/message-frequency exercises.
- `lab6/`: ASK, FSK, and BPSK simulation scripts.

## Running the coursework

Open MATLAB in a lab directory and run its exercise script (`ex1_1.m`, `exercise1.m`, `ex1.m`, or one of the modulation scripts). Keep `GenSignal.m`/`GenSpcm.m` and `.mat` inputs beside the scripts. Run `lab1/ex1_1.m` before `ex1_2.m` to generate `Lab1_1_Out.mat`. `ex1_3.m` calls `GenSignal` and regenerates its large `res_1092584.mat` input automatically. These generated MAT outputs are omitted from the archive. Some signal-processing operations may require Signal Processing Toolbox.

## Archive notes

Preserved as coursework; full execution and numerical results have not been revalidated.

The `GenSignal` and `GenSpcm` files are supplied course helpers; their original contents are preserved. Reports, instructor handouts, autosaves, and superseded lab4 versions are omitted.
