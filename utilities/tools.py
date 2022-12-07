import csv
import math
import os
import json
import modules.requester
import utilities.filepaths
import utilities.config
from datetime import datetime
import utilities.cache
import utilities.format
from concurrent.futures import ThreadPoolExecutor
from utilities.filepaths import responses_dir


def checkCanTokensLogin():
    http_status_code = modules.requester.getContactLists()[0]
    return [True, http_status_code] if modules.requester.getContactLists()[0] == 200 else [False, http_status_code]


def authTokensAreEmpty():
    for cookie in utilities.config.auth_cookies_to_store:
        if utilities.config.settings[cookie] == '':
            return True

    return False


def checkDomainName(domain_name):
    x = modules.requester.getMicrosoftFederationStatus(domain_name)

    status = x['NameSpaceType']

    if status == 'Managed' or status == 'Federated':
        print(f"{x['FederationBrandName']}'s domain {domain_name} is {status}")
    elif status == 'Unknown':
        print('No O365 service could be identified for this domain, or it was entered incorrectly.')
    else:
        print('No O365 status could be found, or there was an error')

    return x


def printOutContactLists():
    contacts = modules.requester.getContactLists()
    for x in contacts[1].json():
        if x["FolderId"]["__type"] == "AddressListId:#Exchange":
            entry = [x["DisplayName"], x["FolderId"]["__type"], x["FolderId"]["Id"]]
            print(entry)


def calculateRequestsNeeded(entries, max_size):
    return math.ceil(entries / max_size)


def getDirectoryUserCount():
    return modules.requester.makeFindPeopleRequest(0, 1, False)["Body"]["TotalNumberOfPeopleInView"]


def write_csv_header(file_to_write):
    header = ['ADObjectId', 'PersonaId', 'Encoded Display Name', 'GivenName', 'Surname', 'EmailAddress',
              'City']

    with open(file_to_write, "w", newline='') as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow(header)


def saveJsonToFile(response, filepath):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as outfile:
        json.dump(response.json(), outfile, indent=4)


def responseFolderToCSV(csv_filepath):
    csv_filepath.parent.mkdir(parents=True, exist_ok=True)
    write_csv_header(csv_filepath)
    for filename in os.listdir(utilities.filepaths.responses_dir):
        with open(f"{utilities.filepaths.responses_dir}/{filename}", encoding="utf-8") as data_file:
            request_json_obj = json.loads(data_file.read())
            responsePrintToCSV(request_json_obj, csv_filepath)


def responsePrintToCSV(json_of_response, output_file):
    input_json = json_of_response['Body']['ResultSet']


    with open(output_file, "a", newline='', encoding="utf-8") as file:
        csvWriter = csv.writer(file)

        for x in input_json:
            if x != "":
                entry = [x["ADObjectId"], x["PersonaId"]["Id"], x.get("DisplayName", "").encode('utf-8'),
                         x.get("GivenName", ""), x.get("Surname", "").encode('utf-8'),
                         x["EmailAddress"]["EmailAddress"],
                         x.get("WorkCity", "")]
                # print(entry)
                csvWriter.writerow(entry)


def wipeResponseFolder():
    responses_dir.mkdir(parents=True, exist_ok=True)

    for filename in os.listdir(utilities.filepaths.responses_dir):
        os.remove(f"{utilities.filepaths.responses_dir}/{filename}")


def make_thread_request(request_id):
    request_size = 1000

    request_start = datetime.now()

    responseData = modules.requester.makeFindPeopleRequest(request_id, request_size, True)
    returned_users = len(responseData['Body']['ResultSet'])

    request_end = datetime.now()

    return request_id, returned_users, request_start, request_end


