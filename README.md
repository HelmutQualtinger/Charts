
# Index Performance Comparison Chart

A web application for visualizing and comparing the performance of major financial indices (DAX, S&P 500, SPI) normalized to a base value of 100 in Swiss Francs (CHF).

## Features

- **Multi-Index Comparison**: Compare performance of DAX (Total Return), S&P 500 (Total Return), and SPI (Swiss Performance Index)
- **Currency Normalization**: All indices are converted to CHF for accurate comparison
- **Base 100 Scaling**: All indices are normalized to start at 100 for easy relative performance comparison
- **Interactive Charts**: Built with Chart.js for responsive, interactive visualizations
- **Date Range Selection**: Choose custom start and end dates for analysis
- **Historical Data**: Access data from 2000 to present
- **Month-End Data**: Data points filtered to month-end values for cleaner visualization

## Prerequisites

- Python 3.13 or higher
- uv package manager (recommended) or pip

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Charts
```

2. Install dependencies:

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the Flask server:
```bash
python3 server.py
```

The server will start on `http://localhost:5000`

### Accessing the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Interface

1. **Set Date Range**: Use the date pickers to select your desired start and end dates
2. **Load Data**: Click the "Chart aktualisieren" (Update Chart) button
3. **Interact with Chart**:
   - Hover over data points to see exact values
   - Click legend items to show/hide specific indices
   - Use browser zoom for detailed analysis

## How It Works

### Data Sources

The application fetches real-time financial data using the yfinance library:
- **DAX**: ^GDAXI (German stock index total return)
- **SPI**: ^SSPI (Swiss Performance Index including dividends)
- **S&P 500**: ^SP500TR (S&P 500 Total Return Index)
- **Exchange Rates**: EUR/CHF and USD/CHF for currency conversion

### Data Processing

1. **Fetch**: Historical data retrieved from Yahoo Finance
2. **Convert**: EUR and USD indices converted to CHF using daily exchange rates
3. **Filter**: Data filtered to month-end values only
4. **Normalize**: All indices scaled to base 100 at the first common data point
5. **Visualize**: Chart.js renders the comparative performance

## Project Structure

```
Charts/
 server.py          # Main Flask server using yfinance
 proxy.py           # Alternative proxy server with rate limiting
 index.html         # Frontend application
 requirements.txt   # Python dependencies
 pyproject.toml     # Project configuration
 README.md          # This file
```

## Technical Details

### Backend (server.py)

- **Framework**: Flask with CORS enabled
- **Data Library**: yfinance for Yahoo Finance data
- **Endpoints**:
  - `GET /` - Serves the frontend HTML
  - `GET /api/data/<ticker>` - Fetch data for a specific ticker
  - `GET /api/data/all` - Fetch all ticker data at once (recommended)

### Frontend (index.html)

- **Charting**: Chart.js 3.7.1 with date-fns adapter
- **Architecture**: Single-page application with vanilla JavaScript
- **Data Processing**: Client-side currency conversion and normalization

### Alternative Proxy Server (proxy.py)

An alternative backend that directly proxies Yahoo Finance API with:
- Rate limiting (0.5s between requests)
- Automatic retry with exponential backoff
- Thread-safe request handling

**Note**: The frontend is configured for `server.py` by default.

## Dependencies

- **Flask** (>=3.0.0): Web framework
- **flask-cors** (>=4.0.0): CORS support
- **yfinance** (>=0.2.0): Yahoo Finance data fetching
- **pandas** (>=2.0.0): Data manipulation
- **requests** (>=2.32.5): HTTP library (for proxy.py)

## Troubleshooting

### Data Not Loading

- Ensure the Flask server is running on port 5000
- Check browser console for CORS or network errors
- Verify internet connection for Yahoo Finance API access

### Missing Data Points

- Some historical data may be unavailable for certain dates
- The chart only displays dates where all indices have data
- Try adjusting the date range if the chart appears empty

### Rate Limiting

If using `proxy.py` and encountering rate limit errors:
- The server implements automatic retry with exponential backoff
- Wait a few minutes before retrying
- Consider using `server.py` which uses yfinance's built-in rate handling

## License

This project is available for personal and educational use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
