from flask import Flask, request, jsonify
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# In-memory trade log for paper trading
paper_trades = []

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'error': 'No data received'}), 400
    # Log the trade
    trade = {
        'received_at': datetime.now().isoformat(),
        'signal': data
    }
    paper_trades.append(trade)
    logging.info(f"Paper trade received: {trade}")
    return jsonify({'status': 'ok', 'received': data}), 200

@app.route('/trades', methods=['GET'])
def get_trades():
    return jsonify(paper_trades)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
