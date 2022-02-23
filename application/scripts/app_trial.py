import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date


import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html

# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# import dash_table
from dash import dash_table
from collections import OrderedDict

from utility import build_category_dropdown_dict, build_sub_category_dropdown_dict, row_fillColor_transactions
from preprocessing import database_preprocessing
import os
from operator import itemgetter

from datetime import datetime

from layout import CONTENT_STYLE, nav_bar, COLORS, bank_color_map, iban_name_map, categories_color_map
import base64

'''
                                    Parameters
'''

# ------------------------------------------------------------------------------
db_filepath = '../data/bank.db'
balance_columns = ['iban', 'institution_id', 'amount', 'currency', 'timestamp', 'date']
transactions_columns = ['transaction_id', 'bank', 'status', 'booking_date', 'UnstructuredInfo',
                        'transaction_amount', 'category']
transactions_table_columns = ['transaction_id', 'status', 'booking_date', 'UnstructuredInfo', 'transaction_amount']
iban_dict = [
    {'iban': '9b709cf4f39917d6da19a0aadc83ff32', 'name': 'PayPal'},
    {'iban': 'IT42G0200811402000103682825', 'name': 'Unicredit_Main'},
    {'iban': 'IT14E0200832974001168463186', 'name': 'Unicredit_Prepaid'},
    {'iban': 'DE29100110012621889892', 'name': 'N26'},
]

image_filename = '../imgs/homepage.jpg'
categories = ['Income', 'Miscellaneous', 'Education', 'Shopping', 'Personal Care', 'Medical',
              'Food & Drink', 'Gifts & Donations', 'Investments', 'Bills & Utilities', 'Auto & Transport', 'Travels',
              'Taxes & Fine']
sub_categories = {
    'Income': ['Paycheck', 'Bonus', 'ReturnedInvestments', 'Reinbursment', 'Mum&Dad', 'Gifts'],
    'Miscellaneous': ['Cash & ATM', 'Check'],
    'Education': ['Courses', 'Hardware', 'Software'],
    'Shopping': ['Clothes', 'Gaming', 'Mtg', 'Home', 'Cigarettes', 'Others'],
    'Personal Care': ['Laundry', 'Hair', 'Gym'],
    'Medical': ['Pharmacy', 'Private visit', 'Health Insurance', 'Physio', 'Others'],
    'Food & Drink': ['Supermarket', 'Mensa', 'Breakfast', 'Restaurants', 'Alcohol'],
    'Gifts & Donations': ['Mum&Dad', 'Marsi', 'Ele', 'Others'],
    'Investments': ['Stocks', 'Crypto', 'Others'],
    'Bills & Utilities': ['Lease', 'Fineco Account', 'Unicredit Account', 'Television', 'Phone', 'Internet', 'Netfilx',
                          'AmazonPrime', 'Others'],
    'Auto & Transport': ['Gas&Fuel', 'Parking', 'Highway fee', 'Auto parts', 'Auto Insurance'],
    'Travels': ['Friends Vacations', 'Marsi Vacations', 'Others'],
    'Taxes & Fine': ['State Tax', 'Multe']
}
csv_filepath = '../results/transactions.csv'
dropdown_category = build_category_dropdown_dict(categories)
dropdown_sub_category = build_sub_category_dropdown_dict(categories, sub_categories)
# ------------------------------------------------------------------------------

'''
                                    Data
'''

# ------------------------------------------------------------------------------
new_df_balances, new_df_transactions, dates, options1, options2, options3, options4, options5 = database_preprocessing(
    db_filepath=db_filepath, balance_columns=balance_columns, transactions_columns=transactions_columns)
options2.append({'label': 'TOTAL', 'value': 'Sum'})
# ------------------------------------------------------------------------------

'''
                                    Home Page
'''

# ------------------------------------------------------------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav_bar(),
    html.Div(id='home-page', style=CONTENT_STYLE)
])

