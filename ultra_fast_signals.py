#!/usr/bin/env python3
"""
Ultra-Fast Real-Time Signal Generator
Generates signals every 10 seconds with real-time market simulation
"""

import requests
import json
import random
import time
import threading
from datetime import datetime

# Your Telegram settings
TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
TELEGRAM_USERS = [
    '5362504152',  # Samuel (original user)
]

class UltraFastSignalGenerator:
    def __init__(self):
        self.is_running = False
        self.signal_count = 0
        self.last_prices = {
            'BTCUSD': 120000,
            'XAUUSD': 3355,
            'US30': 44200
        }
        
    def send_telegram_alert_to_users(self, message, chat_ids=None):
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
                response = requests.post(url, data=data, timeout=5)
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ Message sent to {chat_id}")
                else:
                    print(f"❌ Failed to send to {chat_id}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error sending to {chat_id}: {str(e)}")
        
        return success_count > 0

    def simulate_real_price_movement(self, symbol):
        """Simulate realistic price movements"""
        last_price = self.last_prices[symbol]
        
        # Simulate realistic price movements
        if symbol == 'BTCUSD':
            max_move = 500  # Max $500 movement
        elif symbol == 'XAUUSD':
            max_move = 5    # Max $5 movement
        elif symbol == 'US30':
            max_move = 100  # Max 100 points movement
        
        # Random walk with trend bias
        price_change = random.uniform(-max_move, max_move)
        new_price = last_price + price_change
        
        # Update last price
        self.last_prices[symbol] = new_price
        
        return {
            'price': new_price,
            'change': price_change,
            'change_percent': (price_change / last_price) * 100,
            'high': new_price * 1.005,
            'low': new_price * 0.995,
            'volume': random.randint(50000, 200000),
            'volatility': abs(price_change / last_price) * 100
        }

    def generate_ultra_fast_signal(self, symbol):
        """Generate ultra-fast real-time signal"""
        try:
            market_data = self.simulate_real_price_movement(symbol)
            current_price = market_data['price']
            volatility = market_data['volatility']
            
            # Real-time market conditions
            market_conditions = ['bullish_breakout', 'bearish_breakout', 'range_bound', 'trending']
            market_condition = random.choice(market_conditions)
            
            # Advanced signal logic
            if market_condition == 'bullish_breakout':
                side = 'buy'
                entry = current_price
                sl = entry * (1 - random.uniform(0.01, 0.02))
                tp = entry * (1 + random.uniform(0.03, 0.06))
                signal_strength = random.uniform(0.8, 0.95)
            elif market_condition == 'bearish_breakout':
                side = 'sell'
                entry = current_price
                sl = entry * (1 + random.uniform(0.01, 0.02))
                tp = entry * (1 - random.uniform(0.03, 0.06))
                signal_strength = random.uniform(0.8, 0.95)
            elif market_condition == 'trending':
                side = random.choice(['buy', 'sell'])
                entry = current_price
                if side == 'buy':
                    sl = entry * (1 - random.uniform(0.015, 0.025))
                    tp = entry * (1 + random.uniform(0.04, 0.07))
                else:
                    sl = entry * (1 + random.uniform(0.015, 0.025))
                    tp = entry * (1 - random.uniform(0.04, 0.07))
                signal_strength = random.uniform(0.7, 0.85)
            else:  # range_bound
                if random.random() < 0.4:  # Lower probability in ranging market
                    side = random.choice(['buy', 'sell'])
                    entry = current_price
                    if side == 'buy':
                        sl = entry * (1 - random.uniform(0.01, 0.015))
                        tp = entry * (1 + random.uniform(0.02, 0.04))
                    else:
                        sl = entry * (1 + random.uniform(0.01, 0.015))
                        tp = entry * (1 - random.uniform(0.02, 0.04))
                    signal_strength = random.uniform(0.5, 0.7)
                else:
                    return None
            
            # Calculate metrics
            rsi = random.uniform(20, 80)
            confidence = int(signal_strength * 100)
            tp_probability = int(signal_strength * random.uniform(0.6, 0.9) * 100)
            risk_reward = abs(tp - entry) / abs(sl - entry)
            
            signal = {
                'symbol': symbol,
                'side': side,
                'entry': round(entry, 5),
                'sl': round(sl, 5),
                'tp': round(tp, 5),
                'current_price': round(current_price, 5),
                'price_change': round(market_data['change'], 2),
                'change_percent': round(market_data['change_percent'], 3),
                'rsi': round(rsi, 1),
                'confidence': confidence,
                'tp_probability': tp_probability,
                'market_condition': market_condition,
                'volatility': round(volatility, 3),
                'risk_reward': round(risk_reward, 1),
                'signal_strength': round(signal_strength, 2),
                'timestamp': datetime.now().isoformat(),
                'timeframe': '3M',
                'source': 'Ultra-Fast Generator'
            }
            
            return signal
            
        except Exception as e:
            print(f"Signal generation error: {e}")
            return None

    def format_ultra_fast_message(self, signal):
        """Format ultra-fast signal message"""
        if not signal:
            return None
            
        side_emoji = "🟢" if signal['side'] == 'buy' else "🔴"
        confidence_emoji = "🚀" if signal['confidence'] >= 85 else "🎯" if signal['confidence'] >= 75 else "⚠️"
        
        change_emoji = "📈" if signal['price_change'] > 0 else "📉" if signal['price_change'] < 0 else "➡️"
        
        condition_emojis = {
            'bullish_breakout': '🚀📈',
            'bearish_breakout': '🔻📉', 
            'trending': '📊📈',
            'range_bound': '🔄📊'
        }
        condition_emoji = condition_emojis.get(signal['market_condition'], '📊')
        
        message = f"""⚡ 3-MINUTE SIGNAL #{self.signal_count} {side_emoji}

{signal['side'].upper()} {signal['symbol']} {signal['timeframe']}
Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}

{change_emoji} Price Change: {signal['price_change']:+.2f} ({signal['change_percent']:+.2f}%)
{confidence_emoji} Confidence: {signal['confidence']}%
🎲 TP Probability: {signal['tp_probability']}%
📊 RSI: {signal['rsi']}
{condition_emoji} Market: {signal['market_condition'].replace('_', ' ').title()}
⚖️ R/R: 1:{signal['risk_reward']}

⏰ {datetime.now().strftime('%H:%M:%S')}
⚡ 3-Minute Signal"""
        
        return message

    def run_ultra_fast_generator(self):
        """Run ultra-fast signal generation"""
        print("⚡ Starting 3-Minute Signal Generator...")
        print("🎯 Generating signals every 3 minutes")
        print("📊 Symbols: BTCUSD, XAUUSD, US30")
        print("=" * 60)
        
        self.is_running = True
        symbols = ['BTCUSD', 'XAUUSD', 'US30']
        
        try:
            while self.is_running:
                for symbol in symbols:
                    if not self.is_running:
                        break
                        
                    print(f"\n⚡ Generating ultra-fast signal for {symbol}...")
                    signal = self.generate_ultra_fast_signal(symbol)
                    
                    if signal:
                        self.signal_count += 1
                        
                        print(f"✅ Signal #{self.signal_count} Generated!")
                        print(f"📊 {signal['side'].upper()} {symbol}")
                        print(f"💰 Entry: {signal['entry']}")
                        print(f"📈 Change: {signal['price_change']:+.2f} ({signal['change_percent']:+.2f}%)")
                        print(f"🎯 Confidence: {signal['confidence']}% | TP Prob: {signal['tp_probability']}%")
                        print(f"🔥 Market: {signal['market_condition'].replace('_', ' ').title()}")
                        
                        # Format and send message
                        message = self.format_ultra_fast_message(signal)
                        if message:
                            success = self.send_telegram_alert_to_users(message)
                            if success:
                                print("📱 ✅ Sent to Telegram!")
                            else:
                                print("📱 ❌ Failed to send to Telegram")
                        
                    else:
                        print(f"⏸️ No signal for {symbol} (market conditions)")
                    
                    # 3-minute interval 
                    if self.is_running:
                        time.sleep(180)  # 3 minutes = 180 seconds
                
                print(f"\n🔄 Completed cycle. Total signals: {self.signal_count}")
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Ultra-Fast Generator stopped by user")
        except Exception as e:
            print(f"\n🚫 Error in ultra-fast generator: {e}")
        finally:
            self.is_running = False
            print(f"📊 Final Stats: {self.signal_count} signals generated")

if __name__ == "__main__":
    # Test telegram connection first
    generator = UltraFastSignalGenerator()
    
    print("🧪 Testing Telegram connection...")
    test_msg = f"⚡ Ultra-Fast Signal Generator Starting - {datetime.now().strftime('%H:%M:%S')}"
    
    if generator.send_telegram_alert_to_users(test_msg):
        print("✅ Telegram connection working!")
        print("\n🚀 Starting ultra-fast generator in 3 seconds...")
        time.sleep(3)
        generator.run_ultra_fast_generator()
    else:
        print("❌ Telegram connection failed!")
        print("💡 Check your TELEGRAM_TOKEN and chat IDs")
