import requests
import json
import csv
import math
import os.path
from datetime import datetime

import utils.config


def requestFolderToCSV(folder_path, csv_filepath):
    writeHeader(csv_filepath)
    for filename in os.listdir(folder_path):
        with open(f"{folder_path}/{filename}", encoding="utf-8") as data_file:
            request_json_obj = json.loads(data_file.read())
            responsePrintingToCSV(request_json_obj, "a", csv_filepath)


def responsePrintingToCSV(json_data, writeorappend, output_file):
    input_json = json_data['Body']['ResultSet']

    with open(output_file, writeorappend, newline='', encoding="utf-8") as file:
        csvWriter = csv.writer(file)

        for x in input_json:
            if x != "":
                entry = [x["ADObjectId"], x["PersonaId"]["Id"], x.get("DisplayName", "").encode('utf-8'),
                         x.get("GivenName", ""), x.get("Surname", "").encode('utf-8'), x["EmailAddress"]["EmailAddress"],
                         x.get("WorkCity", "")]
                #print(entry)
                csvWriter.writerow(entry)


def writeHeader(file_to_write):
    header = ['ADObjectId', 'PersonaId', 'UTF-8 Encoded Display Name', 'GivenName', 'Surname', 'EmailAddress',
              'City']

    with open(file_to_write, "w", newline='') as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow(header)


def getContactList():
    cookies = {
        "OpenIdConnect.token.v1": utils.config.settings["openid_token"]
    }

    headers = {
        "Content-Type": "application/json",
        "X-OWA-CANARY": utils.config.settings["x_owa_token"],
        "Action": "GetPeopleFilters"
    }

    response = requests.post(url=utils.config.settings["app_url"], cookies=cookies, headers=headers)
    for x in response.json():
        entry = [x["DisplayName"], x["FolderId"]["__type"], x["FolderId"]["Id"]]
        print(entry)

    return response.json()


def getTotalUsers():
    return makeBatchFindRequest(0, 1, False)["Body"]["TotalNumberOfPeopleInView"]


def batchesNeeded(entries, batch_size):
    return math.ceil(entries / batch_size)


def makeBatchFindRequest(batch_id, batch_size, saveRequest):
    beginning_offset = batch_id * batch_size
    max_entries_returned = batch_size

    cookies = {
        'OpenIdConnect.token.v1': utils.config.settings["openid_token"],
        'X-OWA-CANARY': utils.config.settings["x_owa_token"],
    }

    headers = {
        'x-owa-canary': utils.config.settings["x_owa_token"],
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'x-owa-urlpostdata': f'%7B%22__type%22%3A%22FindPeopleJsonRequest%3A%23Exchange%22%2C%22Header%22%3A%7B%22__type%22%3A%22JsonRequestHeaders%3A%23Exchange%22%2C%22RequestServerVersion%22%3A%22V2018_01_08%22%2C%22TimeZoneContext%22%3A%7B%22__type%22%3A%22TimeZoneContext%3A%23Exchange%22%2C%22TimeZoneDefinition%22%3A%7B%22__type%22%3A%22TimeZoneDefinitionType%3A%23Exchange%22%2C%22Id%22%3A%22Eastern%20Standard%20Time%22%7D%7D%7D%2C%22Body%22%3A%7B%22IndexedPageItemView%22%3A%7B%22__type%22%3A%22IndexedPageView%3A%23Exchange%22%2C%22BasePoint%22%3A%22Beginning%22%2C%22Offset%22%3A{beginning_offset}%2C%22MaxEntriesReturned%22%3A{max_entries_returned}%7D%2C%22QueryString%22%3Anull%2C%22ParentFolderId%22%3A%7B%22__type%22%3A%22TargetFolderId%3A%23Exchange%22%2C%22BaseFolderId%22%3A%7B%22__type%22%3A%22AddressListId%3A%23Exchange%22%2C%22Id%22%3A%22{utils.config.settings["GAL_ID"]}%22%7D%7D%2C%22PersonaShape%22%3A%7B%22__type%22%3A%22PersonaResponseShape%3A%23Exchange%22%2C%22BaseShape%22%3A%22Default%22%2C%22AdditionalProperties%22%3A%5B%7B%22__type%22%3A%22PropertyUri%3A%23Exchange%22%2C%22FieldURI%22%3A%22PersonaAttributions%22%7D%2C%7B%22__type%22%3A%22PropertyUri%3A%23Exchange%22%2C%22FieldURI%22%3A%22PersonaTitle%22%7D%2C%7B%22__type%22%3A%22PropertyUri%3A%23Exchange%22%2C%22FieldURI%22%3A%22PersonaOfficeLocations%22%7D%5D%7D%2C%22ShouldResolveOneOffEmailAddress%22%3Afalse%2C%22SearchPeopleSuggestionIndex%22%3Afalse%7D%7D',
        'action': 'FindPeople',
        'content-type': 'application/json; charset=utf-8',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'origin': 'https://outlook.office.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('action', 'FindPeople'),
        ('app', 'People'),
        ('n', '22'),
    )

    response = requests.post(utils.config.settings["app_url"], headers=headers, params=params, cookies=cookies)

    if saveRequest:
        returned_users = len(response.json()['Body']['ResultSet'])
        with open(f'requests/id_{batch_id}_users_{beginning_offset}_to_{beginning_offset + returned_users - 1}.json',
                  'w') as outfile:
            json.dump(response.json(), outfile, indent=4)

    return response.json()


def loopBetweenBatches(start_batch, end_batch, batch_size, filename):
    writeHeader(filename)
    start_timestamp = datetime.now()
    for batch_id in range(start_batch, end_batch):
        batch_timestamp = datetime.now()

        responseData = makeBatchFindRequest(batch_id, batch_size, True)
        responsePrintingToCSV(responseData, "a", filename)
        returned_users = len(responseData['Body']['ResultSet'])
        print(f"Batch {batch_id} completed. "
              f"Users {batch_id * batch_size} -> {batch_id * batch_size + returned_users - 1} collected. "
              f"Batch took {datetime.now() - batch_timestamp}. Time from start: {datetime.now() - start_timestamp}")
