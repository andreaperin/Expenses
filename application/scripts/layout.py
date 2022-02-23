#import dash_core_components as dcc

# import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import html

bank_color_map = {'PayPal': 'SeaGreen',
                  'Unicredit_Main': 'DarkSlateGrey',
                  'Unicredit_Prepaid': 'cadetblue',
                  'N26': 'Black'}

iban_name_map = {'IT42G0200811402000103682825': 'Unicredit_Main',
                 'IT14E0200832974001168463186': 'Unicredit_Prepaid',
                 '9b709cf4f39917d6da19a0aadc83ff32': 'PayPal',
                 'DE29100110012621889892': 'N26',
                 'None': 'TOTAL'}

categories_color_map ={
    'Income': 'Yellow',
    'Miscellaneous': 'Red',
    'Education': 'Black',
    'Shopping': 'Blue', 
    'Personal Care': 'Green', 
    'Medical': 'LightGreen',
    'Food & Drink': 'Violet', 
    'Gifts & Donations': 'Brown', 
    'Investments': 'White', 
    'Bills & Utilities': 'Orange', 
    'Auto & Transport': 'cadetBlue', 
    'Travels': 'DarkSlateGrey',
    'Taxes & Fine': 'SeaGreen'
}

NAVBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "2rem 1rem",
    "background-color": "#383838",
}

CONTENT_STYLE = {
    "top": 0,
    "margin-top": '2rem',
    "margin-left": "18rem",
    "margin-right": "2rem",
}

COLORS = {
    'BLACK': '#000000',
    'TEXT': '#696969',
    'PLOT_COLOR': '#C0C0C0',
    'WHITE': '#FFFFFF',
    'GOLD': '#EEBC35',
    'BROWN': '#53354D',
    'GREEN': '#42CE90',
    'RED': '#F87861',
    'YELLOW': '#F1F145',
    'SKY_BLUE': '#A3DBE1',
    'SILVER': '#CCCCCC',
    'LIGHT_BLACK': '#374649'
}

def nav_bar():
    """
    Creates Navigation bar
    """
    navbar = html.Div(
        [
            html.H2("Navigate to", className="display-10",
                    style={'textAlign': 'center', 'color': 'white'}),
            html.Hr(),
            html.Hr(),
            html.H3("Bank", className="display-10",
                    style={'textAlign': 'left', 'color': 'white'}),
            dbc.Nav(
                [
                    dbc.NavLink("Bank Balance", href="/Bank", active="exact", external_link=True,
                                style={'color': 'white'}),
                    html.Br(),
                    dbc.NavLink("Bank Transaction", href="/Bank/transactions", active="exact", external_link=True,
                                style={'color': 'white'}),
                    html.Br(),
                    dbc.NavLink("Categorize Transaction", href="/Bank/transactions/categorize", active="exact",
                                external_link=True, style={'color': 'white'}),
                    html.Br(),
                    dbc.NavLink("Visualize Expenses", href="/Bank/transactions/viewExpense", active="exact",
                                external_link=True, style={'color': 'white'}),
                    html.Br(),
                    html.Br(),
                    html.Hr(),
                ],

                pills=True,
                vertical=True
            ),
            html.H3("Crypto", className="display-10",
                    style={'textAlign': 'left', 'color': 'white'}),
            dbc.Nav(
                [
                    dbc.NavLink("Crypto page", href="/Crypto", active="exact", external_link=True,
                                style={'color': 'white'}),
                ], )
        ],
        style=NAVBAR_STYLE,
    )
    return navbar
