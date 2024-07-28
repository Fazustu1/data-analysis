# Analyze historical stock market data
# Import Modules
import pandas as pd
import quandl
import matplotlib.pyplot as plt
import datetime as dt
import statistics
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import plotly.graph_objs as go

# Initializing Paramaters
start_date = "2010-01-01"
end_date = dt.date.today()
symbols = "AAPL"

# Get Data
data = yf.download(symbols, period="max") 

# Calculate Change
close = data["Adj Close"]
change = close.diff(1)
is_gain, is_loss = change > 0, change < 0
gain, loss = change, -change
gain[is_loss] = 0
loss[is_gain] = 0
gain.name = 'gain'
loss.name = 'loss'

# Things for finding RSI
data["change"] = close.diff()
data["gain"] = data.change.mask(data.change < 0, 0.0)
data['loss'] = -data.change.mask(data.change > 0, -0.0)

def rma(x, n):
    """Running moving average"""
    a = np.full_like(x, np.nan)
    a[n] = x[1:n+1].mean()
    for i in range(n+1, len(x)):
        a[i] = (a[i-1] * (n - 1) + x[i]) / n
    return a

data['avg_gain'] = rma(data.gain.to_numpy(), 14)
data['avg_loss'] = rma(data.loss.to_numpy(), 14)

data['rs'] = data.avg_gain / data.avg_loss
data['rsi'] = 100 - (100 / (1 + data.rs))

# User Input
def config():
    start_date = input("Enter a date (YYYY-MM-DD): ")
    try:
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid input format. Please enter date and in the format: YYYY-MM-DD")

# Find Mean, Median and Standard Deviation
def statistics():
    mean_stock_price = data["Adj Close"].mean()
    median_stock_price = data["Adj Close"].median()
    stdev_stock_price = statistics.stdev(data["Adj Close"])
    print(f"Mean: {mean_stock_price}")
    print(f"Median: {median_stock_price}")
    print(f"Standard Deviation: {stdev_stock_price}")

# Finding Patterns
def patterns():
    global closing_data
    closing_data = data["Adj Close"].to_frame()
    closing_data["SMA60"] = data["Adj Close"].rolling(60).mean()
    closing_data["SDV60"] = data["Adj Close"].rolling(60).std()
    closing_data.dropna(inplace=True)

# Display
def main():
    patterns()
    config()
    # Create traces for each data series
    trace_close = go.Scatter(x=data.index, y=data["Adj Close"], mode="lines", name="Adj Close")
    trace_sma = go.Scatter(x=closing_data.index, y=closing_data["SMA60"], mode="lines", name="SMA60")
    trace_sdv = go.Scatter(x=closing_data.index, y=closing_data["SDV60"], mode="lines", name="SDV60")
    trace_rsi = go.Scatter(x=data.index, y=data["rsi"], mode="lines", name="RSI")

    # Create layout
    layout = go.Layout(title=f"All Time Closing Prices for {symbols}", xaxis=dict(title="Date"), yaxis=dict(title="Price"))

    # Combine traces into a single figure
    fig = go.Figure(data=[trace_close, trace_sma, trace_sdv, trace_rsi], layout=layout)

    # Plot
    fig.show()

if __name__ == "__main__":
    main()