import json
import os


def findNamesAndDumpToFile(name_list, list_title, csvInputFilePath, dumpingJsonFilePath):
    email_list = []

    if not os.path.isfile(dumpingJsonFilePath):
        with open(csvInputFilePath) as data_file:
            csv_data_lines = data_file.readlines()
        for current_line in csv_data_lines:
            entry_first_name = current_line.strip().split(",")[3].replace(".", "").split(" ")[0]
            entry_email_address = current_line.strip().split(",")[5]
            email_list.append(entry_email_address) if entry_first_name in name_list else ''
            # print(f"Found email {entry_email_address} associated with name {entry_first_name}!") if entry_first_name in name_list else ''

        print(
            f"Searched for {list_title}. Finding a total of {len(email_list)} emails associated. Dumping the list to {dumpingJsonFilePath}")
        with open(dumpingJsonFilePath, "w") as outfile:
            json.dump({"emails": email_list}, outfile, indent=4)

    else:
        print(f"{dumpingJsonFilePath} already exists! Skipping")


def fixDiscrepancies():
    name_dumps_root = "data/name_dumps"
    filesNotToPutInSorted = ["master_output.csv", "unpopular_names.json"]
    for filename in os.listdir(f"{name_dumps_root}/discrepancies/"):
        sortedOrNot = "" if (filename in filesNotToPutInSorted) else "sorted/"
        os.replace(f"{name_dumps_root}/discrepancies/{filename}", f"{name_dumps_root}/{sortedOrNot}{filename}")
        print(f"Moving {name_dumps_root}/discrepancies/{filename} to {name_dumps_root}/{sortedOrNot}{filename}.")


def dictFromCSV(csv_filename):
    with open(csv_filename) as data_file:
        csv_data_lines = data_file.readlines()

    counter = 0
    total_names = {}
    for current in csv_data_lines:
        entry_first_name = current.strip().split(",")[3].replace(".", "").split(" ")[0]
        if counter > 1 and entry_first_name != "":
            # if current.strip().split(",")[6] != "":
            # print(current.strip())
            value = total_names.get(entry_first_name, 0) + 1
            total_names[entry_first_name] = value
        counter += 1

    return total_names



if __name__ == "__main__":
    # with open('data/new_users/output.csv') as data_file:
    # read_lines = data_file.readlines()

    dictio = dictFromCSV('data/new_users/output.csv')

    popular_names = []
    unpopular_names = []
    for name in dictio:
        popular_names.append(name) if dictio[name] >= 5 else ''
        unpopular_names.append(name) if dictio[name] < 5 else ''

    print(popular_names)
    print(f"There are {len(popular_names)} names in popular names")
    print(f"There are {len(unpopular_names)} names in unpopular names")

    most_popular_first_name = max(dictio, key=dictio.get)
    print(f"The most popular name is {most_popular_first_name}, with {dictio[most_popular_first_name]} people with that name!")