def makeRequestsForScrape(start_request, end_request, request_size):
    batch_start_timestamp = datetime.now()
    print(f"Started scraping batch at {str(batch_start_timestamp)}.")

    users_scraped = 0
    request_end = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        for result in executor.map(make_thread_request, range(start_request, end_request)):

            request_id, returned_users, request_start, request_end = result
            users_scraped += returned_users

            print(f"Request {f'{request_id}':0>3} completed. "
                  f"Users {f'{request_id * request_size}':0>6} -> {f'{request_id * request_size + returned_users - 1}':0>6} collected. "
                  f"Request took {request_end - request_start}. Time from start: {request_end - batch_start_timestamp}")


    scrape_duration = request_end - batch_start_timestamp

    print(
        f"Total scrape time was {scrape_duration}. Collecting a total of {users_scraped} users from the active directory.")

    return [users_scraped, str(request_end), str(scrape_duration)]


def commenceScrape(directory_user_count):
    wipeResponseFolder()

    max_entries = utilities.config.settings["entries_per_response"]
    requests_needed = calculateRequestsNeeded(directory_user_count, max_entries)

    results = makeRequestsForScrape(0, requests_needed, max_entries)

    if results[0] != directory_user_count:
        print(f"Scrape discrepancy found. I was supposed to find {directory_user_count} but instead found {results[0]}. Wiping scrape.")
        wipeResponseFolder()
    else:
        print("*****" * 15)
        print(f"Successfully scraped {results[0]} people taking {results[2]}")
        print("*****" * 15)

        key_list = ["scraped_users_count", "scraped_users_timestamp", "scrape_duration"]
        utilities.cache.updateKeysFromList(key_list, results)


def fixDiscrepancies():
    filesNotToPutInSorted = ["master_output.csv", "unpopular_names.json"]
    for filename in os.listdir(utilities.filepaths.discrepancies_dir):
        sortedOrNot = "" if (filename in filesNotToPutInSorted) else "sorted/"
        os.replace(f"{utilities.filepaths.discrepancies_dir}/{filename}",
                   f"{utilities.filepaths.names_dir}/{sortedOrNot}{filename}")
        print(
            f"Moved {utilities.filepaths.discrepancies_dir}/{filename} to {utilities.filepaths.names_dir}/{sortedOrNot}{filename}.")


def dictFromCSV(csv_filename):
    with open(csv_filename) as data_file:
        csv_data_lines = data_file.readlines()

    counter = 0
    total_names = {}
    for current in csv_data_lines:
        entry_first_name = parseCSVEntry(current)[3]
        if counter > 1:
            if entry_first_name == "":
                entry_first_name = "N/A"
            value = total_names.get(entry_first_name, 0) + 1
            total_names[entry_first_name] = value

        counter += 1

    return total_names


def parseCSVEntry(entry_row_data):
    columns = entry_row_data.strip().split(",")

    adobject_id = columns[0]
    persona_id = columns[1]
    display_name = columns[2]
    first_name = columns[3].replace(".", "").split(" ")[0]
    last_name = columns[4].replace(".", "")
    email_address = columns[5]

    return [adobject_id, persona_id, display_name, first_name, last_name, email_address]


def auth_login():
    print(
        "Visit the outlook website, login. Then paste the 'cookie' string here from your requests. Make sure it contains X-OWA-CANARY & OpenIdConnect.token.v1 token!")

    cookieString = input("Enter cookie message now: \n").replace(";", "").split(" ")
    for cookie in cookieString:
        if len(cookie.split("=", 1)) == 2:  # Very basic cookie string validation
            cookie_name = cookie.split("=", 1)[0]
            cookie_value = cookie.split("=", 1)[1]

            if cookie_name in utilities.config.auth_cookies_to_store:
                utilities.config.update(cookie_name, cookie_value)


def checkLoggedIn():
    # Loops until authentication passes
    notAuthorised = True
    while notAuthorised:
        if authTokensAreEmpty():
            print(f"Missing authorization tokens!")
            utilities.config.wipeAuthTokens()
            auth_login()

        tokenLoginValidity = checkCanTokensLogin()
        if not tokenLoginValidity[0]:
            print(utilities.format.formatTokenAccessDenied(tokenLoginValidity[1]))
            utilities.config.wipeAuthTokens()
            auth_login()

        if not authTokensAreEmpty() and tokenLoginValidity[0]:
            notAuthorised = False
