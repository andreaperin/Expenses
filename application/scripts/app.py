import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from utility import get_df_from_sqlite

from datetime import datetime

# ------------------------------------------------------------------------------

df_balances = get_df_from_sqlite(filepath='../data/bank.db')
dates = []
for idx, row in df_balances.iterrows():
    dates.append(datetime.fromtimestamp(float(df_balances.loc[idx].at['timestamp'])).strftime('%Y-%m-%d %H'))
df_balances['date'] = dates

new_df_balances = df_balances[['iban', 'institution_id', 'amount', 'currency', 'timestamp', 'date']]

unique_dates = list(new_df_balances['date'].unique())
unique_inst_id = list(new_df_balances['institution_id'].unique())
options = []
options2 = []
for date in unique_dates:
    options.append({'label': date, 'value': date})
for inst_id in unique_inst_id:
    options2.append({'label': inst_id, 'value': inst_id})

# ------------------------------------------------------------------------------

app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("Banks Balances", style={'text-align': 'center'}),

    html.Br(),

    html.Div([
        html.Label(['Choose a date:'],
                   style={'font-size': '110%', 'text-align': 'center'}),
        dcc.Dropdown(
            id='my_dropdown',
            options=options,
            value=dates[-1],
            multi=False,
            clearable=False,
            style={'width': '50%', 'align-items': 'center', 'justify-content': 'center'}
        ),
    ]),
    html.Div([
        dcc.Graph(
            id='the_graph',
            style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'left'}
        )
    ]),

    html.Br(),

    html.Div([
        html.Label(['Choose a Bank'],
                   style={'font-size': '110%', 'text-align': 'center'}),
        dcc.Dropdown(
            id='my_dropdown2',
            options=options2,
            value='UNICREDIT_UNCRITMM',
            multi=False,
            clearable=False,
            style={'width': '50%', 'align-items': 'center', 'justify-content': 'center'}
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='the_timeseries',
            style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'left'},
            figure={
                'layout': go.Layout(
                    xaxis={
                        'showgrid': False
                    },
                    yaxis={
                        'showgrid': True
                    })
            },
        )
    ]),
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='the_graph', component_property='figure'),
     Output(component_id='the_timeseries', component_property='figure')],
    # Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value'),
     Input(component_id='my_dropdown2', component_property='value')]
)
def update_graph(my_dropdown, my_dropdown2):
    dff = new_df_balances.copy()
    dff_hist = dff.loc[dff['institution_id'] == my_dropdown2]
    dff = dff.loc[dff['date'] == my_dropdown]
    dff['amount'] = dff['amount'].astype(float)

    tot = dff['amount'].sum()

    # Plotly Express
    piechart = px.pie(
        data_frame=dff,
        values='amount',
        names='iban',
        hole=.7,
        # title="amount percentage",
    )
    piechart.update_layout(
        title={
            'text': f'Total Amount: {tot} Euro',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    history = px.line(
        data_frame=dff_hist,
        x='date',
        y='amount',
        color='iban'
    )
    history.update_layout(
        title={
            'text': f'History of account: {my_dropdown2}',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
    )
    history.update_traces(mode='markers+lines')

    return piechart, history


if __name__ == '__main__':
    app.run_server(debug=True)
