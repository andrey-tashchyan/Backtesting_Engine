import numpy as np 
import pandas as pd
import ccxt
import dotenv as load_dotenv
from datetime import datetime, timedelta
import os
import time
from pathlib import Path

exchange = ccxt.binance()

def loader(path, file_name, symbol, year, period, lim):
    print("\n----- Updating market history...")

    # data downloading and sorting
    start_date = datetime(year, 1, 1)
    end_date = datetime(year+1, 1, 1)

    all_data = []

    #loop by parts
    while start_date<end_date:
        since = int(start_date.timestamp() * 1000)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=period, since=since, limit=lim)
        
        if not ohlcv:
            break

        all_data += ohlcv
        time.sleep(exchange.rateLimit / 1000)
        start_date += timedelta(days=1)
    

    # Creation DataFrame
    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Creation of parent folder if necessary
    path = Path.cwd() / path
    path.mkdir(parents=True, exist_ok=True)

    full_path = path / (file_name + ".csv")
    df.to_csv(full_path, index=False)

    print(f"\n✅ Market history saved to: {full_path}")

    return df



#If you want to run this program alone, set the parameters here
if __name__ == "__main__":
    df = loader(
        path='data',
        file_name='BTCUSDT_2024_1.csv',
        symbol='BTC/USDT',
        year=2024,
        period='5m',
        lim=288
    )