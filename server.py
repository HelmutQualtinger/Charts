#!/usr/bin/env python3
"""
Flask + Dash server to display financial data using Plotly
"""
from flask import Flask
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from smic import smi as smi_data

# Flask app
server = Flask(__name__)

# Dash app integrated with Flask
app = dash.Dash(__name__, server=server, url_base_pathname='/')

# Ticker mappings
TICKERS = {
    'dax': '^GDAXI',  # DAX Total Return
    'smi': 'SMIC.SW',  # SMI Total Return Index
    'sp500': '^SP500TR',  # S&P 500 Total Return
    'gold': 'GC=F',  # Gold Futures
    'eurChf': 'EURCHF=X',
    'usdChf': 'USDCHF=X'
}

# Index configuration
INDEXES = [
    {'name': 'DAX (TR)', 'ticker': 'dax', 'currency': 'EUR', 'color': 'rgb(0, 104, 182)'},
    {'name': 'S&P 500 (TR)', 'ticker': 'sp500', 'currency': 'USD', 'color': 'rgb(75, 192, 192)'},
    {'name': 'SMI (TR)', 'ticker': 'smi', 'currency': 'CHF', 'color': 'rgb(255, 99, 132)'},
    {'name': 'Gold', 'ticker': 'gold', 'currency': 'USD', 'color': 'rgb(255, 215, 0)'}
]


def fetch_all_data():
    """Fetch all ticker data from yfinance"""
    result = {}
    start_date = '2000-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

    for ticker, symbol in TICKERS.items():
        if ticker == 'smi':
            print("Using hardcoded SMI data...")
            result['smi'] = pd.Series(smi_data)
            result['smi'].index = pd.to_datetime(result['smi'].index)
            continue

        print(f"Fetching {ticker} ({symbol})...")
        try:
            data = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=True)
            if not data.empty:
                # Ensure we get a Series, not a DataFrame
                close_data = data['Close']
                if isinstance(close_data, pd.DataFrame):
                    # If multiple columns, take the first one
                    close_data = close_data.iloc[:, 0]
                result[ticker] = close_data
                print(f"  → {len(data)} data points")
            else:
                print(f"Warning: No data for {ticker}")
                result[ticker] = pd.Series(dtype=float)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            result[ticker] = pd.Series(dtype=float)

    # Back-fill exchange rates to 2000-01-01
    for currency_ticker in ['eurChf', 'usdChf']:
        if currency_ticker in result and not result[currency_ticker].empty:
            first_rate = result[currency_ticker].iloc[0]
            first_date = result[currency_ticker].index[0]

            # Create date range from 2000-01-01 to first available date
            start = pd.Timestamp('2000-01-01')
            if first_date > start:
                date_range = pd.date_range(start=start, end=first_date - timedelta(days=1), freq='D')
                backfill = pd.Series(first_rate, index=date_range)
                result[currency_ticker] = pd.concat([backfill, result[currency_ticker]]).sort_index()
                print(f"  Back-filled {currency_ticker} with {len(date_range)} days")

    return result


def process_and_scale_data(all_data, start_date, end_date):
    """
    Convert to CHF, filter to month-end dates, and normalize to base 100

    Returns:
        dict: Processed data ready for plotting
    """
    # Filter data by date range
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    # Prepare DataFrames for each index in CHF
    chf_data = {}

    for index_config in INDEXES:
        ticker = index_config['ticker']
        currency = index_config['currency']

        if ticker not in all_data or all_data[ticker].empty:
            continue

        # Get index data
        index_series = all_data[ticker].copy()

        # Convert to CHF if needed
        if currency == 'EUR':
            if 'eurChf' in all_data:
                index_series = index_series * all_data['eurChf']
            else:
                continue
        elif currency == 'USD':
            if 'usdChf' in all_data:
                index_series = index_series * all_data['usdChf']
            else:
                continue

        # Filter by date range
        index_series = index_series[(index_series.index >= start) & (index_series.index <= end)]

        if not index_series.empty:
            chf_data[index_config['name']] = index_series

    # Combine all data into a single DataFrame
    df = pd.DataFrame(chf_data)

    # Filter to month-end dates only
    df = df.resample('M').last()

    # Drop rows where all values are NaN
    df = df.dropna(how='all')

    # Forward fill missing values
    df = df.ffill()

    # Normalize to base 100 (use first valid value for each column)
    normalized_df = pd.DataFrame()
    for col in df.columns:
        first_valid = df[col].first_valid_index()
        if first_valid is not None:
            base_value = df.loc[first_valid, col]
            normalized_df[col] = (df[col] / base_value) * 100

    return normalized_df


