import yfinance as yf
from backtesting import Backtest
import strategies
import logging
import math

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Helper function to round statistics
def round_stat(value):
    if isinstance(value, (int, float)):
        if math.isnan(value):
            return "NaN"
        else:
            return round(value, 2)
    else:
        return value

def run_backtest(strategy_name, symbol, period):
    try:
        # Fetch historical data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)

        logging.debug(f"Data fetched for {symbol} over period {period}: {data.head()}")

        # Get the strategy class from the strategies module
        strategy_class = getattr(strategies, strategy_name, None)
        
        if strategy_class is None:
            raise ValueError(f"Strategy {strategy_name} not found in strategies module")

        # Initialize and run the backtest
        bt = Backtest(data, strategy_class, commission=.002, hedging=False, trade_on_close=True, exclusive_orders=True)
        stats = bt.run()

        logging.debug(f"Backtest stats: {stats}")

        return {
            "strategyName": strategy_name,
            "overview": {
                "finalEquity": round_stat(stats['Equity Final [$]']),
                "trades": round_stat(stats['# Trades']),
                "winRate": round_stat(stats['Win Rate [%]']),
                "profitFactor": round_stat(stats['Profit Factor']),
                "maxDrawdown": round_stat(stats['Max. Drawdown [%]'])
            },
            "performanceSummary": {
                "exposureTime": round_stat(stats['Exposure Time [%]']),
                "equityFinal": round_stat(stats['Equity Final [$]']),
                "equityPeak": round_stat(stats['Equity Peak [$]']),
                "return": round_stat(stats['Return [%]']),
                "buyAndHoldReturn": round_stat(stats['Buy & Hold Return [%]']),
                "annualReturn": round_stat(stats['Return (Ann.) [%]']),
                "annualVolatility": round_stat(stats['Volatility (Ann.) [%]']),
                "sharpeRatio": round_stat(stats['Sharpe Ratio']),
                "sortinoRatio": round_stat(stats['Sortino Ratio']),
                "calmarRatio": round_stat(stats['Calmar Ratio']),
                "maxDrawdown": round_stat(stats['Max. Drawdown [%]']),
                "avgDrawdown": round_stat(stats['Avg. Drawdown [%]']),
                "trades": round_stat(stats['# Trades']),
                "winRate": round_stat(stats['Win Rate [%]']),
                "bestTrade": round_stat(stats['Best Trade [%]']),
                "worstTrade": round_stat(stats['Worst Trade [%]']),
                "avgTrade": round_stat(stats['Avg. Trade [%]']),
                "profitFactor": round_stat(stats['Profit Factor']),
                "expectancy": round_stat(stats['Expectancy [%]']),
                "sqn": round_stat(stats['SQN'])
            },
            "properties": {
                "initialCapital": 10000,
                "dataRange": f"{stats['Start']} to {stats['End']}",
                "symbolInfo": symbol,
                "start": stats['Start'],
                "end": stats['End'],
                "duration": f"{(stats['End'] - stats['Start']).days} days",
                 "maxTradeDuration": f"{stats['Max. Trade Duration']} days",
                "avgTradeDuration": f"{stats['Avg. Trade Duration']} days",
                "maxDrawdownDuration": f"{stats['Max. Drawdown Duration']} days",
                "avgDrawdownDuration": f"{stats['Avg. Drawdown Duration']} days"
            }
        }
    except Exception as e:
        logging.error("An error occurred during backtesting", exc_info=True)
        raise e
