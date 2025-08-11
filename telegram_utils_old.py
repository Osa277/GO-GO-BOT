import requests
import logging
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_USERS
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced connection settings
SESSION_TIMEOUT = 15  # Reduced timeout
MAX_RETRIES = 2      # Reduced retries for faster operation
RETRY_DELAY = 2      # Shorter delay

def send_telegram_message_to_user(message, chat_id, max_retries=MAX_RETRIES):
    """Send message to a specific Telegram user"""
    
    # Multiple API endpoints to try
    urls = [
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        f"http://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    ]
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    for url in urls:
        for attempt in range(max_retries):
            try:
                print(f"[TELEGRAM DEBUG] Attempt {attempt+1} URL: {url}")
                print(f"[TELEGRAM DEBUG] Payload: {payload}")
                # Create fresh session for each attempt
                with requests.Session() as session:
                    # Configure session
                    session.headers.update({
                        'User-Agent': 'TradingBot/1.0',
                        'Connection': 'close'  # Don't keep connection alive
                    })
                    
                    # Make request with shorter timeout
                    response = session.post(
                        url,
                        json=payload,
                        timeout=SESSION_TIMEOUT,
                        verify=False if 'http://' in url else True
                    )
                    print(f"[TELEGRAM DEBUG] Response code: {response.status_code}")
                    print(f"[TELEGRAM DEBUG] Response text: {response.text}")
                    if response.status_code == 200:
                        protocol = "HTTPS" if "https" in url else "HTTP"
                        logging.info(f"SUCCESS: Telegram message sent via {protocol} (attempt {attempt + 1})")
                        return True
                    else:
                        logging.warning(f"Telegram API error {response.status_code}: {response.text}")
                        
            except requests.exceptions.ConnectTimeout:
                logging.warning(f"❌ Connection timeout to {url} (attempt {attempt + 1}/{max_retries})")
                
            except requests.exceptions.ConnectionError as e:
                logging.warning(f"❌ Connection error to {url} (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
                
            except requests.exceptions.RequestException as e:
                logging.warning(f"❌ Request error to {url} (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
            
            except Exception as e:
                logging.warning(f"❌ Unexpected error to {url} (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY)
    
    return False

def send_telegram_message_to_all_users(message, signal_symbol=None):
    """Send message to all registered users based on their preferences"""
    success_count = 0
    
    for user in TELEGRAM_USERS:
        chat_id = user['chat_id']
        user_name = user.get('name', 'User')
        is_premium = user.get('premium', False)
        user_symbols = user.get('symbols', ['BTCUSD'])
        
        # Check if user wants this symbol
        if signal_symbol and signal_symbol not in user_symbols:
            print(f"⏭️ Skipping {user_name} - doesn't want {signal_symbol} signals")
            continue
        
        # Add user-specific prefix for premium users
        user_message = message
        if is_premium:
            user_message = f"👑 PREMIUM\n{message}"
        else:
            # Free users get basic message
            user_message = f"� FREE\n{message}"
        
        # Send to user
        if send_telegram_message_to_user(user_message, chat_id):
            print(f"✅ Sent to {user_name} ({chat_id})")
            success_count += 1
        else:
            print(f"❌ Failed to send to {user_name} ({chat_id})")
    
    print(f"� Message sent to {success_count}/{len(TELEGRAM_USERS)} users")
    return success_count > 0

def send_telegram_message(message, max_retries=MAX_RETRIES):
    """Backwards compatibility - send to primary user and all users"""
    # Send to primary user (backwards compatibility)
    primary_success = send_telegram_message_to_user(message, TELEGRAM_CHAT_ID, max_retries)
    
    # If we have multiple users configured, send to all
    if len(TELEGRAM_USERS) > 1:
        all_users_success = send_telegram_message_to_all_users(message)
        return primary_success or all_users_success
    
    return primary_success

def send_enhanced_alert(signal):
    """Send enhanced trading signal alert to all users"""
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
� Expected Value: {expected_val:.1f} pts
💡 {recommendation.split(' - ')[0]}"""
        
        message = f"""�🚨 NEW SIGNAL

{side} {order_type} - {symbol} {tf}
Entry: {entry:.5f}
Stop Loss: {sl:.5f}
Take Profit: {tp1:.5f}

Position: ${position_size:.2f}
Confidence: {confidence:.0f}%{probability_info}
Time: {datetime.now().strftime('%H:%M:%S')}"""

        # Also print to console as backup
        print(f"🚨 SIGNAL: {side} {symbol} {tf} @ {entry:.5f}")
        
        # Send to all users based on their symbol preferences
        return send_telegram_message_to_all_users(message, symbol)
        
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
        
        # Try to send to Telegram
        return send_telegram_message(simple_message)
        
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
        
        # Try to send to Telegram
        return send_telegram_message(message)
        
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
        
        # Try to send to Telegram
        return send_telegram_message(message)
        
    except Exception as e:
        logging.error(f"Performance update error: {e}")
        print(f"📈 PERFORMANCE ERROR: {e}")
        return False

# Test function
def test_telegram_connection():
    """Test Telegram connection"""
    test_message = "🧪 Bot connection test - " + datetime.now().strftime('%H:%M:%S')
    result = send_telegram_message(test_message)
    
    if result:
        print("✅ Telegram connection working!")
    else:
        print("❌ Telegram connection failed - but bot will continue with console output")
    
    return result