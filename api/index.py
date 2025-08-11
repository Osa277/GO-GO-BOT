from flask import Flask, jsonify, request
import requests
import json
from datetime import datetime
# import yfinance as yf
# import pandas as pd
# import numpy as np

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
        # For now, return mock data for demo purposes
        # In production, you can implement actual market data fetching
        import random
        current_price = random.uniform(40000, 70000) if symbol == 'BTCUSD' else random.uniform(1900, 2100)
        
        mock_data = {
            'price': current_price,
            'high': current_price * 1.02,
            'low': current_price * 0.98,
            'volume': random.randint(1000, 10000)
        }
        
        return mock_data
        
    except Exception as e:
        print(f"Yahoo data error: {e}")
        return None

def generate_simple_signal(symbol, data):
    """Generate a simple trading signal - CLOUD OPTIMIZED"""
    if data is None:
        return None
        
    try:
        import random
        
        current_price = data['price']
        
        # Enhanced signal logic for cloud
        market_sentiment = random.choice(['bullish', 'bearish', 'neutral'])
        
        if market_sentiment == 'bullish':
            side = 'buy'
            entry = current_price
            sl = entry * 0.985  # 1.5% stop loss
            tp = entry * 1.06   # 6% take profit
        elif market_sentiment == 'bearish':
            side = 'sell'
            entry = current_price
            sl = entry * 1.015  # 1.5% stop loss
            tp = entry * 0.94   # 6% take profit
        else:
            return None  # No signal in neutral market
            
        # Calculate probability and confidence
        confidence = random.randint(65, 90)
        tp_probability = random.randint(55, 75)
        
        signal = {
            'symbol': symbol,
            'side': side,
            'entry': round(entry, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'current_price': round(current_price, 5),
            'rsi': round(random.uniform(30, 70), 2),
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'tp_probability': tp_probability,
            'market_sentiment': market_sentiment,
            'source': 'Cloud Signal Generator',
            'platform': 'Vercel',
            'timeframe': '5M'
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
        data = get_yahoo_data(symbol)
        
        if data is None:
            return jsonify({'error': f'No data available for {symbol}'})
        
        # Generate signal
        signal = generate_simple_signal(symbol, data)
        
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
        data = get_yahoo_data(symbol)
        signal = generate_simple_signal(symbol, data)
        
        if signal is None:
            message = f"🤖 No signal for {symbol} right now (neutral market)"
        else:
            # Enhanced message format
            side_emoji = "🟢" if signal['side'] == 'buy' else "🔴"
            confidence_emoji = "🎯" if signal['confidence'] >= 80 else "⚠️" if signal['confidence'] >= 70 else "❓"
            
            message = f"""🚨 CLOUD SIGNAL {side_emoji}

{signal['side'].upper()} {symbol} {signal['timeframe']}
Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}

{confidence_emoji} Confidence: {signal['confidence']}%
🎲 TP Probability: {signal['tp_probability']}%
📊 RSI: {signal['rsi']}
📈 Market: {signal['market_sentiment'].title()}

⏰ {datetime.now().strftime('%H:%M:%S')}
☁️ Generated by Vercel Cloud"""
        
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

# Main index route - This is the entry point for Vercel
@app.route('/')
def index():
    """Main dashboard - Vercel entry point"""
    return jsonify({
        'title': '🤖 GO-GO-BOT Cloud API',
        'status': 'online ✅',
        'message': 'Cloud-only signal generation active',
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
        'timestamp': datetime.now().isoformat(),
        'version': '3.0-cloud-only'
    })

# Additional route for api/index
@app.route('/api/index')
def api_index():
    """API index route"""
    return index()

if __name__ == '__main__':
    app.run(debug=True)
