import logging
import utility_get as get
import db_create as db_c
import db_populate as db_p
import os
import sys
import time
from datetime import datetime
import json

now = datetime.now().strftime('%Y%m%d_%H')
tmstmp = datetime.now().timestamp()


'''creating a custom log here'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger_path=os.path.join('../logs/main', now+'.log')
fh = logging.FileHandler(logger_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def single_bank_data_retrieving(access_token, requisition_id, general={}, balances={}, transactions={}, details={}):
    try:
        account_resp, account_ids = get.get_account(requisition_id=requisition_id, access_token=access_token)
        if isinstance(account_resp, dict):
            if 'status' in account_resp.keys() and isinstance(account_resp, dict):
                for account in account_ids:
                    general_info_json = get.get_general_info(account_id=account, access_token=access_token)
                    general[account] = general_info_json
                    balance_json = get.get_balances(account_id=account, access_token=access_token)
                    balances[account] = balance_json
                    transaction_json = get.get_transactions(account_id=account, access_token=access_token)
                    transactions[account] = transaction_json
                    details_json = get.get_details(account_id=account, access_token=access_token)
                    details[account] = details_json
                return general, balances, transactions, details
        else:
            account_resp = get.get_account(requisition_id=requisition_id, access_token=access_token)
            logger.warning(f'single_bank_data_retrieving: {account_resp}')
    except ValueError as invalid_token:
        logger.critical(f'single_bank_data_retrieving ----> {invalid_token}')

########################################################################################################################
########################################################################################################################


if __name__ == '__main__':
    start_time = time.time()

    access_token = sys.argv[1]
    requisition_id = sys.argv[2]
    bank = sys.argv[3]
    database_path = sys.argv[4]

    if len(access_token) != 0:
        logger.info(f'access token for {bank} correctly retrieved')
    else:
        logger.warning(f'NULL access token for {bank}')
    
    if len(requisition_id) != 0:
        logger.info(f'requisition id for {bank} correctly retrieved')
    else:
        logger.warning(f'NULL requisition id for {bank}')


    ''' creating database if not existing '''

    if not os.path.isfile(database_path):
        db_c.main(database_path)

    ''' retrieving data '''
    logger.info(f'starting single_bank_data_retrieving for {bank}')
    try:
        general, balance, transaction, detail = single_bank_data_retrieving(access_token=access_token,
                                                                            requisition_id=requisition_id)

        data = {'general': general, 'balances': balance, 'transactions': transaction, 'details': detail}
        logger.info(f'data correctly retrieved for bank {bank}')

        '''' sending data to database '''

###--------------------------------------------------------------------------------------------
###                 UNICREDIT
###--------------------------------------------------------------------------------------------

        if bank == 'UNICREDIT':
            logger.info(f'starting post processing data for bank {bank}')
            try:
                UC_balance, UC_transaction, UC_details = get.postprocessingUnicredit(data=data, tmstmp=tmstmp)
                logger.info(f'post processing data for bank {bank} finisched')
            except Exception as UC_postprocerr:
                logger.critical(f'{bank} data cannot be postprocessed ----> {UC_postprocerr}')
                
            ##        BALANCES
            logger.info(f'Inserting Balances to DB for bank {bank}')
            try:
                for a in UC_balance:
                    db_p.insertVariableIntoBalances(unique_id=a[0], account_id=a[1], iban=a[2], institution_id=a[3],
                                                    created=a[4], last_accessed=a[5], status=a[6], amount=a[7],
                                                    currency=a[8], timestamp=a[9], db_path=database_path)
                logger.info(f'Balances correctly inserted in DB for bank {bank}')
            except Exception as UC_balanceserr:
                logger.critical(f'{bank} balances cannot be inserted into db ----> {UC_balanceserr}')

            ##       TRANSACTIONS
            logger.info(f'Inserting Transactions to DB for bank {bank}')
            try:
                for b in UC_transaction:
                    res_t, to_be_update_t = db_p.check_if_newTransaction(db_path=database_path, single_transaction=b)
                    if len(res_t) == 0:
                        db_p.insertVariableIntoTransactions(transaction_id=b[0], bank=bank, account_id=b[1], status=b[2],
                                                            booking_date=b[3], checkId=b[4], UnstructuredInfo=b[5],
                                                            trasaction_amount=b[6], currency=b[7], value_date=b[8],
                                                            timestamp=b[9], category=b[10], db_path=database_path)
                    else:
                        if to_be_update_t:
                            db_p.delete_updatable_transaction(db_path=database_path, transaction_id=b[0])
                            db_p.insertVariableIntoTransactions(transaction_id=b[0], bank=bank, account_id=b[1], status=b[2],
                                                                booking_date=b[3], checkId=b[4], UnstructuredInfo=b[5],
                                                                trasaction_amount=b[6], currency=b[7], value_date=b[8],
                                                                timestamp=b[9], category=b[10], db_path=database_path)
                logger.info(f'Transactions correctly inserted in DB for bank {bank}')
            except Exception as UC_transactionserr:
                logger.critical(f'{bank} transactions cannot be inserted into db ----> {UC_transactionserr}')

            ##        DETAILS
            logger.info(f'Inserting Details to DB for bank {bank}')
            try:
                for c in UC_details:
                    res_d, to_be_update_d = db_p.check_if_new_accountDetails(db_path=database_path, single_details=c)
                    if len(res_d) == 0:
                        db_p.insertVariableIntoDetails(account_id=c[0], resource_id=c[1], iban=c[2], currency=c[3],
                                                    ownerName=c[4], name=c[5], cashAccountType=c[6], bic=c[7],
                                                    details=c[8], timestamp=c[9], db_path=database_path)
                    else:
                        if to_be_update_d:
                            db_p.delete_updatable_details(db_path=database_path, account_id=c[0])
                            db_p.insertVariableIntoDetails(account_id=c[0], resource_id=c[1], iban=c[2], currency=c[3],
                                                        ownerName=c[4], name=c[5], cashAccountType=c[6], bic=c[7],
                                                        details=c[8], timestamp=c[9], db_path=database_path)
                logger.info(f'Details correctly inserted in DB for bank {bank}')
            except Exception as UC_detailserr:
                logger.critical(f'{bank} details cannot be inserted into db ----> {UC_detailserr}')


