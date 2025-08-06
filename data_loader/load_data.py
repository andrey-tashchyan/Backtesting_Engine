import numpy as np 
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import os
import time
from pathlib import Path

exchange = ccxt.binance()

def loader(path, file_name, symbol, year, period, lim, x):
    print("\n----- Updating market history...")

    # Define start and end dates
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)  # Fin stricte à la fin de l'année

    all_data = []

    # Downloading data
    since = int(start_date.timestamp() * 1000)
    end = int(end_date.timestamp() * 1000)
    
    while since < end:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=period, since=since, limit=lim)
            if not ohlcv:
                break

            # Filter the candles to keep only the right year
            filtered_ohlcv = [candle for candle in ohlcv if candle[0] <= end]
            all_data += filtered_ohlcv

            if not filtered_ohlcv:  # Stop if there is no candles
                break

            last_ts = filtered_ohlcv[-1][0]
            since = last_ts + 1  

            time.sleep(exchange.rateLimit / 1000)

        except Exception as e:
            print(f"⚠️ Erreur : {e}")
            time.sleep(2)

    # DataFrame creation
    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 2nd filtering
    df = df[df['timestamp'].dt.year == year]

    # Create the parent folder relative to the script's directory
    script_dir = Path(__file__).resolve().parent
    path = script_dir / path
    path.mkdir(parents=True, exist_ok=True)
    full_path = path / (file_name + ".csv")
    df.to_csv(full_path, index=False)

    print(f"\n✅ Market history saved to: {full_path}")

    return df





# test data
if __name__ == "__main__":
    df = loader(
        path='data',
        file_name='BTCUSDT_2024_6',
        symbol='BTC/USDT',
        year=2024,
        period='1w',
        lim=365,
        x=367
    )
