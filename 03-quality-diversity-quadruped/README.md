# Quality-Diversity Quadruped Locomotion

Team coursework exploring how to search for a repertoire of quadruped gaits instead of optimizing a single behaviour. The Python demonstration combines a MAP-Elites grid archive with Gaussian-process surrogate models and an upper-confidence-bound acquisition rule in a Surrogate-Assisted Illumination (SAIL) loop.

Four actuator-amplitude parameters describe each candidate. Evaluations produce speed and effort descriptors, which locate candidates in a two-dimensional archive. The code tracks archive coverage and fitness, exports the retained parameters, and visualizes the resulting repertoire.

## Main files

- [QD_dummy_SAILv7.py](QD_dummy_SAILv7.py) — search loop, archive, analytic model, optional PyBullet evaluation and plotting.
- [sail_repertoire.csv](sail_repertoire.csv) — saved repertoire with descriptor bins, fitness and amplitude parameters.
- `Figure_1.png`, `Figure_2.png` — saved visualizations.
- `Intelligent_Control_Final_Project_Report_v2 (1).pdf` and the presentation files — coursework explanation and discussion.
- `minitaur.urdf` — archived robot description. The script's physics path currently uses the Minitaur asset supplied by `pybullet_data`.

## Running the demonstration

Use Python 3 with NumPy, pandas, Matplotlib, scikit-learn and tqdm. Install PyBullet for physics evaluations. From this folder:

```bash
python QD_dummy_SAILv7.py
python QD_dummy_SAILv7.py --physics
python QD_dummy_SAILv7.py --physics --animate
```

The default run uses the analytic toy model; `--physics` selects PyBullet. A run writes `sail_repertoire.csv` beside the script, replacing the existing file, and opens diagnostic plots. Physics evaluations take more computation than the analytic example.

The collection includes assistant-supported teaching code and team project materials. Its simulated repertoire is coursework evidence, not a demonstration of transfer to a physical quadruped.
