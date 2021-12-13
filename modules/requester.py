import requests
import utilities.config
import utilities.filepaths
# from utilities.tools import saveJsonToFile
import utilities.tools


# Every function in this file has to directly make it's own web request.


def getContactLists():
    cookies = {
        "OpenIdConnect.token.v1": utilities.config.settings["OpenIdConnect.token.v1"]
    }
    headers = {
        "Content-Type": "application/json",
        "X-OWA-CANARY": utilities.config.settings["X-OWA-CANARY"],
        "Action": "GetPeopleFilters"
    }

    response = requests.post(url=utilities.config.settings["app_url"], cookies=cookies, headers=headers)
    return [response.status_code, response]


def makeFindPeopleRequest(request_id, max_entries_size, save_request):
    beginning_offset = request_id * max_entries_size

    cookies = {
        'OpenIdConnect.token.v1': utilities.config.settings["OpenIdConnect.token.v1"],
        'X-OWA-CANARY': utilities.config.settings["X-OWA-CANARY"],
    }

    headers = {
        'x-owa-canary': utilities.config.settings["X-OWA-CANARY"],
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'x-owa-urlpostdata': f'%7B%22__type%22%3A%22FindPeopleJsonRequest%3A%23Exchange%22%2C%22Header%22%3A%7B%22__type%22%3A%22JsonRequestHeaders%3A%23Exchange%22%2C%22RequestServerVersion%22%3A%22V2018_01_08%22%2C%22TimeZoneContext%22%3A%7B%22__type%22%3A%22TimeZoneContext%3A%23Exchange%22%2C%22TimeZoneDefinition%22%3A%7B%22__type%22%3A%22TimeZoneDefinitionType%3A%23Exchange%22%2C%22Id%22%3A%22Eastern%20Standard%20Time%22%7D%7D%7D%2C%22Body%22%3A%7B%22IndexedPageItemView%22%3A%7B%22__type%22%3A%22IndexedPageView%3A%23Exchange%22%2C%22BasePoint%22%3A%22Beginning%22%2C%22Offset%22%3A{beginning_offset}%2C%22MaxEntriesReturned%22%3A{max_entries_size}%7D%2C%22QueryString%22%3Anull%2C%22ParentFolderId%22%3A%7B%22__type%22%3A%22TargetFolderId%3A%23Exchange%22%2C%22BaseFolderId%22%3A%7B%22__type%22%3A%22AddressListId%3A%23Exchange%22%2C%22Id%22%3A%22{utilities.config.settings["GAL_ID"]}%22%7D%7D%2C%22PersonaShape%22%3A%7B%22__type%22%3A%22PersonaResponseShape%3A%23Exchange%22%2C%22BaseShape%22%3A%22Default%22%2C%22AdditionalProperties%22%3A%5B%7B%22__type%22%3A%22PropertyUri%3A%23Exchange%22%2C%22FieldURI%22%3A%22PersonaAttributions%22%7D%2C%7B%22__type%22%3A%22PropertyUri%3A%23Exchange%22%2C%22FieldURI%22%3A%22PersonaTitle%22%7D%2C%7B%22__type%22%3A%22PropertyUri%3A%23Exchange%22%2C%22FieldURI%22%3A%22PersonaOfficeLocations%22%7D%5D%7D%2C%22ShouldResolveOneOffEmailAddress%22%3Afalse%2C%22SearchPeopleSuggestionIndex%22%3Afalse%7D%7D',
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

    response = requests.post(utilities.config.settings["app_url"], headers=headers, params=params, cookies=cookies)
    if response.status_code == 200:
        if save_request:
            returned_users = len(response.json()['Body']['ResultSet'])
            response_filepath = f"{utilities.filepaths.responses_dir}/id_{request_id}_users_{beginning_offset}_to_{beginning_offset + returned_users - 1}.json"
            utilities.tools.saveJsonToFile(response, response_filepath)

        return response.json()
    else:
        return {}


def getMicrosoftFederationStatus(domain_name):
    params = {
        'login': 'devil@' + str(domain_name),
        'json': '1'
    }

    try:
        response = requests.get("https://login.microsoftonline.com/getuserrealm.srf", params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print("Http Error:", error)
        raise SystemExit(error)
    except requests.exceptions.ConnectionError as error:
        print("Error Connecting:", error)
        raise SystemExit(error)
    except requests.exceptions.Timeout as error:
        print("Timeout Error:", error)
        raise SystemExit(error)
    except requests.exceptions.RequestException as error:
        print("Uh-oh: Something Bad Happened", error)
        raise SystemExit(error)

    return response.json()
