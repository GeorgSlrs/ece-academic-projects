import tensorflow as tf
import keras
from keras._tf_keras.keras.layers import RandomRotation, RandomZoom, RandomContrast, RandomGaussianBlur, RandomBrightness
from keras._tf_keras.keras import Sequential
import os

SEED = 88

class DatasetManager():
    def __init__(self, path, image_size = (224,224), batch_size = 32, seed = SEED, augment_train = True):
        """
        Loads images from the specified path, applies preprocessing transformations,
        balances classes via undersampling, and splits the resulting dataset 
        into training, validation, and test subsets and provides data augmentation

        Args:
            path (str): Directory path for the dataset with subdirs by class.
            image_size (tuple): Dimensions of the dataset's images
            batch_size (int): Number of samples per training batch.
            seed (int): Random seed for reproducibility.
            augment_train (bool): Whether to use data augmentation for the training dataset
        """
        self._path = path
        self.batch_size = batch_size
        self.image_size = image_size
        self.seed = SEED
        self.ds = None
        self.augment_train = augment_train
        self.augmenter = self.build_augmenter()
    
    def load_dataset(self):
        '''Loads the full dataset from the given path and creates classes using Keras's 
        image_dataset_from_directory'''
        print("Loading Dataset...")
        try:
            self._create_full()
            print("Dataset loaded succesfully")
            return self
        except Exception as e:
            raise ValueError(f"An unexpected error occured: {str(e)}") from e
    
    def balance_classes(self):
        '''Makes classes have same amount of samples'''
        print("Balancing classes...")
        try:
            self._undersample()
            return self
        except Exception as e:
            raise ValueError(f"An unexpected error occured: {str(e)}") from e
    
    def preprocess_data(self):
        '''Applies grayscaling and normalization'''
        print("Applying grayscaling and normalization to data...")
        try:
            self.ds = self.ds.map(apply_all)
            return self
        except Exception as e:
            raise ValueError(f"An unexpected error occured: {str(e)}") from e
    
    def cache_shuffled(self):
        '''Shuffles the entire dataset and caches it. **Must be used before self.make_splits() and after all the other methods**'''
        print("Shuffling and caching the dataset...")
        try:
            self.ds = self.ds.shuffle(
                buffer_size=self.cardinality,
                seed=self.seed,
                reshuffle_each_iteration=False,
                name = "Total_shuffle").cache()
            
            for _ in self.ds:
                pass
            return self
        except Exception as e:
            raise ValueError(f"An unexpected error occured: {str(e)}") from e
        
    def make_splits(self):
        '''Splits the dataset to train (70%), validation (15%) and test (15%) subsets, while also provides data augmentation for the training set if set'''
        print("Splitting dataset to: \ntrain -> 70% \nvalidation -> 15% \ntest -> 15%")
        try:
            self.split()
            return self
        except Exception as e:
            raise ValueError(f"An unexpected error occured: {str(e)}") from e
        


###################################################################################################################################################################


    def _create_full(self):
        self.ds = keras.utils.image_dataset_from_directory(self._path,
            labels = "inferred",
            label_mode = "binary",
            image_size = self.image_size,
            batch_size = None,
            shuffle = False,
            seed = None,
            verbose = True)
        
        # tf.data.experimental.cardinality() returns the number of elements in the dataset
        self.cardinality = tf.data.experimental.cardinality(self.ds).numpy()
    
    def _undersample(self):
        """
        Assumes class 0 is Negative and class 1 is Positive.
        Balances the dataset by limiting the larger class to the size of the smaller class.
        Updates self.ds accordingly.
        """
        class_counts = {0: get_negative_size(), 1: get_positive_size()}
        class0 = self.ds.filter(lambda img, label: tf.squeeze(tf.equal(label, 0)))
        class1 = self.ds.filter(lambda img, label: tf.squeeze(tf.equal(label, 1)))
        
        # Undersample class 0 to match the size of class 1
        class0 = class0.take(class_counts[1])
        # Concatenate the classes back together
        self.ds = class0.concatenate(class1)
        # Adjust the cardinality by removing the difference
        self.cardinality -= class_counts[0] - class_counts[1]
    
    def build_augmenter(self):
        return Sequential([
            RandomRotation(0.1, seed=self.seed),  
            RandomZoom(0.1, seed=self.seed),      
            RandomContrast(0.1, seed=self.seed),  
            RandomBrightness(factor=0.2, value_range=(0,1), seed=self.seed),
            RandomGaussianBlur(kernel_size=3, sigma=(0.1, 2.0), seed=self.seed)
        ])
    
    def split(self):
        """
        Splits the dataset into training, validation, and test subsets in a 70/15/15 ratio.
        Stores them as self.train_ds, self.validation_ds, and self.test_ds respectively.
        """
        
        # split sizes
        train_size = int(0.7 * self.cardinality)
        val_size = int(0.15 * self.cardinality)

        #Cardinalities
        self.train_cardinality = int((self.cardinality * 0.7)//self.batch_size)
        self.validation_cardinality = int((self.cardinality * 0.15)//self.batch_size)
        self.test_cardinality = int((self.cardinality*0.15)//self.batch_size)
        
        # Create splits
        train = self.ds.take(train_size)
        remaining = self.ds.skip(train_size)
        val = remaining.take(val_size)
        test = remaining.skip(val_size)

        if self.augment_train:
            print("Augmenting training data...")
            train = train.map(
                lambda x,y: (self.augmenter(x, training = True), y),
                num_parallel_calls = tf.data.AUTOTUNE
            )
        
        # Isolate shuffling to training set only
        self.train_ds = (train
              .batch(self.batch_size)
              .prefetch(tf.data.AUTOTUNE)
        )
        
        self.val_ds = val.batch(self.batch_size).prefetch(tf.data.AUTOTUNE)
        self.test_ds = test.batch(self.batch_size).prefetch(tf.data.AUTOTUNE)

    # Getter methods for each subset
    def get_train_ds(self):
        '''returns the training subset'''
        return self.train_ds
    
    def get_validation_ds(self):
        '''returns the validation subset'''
        return self.val_ds
    
    def get_test_ds(self):
        '''returns the test subset'''
        return self.test_ds

    def get_train_cardinality(self):
        '''returns training's subset cardinality'''
        return self.train_cardinality
    
    def get_test_cardinality(self):
        '''returns test's subset cardinality'''
        return self.test_cardinality
    
    def get_val_cardinality(self):
        '''returns validation's subset cardinality'''
        return self.validation_cardinality
    
##########################################################################################################################
#Data preprocessing methods
def normalize(image, label):
    """
    Scales image pixels from [0, 255] to [0, 1].
    Returns the (image, label) tuple.
    """
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

def grayscale(image, label):
    """
    Converts an RGB image to grayscale (single channel).
    Returns the (image, label) tuple.
    """
    image = tf.image.rgb_to_grayscale(image)
    return image, label

def apply_all(image, label):
    """
    Applies grayscale conversion and normalization sequentially.
    Returns the (image, label) tuple.
    """
    image, label = grayscale(image, label)
    image, label = normalize(image, label)
    return image, label

def get_negative_size():
    """
    Counts how many 'Negative' images exist in 'data/processed/Negative'.
    """
    negative_path = os.path.join("data", "processed", "Negative")
    return len(os.listdir(negative_path))

def get_positive_size():
    """
    Counts how many 'Positive' images exist in 'data/processed/Positive'.
    """
    positive_path = os.path.join("data", "processed", "Positive")
    return len(os.listdir(positive_path))
