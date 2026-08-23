# Machine Learning — HW1

## What this assignment covers
Probability/classification experiments comparing Bayes-optimal decisions with small neural-network classifiers. The coursework includes synthetic Gaussian/mixture data and MNIST 0-vs-8 experiments.

## Main files
- `deep_learning_1.py` — Bayes decision/error experiment on synthetic distributions.
- `deep_learning_2.py` — neural-network classification on MNIST 0 vs 8.
- `deep_learning_hw/deep_learning_3.py` — related MNIST experiment.
- `deep_learning_hw/deep_learning_4.py` — Bayes-vs-neural comparison on synthetic data.
- `GEORGIOS-SALIARHS-1.pdf` — submitted report.
- `hw1.pdf` — assignment material.
- `Figure_*.png` — saved figures.

## Requirements
- Python 3
- NumPy
- Matplotlib
- MNIST raw IDX files are required by the scripts that load MNIST.

## Install
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install numpy matplotlib
```

## Run
Examples:

```powershell
py .\deep_learning_1.py
py .\deep_learning_hw\deep_learning_4.py
```

For `deep_learning_2.py` / `deep_learning_3.py`, update the hard-coded `mnist_data` folder path before running.

## Notes
The original scripts preserve local coursework paths; they are not packaged as a reusable ML library. This is academic coursework; see the repository-level authorship note for context.
