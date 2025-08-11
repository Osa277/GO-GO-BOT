from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import threading
import time

class CloudSignalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = urlparse(self.path).path
            query = parse_qs(urlparse(self.path).query)
            
            if path == '/' or path == '/status':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'title': '🤖 GO-GO-BOT Cloud Signal Generator',
                    'status': 'online ✅',
                    'message': 'Cloud-only signal generation active',
                    'endpoints': [
                        '/status - System status',
                        '/signal?symbol=BTCUSD - Generate signal',
                        '/send-signal?symbol=BTCUSD - Generate and send signal'
                    ],
                    'supported_symbols': ['BTCUSD', 'XAUUSD', 'US30'],
                    'timestamp': datetime.now().isoformat(),
                    'version': '3.0-standalone'
                }
                
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            elif path == '/signal':
                symbol = query.get('symbol', ['BTCUSD'])[0]
                signal = self.generate_signal(symbol)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(signal, indent=2).encode())
                
            elif path == '/send-signal':
                symbol = query.get('symbol', ['BTCUSD'])[0]
                signal = self.generate_signal(symbol)
                message = self.format_signal_message(signal)
                
                # Here you would send to Telegram
                # For demo, we'll just return the formatted message
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'success': True,
                    'signal': signal,
                    'message': message,
                    'sent_to_telegram': 'Demo mode - message not actually sent'
                }
                
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'404 Not Found')
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
    
    def generate_signal(self, symbol):
        """Generate a trading signal"""
        # Mock data
        if symbol == 'BTCUSD':
            base_price = random.uniform(118000, 122000)
        elif symbol == 'XAUUSD':
            base_price = random.uniform(3350, 3360)
        elif symbol == 'US30':
            base_price = random.uniform(44000, 44500)
        else:
            base_price = random.uniform(1, 100)
        
        market_sentiment = random.choice(['bullish', 'bearish'])
        
        if market_sentiment == 'bullish':
            side = 'buy'
            entry = base_price
            sl = entry * 0.985
            tp = entry * 1.06
        else:
            side = 'sell'
            entry = base_price
            sl = entry * 1.015
            tp = entry * 0.94
        
        return {
            'symbol': symbol,
            'side': side,
            'entry': round(entry, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'confidence': random.randint(70, 92),
            'tp_probability': random.randint(58, 78),
            'rsi': random.randint(25, 75),
            'market_sentiment': market_sentiment,
            'timestamp': datetime.now().isoformat(),
            'timeframe': '5M',
            'source': 'Standalone Cloud Generator'
        }
    
    def format_signal_message(self, signal):
        """Format signal for Telegram"""
        side_emoji = "🟢" if signal['side'] == 'buy' else "🔴"
        confidence_emoji = "🎯" if signal['confidence'] >= 80 else "⚠️"
        
        return f"""🚨 CLOUD SIGNAL {side_emoji}

{signal['side'].upper()} {signal['symbol']} {signal['timeframe']}
Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}

{confidence_emoji} Confidence: {signal['confidence']}%
🎲 TP Probability: {signal['tp_probability']}%
📊 RSI: {signal['rsi']}
📈 Market: {signal['market_sentiment'].title()}

⏰ {datetime.now().strftime('%H:%M:%S')}
☁️ Standalone Signal Generator"""

def run_server():
    """Run the HTTP server"""
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, CloudSignalHandler)
    print(f"🚀 Cloud Signal Server running at http://localhost:8080")
    print("📊 Available endpoints:")
    print("   http://localhost:8080/ - Status")
    print("   http://localhost:8080/signal?symbol=BTCUSD - Generate signal")
    print("   http://localhost:8080/send-signal?symbol=BTCUSD - Generate and format signal")
    print("\n✨ Server is ready for cloud signal generation!")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
