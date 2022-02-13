from preprocessing import create_transactions_csv, update_transaction_csv
import sys
import logging
import os
from datetime import datetime

now = datetime.now().strftime('%Y%m%d_%H')
tmstmp = datetime.now().timestamp()
'''creating a custom log here'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger_path = os.path.join('../logs/', now + '.log')
fh = logging.FileHandler(logger_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


db_filepath = '../../openbank/data/bank.db'
csv_filepath = '../results/transactions.csv'

if not os.path.isfile(csv_filepath):
    try:
        create_transactions_csv(db_filepath, csv_filepath)
    except Exception as csv_creation_error:
        logger.critical(f'impossible to create a csv file for transaction ----> {csv_creation_error}')
else:
    try:
        logger.info(f'updating csv transaction file with new transactions in {db_filepath}')
        update_transaction_csv(db_filepath, csv_filepath)
        logger.info(f'{csv_filepath} updated correctly')
    except Exception as csv_updating_error:
        logger.warning(f'impossible to create a csv file for transaction ----> {csv_updating_error}')


