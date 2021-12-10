import output_stats
import json

from utils.exchange_scraper import requestFolderToCSV

requests_folderpath = "data/requests"
new_csv_filepath = "data/name_dumps/discrepancies/master_output.csv"
old_csv_filepath = "data/name_dumps/master_output.csv"

name_dumps_root = "data/name_dumps"

## ONLY RUN IF THERES A SIZE DISCREPANCY!!


requestFolderToCSV(requests_folderpath, new_csv_filepath)
new_users = output_stats.dictFromCSV(new_csv_filepath)
old_users = output_stats.dictFromCSV(old_csv_filepath)

print(f"New users have {sum(new_users.values())} users!. Old users has {sum(old_users.values())}")

discrepancy_names = []
for key in new_users.keys():
    if old_users[key] != new_users[key]:
        print(f"Key {key} has a size discrepancy between the two sets")
        discrepancy_names.append(key)


new_users_added = []
old_users_removed = []

for i in range(len(discrepancy_names)):
    output_stats.findNamesAndDumpToFile(discrepancy_names[i:i + 1], discrepancy_names[i], new_csv_filepath,
                                        f"data/name_dumps/discrepancies/{discrepancy_names[i]}.json")
    with open(f"data/name_dumps/sorted/{discrepancy_names[i]}.json", encoding="utf-8") as data_file:
        old_list = json.loads(data_file.read())["emails"]
    with open(f"data/name_dumps/discrepancies/{discrepancy_names[i]}.json", encoding="utf-8") as data_file:
        new_list = json.loads(data_file.read())["emails"]

    # If a user is in new list, but not old list. They must be new! Welcome!
    for email in [email for email in new_list if email not in old_list]:
        new_users_added.append(email)

    # If a user is in old list, but not new list. They must have been removed. :(
    for email in [email for email in old_list if email not in new_list]:
        old_users_removed.append(email)



print(new_users_added)
print(old_users_removed)

if len(discrepancy_names) > 0:
    output_stats.fixDiscrepancies()
