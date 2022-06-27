from django_plotly_dash import DjangoDash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas_datareader
import pandas_datareader.data as web
from datetime import date, timedelta
import plotly.graph_objects as go
from .dash_functions import *
# import dash_auth

####################### SETUP
# USERNAME_PASSWORD_PAIRS = [['admin','admin'], ['username','password']]
app = DjangoDash(name='stock_prices', external_stylesheets=[dbc.themes.BOOTSTRAP])
# auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
# server = app.server

####################### DEFAULT TIME RANGE
end_date = date.today()
start_date = date.today() - timedelta(days=60)

####################### GET DATA
### get all available tickers from NASDAQ
tickers = pandas_datareader.nasdaq_trader.get_nasdaq_symbols(retry_count=3, timeout=30, pause=None)
tickers = tickers.reset_index()
tickers['ticker'] = '[' + tickers.iloc[:,0].astype(str) + '] ' + tickers.iloc[:,2].astype(str)


####################### DEFAULT
### data
default_data = web.DataReader(name="AAPL", data_source='yahoo', start=start_date, end=end_date)
default_data = default_data.reset_index()
### graph
default_fig = go.Figure()
default_fig.add_trace(go.Scatter(x=default_data['Date'], y=default_data['Close'], mode='lines', name='AAPL'))
default_fig.update_layout(showlegend=True, plot_bgcolor='white',hovermode="x",
                          title={'text':"AAPL Closing Prices", 'x':0.5},
                          xaxis={'title':'Date','tickformat':"%Y-%m-%d"},
                          yaxis={'rangemode':"tozero"})


####################### LAYOUT
app.layout = html.Div([
    html.H3("Stock Prices Dashboard", style={'padding': '20px', 'padding-bottom': '10px'}),
    html.Div([
        ### Filters section ###
        html.Div([
            # date filters
            html.Div([
                dbc.Label("Date Range", style={'font-weight': 'bold'}),
                dcc.DatePickerRange(id='filter_date', max_date_allowed=date.today(),
                                    start_date=date.today(), end_date=date.today() - timedelta(days=60),
                                    start_date_placeholder_text="Start Date",
                                    end_date_placeholder_text="End Date"),
            ], style={'padding-bottom': '20px'}),
            # stock filters
            html.Div([
                dbc.Label("Stocks", style={'font-weight': 'bold'}),
                dcc.Dropdown(options=dropdown_filters(tickers['ticker']), value='[AAPL] Apple Inc. - Common Stock', 
                            multi=True, id='filter_ticker'),
            ], style={'padding-bottom': '20px'}),
            # apply button
            dbc.Button("Apply", id="submit", color="primary", n_clicks=0, style={'float': 'right'}),

        ], className="side", style={'flex': '20%', 'padding': '20px', 'margin': '10px',
                                    'background-color': 'white', 'box-shadow': '0px 1px 3px lightgrey',
                                    'border-radius': '10px'}),
        ### END Filters section ###

        html.Div([dcc.Graph(id='graph_closing_prices', figure=default_fig)
        ], className="main", style={'flex': '70%', 'padding': '20px', 'margin': '10px',
                                    'background-color': 'white', 'box-shadow': '0px 1px 3px lightgrey',
                                    'border-radius': '10px'})

    ], className="row1", style={'display': 'flex', 'flex-wrap': 'wrap', 'margin': '10px'}),


    
])


###### CALLBACKS
@app.callback(Output('graph_closing_prices', 'figure'),
               Input('submit', 'n_clicks'),
               [State('filter_ticker','value'), State('filter_date','start_date'), State('filter_date','end_date')])
def update_graph(n_clicks, ticket_list, start_date, end_date):
    fig = go.Figure()
    symbols = tickers[tickers['ticker'].isin(ticket_list)]['Symbol'].values
    print(symbols)
    for t in symbols:
        data = web.DataReader(name=t, data_source='yahoo', start=start_date, end=end_date).reset_index()
        print(t)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name=t))
    fig.update_layout(showlegend=True, plot_bgcolor='white',hovermode="x",
                      title={'text':(', '.join(symbols)+" Closing Prices"), 'x':0.5},
                      xaxis={'title':'Date','tickformat':"%Y-%m-%d"},
                      yaxis={'rangemode':"tozero"})
    return fig

