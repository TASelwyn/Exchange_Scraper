import json
import os

global values
cache_filepath = "data/cache.json"


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
        "directory_users_count": -1,
        "exchange_address_list_ids": ""
    }

    if not os.path.exists(os.path.dirname(cache_filepath)):
        os.makedirs(os.path.dirname(cache_filepath))

    saveCache()


def update(key, value):
    # Use function so it auto saves the cache value
    values[key] = value
    saveCache()


# Load cache into memory
if os.path.isfile(cache_filepath):
    readCache()
else:
    createCache()
    readCache()
