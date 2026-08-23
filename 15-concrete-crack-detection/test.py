import matplotlib.pyplot as plt
import numpy as np
from dataset import DatasetManager
from BASE_model import BASE_Model

def visualize_test_predictions(dataset_manager, model, num_samples=16):
    """
    Visualizes test samples with true labels and model predictions.
    
    Args:
        dataset_manager: Your DatasetManager instance
        model: Your trained Keras model
        num_samples: Number of samples to display (default 16)
    """
    test_ds = dataset_manager.get_test_ds()
    
    # Create figure
    rows = int(np.sqrt(num_samples))
    cols = int(np.ceil(num_samples / rows))
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
    
    # Flatten axes if needed
    if num_samples > 1:
        axes = axes.ravel()
    else:
        axes = [axes]
    
    # Get one batch from test set
    for images, true_labels in test_ds.take(1):
        # Get model predictions
        preds = model.predict(images, verbose=0)
        
        for i in range(min(num_samples, len(images))):
            # Process image
            image = images[i].numpy()
            if image.shape[-1] == 1:  # Grayscale
                image = image.squeeze()
                axes[i].imshow(image, cmap='gray')
            else:  # RGB
                axes[i].imshow(image)
            
            # Get labels and predictions
            true_label = true_labels[i].numpy()
            pred = preds[i][0]
            pred_class = 'Positive' if pred > 0.5 else 'Negative'
            confidence = max(pred, 1-pred)  # Get confidence of prediction
            
            # Format title
            title = f"True: {'Positive' if true_label > 0.5 else 'Negative'}\n"
            title += f"Pred: {pred_class} ({confidence:.1%})"
            
            # Color code based on correctness
            color = 'green' if (pred > 0.5) == (true_label > 0.5) else 'red'
            
            axes[i].set_title(title, color=color)
            axes[i].axis('off')
    
    # Hide any empty subplots
    for j in range(i+1, num_samples):
        axes[j].axis('off')
    
    plt.tight_layout()
    plt.show()

# Usage (same as before but shows 16 samples):
# Usage example:
data_path = "data/processed"
dm = (DatasetManager(data_path, augment_train=False)
      .load_dataset()
      .balance_classes()
      .preprocess_data()
      .cache_shuffled()
      .make_splits())

# Load your trained model
model =BASE_Model.load("best_modelV4.keras") 

# Visualize with predictions
visualize_test_predictions(dm, model, num_samples=20)