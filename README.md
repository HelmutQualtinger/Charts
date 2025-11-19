# Index Performance Comparison Chart

A web application for visualizing and comparing the performance of major financial indices and assets, normalized to a base value of 100 in Swiss Francs (CHF).

## Features

- **Multi-Asset Comparison**: Compare the performance of DAX (Total Return), S&P 500 (Total Return), SMI (Total Return), and Gold.
- **Currency Normalization**: All indices are converted to CHF for an accurate, direct comparison.
- **Base 100 Scaling**: All assets are normalized to start at 100 for easy relative performance analysis.
- **Interactive Charts**: Built with Chart.js for responsive and interactive visualizations.
- **Interactive Date Range Slider**: Easily select a custom start and end date for analysis.
- **Historical Data**: Accesses data from September 2003 to the present.
- **Month-End Data Filtering**: Data points are filtered to month-end values for a cleaner and more readable chart.
- **Performance Statistics**: Automatically calculates and displays total return and Compound Annual Growth Rate (CAGR) for each asset over the selected period.

## Prerequisites

- Python 3.13 or higher
- A package manager like `pip` or `uv`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Charts
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If you use `uv`, you can run `uv sync`)*

## Usage

### Starting the Server

To start the Flask server, run:
```bash
python3 server.py
```
The server will start on `http://localhost:5000`.

### Accessing the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Interface

1.  **Update the Chart**: Click the "Chart aktualisieren" (Update Chart) button to load the financial data.
2.  **Set Date Range**: Use the interactive slider to select your desired start and end dates. The chart will update automatically.
3.  **Interact with the Chart**:
    *   Hover over data points to see their exact values.
    *   Click on the legend items to hide or show specific assets.

## How It Works

### Data Sources

The application fetches real-time and historical financial data from Yahoo Finance using the `yfinance` library. The following tickers are used:

-   **DAX**: `^GDAXI` (Total Return)
-   **SMI**: `SMIC.SW` (Total Return)
-   **S&P 500**: `^SP500TR` (Total Return)
-   **Gold**: `GC=F` (Gold Futures)
-   **Exchange Rates**: `EURCHF=X` and `USDCHF=X` for currency conversion.

### Data Processing

1.  **Fetch**: The backend fetches historical data for all tickers from Yahoo Finance.
2.  **Convert**: On the frontend, the DAX (EUR) and S&P 500 / Gold (USD) values are converted to CHF using the daily exchange rates.
3.  **Filter**: The data is filtered to only include month-end data points.
4.  **Normalize**: All asset values are scaled to a base of 100, starting from the first common data point in the selected time range.
5.  **Visualize**: The processed data is rendered as a line chart using Chart.js.

## Project Structure

```
Charts/
├── server.py         # The main Flask server application
├── index.html        # The frontend single-page application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Technical Details

### Backend (`server.py`)

-   **Framework**: Flask
-   **Data Library**: `yfinance` for fetching data from Yahoo Finance.
-   **Endpoint**:
    -   `GET /api/data/all`: Fetches and returns data for all configured tickers.

### Frontend (`index.html`)

-   **Charting Library**: Chart.js with `date-fns` adapter.
-   **UI Components**: Includes an interactive date range slider using `noUiSlider`.
-   **Logic**: All data processing, including currency conversion, normalization, and statistical calculations, is handled client-side in vanilla JavaScript.
