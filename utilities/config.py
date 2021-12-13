import json
import os

global settings
config_filepath = "data/config.json"
auth_cookies_to_store = ["domainName", "OpenIdConnect.token.v1", "X-OWA-CANARY"]


def readConfig():
    global settings

    with open(config_filepath, encoding="utf-8") as data_file:
        settings = json.loads(data_file.read())


def saveConfig():
    global settings

    with open(config_filepath, "w", encoding="utf-8") as data_file:
        json.dump(settings, data_file, indent=4)


def createConfig():
    global settings

    settings = {
        "domainName": "",
        "OpenIdConnect.token.v1": "",
        "X-OWA-CANARY": "",
        "FederationBrandName": "",
        "GAL_ID": "abe38f86-2106-4d28-ad25-9711822096ef", # Fight me im hard coding the global address list ID
        "entries_per_response": 1000,
        "app_url": "https://outlook.office.com/owa/service.svc"
    }

    if not os.path.exists(os.path.dirname(config_filepath)):
        os.makedirs(os.path.dirname(config_filepath))

    saveConfig()


def wipeAuthTokens():
    # Should only be called when the auth tokens are invalid anyways.
    settings["domainName"] = ""
    settings["OpenIdConnect.token.v1"] = ""
    settings["X-OWA-CANARY"] = ""
    settings["FederationBrandName"] = ""
    saveConfig()


def update(key, value):
    settings[key] = value
    saveConfig()


# Load config into memory
if os.path.isfile(config_filepath):
    readConfig()
else:
    createConfig()
    readConfig()
