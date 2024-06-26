# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# from dash import Dash
# import plotly.io as pio

# import config
# from layout import create_layout
# from callbacks import register_callbacks

# # Configure Plotly template
# pio.templates.default = config.PLOTLY_TEMPLATE

# # Initialize Dash app
# app = Dash(__name__)

# # Set app layout
# app.layout = create_layout()

# # Register callbacks
# register_callbacks(app)

# if __name__ == '__main__':
#     app.run_server(debug=True)

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import fetch_btc_data_daily, fetch_btc_data_seconds, fetch_order_book
from heatmap import get_timeframe_limits, fetch_ohlcv_with_pagination
from whales import fetch_whale_movements
from layout import create_layout
from callbacks import register_callbacks
import config

pio.templates.default = config.PLOTLY_TEMPLATE

# Initialize Dash app
app = Dash(__name__)

# Set app layout
app.layout = create_layout()

@app.callback(
    [Output('price-chart', 'figure'),
     Output('volume-bubble-chart', 'figure'),
     Output('candlestick-chart-daily', 'figure'),
     Output('candlestick-chart-seconds', 'figure'),
     Output('volume-bubble-chart-seconds', 'figure'),
     Output('market-depth-chart', 'figure'),
     Output('rsi-chart', 'figure'),
     Output('macd-chart', 'figure'),
     Output('volume-heatmap', 'figure'),
    ],
    [Input('interval-component', 'n_intervals'), Input('pair-selector', 'value'), Input('tabs', 'value')]
)

def update_charts(n, pair, selected_period):
    df = fetch_btc_data_daily(pair)
    dfs = fetch_btc_data_seconds(pair)
    bids, asks = fetch_order_book(pair)

    price_chart = go.Figure()
    price_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], mode='lines', name='Close',
                                     line=dict(width=2)))
    price_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MA50'], mode='lines', name='50-Day MA',
                                     line=dict(width=1, color='#67cbde')))
    price_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MA200'], mode='lines', name='200-Day MA',
                                     line=dict(width=1, color='#ffb3ba')))
    price_chart.update_layout(title='Price with Moving Averages (30 days)', )
    # price_chart = px.line(df, x='timestamp', y='close', title='Bitcoin Price Over Time')
    # price_chart.update_layout(title='Bitcoin Price with Moving Averages')
    
    volume_bubble_chart = px.scatter(df, x='timestamp', y='close', size='volume',
                                     color='volume', hover_name='timestamp',
                                     title='Buy/Sell Volume (30 days)')
    
    candlestick_chart_daily = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                                             open=df['open'],
                                                             high=df['high'],
                                                             low=df['low'],
                                                             close=df['close'])])
    candlestick_chart_daily.update_layout(title='Candlestick Chart (30 days, 1d candle)')
    
    candlestick_chart_seconds = go.Figure(data=[go.Candlestick(x=dfs['timestamp'],
                                                               open=dfs['open'],
                                                               high=dfs['high'],
                                                               low=dfs['low'],
                                                               close=dfs['close'])])
    candlestick_chart_seconds.update_layout(title='Candlestick Chart (1min, 1s candle)')
    
    volume_bubble_chart_seconds = px.scatter(dfs, x='timestamp', y='close', size='volume',
                                             color='volume', hover_name='timestamp',
                                             title='1-Second Volume Bubble')
    
    market_depth_chart = go.Figure()
    market_depth_chart.add_trace(go.Scatter(x=bids['price'], y=bids['amount'],
                                            mode='lines', name='Bids', fill='tozeroy'))
    market_depth_chart.add_trace(go.Scatter(x=asks['price'], y=asks['amount'],
                                            mode='lines', name='Asks', fill='tozeroy'))
    market_depth_chart.update_layout(title='Market Depth', xaxis_title='Price', yaxis_title='Volume')
    
     # RSI Chart
    rsi_chart = px.line(df, x='timestamp', y='RSI', title='Relative Strength Index (RSI)')
    
    # MACD Chart
    macd_chart = go.Figure()
    macd_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD'], mode='lines', name='MACD', line=dict(width=2)))
    macd_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(width=2)))
    macd_chart.add_trace(go.Bar(x=df['timestamp'], y=df['MACD_Hist'], name='MACD Histogram'))
    macd_chart.update_layout(title='Moving Average Convergence Divergence (MACD)')
    
    timeframe, since = get_timeframe_limits(selected_period)
    ohlcv = fetch_ohlcv_with_pagination(pair, timeframe, since, 1000, selected_period)

    df_heatmap = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_heatmap['timestamp'] = pd.to_datetime(df_heatmap['timestamp'], unit='ms')
    df_heatmap['time'] = df_heatmap['timestamp'].dt.strftime('%H:%M')
    df_heatmap['day'] = df_heatmap['timestamp'].dt.date

    heatmap_data = df_heatmap.pivot_table(values='volume', index='day', columns='time', fill_value=0)

    volume_heatmap = go.Figure(data=[go.Heatmap(z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index, colorscale='Viridis')])
    volume_heatmap.update_layout(
        title=f'Trading Volume Heatmap for {pair} ({selected_period})',
        xaxis={'title': 'Time of Day'},
        yaxis={'title': 'Date'},
        annotations=[
            dict(
                xref='paper',
                yref='paper',
                x=1.05,
                y=1.1,
                xanchor='center',
                yanchor='top',
                text=f'Volume in {pair.split("/")[0]}',
                showarrow=False
            )
        ]
    )
    
    return price_chart, volume_bubble_chart, candlestick_chart_daily, candlestick_chart_seconds, volume_bubble_chart_seconds, market_depth_chart, rsi_chart, macd_chart, volume_heatmap

if __name__ == '__main__':
    app.run_server(debug=True)