#!/usr/bin/env python3
"""
Pre-Signal Alert System
Advanced system that analyzes market conditions and sends alerts 1 minute before signal execution
"""

import json
import logging
import time
from datetime import datetime, timedelta
from telegram_utils import send_telegram_message
from mt5_data import get_current_price, fetch_market_data, initialize_mt5, shutdown_mt5
import numpy as np

logger = logging.getLogger(__name__)

class PreSignalAlertSystem:
    def __init__(self):
        self.alert_buffer_seconds = 60  # 1 minute alert before signal
        self.monitoring_symbols = ['BTCUSD', 'ETHUSD', 'XAUUSD']
        self.market_conditions = {}
        self.pending_alerts = []
        self.last_analysis = {}
        
        # Signal formation thresholds
        self.signal_formation_criteria = {
            'price_movement_threshold': 0.002,  # 0.2% price movement
            'volume_spike_threshold': 1.5,     # 1.5x normal volume
            'volatility_threshold': 0.015,     # 1.5% volatility
            'trend_strength_threshold': 0.7    # 70% trend strength
        }
    
    def analyze_pre_signal_conditions(self, symbol, timeframe='M3'):
        """Analyze market conditions that typically precede signal generation"""
        try:
            # Convert timeframe to minutes
            tf_minutes = 3 if timeframe == 'M3' else 5 if timeframe == 'M5' else 15 if timeframe == 'M15' else 3
            
            # Get market data
            bars = fetch_market_data(symbol, tf_minutes, 20)
            if bars is None or len(bars) < 10:
                return None
            
            current_price = get_current_price(symbol)
            if current_price is None:
                return None
            
            # Calculate technical indicators
            prices = bars['close'].values
            highs = bars['high'].values
            lows = bars['low'].values
            volumes = bars['tick_volume'].values if 'tick_volume' in bars.columns else None
            
            # Price momentum analysis
            price_change = (current_price - prices[-5]) / prices[-5]
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-10:])
            ma_divergence = (short_ma - long_ma) / long_ma
            
            # Volatility analysis
            volatility = np.std(prices[-10:]) / np.mean(prices[-10:])
            
            # Support/Resistance analysis
            recent_high = np.max(highs[-10:])
            recent_low = np.min(lows[-10:])
            price_position = (current_price - recent_low) / (recent_high - recent_low)
            
            # Volume analysis (if available)
            volume_ratio = 1.0
            if volumes is not None and len(volumes) > 5:
                recent_volume = np.mean(volumes[-3:])
                avg_volume = np.mean(volumes[-10:])
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate signal probability
            signal_probability = self.calculate_signal_formation_probability(
                price_change, ma_divergence, volatility, price_position, volume_ratio
            )
            
            conditions = {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'price_change_5m': round(price_change * 100, 3),
                'ma_divergence': round(ma_divergence * 100, 3),
                'volatility': round(volatility * 100, 2),
                'price_position': round(price_position * 100, 1),
                'volume_ratio': round(volume_ratio, 2),
                'signal_probability': round(signal_probability * 100, 1),
                'timestamp': datetime.now().isoformat(),
                'alert_level': self.get_alert_level(signal_probability)
            }
            
            return conditions
            
        except Exception as e:
            logger.error(f"Error analyzing pre-signal conditions for {symbol}: {e}")
            return None
    
    def calculate_signal_formation_probability(self, price_change, ma_divergence, 
                                            volatility, price_position, volume_ratio):
        """Calculate probability of signal formation in next 1-2 minutes"""
        probability = 0.0
        
        # Strong price momentum indicates potential signal
        if abs(price_change) > self.signal_formation_criteria['price_movement_threshold']:
            probability += 0.25
        
        # MA divergence suggests trend formation
        if abs(ma_divergence) > 0.005:  # 0.5% MA divergence
            probability += 0.20
        
        # High volatility creates signal opportunities
        if volatility > self.signal_formation_criteria['volatility_threshold']:
            probability += 0.20
        
        # Price near support/resistance levels
        if price_position < 0.2 or price_position > 0.8:
            probability += 0.15
        
        # Volume spike indicates increased interest
        if volume_ratio > self.signal_formation_criteria['volume_spike_threshold']:
            probability += 0.20
        
        return min(probability, 1.0)  # Cap at 100%
    
    def get_alert_level(self, probability):
        """Determine alert level based on signal formation probability"""
        if probability >= 0.8:
            return "🔴 HIGH"
        elif probability >= 0.6:
            return "🟡 MEDIUM"
        elif probability >= 0.4:
            return "🟢 LOW"
        else:
            return "⚪ MINIMAL"
    
    def should_send_alert(self, conditions):
        """Determine if alert should be sent based on conditions"""
        if conditions is None:
            return False
        
        symbol = conditions['symbol']
        probability = conditions['signal_probability']
        
        # Send alert if probability is above 60%
        if probability >= 60:
            # Check if we already sent alert for this symbol recently
            if symbol in self.last_analysis:
                last_alert_time = datetime.fromisoformat(self.last_analysis[symbol].get('timestamp', '2000-01-01T00:00:00'))
                if datetime.now() - last_alert_time < timedelta(minutes=5):
                    return False  # Don't spam alerts
            
            return True
        
        return False
    
    def format_pre_signal_alert(self, conditions):
        """Format the pre-signal alert message"""
        symbol = conditions['symbol']
        probability = conditions['signal_probability']
        alert_level = conditions['alert_level']
        price = conditions['current_price']
        
        # Determine likely signal direction
        price_change = conditions['price_change_5m']
        ma_divergence = conditions['ma_divergence']
        
        likely_direction = "📈 BULLISH" if (price_change > 0 and ma_divergence > 0) else "📉 BEARISH"
        
        alert_message = f"""
🚨 PRE-SIGNAL ALERT {alert_level}

🎯 {symbol} @ ${price:,.2f}
⏰ Signal Expected: ~1 minute
🎲 Formation Probability: {probability}%
📊 Likely Direction: {likely_direction}

📈 MARKET CONDITIONS:
   • Price Change (5m): {conditions['price_change_5m']:+.2f}%
   • MA Divergence: {conditions['ma_divergence']:+.2f}%
   • Volatility: {conditions['volatility']}%
   • Price Position: {conditions['price_position']}%
   • Volume Ratio: {conditions['volume_ratio']}x

⚡ PREPARE FOR SIGNAL EXECUTION
🔔 Monitor your Telegram for incoming signal!

Time: {datetime.now().strftime('%H:%M:%S')}
"""
        return alert_message.strip()
    
    def send_pre_signal_alert(self, conditions):
        """Send pre-signal alert via Telegram"""
        try:
            alert_message = self.format_pre_signal_alert(conditions)
            
            # Send to Telegram
            success = send_telegram_message(alert_message)
            
            if success:
                logger.info(f"✅ Pre-signal alert sent for {conditions['symbol']} - {conditions['signal_probability']}% probability")
                
                # Update last analysis
                self.last_analysis[conditions['symbol']] = conditions
                
                return True
            else:
                logger.error(f"❌ Failed to send pre-signal alert for {conditions['symbol']}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending pre-signal alert: {e}")
            return False
    
    def check_pre_signal_conditions(self, symbol):
        """Check pre-signal conditions for a specific symbol (for integration with main scanner)"""
        try:
            # Only check if symbol is in monitoring list
            if symbol not in self.monitoring_symbols:
                return
                
            # Analyze current market conditions
            conditions = self.analyze_pre_signal_conditions(symbol)
            
            if conditions and self.should_send_alert(conditions):
                self.send_pre_signal_alert(conditions)
                
        except Exception as e:
            logger.error(f"Error checking pre-signal conditions for {symbol}: {e}")
    
    def monitor_pre_signal_conditions(self):
        """Main monitoring loop for pre-signal conditions"""
        logger.info("🔍 Starting Pre-Signal Alert Monitoring...")
        
        while True:
            try:
                for symbol in self.monitoring_symbols:
                    # Analyze current market conditions
                    conditions = self.analyze_pre_signal_conditions(symbol)
                    
                    if conditions and self.should_send_alert(conditions):
                        self.send_pre_signal_alert(conditions)
                
                # Wait 30 seconds before next analysis
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Pre-Signal Alert Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in pre-signal monitoring: {e}")
                time.sleep(10)  # Brief pause on error
    
    def start_monitoring(self):
        """Start the pre-signal alert monitoring system"""
        try:
            # Initialize MT5 connection
            if not initialize_mt5():
                logger.error("❌ Failed to initialize MT5 for pre-signal alerts")
                return
            
            logger.info("🚀 Pre-Signal Alert System Started")
            logger.info(f"📊 Monitoring: {', '.join(self.monitoring_symbols)}")
            logger.info(f"⏰ Alert Buffer: {self.alert_buffer_seconds} seconds")
            
            # Send startup notification
            startup_message = f"""
🚀 PRE-SIGNAL ALERT SYSTEM ACTIVATED

📊 Monitoring: {', '.join(self.monitoring_symbols)}
⏰ Alert Timing: 1 minute before signal
🎯 Probability Threshold: 60%+

You will now receive advance warnings before signals are generated!
"""
            send_telegram_message(startup_message.strip())
            
            # Start monitoring
            self.monitor_pre_signal_conditions()
            
        except Exception as e:
            logger.error(f"Error starting pre-signal alert system: {e}")
        finally:
            shutdown_mt5()

# Global instance
pre_signal_system = PreSignalAlertSystem()

def start_pre_signal_alerts():
    """Start the pre-signal alert system"""
    pre_signal_system.start_monitoring()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the pre-signal alert system
    start_pre_signal_alerts()
