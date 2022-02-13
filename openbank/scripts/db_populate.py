import sqlite3
import os
import json
from datetime import datetime

''' BALANCES '''

def insertVariableIntoBalances(unique_id, account_id, iban, institution_id, created, last_accessed, status, amount,
                               currency, timestamp, db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    insert_with_parameters = """ INSERT INTO balances
                        (unique_id,
                        account_id,
                        iban,
                        institution_id,
                        created, 
                        last_accessed, 
                        status, 
                        amount, 
                        currency, 
                        timestamp)
                        VALUES (?,?,?,?,?,?,?,?,?,?); """
    data_tuple = (
        unique_id, account_id, iban, institution_id, created, last_accessed, status, amount, currency, timestamp
    )
    cursor.execute(insert_with_parameters, data_tuple)
    connection.commit()
    cursor.close()


''' TRANSACTIONS '''

def insertVariableIntoTransactions(transaction_id, bank, account_id, status, booking_date, checkId, UnstructuredInfo,
                                   trasaction_amount, currency, value_date, timestamp, category, db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    insert_with_parameters = """ INSERT INTO transactions
                        (transaction_id,
                        bank,
                        account_id, 
                        status, 
                        booking_date, 
                        checkId, 
                        UnstructuredInfo, 
                        transaction_amount, 
                        currency, 
                        value_date, 
                        timestamp,
                        category)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?); """
    data_tuple = (transaction_id, bank, account_id, status, booking_date, checkId, UnstructuredInfo, trasaction_amount,
                  currency, value_date, timestamp, category)
    cursor.execute(insert_with_parameters, data_tuple)
    connection.commit()
    cursor.close()


def delete_updatable_transaction(db_path, transaction_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM transactions WHERE transaction_id=?', (transaction_id,))
    connection.commit()


def check_if_newTransaction(db_path, single_transaction):
    # single transaction is 'b'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM transactions WHERE transaction_id =?", (single_transaction[0],))
    res = cursor.fetchall()
    if len(res) == 0:
        res_f = 'There is no transaction with id: %s' % single_transaction[0]
        to_be_update = True
    else:
        res_f = 'transaction with id %s already exists' % single_transaction[0]
        new_res = []
        new_single_transaction = []
        for i in range(9):
            new_res.append(res[0][i])
            new_single_transaction.append(single_transaction[i])
        if new_res == new_single_transaction:
            to_be_update = False
        else:
            to_be_update = True

    return res, to_be_update


''' DETAILS '''

def insertVariableIntoDetails(account_id, resource_id, iban, currency, ownerName, name, cashAccountType, bic, details,
                              timestamp, db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    insert_with_parameters = """ INSERT INTO details
                        (account_id, 
                        resource_id, 
                        iban, 
                        currency, 
                        ownerName, 
                        name, 
                        cashAccountType, 
                        bic, 
                        details, 
                        timestamp)
                        VALUES (?,?,?,?,?,?,?,?,?,?); """
    data_tuple = (account_id, resource_id, iban, currency, ownerName, name, cashAccountType, bic, details, timestamp)
    cursor.execute(insert_with_parameters, data_tuple)
    connection.commit()
    cursor.close()

def delete_updatable_details(db_path, account_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM details WHERE acoount_id=?', (account_id,))
    connection.commit()


def check_if_new_accountDetails(db_path, single_details):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM details WHERE account_id =?", (single_details[0],))
    res = cursor.fetchall()
    if len(res) == 0:
        res_f = 'There is no account with id: %s' % single_details[0]
        to_be_update = True
    else:
        res_f = 'account with id %s already exists' % single_details[0]
        new_res = []
        new_single_details = []
        for i in range(8):
            new_res.append(res[0][i])
            new_single_details.append(single_details[i])
        if new_res == new_single_details:
            to_be_update = False
        else:
            to_be_update = True

    return res, to_be_update
