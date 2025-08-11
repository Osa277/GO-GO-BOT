#!/usr/bin/env python3
"""
Quick test to send a manual signal to Telegram
"""

from telegram_utils import send_enhanced_alert
from datetime import datetime

def test_signal_notification():
    """Test sending a signal notification"""
    
    print("🔄 Testing signal notification...")
    
    # Create a test signal
    test_signal = {
        'symbol': 'BTCUSD',
        'side': 'buy',
        'order_type': 'BUY',
        'entry': 65432.10,
        'sl': 64000.00,
        'tp': [67000.00, 68500.00, 70000.00],
        'tp.1': 67000.00,
        'current_price': 65432.10,
        'tf': 'M15',
        'timeframe': 'M15',
        'confidence': 0.89,
        'position_size': 0.01,
        'timestamp': datetime.now().isoformat(),
        'session_analysis': {'action': 'TAKE', 'recommendation': '🟢 OPTIMAL - High probability setup'},
        'correlation_advice': {'correlation_risk': 'LOW'},
        'risk_analysis': {'risk_level': 'ACCEPTABLE'},
        'tp_probability': 85.5
    }
    
    try:
        # Send the signal
        result = send_enhanced_alert(test_signal)
        
        if result:
            print("✅ TEST SIGNAL SENT SUCCESSFULLY!")
            print("📱 Check your Telegram for the signal notification")
            return True
        else:
            print("❌ Failed to send test signal")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test signal: {e}")
        return False

if __name__ == "__main__":
    test_signal_notification()
