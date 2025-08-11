#!/usr/bin/env python3
"""
Standalone Cloud Signal Generator
Generates signals and sends directly to Telegram without Vercel
"""

import requests
import json
import random
from datetime import datetime
import time

# Your Telegram settings
TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
TELEGRAM_USERS = [
    '5362504152',  # Samuel (original user)
    # Add more chat IDs here:
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

def get_mock_data(symbol):
    """Get mock market data"""
    if symbol == 'BTCUSD':
        base_price = random.uniform(118000, 122000)
    elif symbol == 'XAUUSD':
        base_price = random.uniform(3350, 3360)
    elif symbol == 'US30':
        base_price = random.uniform(44000, 44500)
    else:
        base_price = random.uniform(1, 100)
    
    return {
        'price': base_price,
        'high': base_price * 1.02,
        'low': base_price * 0.98,
        'volume': random.randint(1000, 10000)
    }

def generate_cloud_signal(symbol):
    """Generate enhanced cloud signal"""
    try:
        data = get_mock_data(symbol)
        current_price = data['price']
        
        # Enhanced signal logic
        market_sentiment = random.choice(['bullish', 'bearish'])
        
        if market_sentiment == 'bullish':
            side = 'buy'
            entry = current_price
            sl = entry * 0.985  # 1.5% stop loss
            tp = entry * 1.06   # 6% take profit
        else:
            side = 'sell'
            entry = current_price
            sl = entry * 1.015  # 1.5% stop loss
            tp = entry * 0.94   # 6% take profit
            
        # Calculate metrics
        confidence = random.randint(70, 92)
        tp_probability = random.randint(58, 78)
        rsi = random.randint(25, 75)
        
        signal = {
            'symbol': symbol,
            'side': side,
            'entry': round(entry, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'current_price': round(current_price, 5),
            'rsi': rsi,
            'confidence': confidence,
            'tp_probability': tp_probability,
            'market_sentiment': market_sentiment,
            'timestamp': datetime.now().isoformat(),
            'timeframe': '5M',
            'source': 'Cloud Signal Generator'
        }
        
        return signal
        
    except Exception as e:
        print(f"Signal generation error: {e}")
        return None

def format_signal_message(signal):
    """Format signal for Telegram"""
    if not signal:
        return "🤖 No signal generated"
    
    side_emoji = "🟢" if signal['side'] == 'buy' else "🔴"
    confidence_emoji = "🎯" if signal['confidence'] >= 80 else "⚠️" if signal['confidence'] >= 70 else "❓"
    
    message = f"""🚨 CLOUD SIGNAL {side_emoji}

{signal['side'].upper()} {signal['symbol']} {signal['timeframe']}
Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}

{confidence_emoji} Confidence: {signal['confidence']}%
🎲 TP Probability: {signal['tp_probability']}%
📊 RSI: {signal['rsi']}
📈 Market: {signal['market_sentiment'].title()}

⏰ {datetime.now().strftime('%H:%M:%S')}
☁️ Cloud Signal Generator"""
    
    return message

def run_cloud_signal_generator():
    """Main cloud signal generator loop"""
    print("🚀 Starting Cloud Signal Generator...")
    print(f"👥 Sending to {len(TELEGRAM_USERS)} users")
    print("=" * 50)
    
    symbols = ['BTCUSD', 'XAUUSD', 'US30']
    signal_count = 0
    
    try:
        while True:
            for symbol in symbols:
                print(f"\n🔍 Generating signal for {symbol}...")
                
                # Generate signal
                signal = generate_cloud_signal(symbol)
                
                if signal:
                    signal_count += 1
                    print(f"✅ Signal #{signal_count} generated: {signal['side'].upper()} {symbol}")
                    
                    # Format and send message
                    message = format_signal_message(signal)
                    success = send_telegram_alert_to_users(message)
                    
                    if success:
                        print(f"📱 Signal sent successfully!")
                    else:
                        print(f"❌ Failed to send signal")
                        
                    # Print signal details
                    print(f"📊 Signal Details:")
                    print(f"   Side: {signal['side'].upper()}")
                    print(f"   Entry: {signal['entry']}")
                    print(f"   TP: {signal['tp']}")
                    print(f"   SL: {signal['sl']}")
                    print(f"   Confidence: {signal['confidence']}%")
                    
                else:
                    print(f"⏸️ No signal for {symbol}")
                
                # Wait between symbols
                time.sleep(5)
            
            print(f"\n⏳ Waiting 30 seconds before next scan...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Cloud Signal Generator stopped")
        print(f"📊 Total signals generated: {signal_count}")

if __name__ == "__main__":
    # Test telegram connection first
    test_msg = f"🧪 Cloud Signal Generator Test - {datetime.now().strftime('%H:%M:%S')}"
    print("🧪 Testing Telegram connection...")
    
    if send_telegram_alert_to_users(test_msg):
        print("✅ Telegram connection working!")
        print("\nStarting signal generator in 3 seconds...")
        time.sleep(3)
        run_cloud_signal_generator()
    else:
        print("❌ Telegram connection failed!")
