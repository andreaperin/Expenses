import numpy as np
import pandas as pd
from utility import get_dfbal_from_sqlite, get_dftrans_from_sqlite
from datetime import datetime as dt
import datetime


def database_preprocessing(db_filepath, balance_columns, transactions_columns):
    df_balances = get_dfbal_from_sqlite(filepath=db_filepath)
    df_transactions = get_dftrans_from_sqlite(filepath=db_filepath)
    dates = []
    for idx, row in df_balances.iterrows():
        dates.append(dt.fromtimestamp(float(df_balances.loc[idx].at['timestamp'])).strftime('%Y-%m-%d %H'))
    df_balances['date'] = dates
    new_df_balances = df_balances[balance_columns]
    new_df_transactions = df_transactions[transactions_columns]
    unique_dates = list(new_df_balances['date'].unique())
    unique_inst_id = list(new_df_balances['institution_id'].unique())
    unique_account_id = list(df_transactions['bank'].unique())
    months = []
    years = []
    for i in df_transactions['booking_date']:
        months.append(i[:-3])
        years.append(i[:-6])
    unique_months = set(months)
    unique_years = set(years)
    unique_months = sorted(unique_months, key=lambda x: datetime.datetime.strptime(x, '%Y-%m'))
    options1 = []
    options2 = []
    options3 = []
    options4 = []
    options5 = []
    for date in unique_dates:
        options1.append({'label': date, 'value': date})
    for inst_id in unique_inst_id:
        options2.append({'label': inst_id, 'value': inst_id})
    for account_id in unique_account_id:
        options3.append({'label': account_id, 'value': account_id})
    for month in unique_months:
        options4.append({'label': month, 'value': month})
    for year in unique_years:
        options5.append({'label': year, 'value': year})

    return new_df_balances, new_df_transactions, dates, options1, options2, options3, options4, options5


def create_transactions_csv(db_filepath, csv_filepath):
    df_transactions = get_dftrans_from_sqlite(filepath=db_filepath)
    csv_dataframe = df_transactions[
        ['transaction_id', 'status', 'bank', 'booking_date', 'UnstructuredInfo', 'transaction_amount', 'category']
    ]
    csv_dataframe['sub_category'] = 'tbd'
    csv_dataframe.to_csv(csv_filepath, index=False)


def update_transaction_csv(db_filepath, csv_filepath):
    df_transactions_fromdb = get_dftrans_from_sqlite(filepath=db_filepath)
    df_transactions_fromdb = df_transactions_fromdb[
        ['transaction_id', 'status', 'bank', 'booking_date', 'UnstructuredInfo', 'transaction_amount', 'category']
    ]
    df_transactions_fromcsv = pd.read_csv(csv_filepath, index_col=False)
    transaction_list_csv = []
    for a, b in df_transactions_fromcsv.iterrows():
        transaction_list_csv.append(b['transaction_id'])
    for a, b in df_transactions_fromdb.iterrows():
        if b['transaction_id'] not in transaction_list_csv:
            df_transactions_fromcsv = df_transactions_fromcsv.append(
                df_transactions_fromdb[df_transactions_fromdb['transaction_id'] == b['transaction_id']])
    df_transactions_fromcsv.to_csv(csv_filepath, index=False)
