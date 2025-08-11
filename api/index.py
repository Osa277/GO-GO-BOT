from flask import Flask, jsonify, request
import requests
import json
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

# Environment variables (will be set in Vercel)
TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
TELEGRAM_CHAT_ID = "5362504152"

# Multi-user support - Add more chat IDs here
TELEGRAM_USERS = [
    '5362504152',  # Samuel (original user)
    # Add more chat IDs here as needed:
    # '1234567890',  # User 2
    # '0987654321',  # User 3
]

def send_telegram_alert_to_users(message, chat_ids=None):
    """Send alert to multiple Telegram users"""
    if chat_ids is None:
        chat_ids = TELEGRAM_USERS
    
    success_count = 0
    
    for chat_id in chat_ids:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Message sent to {chat_id}")
            else:
                print(f"❌ Failed to send to {chat_id}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending to {chat_id}: {str(e)}")
    
    print(f"📊 Successfully sent to {success_count}/{len(chat_ids)} users")
    return success_count > 0

def send_telegram_alert(message):
    """Send alert to Telegram (backwards compatibility)"""
    return send_telegram_alert_to_users(message, TELEGRAM_USERS)

def get_yahoo_data(symbol, period="1d", interval="5m"):
    """Get market data from Yahoo Finance (free alternative to MT5)"""
    try:
        # Map crypto symbols
        symbol_map = {
            'BTCUSD': 'BTC-USD',
            'XAUUSD': 'GC=F',  # Gold futures
            'US30': '^DJI'     # Dow Jones
        }
        
        yahoo_symbol = symbol_map.get(symbol, symbol)
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            return None
            
        # Convert to format similar to MT5
        df = pd.DataFrame({
            'time': data.index,
            'open': data['Open'],
            'high': data['High'], 
            'low': data['Low'],
            'close': data['Close'],
            'volume': data['Volume']
        })
        
        return df.tail(50)  # Last 50 bars
        
    except Exception as e:
        print(f"Yahoo data error: {e}")
        return None

def generate_simple_signal(symbol, df):
    """Generate a simple trading signal"""
    if df is None or len(df) < 20:
        return None
        
    try:
        # Simple moving averages
        df['sma_fast'] = df['close'].rolling(10).mean()
        df['sma_slow'] = df['close'].rolling(20).mean()
        
        # RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_price = df['close'].iloc[-1]
        sma_fast = df['sma_fast'].iloc[-1]
        sma_slow = df['sma_slow'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Signal logic
        if sma_fast > sma_slow and current_rsi < 70:
            side = 'buy'
            entry = current_price
            sl = entry * 0.98  # 2% stop loss
            tp = entry * 1.04  # 4% take profit
        elif sma_fast < sma_slow and current_rsi > 30:
            side = 'sell'
            entry = current_price
            sl = entry * 1.02  # 2% stop loss
            tp = entry * 0.96  # 4% take profit
        else:
            return None
            
        signal = {
            'symbol': symbol,
            'side': side,
            'entry': round(entry, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'current_price': round(current_price, 5),
            'rsi': round(current_rsi, 2),
            'timestamp': datetime.now().isoformat(),
            'confidence': 75,
            'source': 'Vercel Bot'
        }
        
        return signal
        
    except Exception as e:
        print(f"Signal generation error: {e}")
        return None

@app.route('/api/status')
def status():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'Vercel Trading Bot API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/api/signal')
def get_signal():
    """Generate trading signal"""
    symbol = request.args.get('symbol', 'BTCUSD')
    
    try:
        # Get market data
        df = get_yahoo_data(symbol)
        
        if df is None:
            return jsonify({'error': f'No data available for {symbol}'})
        
        # Generate signal
        signal = generate_simple_signal(symbol, df)
        
        if signal is None:
            return jsonify({'message': f'No trading signal for {symbol} at this time'})
        
        return jsonify(signal)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/send-signal')
def send_signal():
    """Generate and send signal to Telegram"""
    symbol = request.args.get('symbol', 'BTCUSD')
    
    try:
        # Get signal
        df = get_yahoo_data(symbol)
        signal = generate_simple_signal(symbol, df)
        
        if signal is None:
            message = f"🤖 No signal for {symbol} right now"
        else:
            message = f"""🚨 NEW SIGNAL

{signal['side'].upper()} {symbol}
Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}

RSI: {signal['rsi']}
Confidence: {signal['confidence']}%
Time: {datetime.now().strftime('%H:%M:%S')}

🤖 Vercel Trading Bot"""
        
        # Send to all Telegram users
        success = send_telegram_alert_to_users(message)
        
        return jsonify({
            'success': success,
            'signal': signal,
            'message_sent': message if success else 'Failed to send Telegram alert'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for external signals"""
    try:
        data = request.json
        
        # Send webhook data to all Telegram users
        message = f"""📡 WEBHOOK SIGNAL

Symbol: {data.get('symbol', 'Unknown')}
Action: {data.get('action', 'Unknown')}
Price: {data.get('price', 'Unknown')}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        success = send_telegram_alert_to_users(message)
        
        return jsonify({'success': success, 'received': data})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/users')
def get_users():
    """Get current user list"""
    return jsonify({
        'users': TELEGRAM_USERS,
        'count': len(TELEGRAM_USERS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/add-user', methods=['POST'])
def add_user():
    """Add new user to Telegram notifications"""
    try:
        data = request.json
        chat_id = str(data.get('chat_id'))
        
        if not chat_id:
            return jsonify({'error': 'chat_id is required'})
        
        if chat_id in TELEGRAM_USERS:
            return jsonify({'message': f'User {chat_id} already exists', 'users': TELEGRAM_USERS})
        
        TELEGRAM_USERS.append(chat_id)
        
        # Send welcome message to new user
        welcome_msg = f"""👋 Welcome to Vercel Trading Bot!

🤖 You've been added to receive trading signals!

📊 You will receive:
✅ Real-time trading signals
✅ Entry, Stop Loss, Take Profit levels
✅ Market analysis updates

🎯 Supported symbols: BTCUSD, XAUUSD, US30

Happy Trading! 🚀"""
        
        send_telegram_alert_to_users(welcome_msg, [chat_id])
        
        return jsonify({
            'success': True,
            'message': f'User {chat_id} added successfully',
            'users': TELEGRAM_USERS,
            'count': len(TELEGRAM_USERS)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/test-users')
def test_users():
    """Test message to all users"""
    test_message = f"🧪 Vercel Bot Test - {datetime.now().strftime('%H:%M:%S')}"
    success = send_telegram_alert_to_users(test_message)
    
    return jsonify({
        'success': success,
        'message': 'Test sent to all users',
        'users': TELEGRAM_USERS,
        'count': len(TELEGRAM_USERS)
    })

# Main index route
@app.route('/api/index')
@app.route('/')
def index():
    """Main dashboard"""
    return jsonify({
        'title': 'Vercel Trading Bot',
        'status': 'online',
        'endpoints': {
            'status': '/api/status',
            'signal': '/api/signal?symbol=BTCUSD',
            'send_signal': '/api/send-signal?symbol=BTCUSD',
            'webhook': '/api/webhook (POST)',
            'users': '/api/users',
            'add_user': '/api/add-user (POST)',
            'test_users': '/api/test-users'
        },
        'supported_symbols': ['BTCUSD', 'XAUUSD', 'US30'],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
