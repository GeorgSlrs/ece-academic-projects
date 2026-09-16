# Concrete Crack Detection with a CNN

A team Embodied Intelligence project for binary classification of concrete-surface images as cracked (`Positive`) or uncracked (`Negative`). The workflow downloads the source dataset, prepares class folders, constructs training/validation/test splits, trains a small convolutional network and evaluates the saved model.

## Approach

`dataset.py` loads images at 224×224 pixels, converts them to grayscale, normalizes them and constructs 70/15/15 splits. It also contains class-balancing and optional augmentation code; the main training script currently disables augmentation.

`BASE_model.py` defines two convolutional layers with batch normalization, pooling, dropout and a sigmoid classification head. Training uses binary cross-entropy, Adam and callbacks for learning-rate scheduling, early stopping, checkpointing and TensorBoard logs.

## Main files

- [setup.py](setup.py) — Kaggle download, perceptual-hash duplicate handling and optional image resizing.
- [settings.json](settings.json) — preprocessing settings.
- [dataset.py](dataset.py) — loading, preprocessing and split construction.
- [BASE_model.py](BASE_model.py) — CNN and training/evaluation helpers.
- [CrackDetector.py](CrackDetector.py) — main training and evaluation script.
- `Evaluation_test.py`, `Check_dataset.py`, `test.py`, `visualization.py` — additional inspection/evaluation experiments.
- `6thTry.keras`, `best_model.keras` — archived model files; training can replace these files.
- `Embodied Intelligence Project/` — retained nested project material.

## Setup and workflow

The original project used Python 3.12.4. Dependencies are listed in `requirements.txt` and include TensorFlow/Keras, NumPy, pandas, Matplotlib, scikit-learn, Kaggle and imagehash. The source also imports Pillow. Package versions are not pinned, and the use of internal `keras._tf_keras` imports makes TensorFlow/Keras compatibility relevant.

From this folder, create a Python environment, install the dependencies, and configure authentication for the Kaggle API. The dataset identifier in the source is `arunrk7/surface-crack-detection`.

```bash
python -m pip install -r requirements.txt
python setup.py
python CrackDetector.py
```

Review the preprocessing settings and confirm that `data/processed/Negative` and `data/processed/Positive` contain images before training. The setup script performs work when executed or imported and modifies its settings after processing. The training script trains for up to five epochs, saves a model and evaluates its test split.

## Results and scope

The original README reported 98% accuracy and 99% precision, while also raising concerns about overconfidence and easily separable classes. Those are historical team-reported figures, not independently reproduced results. Generalization to new cameras, surfaces or deployment conditions remains to be evaluated; this archive does not establish real-time industrial performance.

Developed by Παλάσκας Γιώργος, Σάλιαρης Γιώργος, Κορομηλάς Χρήστος and Κόνης Νίκος.
