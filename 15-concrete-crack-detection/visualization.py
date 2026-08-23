from BASE_model import BASE_Model
from dataset import DatasetManager
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import keras._tf_keras.keras as keras

# Initialize your dataset manager
data_path = "data/processed"
dm = (DatasetManager(data_path, augment_train=False)
      .load_dataset()
      .balance_classes()
      .preprocess_data()
      .cache_shuffled()
      .make_splits())

# Load your saved model
model = BASE_Model.load("models/best_modelV5.keras")  # or .h5 depending on format
val_data = dm.get_validation_ds()

def visualize_activations(model, dataset, sample_index=0, layer_names=None):
    # Get the Keras model from your BASE_Model
    keras_model = model.model  # Assuming your BASE_Model has a .model attribute
    
    # Get a sample image
    sample = next(iter(dataset.skip(sample_index).take(1)))
    img, label = sample
    img = img[0:1]  # Keep batch dimension
    
    # Default to all Conv layers if not specified
    if layer_names is None:
        layer_names = [layer.name for layer in keras_model.layers 
                      if 'conv' in layer.name.lower()]
    
    # Create activation model
    outputs = [keras_model.get_layer(name).output for name in layer_names]
    activation_model = keras.models.Model(inputs=keras_model.inputs, outputs=outputs)
    
    # Get activations
    activations = activation_model.predict(img)
    
    # Visualize each layer
    for layer_name, layer_activation in zip(layer_names, activations):
        print(f"Layer: {layer_name} ({layer_activation.shape[-1]} filters)")
        
        # Display first 8 filters
        plt.figure(figsize=(12, 3))
        for i in range(min(8, layer_activation.shape[-1])):
            plt.subplot(1, 8, i+1)
            plt.imshow(layer_activation[0, :, :, i], cmap='viridis')
            plt.axis('off')
        plt.suptitle(f"{layer_name} Activations", y=1.1)
        plt.tight_layout()
        plt.show()

# Usage
visualize_activations(model, val_data, sample_index=2)


def analyze_predictions(model, dataset, num_batches=5):
    preds = []
    labels = []
    
    for batch in dataset.take(num_batches):
        images, true_labels = batch
        batch_preds = model.predict(images, verbose=0)
        preds.extend(batch_preds.flatten())
        labels.extend(true_labels.numpy())
    
    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist([p for p, l in zip(preds, labels) if l == 1], 
             bins=20, alpha=0.5, label='Positive')
    plt.hist([p for p, l in zip(preds, labels) if l == 0], 
             bins=20, alpha=0.5, label='Negative')
    plt.xlabel('Prediction Confidence')
    plt.ylabel('Count')
    plt.legend()
    plt.title('Prediction Distribution by True Class')
    plt.show()

analyze_predictions(model, val_data)

