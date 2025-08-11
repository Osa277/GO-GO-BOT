import requests
import logging

def send_signal_to_webhook(signal, webhook_url='http://localhost:5001/webhook'):
    """Send a trading signal to the paper trading webhook server."""
    try:
        response = requests.post(webhook_url, json=signal, timeout=5)
        if response.status_code == 200:
            logging.info(f"Signal sent to webhook: {signal}")
            return True
        else:
            logging.error(f"Failed to send signal to webhook: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exception sending signal to webhook: {e}")
        return False