def calculate_statistics(df):
    """Calculate CAGR and total return for each index"""
    stats = []

    for col in df.columns:
        series = df[col].dropna()
        if len(series) < 2:
            continue

        first_value = series.iloc[0]
        last_value = series.iloc[-1]

        # Skip if first value is zero or negative (cannot calculate CAGR)
        if first_value <= 0:
            continue

        # Total return
        total_return = ((last_value - first_value) / first_value) * 100

        # CAGR
        start_date = series.index[0]
        end_date = series.index[-1]
        years = (end_date - start_date).days / 365.25

        cagr = (pow(last_value / first_value, 1 / years) - 1) * 100 if years > 0 else 0
        color = next((idx['color'] for idx in INDEXES if idx['name'] == col), 'black')

        stats.append({
            'name': col,
            'total_return': total_return,
            'cagr': cagr,
            'color': color
        })

    return stats


def generate_slider_marks():
    """Generate marks for the date slider (every 2 years)"""
    marks = {}
    start_year = 2000
    end_year = datetime.now().year

    for year in range(start_year, end_year + 1, 2):
        timestamp = datetime(year, 1, 1).timestamp()
        marks[timestamp] = {'label': str(year), 'style': {'color': '#e0e0e0'}}

    # Add current year if not already there
    current_timestamp = datetime(end_year, 1, 1).timestamp()
    if current_timestamp not in marks:
        marks[current_timestamp] = {'label': str(end_year), 'style': {'color': '#e0e0e0'}}

    return marks


# Dash Layout
app.layout = html.Div(style={'backgroundColor': '#1a1a1a', 'color': '#e0e0e0', 'padding': '20px', 'fontFamily': 'sans-serif'}, children=[
    html.H1('🚀 Index-Performance-Vergleich (CHF, Basis 100)',
            style={'color': '#e0e0e0', 'marginBottom': '20px'}),

    dcc.Loading(
        id="loading",
        type="default",
        children=[
            dcc.Graph(id='performance-chart',
                     style={'height': '600px'})
        ]
    ),

    html.Div([
        html.Label('Datumsbereich wählen:', style={'marginBottom': '15px', 'display': 'block', 'fontSize': '14px', 'textAlign': 'center', 'color': '#b0b0b0'}),
        html.Div([
            html.Div([
                html.Span('Von: ', style={'color': '#b0b0b0', 'marginRight': '5px'}),
                html.Span(id='start-date-label', style={'fontWeight': 'bold', 'color': '#4da6ff', 'fontSize': '15px'})
            ], style={'display': 'inline-block', 'marginRight': '30px'}),
            html.Div([
                html.Span('Bis: ', style={'color': '#b0b0b0', 'marginRight': '5px'}),
                html.Span(id='end-date-label', style={'fontWeight': 'bold', 'color': '#4da6ff', 'fontSize': '15px'})
            ], style={'display': 'inline-block'})
        ], style={'marginBottom': '25px', 'textAlign': 'center'}),
        dcc.RangeSlider(
            id='date-range-slider',
            min=datetime(2000, 1, 1).timestamp(),
            max=datetime.now().timestamp(),
            value=[datetime(2000, 1, 1).timestamp(), datetime.now().timestamp()],
            marks=generate_slider_marks(),
            tooltip={
                "placement": "top",
                "always_visible": True,
                "template": "{value}"
            },
            allowCross=False
        ),
        html.Div(id='tooltip-formatter', style={'display': 'none'})
    ], style={
        'marginTop': '20px',
        'marginBottom': '20px',
        'padding': '20px',
        'border': '1px solid #444',
        'borderRadius': '5px',
        'backgroundColor': '#2a2a2a'
    }),

    html.Div(id='statistics',
             style={
                 'marginTop': '20px',
                 'padding': '15px',
                 'backgroundColor': '#2a2a2a',
                 'border': '1px solid #444',
                 'borderRadius': '5px'
             })
])


