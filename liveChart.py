import yfinance as yf
import pandas as pd

def live_Chart(symbol):
    try:
        # Fetch data directly — let yfinance handle the session internally
        data = yf.download(symbol, period="6mo", progress=False)

        if data.empty:
            return {"error": f"No data found for symbol: {symbol}"}

        # Flatten MultiIndex columns (if present)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Reset index to get 'Date' as a column
        data.reset_index(inplace=True)
        data['Date'] = pd.to_datetime(data['Date'])

        # Format OHLC data
        ohlc_data = [
            {
                "Close": row['Close'],
                "High": row['High'],
                "Low": row['Low'],
                "Open": row['Open'],
                "Volume": row['Volume'],
                "time": row['Date'].strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
            for _, row in data.iterrows()
        ]

        return {"ohlc": ohlc_data}

    except Exception as e:
        return {"error": str(e)}
