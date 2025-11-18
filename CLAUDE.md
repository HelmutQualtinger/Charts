# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a financial data visualization application that displays index performance comparisons (DAX, S&P 500, SPI) normalized to a base value of 100 in CHF. The application consists of a Flask backend that fetches financial data and a single-page HTML/JavaScript frontend that renders interactive charts.

## Architecture

### Backend Services

The project has **two separate Flask servers** that serve different purposes:

1. **`server.py`** (Primary/Recommended): Uses `yfinance` library to fetch financial data
   - Main endpoint: `/api/data/all` - fetches all ticker data at once
   - Individual endpoint: `/api/data/<ticker>` - fetches data for a specific ticker
   - Serves `index.html` at the root route
   - Handles: DAX (^GDAXI), SPI (^SSPI), S&P 500 (^SP500TR), EUR/CHF, USD/CHF

2. **`proxy.py`** (Alternative): Direct Yahoo Finance API proxy with rate limiting
   - Endpoint: `/history/<symbol>` - proxies requests to Yahoo Finance
   - Implements rate limiting (0.5s between requests) and retry logic with exponential backoff
   - Does NOT serve the frontend

**Important**: The frontend (`index.html`) is configured to work with `server.py` by default. Both servers run on port 5000 and cannot run simultaneously.

### Frontend

`index.html` is a self-contained single-page application that:
- Fetches data from the Flask backend at `http://127.0.0.1:5000/api/data/all`
- Converts all indices to CHF using exchange rate data
- Filters to month-end data points only
- Normalizes all indices to base 100 starting from the first common data point
- Renders an interactive Chart.js visualization with date range controls

### Data Flow

1. User loads `index.html` (served by `server.py` or opened directly)
2. User clicks "Chart aktualisieren" button
3. Frontend calls `/api/data/all` endpoint
4. Backend fetches data from yfinance for all tickers (indices + exchange rates)
5. Frontend converts foreign currency indices to CHF
6. Frontend filters to month-end dates and normalizes to base 100
7. Chart.js renders the performance comparison

## Development Commands

### Running the Application

Start the main server:
```bash
python3 server.py
```

The application will be available at `http://localhost:5000`

### Running the Alternative Proxy

If you need the proxy server instead:
```bash
python3 proxy.py
```

**Note**: The frontend will need modification to use the proxy endpoints instead of the yfinance endpoints.

### Dependencies

Install dependencies using pip:
```bash
pip install -r requirements.txt
```

Or using uv (if available):
```bash
uv pip install -r requirements.txt
```

Required packages:
- Flask >= 3.0.0
- flask-cors >= 4.0.0
- yfinance >= 0.2.0 (for server.py)
- pandas >= 2.0.0
- requests >= 2.32.5 (for proxy.py)

## Key Implementation Details

### Ticker Mappings (server.py:14-20)

```python
TICKERS = {
    'dax': '^GDAXI',       # DAX Total Return
    'smi': '^SSPI',        # SPI (includes dividends)
    'sp500': '^SP500TR',   # S&P 500 Total Return
    'eurChf': 'EURCHF=X',
    'usdChf': 'USDCHF=X'
}
```

### Data Normalization Logic

The frontend performs multi-step data processing (index.html:143-242):
1. Converts EUR/USD indices to CHF using exchange rates
2. Filters to month-end dates only (last date of each month)
3. Finds first date where ALL indices have data
4. Normalizes each index to 100 at that first common date
5. All subsequent values are scaled relative to that base

### Rate Limiting (proxy.py only)

The proxy implements rate limiting with:
- 0.5 second delay between requests
- Thread-safe request lock
- Exponential backoff for 429 errors (1s, 2s, 4s delays)
- Maximum 3 retry attempts

## Common Modifications

### Adding a New Index

1. Add ticker mapping in `server.py` TICKERS dict
2. Add configuration in `index.html` INDEXES array (line 42-46)
3. Specify currency and add exchange rate ticker if needed

### Changing Date Range

Default date range: 2000-01-01 to present (server.py:39)

To modify, change the `start_date` in `get_ticker_data()` and `get_all_data()` functions.

### Adjusting Chart Display

Chart configuration is in `index.html` at the `renderChart()` function (line 248-318). Modify Chart.js options for appearance, tooltips, axes, etc.