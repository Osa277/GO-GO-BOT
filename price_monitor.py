#!/usr/bin/env python3
"""
Real-time Bitcoin Price Monitor with Smart Alerts
Tracks key price levels and market movements
"""

import time
import json
from datetime import datetime, timedelta
from threading import Thread, Lock
import requests

class BitcoinPriceMonitor:
    def __init__(self):
        self.current_price = 0
        self.price_history = []
        self.alerts = []
        self.lock = Lock()
        self.running = False
        self.price_change_threshold = 500  # Alert if price changes by this amount
        self.monitoring_interval = 30  # Check every 30 seconds
        
    def add_price_alert(self, price_level, alert_type="above", message=""):
        """Add a price alert
        alert_type: 'above', 'below', 'cross_up', 'cross_down'
        """
        alert = {
            'id': len(self.alerts) + 1,
            'price_level': float(price_level),
            'alert_type': alert_type,
            'message': message or f"Bitcoin {alert_type} ${price_level:,.2f}",
            'created': datetime.now().isoformat(),
            'triggered': False,
            'triggered_at': None
        }
        
        with self.lock:
            self.alerts.append(alert)
        
        print(f"🔔 Price Alert #{alert['id']} Added: {alert['message']}")
        return alert['id']
    
    def check_price_alerts(self, new_price, old_price):
        """Check if any price alerts should be triggered"""
        with self.lock:
            for alert in self.alerts:
                if alert['triggered']:
                    continue
                
                should_trigger = False
                price_level = alert['price_level']
                
                if alert['alert_type'] == 'above' and new_price >= price_level:
                    should_trigger = True
                elif alert['alert_type'] == 'below' and new_price <= price_level:
                    should_trigger = True
                elif alert['alert_type'] == 'cross_up' and old_price < price_level <= new_price:
                    should_trigger = True
                elif alert['alert_type'] == 'cross_down' and old_price > price_level >= new_price:
                    should_trigger = True
                
                if should_trigger:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.now().isoformat()
                    
                    print(f"🚨 PRICE ALERT TRIGGERED #{alert['id']}")
                    print(f"   {alert['message']}")
                    print(f"   Current Price: ${new_price:,.2f}")
                    
                    # You can add Telegram notification here
                    self.send_price_alert_notification(alert, new_price)
    
    def send_price_alert_notification(self, alert, current_price):
        """Send price alert notification (integrate with your telegram_utils)"""
        try:
            from telegram_utils import send_system_alert
            message = f"PRICE ALERT: {alert['message']} - Current: ${current_price:,.2f}"
            send_system_alert(message, "WARNING")
        except:
            print(f"📱 Price alert notification: {alert['message']}")
    
    def analyze_price_movement(self, new_price):
        """Analyze price movement and generate insights"""
        if len(self.price_history) < 2:
            return None
        
        # Calculate price change
        old_price = self.price_history[-1]['price']
        price_change = new_price - old_price
        price_change_pct = (price_change / old_price) * 100
        
        # Check for significant movements
        if abs(price_change) >= self.price_change_threshold:
            direction = "UP" if price_change > 0 else "DOWN"
            emoji = "🚀" if price_change > 0 else "📉"
            
            print(f"{emoji} SIGNIFICANT BITCOIN MOVEMENT:")
            print(f"   Price: ${old_price:,.2f} → ${new_price:,.2f}")
            print(f"   Change: ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
            
            # Send movement alert
            try:
                from telegram_utils import send_system_alert
                message = f"BTC MOVEMENT: ${price_change:+,.2f} ({price_change_pct:+.2f}%) - Now ${new_price:,.2f}"
                send_system_alert(message, "INFO")
            except:
                pass
        
        return {
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'direction': 'up' if price_change > 0 else 'down',
            'significant': abs(price_change) >= self.price_change_threshold
        }
    
    def get_mt5_price(self):
        """Get Bitcoin price from MT5 (integrate with your mt5_data)"""
        try:
            from mt5_data import get_current_price
            price = get_current_price('BTCUSD')
            return price if price else None
        except:
            return None
    
    def get_backup_price(self):
        """Get Bitcoin price from external API as backup"""
        try:
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data['bitcoin']['usd']
        except:
            pass
        return None
    
    def update_price(self):
        """Update Bitcoin price from best available source"""
        # Try MT5 first (most accurate)
        price = self.get_mt5_price()
        
        # Fallback to external API
        if price is None:
            price = self.get_backup_price()
        
        if price is None:
            print("⚠️ Could not fetch Bitcoin price")
            return False
        
        old_price = self.current_price
        self.current_price = price
        
        # Store price history
        price_data = {
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'source': 'MT5' if self.get_mt5_price() else 'CoinGecko'
        }
        
        with self.lock:
            self.price_history.append(price_data)
            # Keep only last 100 prices
            if len(self.price_history) > 100:
                self.price_history.pop(0)
        
        # Check alerts and analyze movement
        if old_price > 0:
            self.check_price_alerts(price, old_price)
            self.analyze_price_movement(price)
        
        return True
    
    def start_monitoring(self):
        """Start real-time price monitoring"""
        self.running = True
        print(f"🔍 Bitcoin Price Monitor Started (interval: {self.monitoring_interval}s)")
        
        def monitor_loop():
            while self.running:
                try:
                    success = self.update_price()
                    if success:
                        print(f"💰 BTC: ${self.current_price:,.2f} | Alerts: {len([a for a in self.alerts if not a['triggered']])}")
                    
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    print(f"❌ Price monitor error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        # Start monitoring in background thread
        monitor_thread = Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop price monitoring"""
        self.running = False
        print("🛑 Bitcoin Price Monitor Stopped")
    
    def get_price_summary(self):
        """Get current price summary"""
        if not self.price_history:
            return "No price data available"
        
        recent_prices = self.price_history[-10:]  # Last 10 prices
        prices = [p['price'] for p in recent_prices]
        
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        active_alerts = len([a for a in self.alerts if not a['triggered']])
        triggered_alerts = len([a for a in self.alerts if a['triggered']])
        
        return f"""
💰 BITCOIN PRICE MONITOR
========================
Current Price: ${self.current_price:,.2f}
Recent Range: ${min_price:,.2f} - ${max_price:,.2f}
Recent Average: ${avg_price:,.2f}

🔔 Alerts:
• Active: {active_alerts}
• Triggered: {triggered_alerts}
• Total: {len(self.alerts)}

📊 Monitoring: {'✅ ACTIVE' if self.running else '❌ STOPPED'}
        """

def setup_bitcoin_alerts():
    """Setup common Bitcoin price alerts"""
    monitor = BitcoinPriceMonitor()
    
    # Get current price first
    monitor.update_price()
    current = monitor.current_price
    
    if current > 0:
        # Setup common alerts
        monitor.add_price_alert(current + 1000, "above", "Bitcoin gained $1000+")
        monitor.add_price_alert(current - 1000, "below", "Bitcoin dropped $1000+")
        monitor.add_price_alert(120000, "cross_up", "Bitcoin breaking $120,000!")
        monitor.add_price_alert(115000, "cross_down", "Bitcoin falling below $115,000")
        
        print(f"🎯 Default alerts set around current price: ${current:,.2f}")
    
    return monitor

if __name__ == "__main__":
    # Demo setup
    monitor = setup_bitcoin_alerts()
    monitor.start_monitoring()
    
    print(monitor.get_price_summary())
    print("\n🎯 Monitor running... Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(10)
            print(monitor.get_price_summary())
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n👋 Price monitoring stopped")