encoded_image = base64.b64encode(open(image_filename, 'rb').read())
homePage_layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
             style={'height': '120%', 'width': '100%', 'background-color': 'black'})
])
# ------------------------------------------------------------------------------

'''
                                    Bank Page
'''

# ------------------------------------------------------------------------------

Bank_layout = html.Div([
    html.H1("Banks Balances", style={'text-align': 'center'}),  # , 'background-color': COLORS['PLOT_COLOR']}),
    # , 'color': COLORS['SILVER'], 'background-color': 'black'}),
    html.Br(),
    html.Div([
        html.Label(['Choose a date:'],
                   style={'font-size': '130%', 'text-align': 'center', 'font-weight': 'normal'}),
        dcc.Dropdown(
            id='my_dropdown',
            options=options1,
            value=dates[-1],
            multi=False,
            clearable=False,
            style={'width': '50%', 'align-items': 'center', 'justify-content': 'center'}
        ),
    ]),
    html.Br(),
    html.Div(children=[
        dcc.Graph(id='the_pieChart', style={'width': '50%', 'height': 500, 'display': 'inline-block'}),
        dcc.Graph(id='resume_table', style={'width': '50%', 'height': 500, 'display': 'inline-block'})
    ]),
    html.Hr(),
    html.Br(),

    html.Div(children=[
        dcc.Checklist(
            id="checklist",
            options=options2,
            value=new_df_balances.institution_id.unique(),
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id='the_timeseries')]),
    html.Div(id='Bank-content'),
])


@app.callback(
    [Output(component_id='the_pieChart', component_property='figure'),
     Output(component_id='the_timeseries', component_property='figure'),
     Output(component_id='resume_table', component_property='figure')],
    [Input(component_id='my_dropdown', component_property='value'),
     Input(component_id="checklist", component_property="value")]
)
def update_graph(my_dropdown, checklist):
    dff = new_df_balances.copy()
    dff_hist = dff[['iban', 'institution_id', 'amount', 'date']]
    dff_hist['amount'] = pd.to_numeric(dff_hist['amount'], downcast="float")
    grouped_df_hist = dff_hist.groupby('date')
    dates_list = grouped_df_hist.groups.keys()
    institution_id_list = []
    iban_list = []
    amount_list = []
    date_list = []
    for key in dates_list:
        iban_list.append('None')
        institution_id_list.append('Sum')
        amount_list.append(sum(grouped_df_hist.get_group(key)['amount']))
        date_list.append(key)
    total_dict = {'iban': iban_list, 'institution_id': institution_id_list, 'amount': amount_list, 'date': date_list}
    dff_hist_tot = pd.DataFrame.from_dict(total_dict)
    dff_hist = dff_hist.append(dff_hist_tot, ignore_index=True)
    # adding name column to dff_hist for history line chart:
    dff_hist['name'] = ''
    for iban in iban_name_map:
        dff_hist.loc[dff_hist.iban == iban, 'name'] = iban_name_map[iban]

    dff = dff.loc[dff['date'] == my_dropdown]
    dff['amount'] = dff['amount'].astype(float)
    dff['name'] = ""
    for element in iban_dict:
        dff.loc[dff.iban == element['iban'], 'name'] = element['name']
    tot = dff['amount'].sum()
    piechart = px.pie(
        data_frame=dff,
        values='amount',
        names='name',
        hole=.7,
        hover_data=['iban'],
        color='name',
        color_discrete_map=bank_color_map,
    )
    piechart.update_layout(
        title={
            'text': f'<b>Total Amount: {tot} Euro</b>',
            'y': 1,
            'x': 0.5,
            'xanchor': 'left',
            'yanchor': 'top'},
    )

    # adding row colors:
    colors = dff.copy()
    colors['color'] = ""
    for bank in bank_color_map:
        colors.loc[colors.name == bank, 'color'] = bank_color_map[bank]

    resume_table = go.Figure(data=[go.Table(
        columnwidth=[40, 80, 40],
        header=dict(values=['<b>name</b>', '<b>iban</b>', '<b>amount</b>'],
                    fill_color='white',
                    font=dict(color='black', size=18),
                    align=['left', 'center'],
                    height=40,
                    ),
        cells=dict(values=[dff['name'], dff['iban'], dff['amount']],
                   line_color=[colors.color],
                   fill_color=[colors.color],
                   align=['left', 'center'],
                   font=dict(color='white', size=15),
                   height=30)
    )
    ])
    mask = dff_hist.institution_id.isin(checklist)
    history = px.line(
        data_frame=dff_hist[mask],
        x='date',
        y='amount',
        color='name',
        color_discrete_map=bank_color_map,
    )
    history.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            )
        ),
        autosize=False,
        showlegend=True,
        plot_bgcolor=COLORS['SILVER'],
    )
    history.update_traces(mode='markers+lines')

    return piechart, history, resume_table


