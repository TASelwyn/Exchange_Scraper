import json
import os
from utilities.filepaths import data_root
global values
cache_filepath = data_root.joinpath("cache.json")


def readCache():
    global values

    with open(cache_filepath, encoding="utf-8") as data_file:
        values = json.loads(data_file.read())


def saveCache():
    global values

    with open(cache_filepath, "w", encoding="utf-8") as data_file:
        json.dump(values, data_file, indent=4)


def createCache():
    global values

    values = {
        "scraped_users_count": None,
        "scraped_users_timestamp": "",
        "scrape_duration": ""
    }

    data_root.mkdir(parents=True, exist_ok=True)

    saveCache()


def update(key, value):
    # Use function so it auto saves the cache value
    values[key] = value
    saveCache()


def updateKeysFromList(key_list, new_value_list):
    # Use function so it auto saves the cache value
    for i in range(len(key_list)):
        values[key_list[i]] = new_value_list[i]
    saveCache()


# Load cache into memory
if os.path.isfile(cache_filepath):
    readCache()
else:
    createCache()
    readCache()
