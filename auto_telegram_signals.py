#!/usr/bin/env python3
"""
Automatic Telegram Signal Sender
Sends live trading signals to your Telegram every 5 minutes
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BOT_URL = "https://go-go-production.up.railway.app"
TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
CHAT_ID = "5362504152"
SIGNAL_INTERVAL = 180  # 3 minutes (perfect for 3min timeframe!)

def send_telegram_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"Telegram send error: {e}")
        return None

def get_latest_signals():
    """Get latest signals from your bot"""
    try:
        response = requests.get(f"{BOT_URL}/api/signals")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Signal fetch error: {e}")
        return None

def format_signal_message(signal, signal_source="LIVE SIGNAL"):
    """Format signal for Telegram"""
    confidence_emoji = "🔥" if signal['confidence'] > 75 else "⚡" if signal['confidence'] > 65 else "📊"
    side_emoji = "🟢" if signal['side'] == 'buy' else "🔴"
    
    message = f"""
{confidence_emoji} <b>{signal_source}</b> {side_emoji}

<b>Symbol:</b> {signal['symbol']}
<b>Action:</b> {signal['side'].upper()}
<b>Entry:</b> {signal['entry']}
<b>Stop Loss:</b> {signal['sl']}
<b>Take Profit:</b> {signal['tp']}
<b>Confidence:</b> {signal['confidence']}%
<b>Timeframe:</b> {signal['timeframe']}
<b>Risk/Reward:</b> {signal.get('risk_reward', 'N/A')}

🕐 <i>{datetime.now().strftime('%H:%M:%S')}</i>
🚀 <b>GO-GO Trading Bot</b>
"""
    return message

def send_best_signal():
    """Send the best available signal, prioritizing 3-minute timeframe"""
    signals_data = get_latest_signals()
    
    if not signals_data or 'signals' not in signals_data:
        send_telegram_message("⚠️ <b>Signal Update</b>\n\nNo signals available at the moment.\nBot is monitoring markets...")
        return
    
    signals = signals_data['signals']
    
    # First, try to get 3-minute signals (your preference!)
    three_min_signals = [s for s in signals if s.get('timeframe') == '3M' and s['confidence'] >= 65]
    
    if three_min_signals:
        # Get the best 3-minute signal
        best_signal = max(three_min_signals, key=lambda x: x['confidence'])
        signal_source = "3-MINUTE TIMEFRAME ⚡"
    else:
        # Fallback to any high confidence signal
        high_conf_signals = [s for s in signals if s['confidence'] >= 65]
        if high_conf_signals:
            best_signal = max(high_conf_signals, key=lambda x: x['confidence'])
            signal_source = f"{best_signal.get('timeframe', 'Unknown')} TIMEFRAME"
        else:
            send_telegram_message("📊 <b>Market Update</b>\n\nNo high-confidence signals at the moment.\nContinuing to monitor...")
            return
    
    # Format and send the signal
    message = format_signal_message(best_signal, signal_source)
    result = send_telegram_message(message)
    
    if result and result.get('ok'):
        print(f"Signal sent: {best_signal['symbol']} {best_signal['side']} - {best_signal['confidence']}% ({best_signal.get('timeframe', 'Unknown')})")
    else:
        print("Failed to send signal")

def main():
    """Main function - run automatic signal sender"""
    print("🚀 Starting GO-GO Automatic Signal Sender...")
    
    # Send startup message
    startup_msg = """
🚀 <b>GO-GO Trading Bot ACTIVATED!</b>

✅ <b>Status:</b> Online and Monitoring
📊 <b>Timeframes:</b> 3min, 5min, 15min  
🎯 <b>Min Confidence:</b> 65%
⏰ <b>Signal Frequency:</b> Every 3 minutes
🔥 <b>Focus:</b> 3-minute timeframe signals

<i>You'll now receive live professional trading signals every 3 minutes!</i>
"""
    send_telegram_message(startup_msg)
    
    # Main loop
    while True:
        try:
            print(f"Checking for signals at {datetime.now().strftime('%H:%M:%S')}")
            send_best_signal()
            
            print(f"Waiting {SIGNAL_INTERVAL} seconds for next check...")
            time.sleep(SIGNAL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Stopping signal sender...")
            send_telegram_message("⏹️ <b>Signal Sender Stopped</b>\n\nAutomatic signals have been paused.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    main()