# ------------------------------------------------------------------------------

'''
                                    Transactions Page
'''

# ------------------------------------------------------------------------------
Bank_transaction_layout = html.Div([
    html.H1("Banks Transactions", style={'text-align': 'center'}),  # , 'background-color': COLORS['PLOT_COLOR']}),
    html.Br(),
    html.Div([
        html.Label(['Choose an account:'],
                   style={'font-size': '110%', 'text-align': 'center'}),
        dcc.Dropdown(
            id='transactions_dropdown',
            options=options3,
            value=options3[-1]['value'],
            multi=False,
            clearable=False,
            style={'width': '50%', 'align-items': 'center', 'justify-content': 'center'}
        ),
    ]),

    html.Div(children=[
        dcc.Graph(id='the_transactions_graph', style={'width': '40%', 'height': 500, 'display': 'inline-block'}),
        dcc.Graph(id='income_outcome', style={'width': '50%', 'height': 500, 'display': 'inline-block'})

    ]),

    html.Hr(),
    html.Div(children=[
        # dcc.Graph(id='income_outcome', style={'width': '50%', 'height': 500, 'display': 'inline-block'}),
        dcc.Graph(id='income_outcome_global', style={'width': '100%', 'height': 500, 'display': 'inline-block'}),
    ]),

    html.Br(),

    html.Div(id='Bank-transactions-content'),
])


