import ccxt
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path
from algo import my_algo
from data_loader.load_data import loader
import quantstats as qs

def main():
    
    #------------------------Setting the backtesting parameters

    symbol = input("What cryptocurrency do you want to trade ? (i.e BTC, ETH, SOL, XRP...) \n")
    symbol = symbol.strip().upper()
    symbol = symbol + '/USDT'

    timeframe = int(input("On which timeframe are you trading ? \n(enter : '1' for 5 min, '2' for 15 min, '3' for 1h, '4' for 4h, '5' for 1 day, '6' for 1 week) \n"))

    year = int(input("Select on which year you want to backtest your strategy (i.e from 2015 to 2024) \n"))
    
    sensitivity = int(input("Enter the period sensitivity (from 4 to 30 (highest to lowest) : \n"))
    
    initial_capital = int(input("Select your initial capital (i.e 1000 ($)) : \n"))




    #------------------------Case validity

    #Testing timeframe & setting lim
    if timeframe not in [1, 2, 3, 4, 5, 6]:
        print("Selected timeframe is incorrect")
        return
    else:
        match timeframe:
            case 1:                                 #looping each day
                period = '5m'
                lim = 288
            case 2:                                 #looping each day
                period = '15m'
                lim = 96
            case 3:                                 #looping each weeks
                period = '1h'
                lim = 168
            case 4:                                 #looping each  2 weeks
                period = '4h'
                lim = 84
            case 5:                                 #looping the year
                period = '1d'
                lim = 365
            case 6:                                 #looping the year
                period = '1w'
                lim = 52
    
    #Testing backtesting year
    if(year<2015 or year>2024):
        print("Incorrect backtesting year")
        return
    
    #Testing sensitivity
    if (sensitivity>30) or (sensitivity<4) :
        print("Wrong sensitivity")
        return


    #----------------------------Data Loader

    #We build the parent folder path
    try:
        path = Path(__file__).resolve().parent
    except NameError:
        path = Path().resolve()


    #We check if we have the data at this adress
    file_name = symbol.replace("/", "") + '_' + str(year) + '_' + str(timeframe)
    total_path = path / "data_loader" / "data" / (file_name + ".csv")

    if total_path.exists():
        print("We already have the data, proceeding to loading it")
        df = pd.read_csv(total_path)
    else:
        print("Data not found, proceeding to the download, this may take some time...")
        df = loader(path, file_name, symbol, year, period, lim)
    
    




    #------------------------------Trading Loop
    
    #Performance indicators
    capital = initial_capital
    capital_history = [initial_capital]
    returns = []
    PnL = 0
    win_trade_rate = 0
    avg_gain, avg_loss = 0, 0
    max_win, max_loss = 0, 0
    num_trade = 1
    num_wins, num_losses = 0,0


    #Iterative Part
    window_size = sensitivity + 30
    cur_pos = 0
    capital_invested = 0
    
    #Loop
    for i in range(sensitivity, len(df)):
        
        #Checking Liquidation (<5%)
        if capital < initial_capital * 0.05:
            liquidation_time = df['timestamp'].iloc[i] if 'timestamp' in df.columns else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"!!! Position Liquidated at {liquidation_time} !!!")
            return
        
        #Calling my_algo
        prices = df.iloc[max(0, i - window_size): i].reset_index(drop=True)
        order, exposure = my_algo(prices, cur_pos, sensitivity) 
        close_price = df['close'].iloc[i]

        #Checking cases
        if cur_pos == 0:
            if order == 1:
                cur_pos = 1
                capital_invested = capital*exposure
                capital = capital - capital_invested
                entry_price = close_price
            elif order == -1:
                cur_pos = -1
                capital_invested = capital*exposure
                capital = capital - capital_invested
                entry_price = close_price
        elif order in [-2, 2]:
            if cur_pos == 1:
                profit = ((close_price - entry_price)/entry_price)*capital_invested
                
            elif cur_pos == -1:
                profit = ((entry_price - close_price)/close_price)*capital_invested
                
            capital += profit
            capital_history.append(capital)
            returns.append(profit)
            

            #Reinitializing position
            cur_pos = 0
            num_trade += 1
            PnL += profit
            
            if profit>0:
                avg_gain += profit
                num_wins += 1
                if profit>max_win:
                    max_win = profit
            elif profit<0:
                avg_loss += profit
                num_losses += 1
                if profit<max_loss:
                    max_loss = profit
    
    #Closing last position
    close_price = df['close'].iloc[len(df)-1]
    if cur_pos == 1:
        profit = close_price - entry_price
    if cur_pos == -1:
        profit = entry_price - close_price
        capital += profit
        capital_history.append(capital)

        #Relative PnL
        returns.append(profit)
        
        #Reinitializing position
        capital_history.append(capital)
        cur_pos = 0
        num_trade += 1
        PnL += profit
        
        if profit>0:
            avg_gain += profit
            num_wins += 1
            if profit>max_win:
                max_win = profit
        elif profit<0:
            avg_loss += profit
            num_losses += 1
            if profit<max_loss:
                max_loss = profit

    
    #Key stats
    if num_losses != 0:
        win_trade_rate = num_wins/num_losses
    if num_wins != 0:
        avg_gain /= num_wins
    if num_losses != 0:
        avg_loss /= num_losses
    avg_outcome = (avg_gain+avg_loss)/num_trade

    qs.extend_pandas()

    print(f"[DEBUG] Capital history length: {len(capital_history)}")
    print(f"[DEBUG] Last 5 capital values: {capital_history[-5:]}")

    #Temporal series of returns
    returns_series = pd.Series([capital_history[i+1]/capital_history[i] - 1 for i in range(len(capital_history)-1)])

    # Quick Overview
    returns_series.index = pd.date_range(start='2023-01-01', periods=len(returns_series), freq='5min')  # ou '1min' ou '1d'
    print("Sharpe:", returns_series.sharpe())
    print("Max Drawdown:", returns_series.max_drawdown())
    returns_series.plot(title="Backtest PnL")

    # HTML Report
    qs.reports.full(returns_series, title="Backtest Report", output='report.html')

    print(f"\n Number of trades : {num_trade}")
    print(f"PnL : {PnL}" )
    print(f"Average gain : {avg_gain}")
    print(f"Average loss : {avg_loss}")
    print(f"Win/Loss rate : {win_trade_rate}")
    print(f"Average outcome : {avg_outcome}")
    print(f"Final Capital : {capital}")



if __name__ == "__main__":
    main()