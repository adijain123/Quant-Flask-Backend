import yfinance as yf
import pandas as pd

def live_Chart(symbol):
    # Fetch data from Yahoo Finance
    data = yf.download(symbol, period="6mo")

    # Flatten MultiIndex columns (Price/Ticker)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Reset index to get 'Date' as a column
    data.reset_index(inplace=True)

    # Make sure 'Date' is datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Format the data
    ohlc_data = []
    for _, row in data.iterrows():
        ohlc_data.append({
            "Close": row['Close'],
            "High": row['High'],
            "Low": row['Low'],
            "Open": row['Open'],
            "Volume": row['Volume'],
            "time": row['Date'].strftime("%a, %d %b %Y %H:%M:%S GMT")
        })

    return {"ohlc": ohlc_data}
