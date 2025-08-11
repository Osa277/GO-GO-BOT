#!/usr/bin/env python3
"""
Real-Time Signal Dashboard
Monitor and control cloud signal generation
"""

import requests
import json
import time
import threading
from datetime import datetime

class RealTimeSignalDashboard:
    def __init__(self, cloud_url="https://go-go-nfoxqvmeb-asiyanbis-projects.vercel.app"):
        self.cloud_url = cloud_url
        self.is_running = False
        self.signal_count = 0
        
    def test_connection(self):
        """Test connection to cloud API"""
        try:
            response = requests.get(f"{self.cloud_url}/api/status", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def generate_single_signal(self, symbol="BTCUSD"):
        """Generate a single real-time signal"""
        try:
            response = requests.get(f"{self.cloud_url}/api/realtime-signal?symbol={symbol}", timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to generate signal: {response.status_code}")
                return None
        except Exception as e:
            print(f"🚫 Error generating signal: {e}")
            return None
    
    def start_realtime_stream(self):
        """Start real-time signal streaming"""
        self.is_running = True
        symbols = ['BTCUSD', 'XAUUSD', 'US30']
        
        print("🚀 Starting Real-Time Signal Stream...")
        print("=" * 50)
        
        while self.is_running:
            for symbol in symbols:
                if not self.is_running:
                    break
                    
                print(f"\n⚡ Generating real-time signal for {symbol}...")
                result = self.generate_single_signal(symbol)
                
                if result and result.get('success'):
                    self.signal_count += 1
                    signal = result.get('signal')
                    
                    print(f"✅ Signal #{self.signal_count} Generated!")
                    print(f"📊 {signal['side'].upper()} {symbol}")
                    print(f"💰 Entry: {signal['entry']}")
                    print(f"🎯 Confidence: {signal['confidence']}%")
                    print(f"📈 Market: {signal['market_condition'].title()}")
                    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    if result.get('success'):
                        print("📱 ✅ Sent to Telegram!")
                    else:
                        print("📱 ❌ Failed to send to Telegram")
                        
                else:
                    print(f"⏸️ No signal for {symbol}")
                
                # Wait between symbols (real-time feel)
                if self.is_running:
                    time.sleep(15)  # 15 seconds between symbols
            
            # Wait between cycles
            if self.is_running:
                print(f"\n⏳ Cycle complete. Waiting 45 seconds...")
                time.sleep(45)  # 45 seconds between cycles
    
    def stop_stream(self):
        """Stop the real-time stream"""
        self.is_running = False
        print(f"\n🛑 Real-time stream stopped")
        print(f"📊 Total signals generated: {self.signal_count}")
    
    def run_dashboard(self):
        """Run the interactive dashboard"""
        print("🎛️ Real-Time Signal Dashboard")
        print("=" * 40)
        
        # Test connection
        print("🧪 Testing cloud connection...")
        if self.test_connection():
            print("✅ Cloud API connected!")
        else:
            print("❌ Cloud API not accessible (authentication required)")
            print("💡 Using local generation mode...")
        
        print(f"\n📍 Cloud URL: {self.cloud_url}")
        print("\n📋 Available Commands:")
        print("  1 - Generate single signal")
        print("  2 - Start real-time stream")
        print("  3 - Stop stream")
        print("  4 - Check status")
        print("  q - Quit")
        
        while True:
            try:
                choice = input(f"\n🎮 Enter command: ").strip()
                
                if choice == '1':
                    symbol = input("📊 Enter symbol (BTCUSD/XAUUSD/US30): ").strip().upper()
                    if not symbol:
                        symbol = "BTCUSD"
                    
                    print(f"⚡ Generating signal for {symbol}...")
                    result = self.generate_single_signal(symbol)
                    
                    if result:
                        print(f"✅ Signal generated successfully!")
                        print(json.dumps(result, indent=2))
                    else:
                        print("❌ Failed to generate signal")
                
                elif choice == '2':
                    if not self.is_running:
                        print("🚀 Starting real-time stream...")
                        stream_thread = threading.Thread(target=self.start_realtime_stream, daemon=True)
                        stream_thread.start()
                    else:
                        print("⚠️ Stream already running!")
                
                elif choice == '3':
                    self.stop_stream()
                
                elif choice == '4':
                    print(f"📊 Status: {'🟢 Running' if self.is_running else '🔴 Stopped'}")
                    print(f"📈 Signals generated: {self.signal_count}")
                    print(f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}")
                
                elif choice.lower() == 'q':
                    self.stop_stream()
                    print("👋 Dashboard closed!")
                    break
                
                else:
                    print("❓ Invalid command. Try again.")
                    
            except KeyboardInterrupt:
                self.stop_stream()
                print("\n👋 Dashboard closed!")
                break
            except Exception as e:
                print(f"🚫 Error: {e}")

if __name__ == "__main__":
    dashboard = RealTimeSignalDashboard()
    dashboard.run_dashboard()
