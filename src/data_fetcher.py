from os import write
import ccxt 
import pandas as pd
import requests

binance = ccxt.binance()

def fetch_btc_data_daily(pair):
    ohlcv = binance.fetch_ohlcv(pair, timeframe='1h', limit=720)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['MA200'] = df['close'].rolling(window=200).mean()
    df['RSI'] = calculate_rsi(df['close'], 14)
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df['close'])  
      
    return df

def fetch_btc_data_seconds(pair):
    since = binance.milliseconds() - 1000 * 60
    trades = binance.fetch_trades(pair, since=since)
    data = []
    for trade in trades:
        timestamp = trade['timestamp']
        price = trade['price']
        amount = trade['amount']
        data.append([timestamp, price, price, price, price, amount])
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.resample('1s').agg({'open' : 'first', 'high' : 'max', 'low' : 'min', 'close' : 'last', 'volume' : 'sum' }).dropna()
    df.reset_index(inplace=True)
    
    return df

def fetch_order_book(pair):
    order_book = binance.fetch_order_book(pair)
    bids = pd.DataFrame(order_book['bids'], columns=['price', 'amount'])
    asks = pd.DataFrame(order_book['asks'], columns=['price', 'amount'])
    
    return bids, asks

def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(series, fast_period=12, slow_period=26, signal_period=9):
    exp1 = series.ewm(span=fast_period, adjust=False).mean()
    exp2 = series.ewm(span=slow_period, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    macd_hist = macd - signal
    
    return macd, signal, macd_hist

def fetch_trading_pairs():
    markets = binance.load_markets()
    trading_pairs = list(markets.keys())
    
    return trading_pairs

def fetch_initial_data(pair):
    df_daily = fetch_btc_data_daily(pair)
    df_seconds = fetch_btc_data_seconds(pair)
    bids, asks = fetch_order_book(pair)

    return df_daily, df_seconds, bids, asks