@app.callback(
    [Output(component_id='the_transactions_graph', component_property='figure'),
     Output(component_id='income_outcome', component_property='figure'),
     Output(component_id='income_outcome_global', component_property='figure')],
    [Input(component_id='transactions_dropdown', component_property='value')]
)
def update_transaction_graphs(transactions_dropdown):
    dff_trans = new_df_transactions.copy()
    dff_trans['transaction_amount'] = dff_trans['transaction_amount'].astype(float)
    dff_trans = dff_trans.round({'transaction_amount': 0})
    dff_trans['month'] = ''
    for date in dff_trans['booking_date']:
        datee = datetime.strptime(date, "%Y-%m-%d")
        month = datee.strftime("%Y %m")
        dff_trans.loc[dff_trans.booking_date == date, 'month'] = month

    inc_global = []
    outc_global = []
    mean_global = []
    for m in dff_trans['month'].unique():
        income_global = 0
        outcome_global = 0
        for tr in dff_trans.loc[dff_trans.month == m, 'transaction_amount']:
            if tr > 0:
                income_global = income_global + tr
            if tr < 0:
                outcome_global = outcome_global + tr
        inc_global.append({'month': m, 'amount': income_global, 'type': 'income'})
        outc_global.append({'month': m, 'amount': outcome_global, 'type': 'outcome'})
        mean_global.append([m, income_global + outcome_global])

    dff_total_transaction_global = pd.DataFrame(inc_global + outc_global)
    dff_total_transaction_global = dff_total_transaction_global.sort_values('month', ascending=True)
    mean_global.sort(key=itemgetter(0), reverse=True)

    mean_values_global = []
    mean_month_global = []
    for val in mean_global:
        mean_values_global.append(val[1])
        mean_month_global.append(val[0])

    dff_trans = dff_trans.loc[dff_trans['bank'] == transactions_dropdown]
    inc = []
    outc = []
    mean = []
    for m in dff_trans['month'].unique():
        income = 0
        outcome = 0
        for tr in dff_trans.loc[dff_trans.month == m, 'transaction_amount']:
            if tr > 0:
                income = income + tr
            if tr < 0:
                outcome = outcome + tr
        inc.append({'month': m, 'amount': income, 'type': 'income'})
        outc.append({'month': m, 'amount': outcome, 'type': 'outcome'})
        mean.append([m, income + outcome])

    dff_total_transaction = pd.DataFrame(inc + outc)
    dff_total_transaction = dff_total_transaction.sort_values('month', ascending=True)
    mean.sort(key=itemgetter(0), reverse=True)

    mean_values = []
    mean_month = []
    for val in mean:
        mean_values.append(val[1])
        mean_month.append(val[0])

    bar_plot = px.bar(
        data_frame=dff_trans,
        x='booking_date',
        y='transaction_amount',
        color='transaction_amount',
    )
    bar_plot.update_layout(barmode='group',
                           yaxis={'visible': False, 'showticklabels': False},
                           title={
                               'text': "<b>Single Transactions</b>",
                               'y': 0.97,
                               'x': 0.5,
                               'xanchor': 'center',
                               'yanchor': 'top'}
                           )

    income_outcome = px.bar(
        data_frame=dff_total_transaction,
        x='month',
        y='amount',
        color='type',
        text='amount',
    )
    income_outcome.update_traces(width=0.3)

    income_outcome.update_layout(yaxis={'visible': False, 'showticklabels': False},
                                 title={
                                     'text': f"<b>Monthly Income vs Outcome {transactions_dropdown}</b>",
                                     'y': 0.97,
                                     'x': 0.5,
                                     'xanchor': 'center',
                                     'yanchor': 'top'}
                                 )
    income_outcome.add_scatter(
        y=mean_values,
        x=mean_month,
        mode="markers+lines",
        marker=dict(color="DarkSlateGray"),
        hovertext=mean_values,
        name='monthly balance'
    )

    income_outcome_global = px.bar(
        data_frame=dff_total_transaction_global,
        x='month',
        y='amount',
        color='type',
        text='amount',
    )
    income_outcome_global.update_traces(width=0.3)

    income_outcome_global.update_layout(yaxis={'visible': False, 'showticklabels': False},
                                        title={
                                            'text': "<b> GLOBAL Monthly Income vs Outcome</b>",
                                            'y': 0.97,
                                            'x': 0.5,
                                            'xanchor': 'center',
                                            'yanchor': 'top'}
                                        )
    income_outcome_global.add_scatter(
        y=mean_values_global,
        x=mean_month_global,
        mode="markers+lines",
        marker=dict(color="DarkSlateGray"),
        hovertext=mean_values_global,
        name='monthly balance'
    )

    # '''
    #      Table
    #             '''
    # dff_trans = dff_trans.sort_values(by=['booking_date'], ascending=False)
    # columns = ['transaction_id', 'booking_date', 'UnstructuredInfo', 'transaction_amount']
    # rowEvenColor = 'LightGray'
    # rowOddColor = 'Silver'
    # row_fill_list = row_fillColor_transactions(dff_trans, rowEvenColor, rowOddColor)
    #
    # table = go.Figure(data=[go.Table(
    #     columnwidth=[10, 4, 10, 6],
    #     header=dict(values=columns,
    #                 line_color='black',
    #                 fill_color='DarkSlateGrey',
    #                 align=['center'],
    #                 font=dict(color='white', size=12),
    #                 ),
    #     cells=dict(values=[dff_trans['transaction_id'], dff_trans['booking_date'],
    #                        dff_trans['UnstructuredInfo'], dff_trans['transaction_amount']],
    #                line_color='black',
    #                fill_color=[row_fill_list * 5],
    #                fill=dict(color=['white']),
    #                align=['left', 'center'],
    #                font_size=10,
    #                )
    # ),
    #
    # ])

    return bar_plot, income_outcome, income_outcome_global


