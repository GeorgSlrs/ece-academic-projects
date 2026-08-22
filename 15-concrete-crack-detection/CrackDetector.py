from BASE_model import BASE_Model
from dataset import DatasetManager
import tensorflow as tf

SEED = 88

data_path = "data/processed"

dataManager = (DatasetManager(data_path,augment_train=False)
               .load_dataset()
               .balance_classes()
               .preprocess_data()
               .cache_shuffled()
               .make_splits())

train_data = dataManager.get_train_ds().shuffle(buffer_size = 1000,
                            seed=SEED,
                            reshuffle_each_iteration = True,
                            name = "Test_shuffle").prefetch(tf.data.AUTOTUNE).repeat()

val_data = dataManager.get_validation_ds()
test_data = dataManager.get_test_ds()
train_cardinality = dataManager.get_train_cardinality()
test_cardinality = dataManager.get_test_cardinality()
val_cardinality = dataManager.get_val_cardinality()

print(f"Cardinalities: \n train: {train_cardinality} \n validaton: {val_cardinality} \n test: {test_cardinality}")

model = BASE_Model()
model.compile()
model.summary()
history = model.fit(train_data,
                    val_data,
                    steps_per_epoch=train_cardinality,
                    validation_steps=val_cardinality,
                    epochs=5)
model.save("6thTry.keras")
model.evaluate(test_data=test_data)
