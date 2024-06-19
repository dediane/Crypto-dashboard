from dash import Output, Input
from data_fetcher import fetch_btc_data_daily, fetch_btc_data_seconds, fetch_order_book
import plotly.graph_objects as go
import plotly.express as px

def register_callbacks(app):

    @app.callback(
        [
            Output('price-chart', 'figure'),
            Output('volume-bubble-chart', 'figure'),
            Output('candlestick-chart-daily', 'figure'),
            Output('candlestick-chart-seconds', 'figure'),
            Output('volume-bubble-chart-seconds', 'figure'),
            Output('market-depth-chart', 'figure'),
            Output('rsi-chart', 'figure'),
            Output('macd-chart', 'figure'),
            Output('loading-spinner', 'children')
        ],
        [Input('interval-component', 'n_intervals'), Input('pair-selector', 'value')]
    )
    def update_charts(n, pair):
        df = fetch_btc_data_daily(pair)
        dfs = fetch_btc_data_seconds(pair)
        bids, asks = fetch_order_book(pair)

        price_chart = create_price_chart(df)
        volume_bubble_chart = create_volume_bubble_chart(df)
        candlestick_chart_daily = create_candlestick_chart(df, '30 days, 1d candle')
        candlestick_chart_seconds = create_candlestick_chart(dfs, '1min, 1s candle')
        volume_bubble_chart_seconds = create_volume_bubble_chart(dfs, '1-Second Volume Bubble')
        market_depth_chart = create_market_depth_chart(bids, asks)
        rsi_chart = create_rsi_chart(df)
        macd_chart = create_macd_chart(df)

        return (
            price_chart, volume_bubble_chart, candlestick_chart_daily, candlestick_chart_seconds,
            volume_bubble_chart_seconds, market_depth_chart, rsi_chart, macd_chart, ''
        )

def create_price_chart(df):
    price_chart = go.Figure()
    price_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], mode='lines', name='Close', line=dict(width=2)))
    price_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MA50'], mode='lines', name='50-Day MA', line=dict(width=1, color='#67cbde')))
    price_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MA200'], mode='lines', name='200-Day MA', line=dict(width=1, color='#ffb3ba')))
    price_chart.update_layout(title='Price with Moving Averages (30 days)')
    return price_chart

def create_volume_bubble_chart(df, title='Buy/Sell Volume (30 days)'):
    return px.scatter(df, x='timestamp', y='close', size='volume', color='volume', hover_name='timestamp', title=title)

def create_candlestick_chart(df, title):
    return go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])]).update_layout(title=title)

def create_market_depth_chart(bids, asks):
    market_depth_chart = go.Figure()
    market_depth_chart.add_trace(go.Scatter(x=bids['price'], y=bids['amount'], mode='lines', name='Bids', fill='tozeroy'))
    market_depth_chart.add_trace(go.Scatter(x=asks['price'], y=asks['amount'], mode='lines', name='Asks', fill='tozeroy'))
    market_depth_chart.update_layout(title='Market Depth', xaxis_title='Price', yaxis_title='Volume')
    return market_depth_chart

def create_rsi_chart(df):
    return px.line(df, x='timestamp', y='RSI', title='Relative Strength Index (RSI)')

def create_macd_chart(df):
    macd_chart = go.Figure()
    macd_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD'], mode='lines', name='MACD', line=dict(width=2)))
    macd_chart.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(width=2)))
    macd_chart.add_trace(go.Bar(x=df['timestamp'], y=df['MACD_Hist'], name='MACD Histogram'))
    macd_chart.update_layout(title='Moving Average Convergence Divergence (MACD)')
    return macd_chart