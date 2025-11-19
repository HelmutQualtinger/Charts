from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
from threading import Lock

app = Flask(__name__)
# Erlaube Anfragen von Ihrem Frontend (z.B. von http://127.0.0.1:5000 oder '*' für alle)
CORS(app)

# Rate limiting configuration
REQUEST_DELAY = 0.5  # Sekunden zwischen Requests
last_request_time = 0
request_lock = Lock() 

# Yahoo Finance Basis-URL
YAHOO_BASE_URL = "https://query1.finance.yahoo.com/v7/finance/download/"

@app.route('/history/<symbol>', methods=['GET'])
def get_history(symbol):
    """
    Proxy-Endpunkt, der historische Daten von Yahoo Finance abruft.
    Implementiert Rate-Limiting und Retry-Logic.
    """
    global last_request_time

    try:
        # Parameter aus der Frontend-Anfrage übernehmen (period1, period2)
        params = {
            'period1': request.args.get('period1'),
            'period2': request.args.get('period2'),
            'interval': '1d',
            'events': 'history',
            'includeAdjustedClose': 'true'
        }

        # Rate-Limiting: Warte zwischen Requests
        with request_lock:
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            if time_since_last_request < REQUEST_DELAY:
                sleep_time = REQUEST_DELAY - time_since_last_request
                app.logger.info(f"Rate limiting: Warte {sleep_time:.2f}s für {symbol}")
                time.sleep(sleep_time)
            last_request_time = time.time()

        # Retry-Logic mit exponential backoff
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            # Anfrage an Yahoo Finance senden
            url = f"{YAHOO_BASE_URL}{symbol}"
            response = requests.get(url, params=params, timeout=10)

            # Erfolgreiche Antwort
            if response.status_code == 200:
                app.logger.info(f"Erfolgreicher Abruf für {symbol}")
                return response.text, 200, {'Content-Type': 'text/csv'}

            # Rate-Limit-Fehler: Warte und versuche erneut
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    app.logger.warning(f"Rate limit für {symbol}, Versuch {attempt + 1}/{max_retries}, warte {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    app.logger.error(f"Rate limit für {symbol} nach {max_retries} Versuchen")
                    return jsonify({"error": "Rate limit erreicht. Bitte versuchen Sie es später erneut.", "status": 429}), 429

            # Andere Fehler
            app.logger.error(f"Fehler beim Abruf von {symbol}: Status {response.status_code}")
            return jsonify({"error": "Fehler beim Abruf von Yahoo Finance", "status": response.status_code}), response.status_code

    except Exception as e:
        app.logger.error(f"Proxy-Fehler für {symbol}: {e}")
        return jsonify({"error": "Interner Serverfehler", "details": str(e)}), 500

if __name__ == '__main__':
    # Starten Sie den Server auf Port 5001 (Standard)
    # Sie müssen den Browser-Code auf den gleichen Ursprung oder Port umstellen,
    # oder die CORS-Konfiguration oben verwenden.
    print("Starte Flask Proxy auf http://127.0.0.1:5001")
    app.run(debug=True, port=5001)