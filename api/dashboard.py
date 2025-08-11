from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Vercel Trading Bot Dashboard</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #1a1a1a; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #2d2d2d; padding: 20px; margin: 20px 0; border-radius: 10px; }
        .btn { background: #0070f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; }
        .btn:hover { background: #0051a2; }
        .status { color: #00ff00; }
        .endpoint { background: #333; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Vercel Trading Bot</h1>
        
        <div class="card">
            <h2>📊 Status</h2>
            <p class="status">✅ Online and Running</p>
            <p>🕐 Current Time: {{ current_time }}</p>
            <p>🌐 Deployed on Vercel</p>
        </div>
        
        <div class="card">
            <h2>🎯 Quick Actions</h2>
            <a href="/api/signal?symbol=BTCUSD" class="btn">Get BTC Signal</a>
            <a href="/api/send-signal?symbol=BTCUSD" class="btn">Send BTC Alert</a>
            <a href="/api/test-telegram" class="btn">Test Telegram</a>
            <a href="/api/status" class="btn">API Status</a>
        </div>
        
        <div class="card">
            <h2>🔗 API Endpoints</h2>
            <div class="endpoint">/api/status - Health check</div>
            <div class="endpoint">/api/signal?symbol=BTCUSD - Get trading signal</div>
            <div class="endpoint">/api/send-signal?symbol=BTCUSD - Send signal to Telegram</div>
            <div class="endpoint">/api/webhook - Receive external signals (POST)</div>
            <div class="endpoint">/api/test-telegram - Test Telegram connection</div>
        </div>
        
        <div class="card">
            <h2>📱 Supported Symbols</h2>
            <p>🟡 BTCUSD - Bitcoin</p>
            <p>🥇 XAUUSD - Gold</p>
            <p>📈 US30 - Dow Jones</p>
        </div>
        
        <div class="card">
            <h2>🚀 Features</h2>
            <p>✅ Real-time market data (Yahoo Finance)</p>
            <p>✅ Telegram notifications</p>
            <p>✅ Webhook support</p>
            <p>✅ RESTful API</p>
            <p>✅ Signal generation</p>
            <p>✅ Zero-cost deployment</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/api/dashboard')
def dashboard():
    """Trading bot dashboard"""
    return render_template_string(dashboard_html, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    app.run(debug=True)
