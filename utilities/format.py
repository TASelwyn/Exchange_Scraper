import utilities.cache
import utilities.config


def formatUserChangeString(new_user_count):
    cached_user_count = utilities.cache.values["scraped_users_count"]
    directory_name = utilities.config.settings["FederationBrandName"]
    return f"There are {new_user_count} users in the {directory_name} directory. Change {cached_user_count} -> {new_user_count}"


def formatTokenAccessDenied(http_status_code):
    return f"Access denied. OWA Token & Client ID Tokens must be authorized. " \
           f"Let's reset them. (HTTP {http_status_code})"
