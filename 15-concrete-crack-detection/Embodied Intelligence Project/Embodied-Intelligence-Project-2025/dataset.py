import tensorflow as tf
import keras
import os

SEED = 88
def normalize(image, label):
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

def grayscale(image, label):
    image = tf.image.rgb_to_grayscale(image)
    return image, label

def apply_all(image, label):
    image, label = grayscale(image, label)
    image, label = normalize(image, label)
    return image, label

def get_negative_size():
    negative_path = os.path.join("data", "processed", "Negative")
    return len(os.listdir(negative_path))

def get_positive_size():
    positive_path = os.path.join("data", "processed", "Positive")
    return len(os.listdir(positive_path))



class DatasetManager():
    def __init__(self, path, batch_size = 32, seed = SEED):
        self._path = path
        self.batch_size = batch_size
        self.seed = SEED

        self._create_full()
        self._undersample()
        self.ds = self.ds.map(apply_all)
        self.shuffle()
        self.batch()
        self.split()

    def _create_full(self):
        full_ds = keras.preprocessing.image_dataset_from_directory(
            self._path,
            image_size = (224, 224),
            batch_size = None,
            shuffle = False,
            seed = SEED
        )
        self.ds = full_ds
        self.cardinality = tf.data.experimental.cardinality(full_ds).numpy()
    
    def _undersample(self):
        #Assumes class 0 > class 1
        class_counts = {0: get_negative_size(), 1: get_positive_size()}
        class0 = self.ds.filter(lambda img, label: label == 0)
        class1 = self.ds.filter(lambda img, label: label == 1)
        class0 = class0.take(class_counts[1])
        self.ds = class0.concatenate(class1)
        self.cardinality -= class_counts[0] - class_counts[1]

    def shuffle(self, buffer_size = 1000):
        self.ds = self.ds.shuffle(buffer_size, seed = self.seed)

    def batch(self):
        self.ds = self.ds.batch(self.batch_size, drop_remainder = True)
        self.cardinality //= 32
    
    def split(self):
        #TODO store cardinalities
        train_ds = self.ds.take(int(self.cardinality * 0.7))
        rest_ds = self.ds.skip(int(self.cardinality * 0.7)) 

        rest_ds_cardinality = self.cardinality - int(self.cardinality * 0.7) 
        validation_ds = rest_ds.take(int(rest_ds_cardinality * 0.5))
        test_ds = rest_ds.skip(int(rest_ds_cardinality * 0.5))

        self.train_ds = train_ds
        self.validation_ds = validation_ds   
        self.test_ds = test_ds
    
    def get_train_ds(self):
        return self.train_ds
    
    def get_validation_ds(self):
        return self.validation_ds 
    
    def get_test_ds(self):
        return self.test_ds