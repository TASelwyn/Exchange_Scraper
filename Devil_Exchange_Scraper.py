import os
import json
import utils.config
import utils.cache
from utils.exchange_scraper import *
from output_stats import *

if __name__ == "__main__":
    utils.cache.update("directory_users_count", getTotalUsers())

    print(f"There are {(utils.cache.values['directory_users_count'])} users in the Carleton University directory.")
    getContactList()


