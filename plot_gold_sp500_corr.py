import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# Define tickers
gold_ticker = "GC=F"  # Gold in USD
sp500_tr_ticker = "^SP500TR"  # S&P 500 Total Return

# Define time period
start_date = "2000-01-01"
end_date = "2025-12-31"

# Fetch USD/CHF data from European Central Bank (ECB) API - FREE, NO KEY REQUIRED
def fetch_usd_chf_ecb():
    """
    Fetch USD/CHF exchange rates from ECB.
    Uses ECB's 90-day reference rates with fallback to calculate from EUR rates.
    Historical data available from 1999.
    """
    try:
        import io
        import zipfile

        print("  - Downloading ECB historical exchange rates...")

        # Download the ZIP file with all historical ECB rates
        zip_url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip'
        response = requests.get(zip_url, timeout=10)

        # Extract and read CSV from ZIP
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_file = z.namelist()[0]
            with z.open(csv_file) as f:
                df_rates = pd.read_csv(f)

        # Parse date column (should be first column)
        df_rates.rename(columns={df_rates.columns[0]: 'Date'}, inplace=True)
        df_rates['Date'] = pd.to_datetime(df_rates['Date'])
        df_rates.set_index('Date', inplace=True)

        # Find USD and CHF columns
        usd_col = next((col for col in df_rates.columns if 'USD' in col.upper()), None)
        chf_col = next((col for col in df_rates.columns if 'CHF' in col.upper()), None)

        if usd_col is None or chf_col is None:
            raise ValueError(f"Could not find USD or CHF columns. Available: {df_rates.columns.tolist()}")

        # Convert to numeric, handling any non-numeric values
        df_rates[usd_col] = pd.to_numeric(df_rates[usd_col], errors='coerce')
        df_rates[chf_col] = pd.to_numeric(df_rates[chf_col], errors='coerce')

        # Calculate USD/CHF: if 1 EUR = X USD and 1 EUR = Y CHF, then 1 USD = Y/X CHF
        df_rates['USD_CHF'] = df_rates[chf_col] / df_rates[usd_col]

        # Keep only USD_CHF column and rename
        result = df_rates[['USD_CHF']].copy()
        result.columns = ['Close']

        # Remove NaN values
        result = result.dropna()

        # Resample to monthly (first day of month for alignment with yfinance data)
        result = result.resample('MS').first().dropna()

        print(f"  - ECB data range: {result.index.min().date()} to {result.index.max().date()}")
        print(f"  - Total monthly records: {len(result)}")
        return result

    except Exception as e:
        print(f"Error fetching from ECB: {e}")
        import traceback
        traceback.print_exc()
        return None

# Fetch data
print("Fetching Gold data...")
gold_data = yf.download(gold_ticker, start=start_date, end=end_date, interval="1mo", progress=False)

print("Fetching USD/CHF exchange rates from ECB...")
chf_data = fetch_usd_chf_ecb()

if chf_data is None:
    print("Failed to fetch USD/CHF data from ECB.")
    exit(1)

print("Fetching S&P 500 Total Return data...")
sp500_tr_data = yf.download(sp500_tr_ticker, start=start_date, end=end_date, interval="1mo", progress=False)

# Calculate Gold price in CHF
# We need to align the data by date (index)
# Handle multi-level columns from yfinance
gold_close = gold_data['Close'] if 'Close' in gold_data.columns.get_level_values(0) else gold_data.iloc[:, 0]
if isinstance(gold_close, pd.DataFrame):
    gold_close = gold_close.iloc[:, 0]

sp500_close = sp500_tr_data['Close'] if 'Close' in sp500_tr_data.columns.get_level_values(0) else sp500_tr_data.iloc[:, 0]
if isinstance(sp500_close, pd.DataFrame):
    sp500_close = sp500_close.iloc[:, 0]

df = pd.DataFrame(index=gold_data.index)
df['Gold_USD'] = gold_close
df['USD_CHF'] = chf_data['Close']
df['SP500_TR'] = sp500_close

# Forward-fill missing values for exchange rate and S&P500 data to match gold trading days
df['USD_CHF'] = df['USD_CHF'].ffill()
df['SP500_TR'] = df['SP500_TR'].ffill()

# Drop rows where we still have NaNs (especially at the beginning)
df.dropna(inplace=True)

df['Gold_CHF'] = df['Gold_USD'] * df['USD_CHF']
df['SP500_TR_CHF'] = df['SP500_TR'] * df['USD_CHF']

# Reset index to use date as a column
df.reset_index(inplace=True)
df.rename(columns={'Date': 'Date'}, inplace=True)

# Export to CSV
csv_columns = ['Date', 'USD_CHF', 'Gold_USD', 'Gold_CHF', 'SP500_TR', 'SP500_TR_CHF']
df_export = df[csv_columns].copy()

# Round values for CSV export
df_export['USD_CHF'] = df_export['USD_CHF'].round(4)
for col in ['Gold_USD', 'Gold_CHF', 'SP500_TR', 'SP500_TR_CHF']:
    df_export[col] = df_export[col].round(0).astype(int)

df_export.to_csv('gold_vs_sp500_data.csv', index=False)
print("CSV file saved: gold_vs_sp500_data.csv")

# Create the scatter plot with plotly
fig = go.Figure()

# Calculate appropriate tick spacing for colorbar
step = max(1, len(df) // 10) if len(df) > 10 else 1
tick_indices = df.index[::step]
tick_texts = [df.loc[i, 'Date'].strftime('%Y-%m-%d') for i in tick_indices]

fig.add_trace(go.Scatter(
    x=df['SP500_TR_CHF'],
    y=df['Gold_CHF'],
    mode='markers',
    marker=dict(
        size=6,
        color=df.index,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(
            title='Date',
            tickvals=tick_indices,
            ticktext=tick_texts,
        ),
        opacity=0.7
    ),
    text=[date.strftime('%Y-%m-%d') for date in df['Date']],
    hovertemplate='<b>Date:</b> %{text}<br><b>S&P 500 (CHF):</b> %{x:.2f}<br><b>Gold (CHF):</b> %{y:.2f}<extra></extra>'
))

fig.update_layout(
    title='Gold Price (CHF) vs. S&P 500 Total Return (2000-2025, Monthly)',
    xaxis_title='S&P 500 Total Return Index (CHF)',
    yaxis_title='Gold Price in CHF',
    hovermode='closest',
    template='plotly_dark',
    width=1400,
    height=800,
    showlegend=False,
    xaxis=dict(type='linear', showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 0, 0.4)', griddash='dot'),
    yaxis=dict(type='linear', showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 0, 0.4)', griddash='dot')
)

# Display the plot
fig.show()
