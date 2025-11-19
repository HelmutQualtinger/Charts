# Project Information for Gemini

This file provides context to the Gemini model about the 'Charts' project.

## Project Overview

This project is a Flask-based web application designed to fetch and serve financial data using the `yfinance` library. It provides API endpoints to retrieve historical stock and currency exchange data for various tickers (DAX, SMI, S&P 500, Gold, EUR/CHF, USD/CHF). The application also serves a main `index.html` file, presumably for a frontend that visualizes this data.

## Key Technologies

*   **Python**: The primary programming language.
*   **Flask**: Web framework for building the API and serving the frontend.
*   **Flask-CORS**: Enables Cross-Origin Resource Sharing.
*   **yfinance**: Library for fetching financial market data.
*   **pandas**: Data manipulation and analysis library.
*   **IPython**: (Development dependency) Enhanced interactive Python shell.

## Development Setup

To set up the development environment, you need Python 3.13 or higher.

1.  **Create a virtual environment (if not already done):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # or if using uv:
    uv pip install -r requirements.txt
    ```

## Running the Application

To start the Flask development server:

```bash
source .venv/bin/activate # if not already active
python server.py
```

The application will then be accessible at `http://localhost:5002`.

## Current Folder Structure

This overview helps in understanding the project's layout as of **Mittwoch, 19. November 2025**.

```
/Users/haraldbeker/PythonProjects/Charts/
├───.python-version
├───AAPL_since_2024.csv
├───apple.py
├───CLAUDE.md
├───gemini.md
├───index.html
├───main.py
├───proxy.py
├───pyproject.toml
├───README.md
├───requirements.txt
├───server.py
├───uv.lock
├───währungs.md
├───währungs.pdf
├───.claude/
└───.venv/
```