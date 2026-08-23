# Embodied Intelligence Project — Project Guide

## What this subfolder contains
A smaller/original snapshot of the team concrete-defect image-classification project. The parent `15-concrete-crack-detection` folder contains the fuller training/evaluation code, saved Keras models, requirements and presentation/report artifacts.

## Files here
- `dataset.py` — dataset loading/preprocessing logic.
- `settings.json` — project settings.
- `setup.py` — project/setup helper.
- `README.md` — original short team-project description.

## Recommended place to run the project
Use the **parent `15-concrete-crack-detection` folder** for the more complete version. Its `requirements.txt` lists:
- NumPy
- Pandas
- Matplotlib
- scikit-learn
- TensorFlow
- Kaggle
- ImageHash

From the parent folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r .\requirements.txt
```

## Notes
This was a team coursework project. Large image datasets are not stored in this repository. See the parent folder and repository-level authorship note for contribution context.
