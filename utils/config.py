import json
import os

global settings
config_filepath = "data/config.json"


def readConfig():
    global settings

    with open(config_filepath, encoding="utf-8") as data_file:
        settings = json.loads(data_file.read())


def saveConfig():
    global settings

    with open(config_filepath, "w", encoding="utf-8") as data_file:
        json.dump(settings, data_file, indent=4)


def createConfig():
    config = {
        "x_owa_token": "",
        "openid_token": "",
        "GAL_ID": "abe38f86-2106-4d28-ad25-9711822096ef",
        "app_url": "https://outlook.office.com/owa/service.svc"
    }

    if not os.path.exists(os.path.dirname(config_filepath)):
        os.makedirs(os.path.dirname(config_filepath))

    with open(config_filepath, "w", encoding="utf-8") as data_file:
        json.dump(config, data_file, indent=4)


# Load config into memory
if os.path.isfile(config_filepath):
    readConfig()
else:
    createConfig()
    readConfig()
