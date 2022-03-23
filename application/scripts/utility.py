import sqlite3
from sqlite3.dbapi2 import DateFromTicks

import numpy as np
import pandas as pd


def get_dfbal_from_sqlite(filepath):
    conn = sqlite3.connect(filepath)
    df = pd.read_sql_query("SELECT * FROM balances", conn)
    return df


def get_dftrans_from_sqlite(filepath):
    conn = sqlite3.connect(filepath)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    return df


def build_category_dropdown_dict(categories):
    dropdown_category = {
        'category': {
            'options': [
                {'label': i, 'value': i}
                for i in categories
            ],
            'clearable': True,
        }
    }
    return dropdown_category


def build_sub_category_dropdown_dict(categories, sub_categories):
    dropdown_sub_category = [{
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Income"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Income']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Miscellaneous"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Miscellaneous']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Education"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Education']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Shopping"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Shopping']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Personal Care"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Personal Care']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Medical"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Medical']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Food & Drink"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Food & Drink']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Gifts & Donations"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Gifts & Donations']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Investments"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Investments']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Bills & Utilities"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Bills & Utilities']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Auto & Transport"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Auto & Transport']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Travels"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Travels']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Taxes & Fine"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Taxes & Fine']
        ],
        'clearable': True,
    }, {
        'if': {
            'column_id': 'sub_category',
            'filter_query': '{category} eq "Internal Transfer"'
        },
        'options': [
            {'label': i, 'value': i}
            for i in sub_categories['Internal Transfer']
        ],
        'clearable': True,
    }]
    return dropdown_sub_category


def row_fillColor_transactions(dff, rowOddColor, rowEvenColor):
    output = []
    for n in range(0, len(dff.index)):
        if n % 2:
            output.insert(n, rowEvenColor)
        else:
            output.insert(n, rowOddColor)
    return output
