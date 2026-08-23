import os
import json
import pickle
from collections import defaultdict

import numpy as np
from PIL import Image
import imagehash
from kaggle.api.kaggle_api_extended import KaggleApi

# Constants specifying where our dataset is coming from on Kaggle,
# and where it will be stored locally (raw and processed).
DATASET_REMOTE_PATH = "arunrk7/surface-crack-detection"
DATASET_LOCAL_PATH = "data/raw"
DATASET_PROCESSED_PATH = "data/processed"
CACHE_DIR_PATH = "cache"
SETTINGS_PATH = "settings.json"


def setup_dir(path):
    """
    Ensures that the directory at 'path' exists,
    creating it if it does not already exist.
    """
    os.makedirs(path, exist_ok=True)


def download_dataset():
    """
    Downloads the dataset from Kaggle into DATASET_LOCAL_PATH
    if it is not already present.
    """
    api = KaggleApi()
    api.authenticate()  # Authenticate with Kaggle credentials

    # Create the local raw data folder if necessary
    setup_dir(DATASET_LOCAL_PATH)

    # If the directory already exists and is non-empty, assume dataset is installed
    if os.path.isdir(DATASET_LOCAL_PATH) and os.listdir(DATASET_LOCAL_PATH):
        print("Dataset already installed")
        return

    # Download and unzip the Kaggle dataset to our local path
    api.dataset_download_files(
        DATASET_REMOTE_PATH,
        path=DATASET_LOCAL_PATH,
        unzip=True
    )
    print("Dataset downloaded and unzipped.")


def get_settings():
    """
    Reads settings from the JSON file at SETTINGS_PATH and
    returns them as a dictionary.
    """
    with open(SETTINGS_PATH, 'r') as file:
        settings = json.load(file)
    return settings


def set_setting(**kwargs):
    """
    Merges current settings with the provided keyword arguments and
    writes them back to the settings file.

    Example usage:
        set_setting(resize=True, remove_duplicates=False)
    """
    settings = get_settings()
    new_settings = {**settings, **kwargs}
    json_object = json.dumps(new_settings, indent=4)
    with open(SETTINGS_PATH, 'w') as file:
        file.write(json_object)


def hash_dataset(rel_path):
    """
    Computes a perceptual hash (pHash) for each image in the subdirectory 'rel_path'
    inside DATASET_LOCAL_PATH. Returns a dictionary {filename: pHash}.
    """
    print(f"Hashing {rel_path} dataset")
    full_path = os.path.join(DATASET_LOCAL_PATH, rel_path)
    result = {}

    # Enumerate over each file in the specified path to compute its pHash
    for count, filename in enumerate(os.listdir(full_path)):
        file_path = os.path.join(full_path, filename)
        with Image.open(file_path) as image:
            phash = imagehash.phash(image)
            result[filename] = phash

        # Print progress every 2000 images
        if count % 2000 == 0:
            print(f"Hashed {count} images in {rel_path} so far.")

    return result


def get_cached_unique():
    """
    Attempts to load a cached dictionary of unique images from CACHE_DIR_PATH.
    Returns a dict containing:
      - "cached": bool
      - "value": the cached dataset if found, otherwise None
    """
    unique_cache_path = os.path.join(CACHE_DIR_PATH, "unique")
    if not os.path.isfile(unique_cache_path):
        return {"cached": False}

    try:
        with open(unique_cache_path, 'rb') as file:
            unique_dataset = pickle.load(file)
        return {"cached": True, "value": unique_dataset}
    except:  # noqa: E722 - Catch-all exception to avoid breaking on any unpickling/IO error
        return {"cached": False}


def cache_unique(data):
    """
    Saves the given 'data' (dictionary of unique images) to a file in CACHE_DIR_PATH.
    """
    print("Caching unique dataset")
    unique_cache_path = os.path.join(CACHE_DIR_PATH, "unique")
    setup_dir(CACHE_DIR_PATH)  # Ensure cache directory exists

    try:
        with open(unique_cache_path, 'wb') as file:
            pickle.dump(data, file)
    except Exception as error:
        print(error)
        print("Caching unique dataset failed")


def get_unique():
    """
    Retrieves unique images from cache if available. Otherwise:
      1. Hashes all images in 'Negative' and 'Positive' folders.
      2. For each set of images sharing the same pHash, only keeps the first image.

    The result is cached for future calls.
    """
    # Check if we have a cached unique dataset
    response = get_cached_unique()
    if response["cached"]:
        print("Retrieving unique from cache")
        print("If you don't want that, remove the cache/unique file")
        return response["value"]

    # If not cached, build the unique dataset
    result = defaultdict(list)
    for status in ["Negative", "Positive"]:
        # Hash all images in each status subdirectory
        collection_map = defaultdict(list)
        for path, phash in hash_dataset(status).items():
            # Group images by their pHash
            collection_map[str(phash)].append(path)

        # From each group of duplicates, keep only the first
        for paths in collection_map.values():
            result[status].append(paths[0])

    # Cache this unique dataset so it doesn't need to be recomputed
    cache_unique(result)
    return result


def remove_duplicates():
    """
    If 'remove_duplicates' is True in settings, copies only the first occurrence
    of each pHash (for Negative and Positive) to the processed directory,
    effectively skipping duplicates.
    """
    settings = get_settings()

    # If remove_duplicates is disabled, do nothing
    if settings.get("remove_duplicates") is False:
        print("Removing duplicates is disabled from settings")
        print("If you don't want that, set that setting to 1")
        return

    print("Removing duplicates")
    status_counts = defaultdict(int)

    # Ensure that processed subdirectories exist for Negative/Positive
    for status in ["Negative", "Positive"]:
        setup_dir(os.path.join(DATASET_PROCESSED_PATH, status))

    # Retrieve the unique dataset
    unique_dataset = get_unique()
    print("Copying all unique images, this might take a while")

    # Go through each class (Negative or Positive) and copy images
    for status, image_list in unique_dataset.items():
        for image_path in image_list:
            copy_path = os.path.join(DATASET_PROCESSED_PATH, status, image_path)
            full_image_path = os.path.join(DATASET_LOCAL_PATH, status, image_path)
            # Open and copy the image to the processed folder
            with Image.open(full_image_path) as image:
                image_copy = image.copy()
                image_copy.save(copy_path)
                status_counts[status] += 1

    # Report how many unique images were copied for each class
    print(f"Negative unique: {status_counts['Negative']}")
    print(f"Positive unique: {status_counts['Positive']}")

    # Disable remove_duplicates in settings after completion
    set_setting(remove_duplicates=0)


def resize_images():
    """
    If 'resize' is True in settings, resizes all images in the processed subdirectories
    ('Negative' and 'Positive') to 224x224.
    """
    settings = get_settings()
    if not settings.get("resize"):
        print("Resize disabled")
        return

    print("Resizing images")
    count = 0
    for status in ["Negative", "Positive"]:
        full_dir_path = os.path.join(DATASET_PROCESSED_PATH, status)
        # Resize each image to 224x224 and overwrite it
        for image_path in os.listdir(full_dir_path):
            if count % 2000 == 0:
                print(f"Resized {count} images")
            full_image_path = os.path.join(full_dir_path, image_path)
            with Image.open(full_image_path) as image:
                new_image = image.resize((224, 224))
                new_image.save(full_image_path)
            count += 1

    # After resizing, disable the resize flag in settings
    set_setting(resize=0)


# Main workflow
download_dataset()
remove_duplicates()
resize_images()
