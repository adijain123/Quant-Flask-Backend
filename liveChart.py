import MetaTrader5 as mt
from datetime import datetime
import pandas as pd

# Initialize MetaTrader 5
mt.initialize()

# Login to MetaTrader 5
login = 51825405
password = '4Z&Bzq39lhA9G9'
server = 'ICMarketsSC-Demo'
mt.login(login, password, server)

def live_Chart(symbol):
    prices = pd.DataFrame(mt.copy_rates_range(symbol, mt.TIMEFRAME_D1, datetime(2024, 1, 1), datetime.now()))
    prices['time'] = pd.to_datetime(prices['time'], unit='s')
    prices.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    prices = prices[['time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    prices.set_index('time', inplace=True)

    return{
        "ohlc": prices.reset_index().to_dict(orient='records')
        }