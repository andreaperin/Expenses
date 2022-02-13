import json
import requests
from utility_auth import pr, BearerAuth
from datetime import datetime


def get_account(requisition_id, access_token):
    url = "https://ob.nordigen.com/api/v2/requisitions/" + requisition_id + '/'
    response = requests.get(url, auth=BearerAuth(access_token))
    response_json = json.loads(response.content.decode('utf-8'))
    try:
        account_ids = response_json['accounts']
        return response_json, account_ids
    except KeyError as invalid_token:
        return response_json


def get_general_info(account_id, access_token):
    url = "https://ob.nordigen.com/api/v2/accounts/" + account_id + "/"
    response = requests.get(url=url, auth=BearerAuth(access_token))
    response_json = json.loads(response.content.decode('utf-8'))
    return response_json


def get_balances(account_id, access_token):
    url = "https://ob.nordigen.com/api/v2/accounts/" + account_id + "/balances/"
    response = requests.get(url=url, auth=BearerAuth(access_token))
    response_json = json.loads(response.content.decode('utf-8'))
    return response_json


def get_transactions(account_id, access_token):
    url = "https://ob.nordigen.com/api/v2/accounts/" + account_id + "/transactions/"
    response = requests.get(url=url, auth=BearerAuth(access_token))
    response_json = json.loads(response.content.decode('utf-8'))
    return response_json


def get_details(account_id, access_token):
    url = "https://ob.nordigen.com/api/v2/accounts/" + account_id + "/details/"
    response = requests.get(url=url, auth=BearerAuth(access_token))
    response_json = json.loads(response.content.decode('utf-8'))
    return response_json


''' Post-Processing based on single bank output '''


def postprocessingUnicredit(data, tmstmp, UC_balances=[], UC_transactions=[], UC_details=[]):
    '''
        Balances
    '''
    for account in list(data['general'].keys()):
        account_id = account
        iban = data['general'][account]['iban']
        institution_id = data['general'][account]['institution_id']
        created = data['general'][account]['created']
        last_accessed = data['general'][account]['last_accessed']
        status = data['general'][account]['status']
        amount = data['balances'][account]['balances'][0]['balanceAmount']['amount']
        currency = data['balances'][account]['balances'][0]['balanceAmount']['currency']
        timestamp = tmstmp
        unique_id = datetime.fromtimestamp(tmstmp).strftime('%Y.%m.%d-%H:%M') + '_account:' + account[:5]
        i = (unique_id, account_id, iban, institution_id, created, last_accessed, status, amount, currency, timestamp)
        UC_balances.append(i)

    '''
        Transactions
    '''
    for account in list(data['transactions'].keys()):
        for status in list(data['transactions'][account]['transactions']):
            for single_transaction in data['transactions'][account]['transactions'][status]:
                if status == 'booked':
                    transaction_id = single_transaction['transactionId']
                    account_id = account
                    booking_date = single_transaction['bookingDate']
                    checkId = single_transaction['checkId']
                    UnstructuredInfo = single_transaction['remittanceInformationUnstructured']
                    transaction_amount = single_transaction['transactionAmount']['amount']
                    currency = single_transaction['transactionAmount']['currency']
                    value_date = single_transaction['valueDate']
                    timestamp = tmstmp
                    category = 'TBD'
                if status == 'pending':
                    try:
                        transaction_id = single_transaction['transactionId']
                        account_id = account
                        booking_date = single_transaction['bookingDate']
                        checkId = single_transaction['checkId']
                        UnstructuredInfo = single_transaction['remittanceInformationUnstructured']
                        transaction_amount = single_transaction['transactionAmount']['amount']
                        currency = single_transaction['transactionAmount']['currency']
                        value_date = single_transaction['valueDate']
                        timestamp = tmstmp
                        category = 'TBD'
                    except Exception:
                        transaction_id = 'TBD'
                        account_id = 'TBD'
                        booking_date = 'TBD'
                        checkId = 'TBD'
                        UnstructuredInfo = 'TBD'
                        transaction_amount = 'TBD'
                        currency = 'TBD'
                        value_date = 'TBD'
                        timestamp = tmstmp
                        category = 'TBD'
                j = (transaction_id, account_id, status, booking_date, checkId, UnstructuredInfo, transaction_amount,
                     currency, value_date, timestamp, category)
                UC_transactions.append(j)

    '''
            Details
    '''
    for account in list(data['details'].keys()):
        account_id = account
        resource_id = data['details'][account]['account']['resourceId']
        iban = data['details'][account]['account']['iban']
        currency = data['details'][account]['account']['currency']
        ownerName = data['details'][account]['account']['ownerName']
        name = data['details'][account]['account']['name']
        cashAccountType = data['details'][account]['account']['cashAccountType']
        bic = data['details'][account]['account']['bic']
        details = data['details'][account]['account']['details']
        timestamp = tmstmp
        k = (account_id, resource_id, iban, currency, ownerName, name, cashAccountType, bic, details, timestamp)
        UC_details.append(k)

    return UC_balances, UC_transactions, UC_details


