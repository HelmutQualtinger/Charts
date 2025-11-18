#!/usr/bin/env python3
"""
Flask server to fetch financial data using yfinance
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

TICKERS = {
    'dax': '^GDAXI',  # DAX Total Return
    'smi': 'SMIC.SW',  # SMI Total Return Index
    'sp500': '^SP500TR',  # S&P 500 Total Return
    'gold': 'GC=F',  # Gold Futures
    'eurChf': 'EURCHF=X',
    'usdChf': 'USDCHF=X'
}


@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')


@app.route('/api/data/<ticker>')
def get_ticker_data(ticker):
    """Fetch data for a specific ticker"""
    try:
        if ticker not in TICKERS:
            return jsonify({'error': f'Unknown ticker: {ticker}'}), 400

        symbol = TICKERS[ticker]

        # Fetch data from Sept 2003 to present (USD/CHF data available from Sept 2003)
        start_date = '2003-09-01'
        end_date = datetime.now().strftime('%Y-%m-%d')

        print(f"Fetching {ticker} ({symbol}) from {start_date} to {end_date}...")

        # Download data using yfinance
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if data.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404

        # Convert to dictionary format: {date: close_price}
        result = {}
        for date, row in data.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            close_price = float(row['Close'])
            result[date_str] = close_price

        print(f"Successfully fetched {len(result)} data points for {ticker}")

        return jsonify(result)

    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/data/all')
def get_all_data():
    """Fetch all ticker data at once"""
    try:
        result = {}

        for ticker, symbol in TICKERS.items():
            print(f"Fetching {ticker} ({symbol})...")

            start_date = '2003-09-01'
            end_date = datetime.now().strftime('%Y-%m-%d')

            data = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if data.empty:
                print(f"Warning: No data for {ticker}")
                result[ticker] = {}
                continue

            # Convert to dictionary
            ticker_data = {}
            for date, row in data.iterrows():
                date_str = date.strftime('%Y-%m-%d')
                close_price = float(row['Close'])
                ticker_data[date_str] = close_price

            result[ticker] = ticker_data
            print(f"  → {len(ticker_data)} data points")

        return jsonify(result)

    except Exception as e:
        print(f"Error fetching all data: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, port=5000)