###--------------------------------------------------------------------------------------------
###                 N26 - Deutsche Bank
###--------------------------------------------------------------------------------------------

        if bank == 'N26':
            logger.info(f'starting post processing data for bank {bank}')
            try:
                N26_balance, N26_transaction, N26_details = get.postprocessingN26(data=data, tmstmp=tmstmp)
                logger.info(f'post processing data for bank {bank} finisched')
            except Exception as N26_postprocerr:
                logger.critical(f'{bank} data cannot be postprocessed ----> {N26_postprocerr}')
                
            ##        BALANCES
            logger.info(f'Inserting Balances to DB for bank {bank}')
            try:
                for a in N26_balance:
                    db_p.insertVariableIntoBalances(unique_id=a[0], account_id=a[1], iban=a[2], institution_id=a[3],
                                                    created=a[4], last_accessed=a[5], status=a[6], amount=a[7],
                                                    currency=a[8], timestamp=a[9], db_path=database_path)
                logger.info(f'Balances correctly inserted in DB for bank {bank}')
            except Exception as N26_balanceserr:
                logger.critical(f'{bank} balances cannot be inserted into db ----> {N26_balanceserr}')

            ##       TRANSACTIONS
            logger.info(f'Inserting Transactions to DB for bank {bank}')
            try:
                for b in N26_transaction:
                    res_t, to_be_update_t = db_p.check_if_newTransaction(db_path=database_path, single_transaction=b)
                    if len(res_t) == 0:
                        db_p.insertVariableIntoTransactions(transaction_id=b[0], bank=bank, account_id=b[1], status=b[2],
                                                            booking_date=b[3], checkId=b[4], UnstructuredInfo=b[5],
                                                            trasaction_amount=b[6], currency=b[7], value_date=b[8],
                                                            timestamp=b[9], category=b[10], db_path=database_path)
                    else:
                        if to_be_update_t:
                            db_p.delete_updatable_transaction(db_path=database_path, transaction_id=b[0])
                            db_p.insertVariableIntoTransactions(transaction_id=b[0], bank=bank, account_id=b[1], status=b[2],
                                                                booking_date=b[3], checkId=b[4], UnstructuredInfo=b[5],
                                                                trasaction_amount=b[6], currency=b[7], value_date=b[8],
                                                                timestamp=b[9], category=b[10], db_path=database_path)
                logger.info(f'Transactions correctly inserted in DB for bank {bank}')
            except Exception as N26_transactionserr:
                logger.critical(f'{bank} transactions cannot be inserted into db ----> {N26_transactionserr}')

            ##        DETAILS
            logger.info(f'Inserting Details to DB for bank {bank}')
            try:
                for c in N26_details:
                    res_d, to_be_update_d = db_p.check_if_new_accountDetails(db_path=database_path, single_details=c)
                    if len(res_d) == 0:
                        db_p.insertVariableIntoDetails(account_id=c[0], resource_id=c[1], iban=c[2], currency=c[3],
                                                    ownerName=c[4], name=c[5], cashAccountType=c[6], bic=c[7],
                                                    details=c[8], timestamp=c[9], db_path=database_path)
                    else:
                        if to_be_update_d:
                            db_p.delete_updatable_details(db_path=database_path, account_id=c[0])
                            db_p.insertVariableIntoDetails(account_id=c[0], resource_id=c[1], iban=c[2], currency=c[3],
                                                        ownerName=c[4], name=c[5], cashAccountType=c[6], bic=c[7],
                                                        details=c[8], timestamp=c[9], db_path=database_path)
                logger.info(f'Details correctly inserted in DB for bank {bank}')
            except Exception as N26_detailserr:
                logger.critical(f'{bank} details cannot be inserted into db ----> {N26_detailserr}')


