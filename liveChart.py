import yfinance as yf

def live_Chart(symbol):
     # Fetch data from Yahoo Finance
    data = yf.download(symbol, period="6mo")

    # Reset index to get the date column
    data.reset_index(inplace=True)

    # Convert to the desired format
    ohlc_data = []
    for index, row in data.iterrows():
        ohlc_data.append({
            "Close": row['Close'],
            "High": row['High'],
            "Low": row['Low'],
            "Open": row['Open'],
            "Volume": row['Volume'],
            "time": row['Date'].strftime("%a, %d %b %Y %H:%M:%S GMT")
        })

    return {"ohlc": ohlc_data}