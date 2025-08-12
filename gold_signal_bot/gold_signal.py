import time
import requests
import logging
import os
from datetime import datetime

# Telegram setup
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def get_gold_ohlcv():
    url = "https://api.binance.com/api/v3/klines?symbol=XAUUSDT&interval=15m&limit=50"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        closes = [float(row[4]) for row in data]
        return closes
    except Exception as e:
        print(f"Binance error: {e}")
        return []

def generate_gold_signal():
    closes = get_gold_ohlcv()
    if len(closes) < 20:
        return None
    ema_20 = sum(closes[-20:]) / 20
    ema_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sum(closes) / len(closes)
    current_price = closes[-1]
    if current_price > ema_20 > ema_50:
        return f"GOLD BUY SIGNAL: Price={current_price:.2f} EMA20={ema_20:.2f} EMA50={ema_50:.2f}"
    elif current_price < ema_20 < ema_50:
        return f"GOLD SELL SIGNAL: Price={current_price:.2f} EMA20={ema_20:.2f} EMA50={ema_50:.2f}"
    else:
        return None

def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        signal = generate_gold_signal()
        if signal:
            sent = send_telegram_message(signal)
            logging.info(f"Sent: {signal}")
        else:
            logging.info("No gold signal generated.")
        time.sleep(180)  # Run every 3 minutes

if __name__ == "__main__":
    main()
