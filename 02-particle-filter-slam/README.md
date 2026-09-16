# Particle Filter-Based SLAM

Team coursework investigating how a differential-drive robot can estimate its pose and build a map from noisy simulated range measurements. The notebook combines robot motion, particle weighting and resampling, obstacle checks, and the extraction and merging of line segments into a map representation.

## What is implemented

- Differential-drive kinematics and numerical motion integration.
- Grid-based obstacles and simulated LiDAR/range-bearing observations.
- Measurement-likelihood calculations, weight normalization and systematic resampling.
- Line-segment matching and merging, belief-map updates, and plots of robot and particle trajectories.

## Files and prerequisites

- [2d-simulation.ipynb](2d-simulation.ipynb) — original notebook workflow.
- [2d_simulation.py](2d_simulation.py) — cell-by-cell source export for browsing.
- `project-files.zip` — archived copy of the source export.

The source imports NumPy, SciPy, Matplotlib and Pillow. A notebook environment is useful for stepping through the experiments.

The first map-loading cell expects `pppp.png`, which is not included in this public folder. It generates `pppp.npy`, and later cells write/read `belief.npy` and result images. Restore or replace that input and check the map dimensions before attempting the full workflow. The export executes notebook cells sequentially; it is preserved as a coursework experiment rather than a packaged, immediately reproducible SLAM application.
