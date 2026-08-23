import tensorflow as tf
from BASE_model import BASE_Model
from dataset import DatasetManager

data_path = "data/processed"

dataManager = (DatasetManager(data_path)
               .load_dataset()
               .balance_classes()
               .preprocess_data()
               .cache_shuffled()
               .make_splits())

test_data = dataManager.get_test_ds()

model = BASE_Model.load("models/best_modelV4.keras")

model.evaluate(test_data)