@app.callback(
    [Output('start-date-label', 'children'),
     Output('end-date-label', 'children')],
    [Input('date-range-slider', 'value')]
)
def update_date_labels(slider_values):
    """Update date labels when slider changes"""
    start_date = datetime.fromtimestamp(slider_values[0]).strftime('%Y-%m-%d')
    end_date = datetime.fromtimestamp(slider_values[1]).strftime('%Y-%m-%d')
    return start_date, end_date


# Clientside callback to format tooltip values as human-readable dates
app.clientside_callback(
    """
    function(value) {
        if (!value) return window.dash_clientside.no_update;

        // Format timestamps to readable dates
        const formatDate = (timestamp) => {
            const date = new Date(timestamp * 1000);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };

        // Find all tooltip elements and update their content
        setTimeout(() => {
            const tooltips = document.querySelectorAll('.rc-slider-tooltip-content');
            tooltips.forEach((tooltip, index) => {
                if (value[index]) {
                    tooltip.textContent = formatDate(value[index]);
                }
            });
        }, 10);

        return window.dash_clientside.no_update;
    }
    """,
    Output('tooltip-formatter', 'children'),
    Input('date-range-slider', 'value')
)


@app.callback(
    [Output('performance-chart', 'figure'),
     Output('statistics', 'children')],
    [Input('date-range-slider', 'value')]
)
def update_chart(slider_values):
    """Update chart and statistics based on date range"""

    # Convert timestamps to date strings
    start_date = datetime.fromtimestamp(slider_values[0]).strftime('%Y-%m-%d')
    end_date = datetime.fromtimestamp(slider_values[1]).strftime('%Y-%m-%d')

    # Fetch all data
    all_data = fetch_all_data()

    # Process and scale data
    df = process_and_scale_data(all_data, start_date, end_date)

    # Create Plotly figure
    fig = go.Figure()

    for index_config in INDEXES:
        name = index_config['name']
        if name in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[name],
                mode='lines',
                name=name,
                line=dict(color=index_config['color'], width=2),
                hovertemplate='%{y:.2f}<extra></extra>'
            ))

    # Update layout
    fig.update_layout(
        title='Index Performance Vergleich (Basis 100 in CHF)',
        xaxis_title='Datum',
        yaxis_title='Indexwert (Basis 100)',
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#2a2a2a',
        font=dict(color='#e0e0e0'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Calculate statistics
    stats = calculate_statistics(df)

    # Create statistics display
    stats_children = [
        html.H2('Performance Statistiken', style={'marginTop': '0', 'color': '#4da6ff'})
    ]

    for stat in stats:
        stats_children.append(
            html.Div([
                html.Div(stat['name'],
                        style={'fontWeight': 'bold', 'color': stat['color']}),
                html.Div([
                    html.Span("Kursanstieg: ", style={'marginRight': '5px'}),
                    html.Strong(f"{stat['total_return']:.2f}%"),
                    html.Span(" | CAGR: ", style={'marginLeft': '20px', 'marginRight': '5px'}),
                    html.Strong(f"{stat['cagr']:.2f}%")
                ])
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'padding': '8px 0',
                'borderBottom': '1px solid #444'
            })
        )

    return fig, stats_children


if __name__ == '__main__':
    print("Starting Flask + Dash server...")
    print("Access the application at: http://localhost:8000")
    server.run(debug=False, port=8000)
