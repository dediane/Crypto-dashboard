import ccxt
import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta, timezone

# Initialize the exchange
exchange = ccxt.binance()

# Cache dictionary to store data and timestamps
cache = {}

# Fetch OHLCV data with pagination and caching
def fetch_ohlcv_with_pagination(symbol, timeframe, since, limit, period):
    global cache
    
    cache_key = f"{symbol}_{period}"
    
    if cache_key not in cache:
        cache[cache_key] = {'data': None, 'timestamp': None}

    # Check if cache is valid (24 hours for most periods, 1 hour for '1week')
    cache_expiry = timedelta(hours=1) if period == '1week' else timedelta(hours=24)
    if cache[cache_key]['data'] is not None and cache[cache_key]['timestamp'] is not None:
        if datetime.now(timezone.utc) - cache[cache_key]['timestamp'] < cache_expiry:
            return cache[cache_key]['data']

    # Fetch data from exchange
    all_ohlcv = []
    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        if not ohlcv:
            break
        all_ohlcv.extend(ohlcv)
        since = ohlcv[-1][0] + 1  # Move to the next time period
        if len(ohlcv) < limit:
            break

    # Update cache
    cache[cache_key]['data'] = all_ohlcv
    cache[cache_key]['timestamp'] = datetime.now(timezone.utc)

    return all_ohlcv

def get_timeframe_limits(period):
    timeframe = '30m'
    now = pd.Timestamp.now(tz='UTC')
    if period == '1week':
        since = now - pd.Timedelta(weeks=1)
    elif period == '1month':
        since = now - pd.Timedelta(days=30)
    elif period == '3months':
        since = now - pd.Timedelta(days=90)
    elif period == '6months':
        since = now - pd.Timedelta(days=180)
    return timeframe, exchange.parse8601(since.isoformat())
