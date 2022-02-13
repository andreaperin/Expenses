import logging
import utility_auth as auth
import utility_get as get
import os
import sys
import time
import json
from datetime import datetime

now = datetime.now().strftime('%Y%m%d_%H')

'''creating a custom log here'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger_path=os.path.join('../logs/auth', now+'.log')
fh = logging.FileHandler(logger_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def authentication(SECRET_ID, SECRET_KEY):
    logger.info('obtaining access and refresh token')
    try:
        access_token, refresh_token = auth.get_access_and_refresh_token(SECRET_ID, SECRET_KEY)
        logger.info('token correctly obtained')
    except Exception as auth_err:
        logger.critical(f'auth error ----> {auth_err}')
    ## Refreshing Access Token
    logger.info('refreshing access token')
    try:
        access_token = auth.refresh_access_token(refresh_token=refresh_token)
        logger.info('access token correctly refreshed')
        return access_token
    except Exception as refresh_error:
        logger.critical(f'refresh error ----> {refresh_error}')


def single_bank_auth(bank, access_token, country, max_historical_days, access_valid_days, redirect_uri, need_link):
    ## Getting my bank lists
    logger.info('obtaining the list of banks available in nordigen')
    try:
        all_banks_it, my_banks = auth.list_available_banks(access_token=access_token, my_bank_list=[bank],
                                                       country=country)
        institution_id = my_banks[-1]['id']
        logger.info('list correctly retrieved')
    except Exception as banklist_error:
        logger.critical(f'unable to retrieve bank list ----> {banklist_error}')

    ## Change Default Agreement
    logger.info('changing default agreement')
    try:
        res = auth.change_default_agreement(access_token=access_token, institution_id=institution_id,
                                            max_historical_days=max_historical_days,
                                            access_valid_for_days=access_valid_days)
        responses_change_agreement = res
        logger.info('aggreement correctly changed')
    except Exception as agreement_err:
        logger.critical(f'unable to change default agreement ----> {agreement_err}')

    ## Generate link to allow nordigen retrieve data, and generating requisition_id
    logger.info('generating link to proceed with authentication')
    try:
        res_link, requisition_id = auth.auth_for_specific_institution(access_token=access_token,
                                                                    institution_id=institution_id,
                                                                    redirect_uri=redirect_uri)
        if need_link == '1':
            print(f'Allow Nordigen to get info from {bank} following the link:')
            print(res_link['link'])
        logger.info('link correctly generated')
    except Exception as link_err:
        logger.critical(f'unable to generate link ----> {link_err}')
    return institution_id, responses_change_agreement, requisition_id



########################################################################################################################
########################################################################################################################


if __name__ == '__main__':
    start_time = time.time()

    SECRET_ID = sys.argv[1]
    SECRET_KEY = sys.argv[2]
    country = sys.argv[3]
    max_historical_days = sys.argv[4]
    access_valid_days = sys.argv[5]
    redirect_uri = sys.argv[6]
    need_link = sys.argv[7]
    bank = sys.argv[8]

    # print(f'Authentication for {bank}')
    logger.info(f'starting authentication for bank {bank}')
    try:
        access_token = authentication(SECRET_ID=SECRET_ID, SECRET_KEY=SECRET_KEY)
        logger.info(f'authentication for {bank} correctly done')
    except Exception as error1:
        logger.critical(f'authentication error for {bank} ----> {error1}')
    logger.info(f'generating link for bank {bank}')
    try:
        institution_id, responses_change_agreement, requisition_id = single_bank_auth(access_token=access_token, bank=bank,                                                                                    country=country,                            max_historical_days=max_historical_days,
                                                                                    access_valid_days=access_valid_days,
                                                                                    redirect_uri=redirect_uri,
                                                                                    need_link=need_link)
        logger.info(f'link for {bank} correctly generated')
    except Exception as error2:
        logger.critical(f'failure in generating link for {bank} ----> {error2}')


    # creating a tmp folder to store access_token and requisition_id for a specific bank after having performed log in:
    # created json file will be exploited and deleted by .sh script, that will add everything as environmental variable
    time.sleep(60)
    logging.info('saving tokens in a temporary folder')
    mine = {'access_token': access_token, 'requisition_id': requisition_id}
    if not os.path.exists('../results/tmp'):
        os.mkdir('../results/tmp')
        with open('../results/tmp/mine.json', 'w') as j:
            json.dump(mine, j, indent=4)
    logging.info('deleted temporary folder')



