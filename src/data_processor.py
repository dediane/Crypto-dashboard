def process_data(df):
    df['buy_volume'] = df['volume'] * 0.5
    df['sell_volume'] = df['volume'] * 0.5
    return df