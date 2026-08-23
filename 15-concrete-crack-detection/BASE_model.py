#Library imports
import tensorflow as tf
from keras._tf_keras.keras.models import Sequential, load_model
from keras._tf_keras.keras.layers import Dense,Dropout,Flatten,GlobalAveragePooling2D
from keras._tf_keras.keras.layers import Conv2D, MaxPooling2D, BatchNormalization
from keras._tf_keras.keras.optimizers import Adam
from keras._tf_keras.keras.callbacks import LearningRateScheduler, EarlyStopping, ModelCheckpoint, TensorBoard
from keras._tf_keras.keras.losses import BinaryCrossentropy
from keras._tf_keras.keras import regularizers



class BASE_Model():

    """
    A Convolutional Neural Network model for binary classification tasks.
    Designed by default for input images of size **224x224x1** (Can be changed), with sigmoid output activation. 
    This machine learning model is able to identify defects in images of manufactured products, ensuring quality control in industrial processes.

    """
    def __init__(self, input_shape = (224,224,1)):
        """"""
        self.model = self.build_model(input_shape)
    
    def build_model(self, input_shape):
        #Model code
        model = Sequential()

        #1st convolution layer
        model.add(Conv2D(filters=16, kernel_size=(3, 3), activation='relu', strides=1, padding='same', data_format='channels_last',
                        input_shape=input_shape, kernel_regularizer=regularizers.l2(1e-4)))
        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2), strides=2, padding='valid'))
        model.add(Dropout(0.3))

        #2nd convolution layer
        model.add(Conv2D(filters=16, kernel_size=(3, 3), strides=1, padding='same', activation='relu', data_format='channels_last', kernel_regularizer=regularizers.l2(1e-4)))
        model.add(BatchNormalization())
        model.add(GlobalAveragePooling2D()) #GlobalAveragePooling instead of Flatten
       
        #1st Dense layer
        model.add(Dense(64, activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))

        #2nd Dense layer
        model.add(Dense(1, activation='sigmoid'))
        return model
    
    def compile(self, loss = BinaryCrossentropy() , optimizer = Adam(learning_rate=0.0001, beta_1=0.9, beta_2=0.999) , metrics=['accuracy']):
        """Compiles the model. Uses binary crossentropy as default loss function and Adam as default optimizer"""
        self.model.compile(optimizer = optimizer, loss = loss, metrics = metrics)

    def summary(self): 
        """Prints out the models layers as well as its trainable parameters"""
        self.model.summary()
    
    def fit(self,train_data,val_data,steps_per_epoch,validation_steps,epochs=10,checkpointPath = "best_model.keras"):
        """Trains the model"""
        try:
            #Callbacks
            val_checker = ValDataChecker(val_data) #Custom callback to check validation set prediction scores and debug
            reduce_lr = LearningRateScheduler(lambda x: 1e-3* 0.9 ** x)
            early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
            checkpoint = ModelCheckpoint(checkpointPath, monitor='val_loss',save_best_only=True)
            logs = TensorBoard(log_dir='./logs')
            
            callbacks = [reduce_lr,early_stop,checkpoint,logs,val_checker]

            return self.model.fit(x=train_data, 
                                            validation_data = val_data, 
                                            verbose = 1, 
                                            epochs = epochs,
                                            shuffle = False,
                                            steps_per_epoch = steps_per_epoch,
                                            validation_steps = validation_steps,
                                            callbacks = callbacks)
        except Exception as e:
            raise ValueError(f"An error occured: {str(e)}") from e

    def save(self, name = "BASE_model.keras"):
        """Saves the model. Must use \".keras\" file extension.
         ***Example usage:*** model.save(\"MyAIModel.keras\") """
        self.model.save(name)

    @staticmethod
    def load(model_path):
        '''Loads the keras model in path. Must use the **.keras** extension'''
        try:
            loaded_model = load_model(model_path)
            base_model = BASE_Model(input_shape=loaded_model.input_shape[1:])
            base_model.model = loaded_model
            return base_model
        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}") from e
    
    def predict(self, data, verbose = 0):
        return self.model.predict(data, verbose = verbose)
    
    def evaluate(self,test_data,batch_size=32):
        return self.model.evaluate(x=test_data,batch_size=batch_size, verbose=1)

####################################################################################################################

class ValDataChecker(tf.keras.callbacks.Callback): #The custom callback class for debugging perposes
    def __init__(self, validation_data):
        super().__init__()
        self.val_data = list(validation_data.unbatch().take(10))  # Cache first 10 samples
        self.epoch = 0

    def on_epoch_begin(self, epoch, logs=None):
        print(f"\nEpoch {epoch} - Validating val set consistency...")
        for i, (x_val, y_val) in enumerate(self.val_data):
            # Check image content
            img_mean = x_val.numpy().mean()
            # Check label consistency
            pred = self.model(x_val[tf.newaxis, ...]).numpy()[0][0]
            print(f"Val sample {i}: mean={img_mean:.4f}, label={y_val.numpy()}, pred={pred:.4f}")
