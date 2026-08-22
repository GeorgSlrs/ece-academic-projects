# 1. Initialize with explicit step-by-step control
from dataset import DatasetManager

manager = (DatasetManager("data/processed")
           .load_dataset()
           .balance_classes()
           .preprocess_data()
           .cache_shuffled()
           .make_splits())

# 2. Verify pipeline at each stage
print("Raw dataset samples:")
for img, label in manager.ds.take(1):
    print(img.shape, label.numpy())  # Should be (224,224,3) before grayscale

# 3. Check splits
print("\nClass distribution:")
def count_classes(ds):
    counts = {0:0, 1:0}
    for _, label in ds.unbatch():
        counts[int(label)] += 1
    return counts

print("Train:", count_classes(manager.train_ds))
print("Val:", count_classes(manager.val_ds))
print("Test:", count_classes(manager.test_ds))

# 4. Verify no leakage
def check_duplicates(ds1, ds2):
    hashes1 = {hash(img.numpy().tobytes()) for img, _ in ds1.unbatch()}
    hashes2 = {hash(img.numpy().tobytes()) for img, _ in ds2.unbatch()}
    return hashes1 & hashes2

print("\nDuplicate check:")
print("Train-Val:", len(check_duplicates(manager.train_ds, manager.val_ds)))
print("Train-Test:", len(check_duplicates(manager.train_ds, manager.test_ds)))