# strategies.py

from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 20)
        self.ma2 = self.I(SMA, price, 40)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

import numpy as np

def rolling_std(series, window):
    result = [np.nan] * (window - 1)
    for i in range(window - 1, len(series)):
        window_data = series[i - window + 1:i + 1]
        result.append(window_data.std())
    return result

class BollingerBands(Strategy):
    def init(self):
        price = self.data.Close
        self.ma = self.I(SMA, price, 20)
        self.std = self.I(rolling_std, price, 20)
        self.upper_band = self.ma + 2 * np.array(self.std)
        self.lower_band = self.ma - 2 * np.array(self.std)

    def next(self):
        price = self.data.Close[-1]
        if price > self.upper_band[-1]:
            self.sell()
        elif price < self.lower_band[-1]:
            self.buy()


# Add more strategies here as needed
