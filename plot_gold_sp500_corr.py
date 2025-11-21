
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Define tickers
gold_ticker = "GC=F"  # Gold in USD
chf_ticker = "CHF=X"   # USD to CHF exchange rate
sp500_tr_ticker = "^SP500TR"  # S&P 500 Total Return

# Define time period
start_date = "2000-01-01"
end_date = "2025-12-31"

# Fetch data
gold_data = yf.download(gold_ticker, start=start_date, end=end_date, interval="1mo")
chf_data = yf.download(chf_ticker, start=start_date, end=end_date, interval="1mo")
sp500_tr_data = yf.download(sp500_tr_ticker, start=start_date, end=end_date, interval="1mo")

# Calculate Gold price in CHF
# We need to align the data by date (index)
df = pd.DataFrame(index=gold_data.index)
df['Gold_USD'] = gold_data['Close']
df['USD_CHF'] = chf_data['Close']
df['SP500_TR'] = sp500_tr_data['Close']

# Forward-fill missing values for exchange rate and S&P500 data to match gold trading days
df['USD_CHF'] = df['USD_CHF'].ffill()
df['SP500_TR'] = df['SP500_TR'].ffill()

# Drop rows where we still have NaNs (especially at the beginning)
df.dropna(inplace=True)

df['Gold_CHF'] = df['Gold_USD'] * df['USD_CHF']


# Create the plot
plt.style.use('dark_background')
plt.figure(figsize=(14, 8))
plt.scatter(df['SP500_TR'], df['Gold_CHF'], c=df.index.year, cmap='viridis', alpha=0.7)

# Set logarithmic scale
# plt.xscale('log')
# plt.yscale('log')

# Add labels and title
plt.xlabel("S&P 500 Total Return Index (log scale)")
plt.ylabel("Gold Price in CHF (log scale)")
plt.title("Gold Price (CHF) vs. S&P 500 Total Return (2000-2025, Monthly, Linear Scale)")
plt.grid(True, which="both", ls="--")

# Add a colorbar to show the time progression
cbar = plt.colorbar()
cbar.set_label('Year')


# Save the plot
output_filename = 'gold_vs_sp500_scatter_linear_dark.png'
plt.savefig(output_filename)

print(f"Plot saved as {output_filename}")
