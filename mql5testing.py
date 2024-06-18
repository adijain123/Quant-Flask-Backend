import MetaTrader5 as mt
from datetime import datetime
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

# Initialize MetaTrader 5
mt.initialize()
print(mt.initialize())
# Login to MetaTrader 5
login = 51825405
password = '4Z&Bzq39lhA9G9'
server = 'ICMarketsSC-Demo'
mt.login(login, password, server)

# Convert Unix timestamps to datetime objects
datetimefrom = 1717549200
start_date = datetime.fromtimestamp(datetimefrom)
 
# Fetch prices data
prices = pd.DataFrame(mt.copy_rates_range('AAPL.NAS', mt.TIMEFRAME_M1, datetime(2024,6,17), datetime.now()))

# Convert time column to datetime
prices['time'] = pd.to_datetime(prices['time'], unit='s')

# Rename columns to match the expected format for backtesting
prices.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)

# Ensure the DataFrame contains only the required columns
prices = prices[['time', 'Open', 'High', 'Low', 'Close', 'Volume']]

# Set 'time' column as index
prices.set_index('time', inplace=True)

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 50)
        self.ma2 = self.I(SMA, price, 100)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

# Run the backtest
bt = Backtest(prices, SmaCross, commission=.002, cash=10000)
stats = bt.run()
print(stats)