def postprocessingPaypal(data, tmstmp, PP_balances=[], PP_transactions=[], PP_details=[]):
    '''
        Balances
    '''
    for account in list(data['general'].keys()):
        account_id = account
        iban = data['general'][account]['iban']
        institution_id = data['general'][account]['institution_id']
        created = data['general'][account]['created']
        last_accessed = data['general'][account]['last_accessed']
        status = data['general'][account]['status']
        amount = data['balances'][account]['balances'][0]['balanceAmount']['amount']
        currency = data['balances'][account]['balances'][0]['balanceAmount']['currency']
        timestamp = tmstmp
        unique_id = datetime.fromtimestamp(tmstmp).strftime('%Y.%m.%d-%H:%M') + '_account:' + account[:5]
        i = (unique_id, account_id, iban, institution_id, created, last_accessed, status, amount, currency, timestamp)
        PP_balances.append(i)

    '''
        Transactions
    '''
    for account in list(data['transactions'].keys()):
        for status in list(data['transactions'][account]['transactions']):
            for single_transaction in data['transactions'][account]['transactions'][status]:
                if status == 'booked':
                    transaction_id = single_transaction['transactionId']
                    account_id = account
                    booking_date = single_transaction['bookingDate']
                    checkId = 'N/A'
                    UnstructuredInfo = single_transaction['additionalInformation'] + " " + single_transaction[
                        'creditorName']
                    transaction_amount = single_transaction['transactionAmount']['amount']
                    currency = single_transaction['transactionAmount']['currency']
                    value_date = 'N/A'
                    timestamp = tmstmp
                    category = 'TBD'
                if status == 'pending':
                    try:
                        transaction_id = single_transaction['transactionId']
                        account_id = account
                        booking_date = single_transaction['bookingDate']
                        checkId = 'N/A'
                        UnstructuredInfo = single_transaction['additionalInformation'] + " " + single_transaction[
                            'creditorName']
                        transaction_amount = single_transaction['transactionAmount']['amount']
                        currency = single_transaction['transactionAmount']['currency']
                        value_date = 'N/A'
                        timestamp = tmstmp
                        category = 'TBD'
                    except Exception:
                        transaction_id = 'TBD'
                        account_id = 'TBD'
                        booking_date = 'TBD'
                        checkId = 'TBD'
                        UnstructuredInfo = 'TBD'
                        transaction_amount = 'TBD'
                        currency = 'TBD'
                        value_date = 'TBD'
                        timestamp = tmstmp
                        category = 'TBD'
                j = (transaction_id, account_id, status, booking_date, checkId, UnstructuredInfo, transaction_amount,
                     currency, value_date, timestamp, category)
                PP_transactions.append(j)

    '''
            Details
    '''
    for account in list(data['details'].keys()):
        account_id = account
        resource_id = data['details'][account]['account']['resourceId']
        iban = data['general'][account]['iban']  ## correction cause paypal details do not show iban
        currency = data['details'][account]['account']['currency']
        ownerName = data['details'][account]['account']['ownerName']
        name = ownerName  ## correction cause paypal details do not show iban
        cashAccountType = 'N/A'
        bic = 'N/A'
        details = data['details'][account]['account']['usage']
        timestamp = tmstmp
        k = (account_id, resource_id, iban, currency, ownerName, name, cashAccountType, bic, details, timestamp)
        PP_details.append(k)

    return PP_balances, PP_transactions, PP_details



