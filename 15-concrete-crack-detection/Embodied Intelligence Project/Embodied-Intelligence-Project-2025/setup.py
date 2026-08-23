import json
import os
from PIL import Image
import imagehash
import pickle
from collections import defaultdict
import json
import numpy as np

os.environ["KAGGLE_CONFIG_DIR"] = os.getcwd()
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET_REMOTE_PATH = "arunrk7/surface-crack-detection" 
DATASET_LOCAL_PATH = "data/raw"
DATASET_PROCESSED_PATH = "data/processed"
CACHE_DIR_PATH = "cache"
SETTINGS_PATH = "settings.json"

def setup_dir(path):
    os.makedirs(path, exist_ok = True)


def download_dataset():
    api = KaggleApi()
    api.authenticate()

    setup_dir(DATASET_LOCAL_PATH)
    if(os.path.isdir(DATASET_LOCAL_PATH)):
        print("Dataset already installed")
        return

    api.dataset_download_files(
        DATASET_REMOTE_PATH, path = DATASET_LOCAL_PATH, unzip = True)

def get_settings():
    with open(SETTINGS_PATH) as file:
        settings = json.load(file)
    return settings 

def set_setting(**kargs):
    settings = get_settings() 
    new_settings = settings | kargs
    json_object = json.dumps(new_settings, indent = 4)
    with open(SETTINGS_PATH, 'w') as file:
        file.write(json_object)

def hash_dataset(rel_path):
    print(f"Hashing {rel_path} dataset")
    full_path = os.path.join(DATASET_LOCAL_PATH, rel_path)
    result = {}
    for count, path in enumerate(os.listdir(full_path)):
        with Image.open(os.path.join(full_path, path)) as image:
            phash = imagehash.phash(image) 
            result[path] = phash

        if(count % 2000 == 0):
            print(f"hashed {count} images")
    return result

def get_cached_unique():
    unique_cache_path = os.path.join(CACHE_DIR_PATH, "unique")
    if(not os.path.isfile(unique_cache_path)):
        return {"cached": False}
    try:
        with open(unique_cache_path, 'rb') as file:
            unique_dataset = pickle.load(file)
        return {"cached": True, "value": unique_dataset} 
    except:
        return {"cached": False}

def cache_unique(data):
    print("caching unique dataset")
    unique_cache_path = os.path.join(CACHE_DIR_PATH, "unique")
    setup_dir(CACHE_DIR_PATH)
    try:
        with open(unique_cache_path, 'wb') as file:
            pickle.dump(data, file)
    except Exception as error:
        print(error)
        print("Caching unique dataset failed")

def get_unique():
    response = get_cached_unique()
    if response["cached"]:
        print("Retrieving unique from cache")
        print("If you dont want that remove the cache/unique file")
        return response["value"]

    result = defaultdict(list)
    for status in ["Negative", "Positive"]:
        collection_map = defaultdict(list)
        for path, phash in hash_dataset(status).items():
            collection_map[str(phash)].append(path) 

        for paths in collection_map.values():
            result[status].append(paths[0])
    cache_unique(result)
    return result


def remove_duplicates():
    settings = get_settings()
    if settings["remove_duplicates"] == False:
        print("Removing duplicates is disabled from settings")
        print("If you dont want that set that setting to 1")
        return

    print("Removing duplicates")
    status_counts = defaultdict(int)
    for status in ["Negative", "Positive"]:
        setup_dir(os.path.join(DATASET_PROCESSED_PATH, status))
    unique_dataset = get_unique() 
    print("Copying all unique images, this might take a while")
    for status, image_list in unique_dataset.items():
        for image_path in image_list:
            copy_path = os.path.join(DATASET_PROCESSED_PATH, status, image_path)

            full_image_path = os.path.join(DATASET_LOCAL_PATH, status, image_path)
            with Image.open(full_image_path) as image:
                image_copy = image.copy()
                image_copy.save(copy_path)
                status_counts[status] += 1

    print(f"Negative unique: {status_counts["Negative"]}")
    print(f"Positive unique: {status_counts["Positive"]}")
    set_setting(remove_duplicates = 0)

def resize_images():
    settings = get_settings()
    if settings["resize"] == False:
        print("Resize disabled")
        return

    print("Resizing images")
    count = 0
    for status in ["Negative", "Positive"]:
        full_dir_path = os.path.join(DATASET_PROCESSED_PATH, status)
        for image_path in os.listdir(full_dir_path):
            if count % 2000 == 0:
                print(f"Resized {count} images")
            full_image_path = os.path.join(full_dir_path, image_path) 
            with Image.open(full_image_path) as image:
                new_image = image.resize((224, 224))
                new_image.save(full_image_path)
            
            count += 1

    set_setting(resize = 0)

download_dataset()
remove_duplicates()
resize_images()