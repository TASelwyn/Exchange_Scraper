import utilities.cache
import utilities.filepaths
from utilities.format import formatUserChangeString
from utilities.tools import getDirectoryUserCount, makeRequestsForScrape, calculateRequestsNeeded, wipeResponseFolder, \
    checkDomainName, printOutContactLists, checkLoggedIn, commenceScrape, responseFolderToCSV

import utilities.config
import modules.grouping

def newScrape():
    # New instance. Start fresh
    print(formatUserChangeString(directory_user_count))

    confirmation = input("No active directory scrape found. Would you like to scrape? (Y/N)\n")[:1].upper()
    if confirmation == "Y":
        commenceScrape(directory_user_count)
        responseFolderToCSV(utilities.filepaths.master_csv_path)


def amendScrape():
    # Data folder has already scraped users in the past.
    print(formatUserChangeString(directory_user_count))

    confirmation = input("Active Directory Size discrepancy found. Proceed to re-scrape? (Y/N)\n")[:1].upper()
    if confirmation == "Y":
        commenceScrape(directory_user_count)
        responseFolderToCSV(utilities.filepaths.discrepancies_master_csv_path)


if __name__ == "__main__":
    print("Devil's Exchange Scraper. V0.2")

    checkLoggedIn()

    # Get Federation Name
    directory_name = checkDomainName(utilities.config.settings["domainName"])["FederationBrandName"]
    utilities.config.update("FederationBrandName", directory_name)

    # Print Contact Lists
    printOutContactLists()

    # Check Active Directory User Count
    directory_user_count = getDirectoryUserCount()
    cached_user_count = utilities.cache.values["scraped_users_count"]

    if cached_user_count == -1:
        # New instance. Start fresh
        newScrape()

    elif utilities.cache.values["scraped_users_count"] != directory_user_count:
        # Data folder has already scraped users in the past.
        amendScrape()

    else:
        print(f"There are {directory_user_count} users in the {directory_name} directory. No member count difference.")
