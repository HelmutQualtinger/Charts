import yfinance as yf
import pandas as pd

# Define ticker
ticker = "AAPL"

# Download data from 2024-01-01 until now
df = yf.download(ticker,
                 start="2000-01-01",
                 end=None,
                 interval="1mo",        # daily data; change if you want intraday
                 auto_adjust=True,      # adjust for splits/dividends etc.
                 progress=False)

# Optionally save to CSV
df.to_csv("AAPL_since_2024.csv")

print(df.head())
print(df.tail())