###--------------------------------------------------------------------------------------------
###                 PAYPAL
###--------------------------------------------------------------------------------------------

        if bank == 'PAYPAL':
            logger.info(f'starting post processing data for bank {bank}')
            try:
                PP_balance, PP_transaction, PP_details = get.postprocessingPaypal(data=data, tmstmp=tmstmp)
                logger.info(f'post processing data for bank {bank} finisched')
            except Exception as PP_postprocerr:
                logger.critical(f'{bank} data cannot be postprocessed ----> {PP_postprocerr}')

            ##        BALANCES
            logger.info(f'Inserting Balances to DB for bank {bank}')
            try:
                for a in PP_balance:
                    db_p.insertVariableIntoBalances(unique_id=a[0], account_id=a[1], iban=a[2], institution_id=a[3],
                                                    created=a[4], last_accessed=a[5], status=a[6], amount=a[7],
                                                    currency=a[8], timestamp=a[9], db_path=database_path)
                logger.info(f'Balances correctly inserted in DB for bank {bank}')
            except Exception as PP_balanceserr:
                logger.critical(f'{bank} balances cannot be inserted into db ----> {PP_balanceserr}')

            ##        TRANSACTIONS
            logger.info(f'Inserting Transactions to DB for bank {bank}')
            try:
                for b in PP_transaction:
                    res_t, to_be_update_t = db_p.check_if_newTransaction(db_path=database_path, single_transaction=b)
                    if len(res_t) == 0:
                        db_p.insertVariableIntoTransactions(transaction_id=b[0], bank=bank, account_id=b[1], status=b[2],
                                                            booking_date=b[3], checkId=b[4], UnstructuredInfo=b[5],
                                                            trasaction_amount=b[6], currency=b[7], value_date=b[8],
                                                            timestamp=b[9], category=b[10], db_path=database_path)
                    else:
                        if to_be_update_t:
                            db_p.delete_updatable_transaction(db_path=database_path, transaction_id=b[0])
                            db_p.insertVariableIntoTransactions(transaction_id=b[0], bank=bank, account_id=b[1], status=b[2],
                                                                booking_date=b[3], checkId=b[4], UnstructuredInfo=b[5],
                                                                trasaction_amount=b[6], currency=b[7], value_date=b[8],
                                                                timestamp=b[9], category=b[10], db_path=database_path)
                logger.info(f'Transactions correctly inserted in DB for bank {bank}')
            except Exception as PP_transactionserr:
                logger.critical(f'{bank} transactions cannot be inserted into db ----> {PP_transactionserr}')

            ##        DETAILS
            logger.info(f'Inserting Details to DB for bank {bank}')
            try:
                for c in PP_details:
                    res_d, to_be_update_d = db_p.check_if_new_accountDetails(db_path=database_path, single_details=c)
                    if len(res_d) == 0:
                        db_p.insertVariableIntoDetails(account_id=c[0], resource_id=c[1], iban=c[2], currency=c[3],
                                                    ownerName=c[4], name=c[5], cashAccountType=c[6], bic=c[7],
                                                    details=c[8], timestamp=c[9], db_path=database_path)
                    else:
                        if to_be_update_d:
                            db_p.delete_updatable_details(db_path=database_path, account_id=c[0])
                            db_p.insertVariableIntoDetails(account_id=c[0], resource_id=c[1], iban=c[2], currency=c[3],
                                                        ownerName=c[4], name=c[5], cashAccountType=c[6], bic=c[7],
                                                        details=c[8], timestamp=c[9], db_path=database_path)
                logger.info(f'Details correctly inserted in DB for bank {bank}')
            except Exception as PP_detailserr:
                logger.critical(f'{bank} details cannot be inserted into db ----> {PP_detailserr}')


        
        
        
        
        elapsed_time = time.time() - start_time
        print("Total elapsed: %.2f" % elapsed_time)
        timing="Total elapsed: %.2f" % elapsed_time
        logger.info(f'all data for bank {bank} have been retrieved and inserted into DB in {timing}')

    except TypeError as invalid_token:
        logger.warning(f'new authentication is required for {bank}')
        print(f'new authentication is required for {bank}')

