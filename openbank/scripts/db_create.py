import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database specified by db_file
    
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)


def main(mine_database):
    sql_create_balances_table = """ CREATE TABLE IF NOT EXISTS balances (
                                        unique_id text PRIMARY KEY,
                                        account_id text,
                                        iban text NOT NULL,
                                        institution_id text NOT NULL,
                                        created text,
                                        last_accessed text,
                                        status text,
                                        amount text,
                                        currency text,
                                        timestamp text
                                    ); """

    sql_create_transactions_table = """CREATE TABLE IF NOT EXISTS transactions (
                                    transaction_id text PRIMARY KEY,
                                    bank text,
                                    account_id text,
                                    status text,
                                    booking_date text,
                                    checkId text,
                                    UnstructuredInfo text,
                                    transaction_amount text,
                                    currency text, 
                                    value_date text,
                                    timestamp text,
                                    category text,  
                                    FOREIGN KEY (account_id) REFERENCES balances (account_id)
                                );"""
    # Status can be booked or pending

    sql_create_details_table = """CREATE TABLE IF NOT EXISTS details (
                                    account_id text PRIMARY KEY,
                                    resource_id text,
                                    iban text,
                                    currency text,
                                    ownerName text,
                                    name text,
                                    cashAccountType text,
                                    bic text,
                                    details text,
                                    timestamp text,
                                    FOREIGN KEY (account_id) REFERENCES balances (account_id),
                                    FOREIGN KEY (iban) REFERENCES balances (iban)
                                );"""

    # create a database connection
    conn = create_connection(mine_database)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_balances_table)
        create_table(conn, sql_create_transactions_table)
        create_table(conn, sql_create_details_table)
    else:
        print(f"Error! cannot create the database connection with {mine_database}.")


