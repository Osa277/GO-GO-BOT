from flask import Flask, jsonify, request
from smc_utils import generate_realistic_signal
from mt5_data import fetch_market_data, initialize_mt5, shutdown_mt5
from config import SYMBOLS, TIMEFRAMES

app = Flask(__name__)

@app.route('/status')
def status():
    return jsonify({'status': 'online', 'message': 'Trading bot API is running.'})

@app.route('/signal', methods=['GET'])
def signal():
    symbol = request.args.get('symbol', SYMBOLS[0])
    timeframe = request.args.get('timeframe', TIMEFRAMES[0])
    tf_map = {'M3': 3, 'M5': 5, 'M15': 15, 'M30': 30}
    tf_minutes = tf_map.get(timeframe, 3)
    bars = 55
    try:
        initialize_mt5()
        df = fetch_market_data(symbol, tf_minutes, bars)
        signals = generate_realistic_signal(symbol, timeframe, df)
        shutdown_mt5()
        if signals and signals[0]:
            return jsonify(signals[0])
        else:
            return jsonify({'error': 'No signal generated'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
