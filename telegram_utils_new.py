import requests
import logging
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced connection settings
SESSION_TIMEOUT = 15
MAX_RETRIES = 2
RETRY_DELAY = 2

# Multiple users - Add more chat IDs here (SIMPLE APPROACH)
TELEGRAM_USERS = [
    '5362504152',  # Samuel (original user)
    # Add more chat IDs here:
    # '1234567890',  # User 2
    # '0987654321',  # User 3
]

def send_telegram_message_to_users(message, chat_ids=None, max_retries=MAX_RETRIES):
    """Send message to multiple Telegram users - SIMPLE MT5 VERSION"""
    
    if chat_ids is None:
        chat_ids = TELEGRAM_USERS
    
    success_count = 0
    
    # Multiple API endpoints to try
    urls = [
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        f"http://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    ]
    
    for chat_id in chat_ids:
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        user_success = False
        
        for url in urls:
            for attempt in range(max_retries):
                try:
                    print(f"[TELEGRAM DEBUG] Sending to {chat_id} - Attempt {attempt+1}")
                    
                    with requests.Session() as session:
                        session.headers.update({
                            'User-Agent': 'TradingBot/1.0',
                            'Connection': 'close'
                        })
                        
                        response = session.post(
                            url,
                            json=payload,
                            timeout=SESSION_TIMEOUT,
                            verify=False if 'http://' in url else True
                        )
                        
                        if response.status_code == 200:
                            print(f"✅ Message sent to {chat_id}")
                            success_count += 1
                            user_success = True
                            break
                        else:
                            print(f"❌ Failed to send to {chat_id}: {response.status_code}")
                            
                except Exception as e:
                    print(f"❌ Error sending to {chat_id}: {str(e)[:50]}")
                
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY)
            
            if user_success:
                break
    
    print(f"📊 Successfully sent to {success_count}/{len(chat_ids)} users")
    return success_count > 0

def send_telegram_message(message, max_retries=MAX_RETRIES):
    """Send message to all users (backwards compatibility)"""
    return send_telegram_message_to_users(message, TELEGRAM_USERS, max_retries)

def send_enhanced_alert(signal):
    """Send enhanced trading signal alert to all users - MT5 FOCUSED"""
    try:
        # Create simpler message to avoid parsing issues
        side = signal['side'].upper()
        order_type = signal['order_type'].upper()
        symbol = signal['symbol']
        tf = signal['tf']
        entry = signal['entry']
        sl = signal['sl']
        tp1 = signal['tp'][0] if signal['tp'] else 0
        position_size = signal.get('position_size', 0)
        confidence = signal.get('confidence', 0.8) * 100
        
        # Enhanced message with probability information
        probability_info = ""
        if 'tp_probability' in signal:
            tp_prob = signal['tp_probability']
            expected_val = signal.get('expected_value', 0)
            recommendation = signal.get('recommendation', '')
            
            # Probability emoji
            if tp_prob >= 70:
                prob_emoji = "🟢"
            elif tp_prob >= 60:
                prob_emoji = "🟡"
            elif tp_prob >= 50:
                prob_emoji = "🟠"
            else:
                prob_emoji = "🔴"
            
            probability_info = f"""
{prob_emoji} TP Probability: {tp_prob}%
📈 Expected Value: {expected_val:.1f} pts
💡 {recommendation.split(' - ')[0]}"""
        
        message = f"""🚨 NEW SIGNAL

{side} {order_type} - {symbol} {tf}
Entry: {entry:.5f}
Stop Loss: {sl:.5f}
Take Profit: {tp1:.5f}

Position: ${position_size:.2f}
Confidence: {confidence:.0f}%{probability_info}
Time: {datetime.now().strftime('%H:%M:%S')}"""

        # Also print to console as backup
        print(f"🚨 SIGNAL: {side} {symbol} {tf} @ {entry:.5f}")
        
        # Send to all users
        return send_telegram_message_to_users(message, TELEGRAM_USERS)
        
    except Exception as e:
        logging.error(f"Enhanced alert error: {e}")
        # Print to console as fallback
        print(f"🚨 SIGNAL ERROR: {signal.get('symbol', 'Unknown')} - {e}")
        return False

def send_system_alert(message, alert_type="INFO"):
    """Send system status alerts"""
    try:
        emoji_map = {
            "SUCCESS": "✅",
            "INFO": "ℹ️", 
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        
        emoji = emoji_map.get(alert_type, "📢")
        simple_message = f"{emoji} {alert_type}: {message}"
        
        # Print to console as backup
        print(f"🤖 SYSTEM: {simple_message}")
        
        # Send to all users
        return send_telegram_message_to_users(simple_message, TELEGRAM_USERS)
        
    except Exception as e:
        logging.error(f"System alert error: {e}")
        print(f"🤖 SYSTEM ERROR: {message}")
        return False

def send_trade_update(trade, update_type, pnl=None):
    """Send trade status updates"""
    try:
        symbol = trade.get('symbol', 'Unknown')
        
        if update_type == "entry_filled":
            message = f"✅ ENTRY FILLED: {symbol} at {trade.get('actual_entry', trade.get('entry', 0)):.5f}"
            
        elif update_type == "sl_hit":
            message = f"❌ STOP LOSS: {symbol} P&L: ${pnl:.2f}"
            
        elif "tp" in update_type:
            tp_num = update_type.replace("tp", "").replace("_hit", "")
            message = f"🎯 TP{tp_num} HIT: {symbol} P&L: +${pnl:.2f}"
        else:
            message = f"Trade Update: {update_type} - {symbol}"

        # Print to console as backup
        print(f"📊 TRADE: {message}")
        
        # Send to all users
        return send_telegram_message_to_users(message, TELEGRAM_USERS)
        
    except Exception as e:
        logging.error(f"Trade update error: {e}")
        print(f"📊 TRADE ERROR: {e}")
        return False

def send_performance_update():
    """Send daily performance update"""
    try:
        message = f"📊 Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Print to console as backup
        print(f"📈 PERFORMANCE: {message}")
        
        # Send to all users
        return send_telegram_message_to_users(message, TELEGRAM_USERS)
        
    except Exception as e:
        logging.error(f"Performance update error: {e}")
        print(f"📈 PERFORMANCE ERROR: {e}")
        return False

# Test function
def test_telegram_connection():
    """Test Telegram connection"""
    test_message = "🧪 Bot connection test - " + datetime.now().strftime('%H:%M:%S')
    result = send_telegram_message_to_users(test_message, TELEGRAM_USERS)
    
    if result:
        print("✅ Telegram connection working!")
    else:
        print("❌ Telegram connection failed - but bot will continue with console output")
    
    return result

def add_new_user(chat_id):
    """Add new user to the list (runtime addition)"""
    if chat_id not in TELEGRAM_USERS:
        TELEGRAM_USERS.append(chat_id)
        print(f"✅ Added new user: {chat_id}")
        print(f"📊 Total users: {len(TELEGRAM_USERS)}")
        
        # Send welcome message
        welcome_msg = f"""👋 Welcome to MT5 Trading Bot!

🤖 You've been added to receive trading signals!

📊 You will receive:
✅ Real-time MT5 trading signals
✅ Entry, Stop Loss, Take Profit levels
✅ Probability analysis
✅ Risk management info

🎯 Supported symbols: BTCUSD, XAUUSD, US30

Happy Trading! 🚀"""
        
        send_telegram_message_to_users(welcome_msg, [chat_id])
        return True
    else:
        print(f"⚠️ User {chat_id} already exists")
        return False
