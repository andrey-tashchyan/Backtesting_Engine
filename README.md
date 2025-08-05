# 🚀 Crypto Backtest Engine

A flexible and modular Python-based backtesting engine for testing cryptocurrency trading strategies across historical OHLCV data from Binance.

---

## 🧠 Overview

This project enables users to test **custom trading strategies** on **historical crypto price data** across various **timeframes**, **years**, and **risk exposures**. The engine features dynamic strategy injection, automatic data downloading and saving, and full performance reporting via QuantStats.

You can:
- Choose the cryptocurrency pair (e.g., BTC/USDT)
- Define the backtest year (from 2015 to 2024)
- Select your trading timeframe (from 5 min to 1 week)
- Adjust sensitivity for indicators
- Set your initial capital
- Run your own algorithm via `my_algo()`

---

## 📥 Inputs

| Parameter         | Description                                                                                           |
|-------------------|-------------------------------------------------------------------------------------------------------|
| `symbol`          | Cryptocurrency symbol (BTC, ETH, SOL, etc.)                                                           |
| `timeframe`       | Chosen timeframe: <br> `1` → 5 min • `2` → 15 min • `3` → 1 h • `4` → 4 h • `5` → 1 d • `6` → 1 w       |
| `year`            | Backtest year (from **2015** to **2024**)                                                             |
| `sensitivity`     | Indicator sensitivity (recommended range: **4** to **30**)                                            |
| `initial_capital` | Starting capital in USD (e.g. **1000**)                                                               |

---

## ⚙️ Strategy Interface

To test a strategy, define:

```python
def my_algo(df: pd.DataFrame, cur_pos: int, sensitivity: int) -> tuple:
    """
    Returns:
      - position: {1: enter long, -1: enter short, 2: close long, -2: close short}
      - exposure: float between 0 and 1 (percentage of capital)
    """
    ...
    return position, exposure
```

You can build your own strategy using any mix of RSI, MACD, Volume Z-score, SAR, etc.

---

## 📈 Features

- 📊 Historical OHLCV data fetched from Binance  
- 🧠 Plug & Play strategy design via `my_algo()`  
- 💾 Automatic data caching to `data_loader/data/`  
- 🔍 Live monitoring of capital, trades, and liquidation  
- 📉 Performance metrics: Sharpe, max drawdown, PnL, win/loss stats  
- 📄 QuantStats HTML report output (`report.html`)  
- 📌 Easy backtest for multiple assets and years  

---

## 📁 Project Structure

```
project/
├── engine.py                 # Main backtesting engine (CLI prompts)
├── algo.py                   # Strategy interface & indicators
├── data_loader/
│   ├── load_data.py          # Binance OHLCV fetcher & CSV saver
│   └── data/                 # Cached price data
├── requirements.txt
└── README.md
```

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/crypto-backtest-engine.git
cd crypto-backtest-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🛠️ Usage

```bash
python engine.py
```

You’ll be prompted for:
1. Coin (e.g., BTC)  
2. Timeframe (e.g., 3 → 1 h)  
3. Year (2015–2024)  
4. Sensitivity (4–30)  
5. Initial capital (USD)

---

## ✅ Requirements

```text
numpy
dotenv
datetime
os
time
pathlib
ccxt
pandas
quantstats
```

---

## 🛠️ Roadmap

- [ ] Add slippage & fee models  
- [ ] Support multiple concurrent positions  
- [ ] Multi-asset backtesting  
- [ ] Export trade logs to CSV  
- [ ] Unit tests & CI

---

## 👨‍💻 Author

Andrey Tashchyan  
BSc. Mechanical Engineering @ EPFL • Aspiring Quant  
[LinkedIn](https://www.linkedin.com/in/andreytashchyan/)

---
