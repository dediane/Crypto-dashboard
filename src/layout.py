import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import config
from data_fetcher import fetch_trading_pairs, fetch_initial_data

def create_layout():
    trading_pairs = fetch_trading_pairs()
    initial_pair = 'BTC/USDT'
    df_daily, df_seconds, bids, asks = fetch_initial_data(initial_pair)
    
    content =  html.Div(className='container', children=[
        html.H1(children='Crypto Market Analysis'),
        
         html.Div(className='pair-selector', children=[
            html.Label("Select Pair:"),
            dcc.Dropdown(
                id='pair-selector',
                options=[{'label': pair, 'value': pair} for pair in trading_pairs],
    
                value='BTC/USDT'  # Default value
            )
        ]),
         

        html.Div(className='graph-container', children=[
            dcc.Graph(id='candlestick-chart-seconds'),
        ]),

        html.Div(className='graph-container', children=[
            dcc.Graph(id='volume-bubble-chart-seconds')
        ]),
  
        html.Div(className='graph-container', children=[
            dcc.Graph(id='market-depth-chart')
        ]),
        
        html.Div(className='graph-container', children=[
            dcc.Graph(id='price-chart')
        ]),

        html.Div(className='graph-container', children=[
            dcc.Graph(id='volume-bubble-chart')
        ]),

        html.Div(className='graph-container', children=[
            dcc.Graph(id='candlestick-chart-daily')
        ]),
        
        html.Div(className='graph-container', children=[
            dcc.Graph(id='rsi-chart')
        ]),

        html.Div(className='graph-container', children=[
            dcc.Graph(id='macd-chart')
        ]), 
        
        html.H1("Trading Volume Heatmap"),
        html.Div(className='graph-container', children=[
            dcc.Tabs(id='tabs', value='1week', children=[
                dcc.Tab(label='1 Week', value='1week'),
                dcc.Tab(label='1 Month', value='1month'),
                dcc.Tab(label='3 Months', value='3months'),
                dcc.Tab(label='6 Months', value='6months'),
            ]),
            dcc.Graph(id='volume-heatmap'),
        ]),
        

        # Interval component for real-time updates
        dcc.Interval(
            id='interval-component',
            interval= 1*1000,  # Update every 1 second
            n_intervals=0
        )
    ])
    
    layout = html.Div([
        content,
    ])
    
    return layout
    