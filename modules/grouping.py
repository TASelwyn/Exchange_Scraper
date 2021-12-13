import json
import os

import utilities.filepaths
from utilities.tools import dictFromCSV, parseCSVEntry


def findEmailsFromNames(name_list, csv_input_filepath):
    email_list = []

    if os.path.isfile(csv_input_filepath):
        with open(csv_input_filepath) as data_file:
            csv_data_lines = data_file.readlines()
        for current_line in csv_data_lines:
            entry_first_name = parseCSVEntry(current_line)[3]
            entry_email_address = parseCSVEntry(current_line)[5]

            email_list.append(entry_email_address) if entry_first_name in name_list else ''

    else:
        print(f"{csv_input_filepath} doesn't exist! Skipping")


def findNamesAndDumpToFile(name_list, list_title, csvInputFilePath, dumpingJsonFilePath):
    email_list = []

    if not os.path.isfile(dumpingJsonFilePath):
        with open(csvInputFilePath) as data_file:
            csv_data_lines = data_file.readlines()
        for current_line in csv_data_lines:
            entry_first_name = parseCSVEntry(current_line)[3]
            entry_email_address = parseCSVEntry(current_line)[5]
            email_list.append(entry_email_address) if entry_first_name in name_list else ''
            # print(f"Found email {entry_email_address} associated with name {entry_first_name}!") if entry_first_name in name_list else ''

        print(
            f"Searched for {list_title}. Finding a total of {len(email_list)} emails associated. Dumping the list to {dumpingJsonFilePath}")

    else:
        print(f"{dumpingJsonFilePath} already exists! Skipping")

    if len(email_list) < 5:
        # Too little instances to have their own file. Rip.
        # Go to unpopular names :(
        appendEmailsToFilepath(email_list, utilities.filepaths.discrepancies_unpopular_path)
    else:
        with open(dumpingJsonFilePath, "w") as outfile:
            json.dump({"emails": email_list}, outfile, indent=4)


def appendEmailsToFilepath(emails_being_appended, appending_filepath):
    email_list = []

    if not os.path.exists(appending_filepath):
        os.makedirs(appending_filepath)

    if os.path.isfile(appending_filepath):
        with open(appending_filepath) as data_file:
            email_list = json.loads(data_file.read())["emails"]

    for email in emails_being_appended:
        email_list.append(email)

    with open(appending_filepath) as data_file:
        json.dump({"emails": email_list}, data_file, indent=4)

    print(
        f"Appending emails to {appending_filepath}. Finding a total of {len(emails_being_appended)} (from {len(email_list) - len(emails_being_appended)}) new emails associated.")


def groupCSVFile(csv_filepath):
    grouped_dict = dictFromCSV(csv_filepath)

    popular_names = []
    unpopular_names = []
    for name in grouped_dict:
        popular_names.append(name) if grouped_dict[name] >= 5 else ''
        unpopular_names.append(name) if grouped_dict[name] < 5 else ''

    print(popular_names)
    print(f"There are {len(popular_names)} names in popular names in {os.path.basename(csv_filepath)}")
    print(f"There are {len(unpopular_names)} names in unpopular names in {os.path.basename(csv_filepath)}")

    most_popular_first_name = max(grouped_dict, key=grouped_dict.get)
    print(
        f"The most popular name is {most_popular_first_name}, with {grouped_dict[most_popular_first_name]} people with that name!")

