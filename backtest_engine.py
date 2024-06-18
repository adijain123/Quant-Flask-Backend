import MetaTrader5 as mt
from datetime import datetime
import pandas as pd
from backtesting import Backtest, Strategy
import logging
import math
import json
import plotly.graph_objects as go
import plotly.utils
import strategies

# Initialize MetaTrader 5
mt.initialize()

# Login to MetaTrader 5
login = 51825405
password = '4Z&Bzq39lhA9G9'
server = 'ICMarketsSC-Demo'
mt.login(login, password, server)

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

def run_backtest(strategy_name, symbol, cash, timeframe, datetimefrom, datetimeto):
    try:
        if timeframe == "1 minutes":
            timeframe = mt.TIMEFRAME_M1
        elif timeframe == "5 minutes":
            timeframe = mt.TIMEFRAME_M5
        elif timeframe == "15 minutes":
            timeframe = mt.TIMEFRAME_M15
        elif timeframe == "30 minutes":
            timeframe = mt.TIMEFRAME_M30
        elif timeframe == "1 hour":
            timeframe = mt.TIMEFRAME_H1
        elif timeframe == "1 day":
            timeframe = mt.TIMEFRAME_D1
        elif timeframe == "1 week":
            timeframe = mt.TIMEFRAME_W1
        elif timeframe == "1 month":
            timeframe = mt.TIMEFRAME_MN1

        start_date = datetime.fromtimestamp(datetimefrom)
        end_date = datetime.fromtimestamp(datetimeto)

        prices = pd.DataFrame(mt.copy_rates_range(symbol, timeframe, datetime(start_date.year, start_date.month, start_date.day), datetime(end_date.year, end_date.month, end_date.day)))

        prices['time'] = pd.to_datetime(prices['time'], unit='s')
        prices.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
        prices = prices[['time', 'Open', 'High', 'Low', 'Close', 'Volume']]
        prices.set_index('time', inplace=True)

        logging.debug(f"Data fetched for {symbol} over timeframe {timeframe}: {prices.head()}")

        strategy_class = getattr(strategies, strategy_name, None)
        if strategy_class is None:
            raise ValueError(f"Strategy {strategy_name} not found in strategies module")

        bt = Backtest(prices, strategy_class, cash=float(cash), commission=.002)
        stats = bt.run()

        logging.debug(f"Backtest stats: {stats}")

        # Create Plotly figure manually
        fig = go.Figure()

        # Add the OHLC data to the plot
        fig.add_trace(go.Candlestick(
            x=prices.index,
            open=prices['Open'],
            high=prices['High'],
            low=prices['Low'],
            close=prices['Close'],
            name='OHLC'
        ))

        # Extract trades data
        trades = bt._results['_trades']

        # Add markers for trade entries and exits on the OHLC plot
        for trade in trades.itertuples():
            if trade.EntryTime and trade.ExitTime:
                fig.add_trace(go.Scatter(
                    x=[trade.EntryTime],
                    y=[prices.loc[trade.EntryTime, 'Open']],
                    mode='markers',
                    marker=dict(color='green', symbol='triangle-up', size=10),
                    name='Trade Entry'
                ))
                fig.add_trace(go.Scatter(
                    x=[trade.ExitTime],
                    y=[prices.loc[trade.ExitTime, 'Close']],
                    mode='markers',
                    marker=dict(color='red', symbol='triangle-down', size=10),
                    name='Trade Exit'
                ))

        # Plot the volume as a bar chart
        # fig.add_trace(go.Bar(
        #     x=prices.index,
        #     y=prices['Volume'],
        #     name='Volume'
        # ))

        # Calculate RSI (for example, 14-period RSI)
        # delta = prices['Close'].diff()
        # gain = delta.where(delta > 0, 0)
        # loss = -delta.where(delta < 0, 0)
        # avg_gain = gain.rolling(window=14).mean()
        # avg_loss = loss.rolling(window=14).mean()
        # rs = avg_gain / avg_loss
        # rsi = 100 - (100 / (1 + rs))

        # # Add the RSI to the plot
        # fig.add_trace(go.Scatter(
        #     x=rsi.index,
        #     y=rsi,
        #     mode='lines',
        #     name='RSI'
        # ))

        # Create Equity Plotly figure manually
        fig2 = go.Figure()

        # Add the equity curve to the plot
        equity_curve = bt._results['_equity_curve']
        fig2.add_trace(go.Scatter(
            x=equity_curve.index,
            y=equity_curve['Equity'],
            mode='lines',
            name='Equity Curve'
        ))

        # Convert the figure to JSON
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        plot_json2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

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
                "initialCapital": cash,
                "dataRange": f"{stats['Start']} to {stats['End']}",
                "symbolInfo": symbol,
                "start": stats['Start'],
                "end": stats['End'],
                "duration": f"{(stats['End'] - stats['Start']).days} days",
                "maxTradeDuration": f"{stats['Max. Trade Duration']} days",
                "avgTradeDuration": f"{stats['Avg. Trade Duration']} days",
                "maxDrawdownDuration": f"{stats['Max. Drawdown Duration']} days",
                "avgDrawdownDuration": f"{stats['Avg. Drawdown Duration']} days"
            },
            # "ohlc": prices.reset_index().to_dict(orient='records'),  # Return OHLC data
            "plot": plot_json,  # Return Plotly plot JSON data
            "plotEquity": plot_json2  # Return Plotly plot JSON data
        }
    except Exception as e:
        logging.error("An error occurred during backtesting", exc_info=True)
        raise e