# ------------------------------------------------------------------------------

'''
                                    Categorize Page
'''

# ------------------------------------------------------------------------------
df = pd.read_csv(csv_filepath)
df = pd.DataFrame(OrderedDict(df))
lastch = os.stat(csv_filepath).st_mtime

Categorize_page_layout = html.Div([
    html.H1('Categorize Transactions', style={'text-align': 'center'}),
    html.Br(),
    html.Div(children=[
        dcc.Dropdown(
            id='month_dropdown',
            options=options4,
            value=options4[-1]['value'],
            multi=False,
            clearable=False,
            style={'width': '50%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                   'height': 30}
        ),
    ]),
    html.Div(children=[
        dcc.Dropdown(
            id='bank_dropdown_cat',
            options=options3,
            value=options3[0]['value'],
            multi=False,
            clearable=False,
            style={'width': '50%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                   'height': 30}
        ),
    ]),

    dash_table.DataTable(
        id='table-dropdown',
        css=[{
            "selector": ".Select-menu-outer",
            "rule": 'display : block'
        }],
        editable=True,
        columns=[
            {'id': 'transaction_id', 'name': 'transaction_id', 'hideable': True},
            {'id': 'bank', 'name': 'bank', 'hideable': True},
            {'id': 'status', 'name': 'status', 'hideable': True},
            {'id': 'booking_date', 'name': 'booking_date'},
            {'id': 'UnstructuredInfo', 'name': 'UnstructuredInfo'},
            {'id': 'transaction_amount', 'name': 'transaction_amount'},
            {'id': 'category', 'name': 'category', 'presentation': 'dropdown'},
            {'id': 'sub_category', 'name': 'sub_category', 'presentation': 'dropdown'},
        ],
        dropdown=dropdown_category,
        dropdown_conditional=dropdown_sub_category,
        style_cell_conditional=[  # style_cell_c. refers to the whole table
            {
                'if': {'column_id': c},
                'textAlign': 'center'
            } for c in
            ['transaction_id', 'status', 'booking_date', 'UnstructuredInfo', 'transaction_amount', 'category',
             'sub_category']
        ],
        style_as_list_view=True,
        style_cell={'padding': '5px'},  # style_cell refers to the whole table
        style_header={
            'backgroundColor': 'Black',
            'fontWeight': 'bold',
            'color': 'White',
            'border': '1px solid black'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '15px'
        },
        style_data_conditional=[  # style_data.c refers only to data rows
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'LightGray'
            },
            {
                'if': {'row_index': 'even'},
                'backgroundColor': 'silver'
            }
        ],
        row_deletable=True
    ),
    dcc.Interval(id='interval', interval=50000, n_intervals=0),
    html.Br(),
    html.Button(id="save-button", n_clicks=0, children="Save"),
    html.Div(id="output-1", children="Press button to save changes"),
])


@app.callback(
    Output(component_id="table-dropdown", component_property="data"),
    [Input(component_id="month_dropdown", component_property="value"),
     Input(component_id="bank_dropdown_cat", component_property="value")],
)
def display_table(month, bank):
    new_last_change = os.stat(csv_filepath).st_mtime
    if new_last_change > lastch:
        df_updated = pd.read_csv(csv_filepath)
        df_updated = pd.DataFrame(OrderedDict(df_updated))
    else:
        df_updated = df
    dff = df_updated.copy()
    dff = dff[dff['booking_date'].str.contains(month)]
    dff = dff.sort_values(by='booking_date')
    dff = dff[dff['bank'].str.contains(bank)]
    dff = dff[dff.status != 'pending']
    data = dff.to_dict('records')
    return data


@app.callback(
    Output(component_id="output-1", component_property="children"),
    [Input(component_id="save-button", component_property="n_clicks")],
    [State(component_id='table-dropdown', component_property="data")]
)
def selected_data_to_csv(nclicks, table1):
    if nclicks == 0:
        raise PreventUpdate
    else:
        list_new = []
        list_old = []
        df_old = pd.read_csv(csv_filepath)
        for c, d in df_old.iterrows():
            list_old.append(d.transaction_id)
        for a, b in pd.DataFrame(table1).iterrows():
            list_new.append(b.transaction_id)
            df_old.loc[df.transaction_id == b['transaction_id'], 'category'] = b['category']
            df_old.loc[df.transaction_id == b['transaction_id'], 'sub_category'] = b['sub_category']
        # to_be_drop = list(set(list_old) - set(list_new))
        # for element in to_be_drop:
        #     df_old = df_old.drop(df_old.index[df_old['transaction_id'] == element])

        df_old.to_csv(csv_filepath, index=False)
        return "Data Submitted"


# ------------------------------------------------------------------------------

'''
                                    View Expense Page
'''

# ------------------------------------------------------------------------------

##TODO: add expenses all account since ever; expenses for just one account; if tbd=0.

viewExpense_layout = html.Div([
    html.H1('Visualize Transcations', style={'text-align': 'center'}),

    html.H2('Monthly', style={'text-align': 'center'}),
    html.Div(children=[
        dcc.Dropdown(
            id='month_dropdown2',
            options=options4,
            value=options4[-1]['value'],
            multi=False,
            clearable=False,
            style={'width': '60%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                   'height': 30}
        ),
        dcc.Dropdown(
            id='Account_Dropdown',
            options=options3,
            value=options3[-1]['value'],
            multi=False,
            clearable=False,
            style={'width': '40%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                   'height': 30}
        ),
    
    ]),
    
    html.Div(children=[
        dcc.Graph(id='Expense_sunburst', style={'width': '50%', 'height': 400, 'display': 'inline-block'}),
        dcc.Graph(id='Expense_sunburst_single_account', style={'width': '45%', 'height': 400, 'display': 'inline-block'}),
    ]),

    html.H2('Annual', style={'text-align': 'center'}),
    html.Div(children=[
        dcc.Dropdown(
            id='year_Dropdown',
            options=options5,
            value=options5[-1]['value'],
            multi=False,
            clearable=False,
            style={'width': '60%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                   'height': 30}
        ),
        dcc.Dropdown(
            id='Account_Dropdown_2',
            options=options3,
            value=options3[-1]['value'],
            multi=False,
            clearable=False,
            style={'width': '40%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                   'height': 30}
        ),
    
    ]),
    
    html.Div(children=[
        dcc.Graph(id='Expense_sunburst_year', style={'width': '50%', 'height': 400, 'display': 'inline-block'}),
        dcc.Graph(id='Expense_sunburst_single_account_year', style={'width': '45%', 'height': 400, 'display': 'inline-block'}),
    ]),
])


@app.callback(
    [Output(component_id="Expense_sunburst", component_property="figure"),
     Output(component_id="Expense_sunburst_single_account", component_property="figure")],
    [Input(component_id="month_dropdown2", component_property="value"),
     Input(component_id="Account_Dropdown", component_property="value")],
)
def update_sunburst_month(month, bank_account):
    df_updated = pd.read_csv(csv_filepath)
    df_updated = pd.DataFrame(OrderedDict(df_updated))
    dff = df_updated.copy()
    dff = dff[dff['booking_date'].str.contains(month)]
    dff = dff.sort_values(by='booking_date')
    dff['transaction_amount'] = dff['transaction_amount'].abs()
    dff = dff[dff.status != 'pending']
    dff = dff[dff.bank != 'PayPal']
    dff_single = dff[dff.bank == bank_account]
    fig_tot = px.sunburst(dff, path=['category', 'sub_category'], values='transaction_amount', color='category')
    fig_single = px.sunburst(dff_single, path=['category', 'sub_category'], values='transaction_amount', color='category') 
    return fig_tot, fig_single

@app.callback(
    [Output(component_id="Expense_sunburst_year", component_property="figure"),
     Output(component_id="Expense_sunburst_single_account_year", component_property="figure")],
    [Input(component_id="year_Dropdown", component_property="value"),
     Input(component_id="Account_Dropdown_2", component_property="value")],
)
def update_sunburst_years(year, bank_account_year):
    df_updated = pd.read_csv(csv_filepath)
    df_updated = pd.DataFrame(OrderedDict(df_updated))
    dff = df_updated.copy()
    dff = dff[dff['booking_date'].str.contains(year)]
    dff = dff.sort_values(by='booking_date')
    dff['transaction_amount'] = dff['transaction_amount'].abs()
    dff = dff[dff.status != 'pending']
    dff_single = dff[dff.bank == bank_account_year]
    fig_tot_year = px.sunburst(dff, path=['category', 'sub_category'], values='transaction_amount', color='category')
    fig_single_year = px.sunburst(dff_single, path=['category', 'sub_category'], values='transaction_amount', color='category') 

    return fig_tot_year, fig_single_year


# ------------------------------------------------------------------------------

'''
                                    Personalized View Page
'''

# ------------------------------------------------------------------------------
personalizedView_layout = html.Div([
    html.Div(children=[
    dcc.DatePickerSingle(
        id='starting-date',
        min_date_allowed=date(2022, 1, 1),
        max_date_allowed=date.today(),
        initial_visible_month=date(2022, 1, 1),
        date=date(2022, 1, 1),
        style={'width': '20%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
        'height': 30}
        ),
    dcc.DatePickerSingle(
        id='ending-date',
        min_date_allowed=date(2022, 1, 1),
        max_date_allowed=date.today(),
        initial_visible_month=date(2022, 1, 1),
        date=date.today(),
        style={'width': '20%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
        'height': 30}
        ),
    dcc.Dropdown(
        id='Account_Dropdown_jk',
        options=options3,
        value=options3[-1]['value'],
        multi=False,
        clearable=False,
        style={'width': '40%', 'align-items': 'center', 'justify-content': 'center', 'display': 'inline-block',
                'height': 30}
        ),
    ]),
        html.Div(children=[
        dcc.Graph(id='Expense_p', style={'width': '50%', 'height': 400, 'display': 'inline-block'}),
    ]),
])



# ------------------------------------------------------------------------------

'''
                                    Crypto Page
'''

# ------------------------------------------------------------------------------
Crypto_layout = html.Div([
    html.H1('Crypto'),
    dcc.RadioItems(
        id='Crypto-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    dcc.Link(
    html.Button('Navigate to "page-2"'),
    href='/Bank/transactions/viewExpense/personalized')
])


@app.callback(dash.dependencies.Output('Crypto-content', 'children'),
              [dash.dependencies.Input('Crypto-radios', 'value')])
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)


# ------------------------------------------------------------------------------

'''
                                    Routing
'''


# ------------------------------------------------------------------------------
@app.callback(dash.dependencies.Output('home-page', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Bank':
        return Bank_layout
    elif pathname == '/Crypto':
        return Crypto_layout
    elif pathname == '/Bank/transactions':
        return Bank_transaction_layout
    elif pathname == '/Bank/transactions/categorize':
        return Categorize_page_layout
    elif pathname == '/Bank/transactions/viewExpense':
        return viewExpense_layout
    elif pathname == '/Bank/transactions/viewExpense/personalized':
        return personalizedView_layout
    else:
        return homePage_layout


if __name__ == '__main__':
    app.run_server(debug=True)
