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
        "scraped_users_count": -1,
        "scraped_users_timestamp": "",
        "scrape_duration": ""
    }

    if not os.path.exists(os.path.dirname(cache_filepath)):
        os.makedirs(os.path.dirname(cache_filepath))

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
