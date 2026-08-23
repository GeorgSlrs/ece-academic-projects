## Embodied-Intelligence-Project-2025
# Defect Detection in Manufactured Products

## Overview

This project ensures **quality control** in industrial manufacturing by using **machine learning** to detect defects in product images.  
We built a simple yet powerful **Convolutional Neural Network (CNN)** model that automatically identifies cracks on walls in real-time production scenarios.

## Features

- 📷 **Image-based defect detection**  
- 🧀 **Lightweight CNN model** optimized for quick deployment
- ⚙️ **Real-time quality control** capability
- 📊 **Clear evaluation metrics** to assess model performance

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Giwrgospalaskas/Embodied-Intelligence-Project-2025.git
   cd Embodied-Intelligence-Project-2025
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required packages**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare your dataset**  
   Run the `setup.py` code block and it should download the image dataset and organize it automatically by class (e.g., `Positive` and `Negative`).

2. **Train and evaluate the model**
   ```bash
   python src/Embodied-Intelligence-Project-2025/CrackDetector.py
   ```

4. **Predict new images**
   ```bash
   Use the predict method of the BASE_model class. Make sure the image to predict is in the right format.
   ```

## Requirements

- [python 3.12.4](https://www.python.org/downloads/release/python-3124/)
- TensorFlow / Keras
- NumPy
- Matplotlib (for visualization) 

(See `requirements.txt` for the full list.)

## Results

The CNN achieves strong defect detection performance on our benchmark datasets, demonstrating the potential for reliable industrial quality control through machine learning.

| Metric     | Score  |
|------------|--------|
| Accuracy   |  98%   |
| Precision  |  99%   |

***Notice:*** These metrics seem to be superficially good and the model appears overconfident. More testing need to be done to figure out the cause of this behavior but it's most probably due to the overly differentiable dataset classes.

> ✨ Future improvements include exploring deeper architectures for finer defect detection beyond cracks on walls, better regularization techniques to minimize overconfidence issue and engourage generalization, and real-time deployment on edge devices.

## Team Members

This project was developed by:

- Παλάσκας Γιώργος
- Σάλιαρης Γιώργος
- Κορομηλάς Χρήστος
- Κόνης Νίκος