def postprocessingN26(data, tmstmp, N26_balances=[], N26_transactions=[], N26_details=[]):
    '''
        Balances
    '''
    for account in list(data['general'].keys()):
        account_id = account
        iban = data['general'][account]['iban']
        institution_id = data['general'][account]['institution_id']
        created = data['general'][account]['created']
        last_accessed = data['general'][account]['last_accessed']
        status = data['general'][account]['status']
        amount = data['balances'][account]['balances'][0]['balanceAmount']['amount']
        currency = data['balances'][account]['balances'][0]['balanceAmount']['currency']
        timestamp = tmstmp
        unique_id = datetime.fromtimestamp(tmstmp).strftime('%Y.%m.%d-%H:%M') + '_account:' + account[:5]
        i = (unique_id, account_id, iban, institution_id, created, last_accessed, status, amount, currency, timestamp)
        N26_balances.append(i)

    '''
        Transactions
    '''
    for account in list(data['transactions'].keys()):
        for status in list(data['transactions'][account]['transactions']):
            for single_transaction in data['transactions'][account]['transactions'][status]:
                if status == 'booked':
                    transaction_id = single_transaction['transactionId']
                    account_id = account
                    booking_date = single_transaction['bookingDate']
                    checkId = single_transaction['bankTransactionCode']
                    if 'creditorName' in single_transaction.keys():
                        UnstructuredInfo = single_transaction['creditorName']
                    if 'debtorName' in single_transaction.keys():
                        UnstructuredInfo = single_transaction['debtorName']+'; '+single_transaction['remittanceInformationUnstructuredArray'][0]                    
                    transaction_amount = single_transaction['transactionAmount']['amount']
                    currency = single_transaction['transactionAmount']['currency']
                    value_date = single_transaction['valueDate']
                    timestamp = tmstmp
                    category = 'TBD'
                if status == 'pending':
                    try:
                        transaction_id = single_transaction['transactionId']
                        account_id = account
                        booking_date = single_transaction['bookingDate']
                        checkId = single_transaction['bankTransactionCode']
                        if 'creditorName' in single_transaction.keys():
                            UnstructuredInfo = single_transaction['creditorName']
                        if 'debtorName' in single_transaction.keys():
                            UnstructuredInfo = single_transaction['debtorName']+'; '+single_transaction['remittanceInformationUnstructuredArray'][0]                    
                        transaction_amount = single_transaction['transactionAmount']['amount']
                        currency = single_transaction['transactionAmount']['currency']
                        value_date = single_transaction['valueDate']
                        timestamp = tmstmp
                        category = 'TBD'
                    except Exception:
                        transaction_id = 'TBD'
                        account_id = 'TBD'
                        booking_date = 'TBD'
                        checkId = 'TBD'
                        UnstructuredInfo = 'TBD'
                        transaction_amount = 'TBD'
                        currency = 'TBD'
                        value_date = 'TBD'
                        timestamp = tmstmp
                        category = 'TBD'
                j = (transaction_id, account_id, status, booking_date, checkId, UnstructuredInfo, transaction_amount,
                     currency, value_date, timestamp, category)
                N26_transactions.append(j)

    '''
            Details
    '''
    for account in list(data['details'].keys()):
        account_id = account
        resource_id = data['details'][account]['account']['resourceId']
        iban = data['details'][account]['account']['iban']
        currency = data['details'][account]['account']['currency']
        ownerName = 'Andrea Perin'
        name = data['details'][account]['account']['name']
        cashAccountType = data['details'][account]['account']['cashAccountType']
        bic = data['details'][account]['account']['bic']
        details = 'None'
        timestamp = tmstmp
        k = (account_id, resource_id, iban, currency, ownerName, name, cashAccountType, bic, details, timestamp)
        N26_details.append(k)

    return N26_balances, N26_transactions, N26_details