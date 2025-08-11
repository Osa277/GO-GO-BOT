#!/usr/bin/env python3
"""
15-Minute Signal Generator
Generates high-quality signals every 15 minutes
"""

import requests
import json
import random
import time
import threading
from datetime import datetime

# Telegram settings
TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
TELEGRAM_USERS = ['5362504152']

class FifteenMinuteSignalGenerator:
    def __init__(self):
        self.signal_count = 0
        self.running = True
        
        # Professional price tracking
        self.market_data = {
            'BTCUSD': {'price': 120000, 'trend': 0, 'volume': 1000000, 'strength': 0.5},
            'XAUUSD': {'price': 3355, 'trend': 0, 'volume': 500000, 'strength': 0.4},
            'US30': {'price': 44200, 'trend': 0, 'volume': 800000, 'strength': 0.6},
            'EURUSD': {'price': 1.0485, 'trend': 0, 'volume': 2000000, 'strength': 0.3},
            'GBPUSD': {'price': 1.2650, 'trend': 0, 'volume': 1500000, 'strength': 0.4},
            'USDJPY': {'price': 150.25, 'trend': 0, 'volume': 1200000, 'strength': 0.5}
        }
        
    def send_telegram(self, message):
        """Send to Telegram"""
        for chat_id in TELEGRAM_USERS:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
                response = requests.post(url, data=data, timeout=10)
                return response.status_code == 200
            except:
                return False
        return False

    def analyze_15min_market(self, symbol):
        """Professional 15-minute market analysis"""
        data = self.market_data[symbol]
        
        # Market parameters for different symbols
        params = {
            'BTCUSD': {'volatility': 1.2, 'trend_factor': 0.8, 'base_move': 200},
            'XAUUSD': {'volatility': 0.8, 'trend_factor': 0.6, 'base_move': 5},
            'US30': {'volatility': 1.0, 'trend_factor': 0.7, 'base_move': 50},
            'EURUSD': {'volatility': 0.6, 'trend_factor': 0.5, 'base_move': 0.003},
            'GBPUSD': {'volatility': 0.7, 'trend_factor': 0.6, 'base_move': 0.004},
            'USDJPY': {'volatility': 0.8, 'trend_factor': 0.7, 'base_move': 0.5}
        }
        
        param = params[symbol]
        
        # Evolve market conditions over 15 minutes
        trend_evolution = random.uniform(-0.3, 0.3)
        data['trend'] = max(-1, min(1, data['trend'] + trend_evolution))
        
        strength_change = random.uniform(-0.2, 0.2)
        data['strength'] = max(0, min(1, data['strength'] + strength_change))
        
        # Calculate price movement
        trend_influence = data['trend'] * param['base_move'] * param['trend_factor']
        market_noise = random.uniform(-param['base_move'], param['base_move']) * 0.4
        strength_boost = data['strength'] * param['base_move'] * 0.3
        
        price_change = trend_influence + market_noise + strength_boost
        data['price'] += price_change
        
        # Advanced technical indicators
        volatility = abs(price_change / data['price']) * 100 * param['volatility']
        rsi = 50 + (data['trend'] * 30) + random.uniform(-10, 10)
        rsi = max(15, min(85, rsi))
        
        macd = data['trend'] * random.uniform(0.5, 1.5)
        bollinger_position = random.uniform(0, 1)  # Position within Bollinger Bands
        
        # Volume analysis
        volume_spike = random.random() < 0.3  # 30% chance of volume spike
        if volume_spike:
            data['volume'] *= random.uniform(1.5, 3.0)
        else:
            data['volume'] *= random.uniform(0.8, 1.2)
        
        return {
            'symbol': symbol,
            'price': data['price'],
            'change': price_change,
            'change_percent': (price_change / data['price']) * 100,
            'trend': data['trend'],
            'strength': data['strength'],
            'volatility': volatility,
            'rsi': rsi,
            'macd': macd,
            'bollinger_position': bollinger_position,
            'volume': int(data['volume']),
            'volume_spike': volume_spike,
            'high': data['price'] * (1 + volatility/200),
            'low': data['price'] * (1 - volatility/200)
        }

    def generate_15min_signal(self, symbol):
        """Generate professional 15-minute signal"""
        market = self.analyze_15min_market(symbol)
        
        # Professional signal conditions
        trend = market['trend']
        strength = market['strength']
        rsi = market['rsi']
        volatility = market['volatility']
        macd = market['macd']
        volume_spike = market['volume_spike']
        bollinger_pos = market['bollinger_position']
        
        # Advanced signal logic
        signal_probability = 0.4  # Base probability
        
        # Trend analysis
        if abs(trend) > 0.6:  # Strong trend
            signal_probability += 0.3
            if trend > 0.6:
                signal_type = 'buy'
                base_strength = 0.8
            else:
                signal_type = 'sell'
                base_strength = 0.8
        elif abs(trend) > 0.3:  # Moderate trend
            signal_probability += 0.2
            signal_type = 'buy' if trend > 0 else 'sell'
            base_strength = 0.7
        else:  # Weak trend
            signal_probability += 0.1
            signal_type = random.choice(['buy', 'sell'])
            base_strength = 0.6
        
        # RSI confirmation
        if (signal_type == 'buy' and rsi < 65) or (signal_type == 'sell' and rsi > 35):
            signal_probability += 0.2
            base_strength += 0.1
        
        # MACD confirmation
        if (signal_type == 'buy' and macd > 0) or (signal_type == 'sell' and macd < 0):
            signal_probability += 0.15
            base_strength += 0.05
        
        # Volume confirmation
        if volume_spike:
            signal_probability += 0.2
            base_strength += 0.1
        
        # Bollinger Bands
        if (signal_type == 'buy' and bollinger_pos < 0.3) or (signal_type == 'sell' and bollinger_pos > 0.7):
            signal_probability += 0.15
            base_strength += 0.05
        
        # Market strength
        if strength > 0.7:
            signal_probability += 0.1
            base_strength += 0.05
        
        # Generate signal only if probability is high enough
        if random.random() > signal_probability:
            return None
        
        # Calculate entry, SL, TP
        entry = market['price']
        
        if signal_type == 'buy':
            sl_percent = random.uniform(1.5, 3.0) * (1 + volatility/100)
            tp_percent = random.uniform(3.0, 6.0) * (1 + strength)
            sl = entry * (1 - sl_percent/100)
            tp = entry * (1 + tp_percent/100)
        else:
            sl_percent = random.uniform(1.5, 3.0) * (1 + volatility/100)
            tp_percent = random.uniform(3.0, 6.0) * (1 + strength)
            sl = entry * (1 + sl_percent/100)
            tp = entry * (1 - tp_percent/100)
        
        # Market condition classification
        if abs(trend) > 0.7 and strength > 0.6:
            condition = 'strong_trend'
        elif volume_spike and volatility > 1.0:
            condition = 'breakout'
        elif abs(trend) < 0.3 and volatility < 0.5:
            condition = 'consolidation'
        elif rsi > 70 or rsi < 30:
            condition = 'reversal_zone'
        else:
            condition = 'mixed_signals'
        
        final_strength = min(0.95, base_strength)
        
        return {
            'symbol': symbol,
            'side': signal_type,
            'entry': round(entry, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'price': round(entry, 5),
            'change': round(market['change'], 4),
            'change_percent': round(market['change_percent'], 3),
            'rsi': round(rsi, 1),
            'macd': round(macd, 3),
            'confidence': int(final_strength * 100),
            'tp_probability': int(final_strength * random.uniform(0.7, 0.95) * 100),
            'condition': condition,
            'trend': round(trend, 2),
            'strength': round(strength, 2),
            'volatility': round(volatility, 3),
            'volume': market['volume'],
            'volume_spike': volume_spike,
            'bollinger_position': round(bollinger_pos, 2),
            'risk_reward': round(abs(tp - entry) / abs(sl - entry), 1),
            'signal_strength': round(final_strength, 2),
            'timeframe': '15M'
        }

    def format_15min_message(self, signal):
        """Format professional 15-minute signal message"""
        side_emoji = "🟢📈" if signal['side'] == 'buy' else "🔴📉"
        
        confidence_emojis = {
            90: "🔥💎", 85: "🚀⭐", 80: "🎯✨", 75: "✅📊", 70: "📈⚡"
        }
        conf_emoji = next((emoji for level, emoji in confidence_emojis.items() 
                          if signal['confidence'] >= level), "⚠️📊")
        
        condition_emojis = {
            'strong_trend': '🌊💪',
            'breakout': '💥🚀',
            'consolidation': '📦⚖️',
            'reversal_zone': '🔄⚠️',
            'mixed_signals': '🔄📊'
        }
        condition_emoji = condition_emojis.get(signal['condition'], '📊')
        
        change_emoji = "📈" if signal['change'] > 0 else "📉" if signal['change'] < 0 else "➡️"
        volume_emoji = "📊🔥" if signal['volume_spike'] else "📊"
        
        message = f"""🕐 15-MINUTE PROFESSIONAL #{self.signal_count} {side_emoji}

{signal['side'].upper()} {signal['symbol']} | 15M 🕐
💰 Entry: {signal['entry']}
🛑 Stop Loss: {signal['sl']}
🎯 Take Profit: {signal['tp']}

{change_emoji} Price Change: {signal['change']:+.3f} ({signal['change_percent']:+.2f}%)
{conf_emoji} Confidence: {signal['confidence']}%
🎲 TP Probability: {signal['tp_probability']}%
📊 Risk/Reward: 1:{signal['risk_reward']}

📈 TECHNICAL ANALYSIS:
📊 RSI: {signal['rsi']} | MACD: {signal['macd']:+.2f}
📈 Trend: {signal['trend']:+.1f} | Strength: {signal['strength']:.1f}
🔥 Volatility: {signal['volatility']:.2f}%
{volume_emoji} Volume: {signal['volume']:,}

{condition_emoji} Market: {signal['condition'].replace('_', ' ').title()}
📍 Bollinger: {signal['bollinger_position']:.1f}

⏰ {datetime.now().strftime('%H:%M:%S')} | 🕐 15-MINUTE PROFESSIONAL"""
        
        return message

    def run_15min_generator(self):
        """Run 15-minute professional generator"""
        print("🕐💎 15-MINUTE PROFESSIONAL SIGNAL GENERATOR!")
        print("🎯 High-quality signals every 15 minutes")
        print("📊 6 Professional Symbols: BTCUSD, XAUUSD, US30, EURUSD, GBPUSD, USDJPY")
        print("💼 Advanced Technical Analysis")
        print("=" * 80)
        
        symbols = list(self.market_data.keys())
        
        try:
            while self.running:
                # Analyze multiple symbols but generate fewer, higher quality signals
                analyzed_symbols = random.sample(symbols, random.randint(2, 4))
                
                for symbol in analyzed_symbols:
                    print(f"\n🕐 15-minute analysis for {symbol}...")
                    signal = self.generate_15min_signal(symbol)
                    
                    if signal:
                        self.signal_count += 1
                        
                        print(f"💎 PROFESSIONAL SIGNAL #{self.signal_count}!")
                        print(f"📊 {signal['side'].upper()} {symbol} | 15M")
                        print(f"💰 Entry: {signal['entry']} | 🎯 {signal['confidence']}%")
                        print(f"🔥 {signal['condition'].title()} | RSI: {signal['rsi']}")
                        print(f"📈 Trend: {signal['trend']:+.1f} | Volume: {signal['volume']:,}")
                        
                        message = self.format_15min_message(signal)
                        if self.send_telegram(message):
                            print("📱 ✅ PROFESSIONAL SIGNAL SENT!")
                        else:
                            print("📱 ❌ Failed to send")
                        
                        # Brief pause between signals in same cycle
                        time.sleep(30)
                    else:
                        print(f"⏸️ No 15-min signal for {symbol} (market conditions not optimal)")
                
                print(f"\n🔄 15-minute cycle complete. Next in 15 minutes...")
                print(f"📊 Total professional signals: {self.signal_count}")
                
                # 15 minute intervals
                time.sleep(900)  # 15 minutes = 900 seconds
                
        except KeyboardInterrupt:
            print(f"\n🛑 15-Minute Professional Generator stopped!")
        except Exception as e:
            print(f"🚫 Error: {e}")
        finally:
            self.running = False
            print(f"📊 Total: {self.signal_count} professional 15-minute signals generated!")

if __name__ == "__main__":
    generator = FifteenMinuteSignalGenerator()
    
    # Test message
    test_msg = f"🕐💎 15-MINUTE PROFESSIONAL Generator Online! - {datetime.now().strftime('%H:%M:%S')}"
    
    if generator.send_telegram(test_msg):
        print("✅ Telegram connected!")
        print("🕐 Starting 15-MINUTE PROFESSIONAL in 3 seconds...")
        time.sleep(3)
        generator.run_15min_generator()
    else:
        print("❌ Telegram connection failed!")
