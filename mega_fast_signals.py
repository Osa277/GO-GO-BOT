#!/usr/bin/env python3
"""
Mega-Fast Real-Time Signal Generator
Generates signals every 5 seconds with advanced real-time analysis
"""

import requests
import json
import random
import time
import threading
from datetime import datetime, timedelta

# Telegram settings
TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
TELEGRAM_USERS = ['5362504152']

class MegaFastSignalGenerator:
    def __init__(self):
        self.signal_count = 0
        self.running = True
        
        # Real-time price simulation
        self.prices = {
            'BTCUSD': {'price': 120000, 'trend': 1, 'momentum': 0.5},
            'XAUUSD': {'price': 3355, 'trend': -1, 'momentum': 0.3},
            'US30': {'price': 44200, 'trend': 1, 'momentum': 0.7},
            'EURUSD': {'price': 1.0485, 'trend': -1, 'momentum': 0.4},
            'GBPUSD': {'price': 1.2650, 'trend': 1, 'momentum': 0.6}
        }
        
    def send_telegram(self, message):
        """Send to Telegram with retry"""
        for chat_id in TELEGRAM_USERS:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
                response = requests.post(url, data=data, timeout=5)
                return response.status_code == 200
            except:
                return False
        return False

    def update_real_price(self, symbol):
        """Advanced real-time price simulation"""
        data = self.prices[symbol]
        
        # Price movement parameters
        moves = {
            'BTCUSD': {'base': 100, 'volatility': 0.8},
            'XAUUSD': {'base': 2, 'volatility': 0.5},
            'US30': {'base': 30, 'volatility': 0.6},
            'EURUSD': {'base': 0.0015, 'volatility': 0.4},
            'GBPUSD': {'base': 0.002, 'volatility': 0.5}
        }
        
        move_params = moves[symbol]
        
        # Trend simulation
        trend_change = random.uniform(-0.1, 0.1)
        data['trend'] = max(-1, min(1, data['trend'] + trend_change))
        
        # Momentum simulation
        data['momentum'] = max(0, min(1, data['momentum'] + random.uniform(-0.2, 0.2)))
        
        # Price calculation
        base_move = move_params['base'] * move_params['volatility']
        trend_influence = data['trend'] * base_move * 0.7
        random_move = random.uniform(-base_move, base_move) * 0.3
        momentum_boost = data['momentum'] * base_move * 0.2
        
        price_change = trend_influence + random_move + momentum_boost
        data['price'] += price_change
        
        # Additional metrics
        volatility = abs(price_change / data['price']) * 100
        rsi = 50 + (data['trend'] * 25) + random.uniform(-15, 15)
        rsi = max(10, min(90, rsi))
        
        return {
            'symbol': symbol,
            'price': data['price'],
            'change': price_change,
            'change_percent': (price_change / data['price']) * 100,
            'trend': data['trend'],
            'momentum': data['momentum'],
            'volatility': volatility,
            'rsi': rsi,
            'high': data['price'] * (1 + volatility/200),
            'low': data['price'] * (1 - volatility/200)
        }

    def generate_mega_signal(self, symbol):
        """Generate mega-fast signal with advanced analysis"""
        market_data = self.update_real_price(symbol)
        
        # Advanced signal conditions
        trend = market_data['trend']
        momentum = market_data['momentum']
        rsi = market_data['rsi']
        volatility = market_data['volatility']
        
        # Signal logic
        if volatility > 0.5 and momentum > 0.6:  # High volatility + momentum
            if trend > 0.3 and rsi < 70:
                signal_type = 'buy'
                strength = 0.85 + momentum * 0.1
            elif trend < -0.3 and rsi > 30:
                signal_type = 'sell'
                strength = 0.85 + momentum * 0.1
            else:
                if random.random() < 0.3:  # Lower probability mixed signals
                    signal_type = random.choice(['buy', 'sell'])
                    strength = 0.6 + momentum * 0.15
                else:
                    return None
        elif abs(trend) > 0.5:  # Strong trend
            if trend > 0.5:
                signal_type = 'buy'
                strength = 0.75 + abs(trend) * 0.15
            else:
                signal_type = 'sell'
                strength = 0.75 + abs(trend) * 0.15
        elif momentum > 0.7:  # High momentum
            signal_type = 'buy' if rsi < 60 else 'sell'
            strength = 0.7 + momentum * 0.2
        else:
            # Low probability signals in unclear conditions
            if random.random() < 0.2:
                signal_type = random.choice(['buy', 'sell'])
                strength = 0.5 + random.uniform(0, 0.2)
            else:
                return None
        
        # Calculate entry, SL, TP
        entry = market_data['price']
        
        if signal_type == 'buy':
            sl_percent = random.uniform(0.8, 1.8) * (1 + volatility/100)
            tp_percent = random.uniform(2.5, 5.0) * (1 + momentum)
            sl = entry * (1 - sl_percent/100)
            tp = entry * (1 + tp_percent/100)
        else:
            sl_percent = random.uniform(0.8, 1.8) * (1 + volatility/100)
            tp_percent = random.uniform(2.5, 5.0) * (1 + momentum)
            sl = entry * (1 + sl_percent/100)
            tp = entry * (1 - tp_percent/100)
        
        # Market condition
        if abs(trend) > 0.6:
            condition = 'strong_trend'
        elif momentum > 0.7:
            condition = 'breakout'
        elif volatility > 0.8:
            condition = 'volatile'
        else:
            condition = 'mixed'
        
        return {
            'symbol': symbol,
            'side': signal_type,
            'entry': round(entry, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'price': round(entry, 5),
            'change': round(market_data['change'], 4),
            'change_percent': round(market_data['change_percent'], 3),
            'rsi': round(rsi, 1),
            'confidence': int(strength * 100),
            'tp_probability': int(strength * random.uniform(0.65, 0.9) * 100),
            'condition': condition,
            'trend': round(trend, 2),
            'momentum': round(momentum, 2),
            'volatility': round(volatility, 3),
            'risk_reward': round(abs(tp - entry) / abs(sl - entry), 1),
            'strength': round(strength, 2)
        }

    def format_mega_message(self, signal):
        """Format mega-fast signal message"""
        side_emoji = "🟢🚀" if signal['side'] == 'buy' else "🔴📉"
        
        confidence_emojis = {
            90: "🔥🚀", 85: "🚀", 80: "🎯", 75: "✅", 70: "📊"
        }
        conf_emoji = next((emoji for level, emoji in confidence_emojis.items() 
                          if signal['confidence'] >= level), "⚠️")
        
        condition_emojis = {
            'strong_trend': '🌊📈',
            'breakout': '💥🚀',
            'volatile': '⚡🔥',
            'mixed': '🔄📊'
        }
        condition_emoji = condition_emojis.get(signal['condition'], '📊')
        
        change_emoji = "📈" if signal['change'] > 0 else "📉" if signal['change'] < 0 else "➡️"
        
        message = f"""⚡ 5-MINUTE #{self.signal_count} {side_emoji}

{signal['side'].upper()} {signal['symbol']} | 5M ⚡
💰 Entry: {signal['entry']}
🛑 SL: {signal['sl']}
🎯 TP: {signal['tp']}

{change_emoji} Change: {signal['change']:+.3f} ({signal['change_percent']:+.2f}%)
{conf_emoji} Confidence: {signal['confidence']}%
🎲 TP Prob: {signal['tp_probability']}%
📊 RSI: {signal['rsi']} | R/R: 1:{signal['risk_reward']}

{condition_emoji} {signal['condition'].replace('_', ' ').title()}
📈 Trend: {signal['trend']:+.1f} | ⚡ Momentum: {signal['momentum']:.1f}
🔥 Volatility: {signal['volatility']:.2f}%

⏰ {datetime.now().strftime('%H:%M:%S')} | ⚡ 5-MINUTE"""
        
        return message

    def run_mega_generator(self):
        """Run mega-fast generator - 5 minute intervals"""
        print("⚡🚀 5-MINUTE SIGNAL GENERATOR STARTING!")
        print("🎯 Signal every 5 minutes")
        print("📊 5 Symbols: BTCUSD, XAUUSD, US30, EURUSD, GBPUSD")
        print("=" * 70)
        
        symbols = list(self.prices.keys())
        
        try:
            while self.running:
                symbol = random.choice(symbols)  # Random symbol each cycle
                
                print(f"\n⚡ Analyzing {symbol}...")
                signal = self.generate_mega_signal(symbol)
                
                if signal:
                    self.signal_count += 1
                    
                    print(f"🚀 MEGA SIGNAL #{self.signal_count}!")
                    print(f"📊 {signal['side'].upper()} {symbol}")
                    print(f"💰 {signal['entry']} | 🎯 {signal['confidence']}%")
                    print(f"🔥 {signal['condition'].title()} | Trend: {signal['trend']:+.1f}")
                    
                    message = self.format_mega_message(signal)
                    if self.send_telegram(message):
                        print("📱 ✅ SENT!")
                    else:
                        print("📱 ❌ Failed")
                else:
                    print(f"⏸️ No signal for {symbol}")
                
                # 5 minute intervals
                time.sleep(300)  # 5 minutes = 300 seconds
                
        except KeyboardInterrupt:
            print(f"\n🛑 Mega Generator stopped!")
        except Exception as e:
            print(f"🚫 Error: {e}")
        finally:
            self.running = False
            print(f"📊 Total: {self.signal_count} mega signals generated!")

if __name__ == "__main__":
    generator = MegaFastSignalGenerator()
    
    # Test message
    test_msg = f"🚀 MEGA-FAST Generator Online! - {datetime.now().strftime('%H:%M:%S')}"
    
    if generator.send_telegram(test_msg):
        print("✅ Telegram ready!")
        print("🚀 Starting MEGA-FAST in 2 seconds...")
        time.sleep(2)
        generator.run_mega_generator()
    else:
        print("❌ Telegram failed!")
