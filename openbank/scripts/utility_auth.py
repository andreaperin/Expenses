import json
import pprint
import requests

pp = pprint.PrettyPrinter(indent=4)


def pr(trial):
    pp.pprint(trial)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_access_and_refresh_token(SECRET_ID, SECRET_KEY):
    """

    :param SECRET_ID:       created through nordigen webpage
    :param SECRET_KEY:      created through nordigen webpage
    :return:                access_token and refresh_token

    """

    url = "https://ob.nordigen.com/api/v2/token/new/"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'secret_id': SECRET_ID,
        'secret_key': SECRET_KEY
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    response_json = json.loads(response.content.decode('utf-8'))
    access_token = response_json['access']
    refresh_token = response_json['refresh']

    return access_token, refresh_token


def refresh_access_token(refresh_token):
    """

    :param refresh_token:       obtained though previous function
    :return:                    a new access_token when expired

    """

    url = "https://ob.nordigen.com/api/v2/token/refresh/"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'refresh': refresh_token
    }

    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    response_json = json.loads(response.content.decode('utf-8'))
    access_token = response_json['access']
    return access_token


def list_available_banks(access_token, my_bank_list, country):
    """

    :param access_token:
    :param my_bank_list:    list containing names of all the banks you are interested in
    :return:                list of all available banks for italy, and specific list of interested ones

    """
    url = "https://ob.nordigen.com/api/v2/institutions/?country=" + country
    response = requests.get(url=url, auth=BearerAuth(access_token))
    response_json = json.loads(response.content.decode('utf-8'))
    my_banks = []
    for el in response_json:
        for bank in my_bank_list:
            if bank in el['id']:
                my_banks.append(el)
    return response_json, my_banks


def change_default_agreement(access_token, institution_id, max_historical_days, access_valid_for_days):
    """

    :param access_token:
    :param institution_id:          ID of the banks from previous function
    :param max_historical_days:     number of days back in time
    :param access_valid_for_days:   availability intervall
    :return:                        response if default setting are properly changed

    """

    url = "https://ob.nordigen.com/api/v2/agreements/enduser/"
    headers = {'Authorization': 'Bearer ' + access_token}
    data = {
        "institution_id": institution_id,
        "max_historical_days": max_historical_days,
        "access_valid_for_days": access_valid_for_days,
        "access_scope": [
            "balances",
            "details",
            "transactions"
        ]
    }
    response = requests.post(url=url, json=data, headers=headers)
    response_json = json.loads(response.content.decode('utf-8'))
    return response_json


def auth_for_specific_institution(access_token, institution_id, redirect_uri):
    """

    This function is used to connect nordigen API to banks in order to retrieve data.
    redirect_URI is useless but needed

    :param redirect_uri:
    :param institution_id:
    :param access_token:
    :param account_id:
    :return:                a link to connect nordigen API to interested bank, and requisition_id

    """

    url = "https://ob.nordigen.com/api/v2/requisitions/"
    headers = {'Authorization': 'Bearer ' + access_token}
    data = {
        "redirect": redirect_uri,  # "http://localhost/",
        "institution_id": institution_id,
    }

    response = requests.post(url=url, json=data, headers=headers)
    response_json = json.loads(response.content.decode('utf-8'))
    requisition_id = response_json['id']
    return response_json, requisition_id
