# Machine Learning — HW2

## What this assignment covers
MATLAB-based image reconstruction using a supplied neural generator and latent-variable optimization. The implementation reconstructs 28×28 images from partially observed/noisy data using an ADAM-style optimization loop.

## Main files
- `hw2/learning_2_2v2_machine.m` — main MATLAB implementation.
- `hw2/data21.mat`, `data22.mat`, `data23.mat` — supplied coursework data.
- `GEORGIOS-SALIARHS-2.docx` — submitted work/report.
- `hw2/hw2.pdf`, `hw2/derivatives.pdf` — assignment/reference material.

## Requirements
- MATLAB
- The supplied `.mat` data files in `hw2/`

## Run
1. Open MATLAB.
2. Set the Current Folder to `Machine_Learning_HW2/hw2`.
3. In `learning_2_2v2_machine.m`, replace the original absolute Windows paths with local paths such as:
   ```matlab
   dataPath21 = 'data21.mat';
   dataPath22 = 'data22.mat';
   ```
4. Run `learning_2_2v2_machine`.

## Expected output
Reconstructed image visualizations and optimization/convergence information.

## Notes
The script intentionally preserves the original coursework structure and absolute path references, so the paths must be edited on another computer. This is academic coursework; see the repository-level authorship note for context.
