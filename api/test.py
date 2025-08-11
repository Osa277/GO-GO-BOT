from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
TELEGRAM_CHAT_ID = "5362504152"

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

@app.route('/api/test-telegram')
def test_telegram():
    """Test Telegram connection"""
    message = f"""🧪 TEST MESSAGE

✅ Vercel Deployment Successful!
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 Your trading bot is live on Vercel!"""
    
    success = send_telegram_message(message)
    
    return jsonify({
        'success': success,
        'message': 'Telegram test completed',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
