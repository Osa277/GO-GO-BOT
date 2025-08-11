#!/usr/bin/env python3
"""
Cloud Signal Activator
Activates all signal generators on Vercel cloud
"""

import requests
import time
from datetime import datetime

def activate_cloud_signals():
    """Activate all cloud signal generators"""
    
    base_url = "https://go-go-c4zlc1o4p-asiyanbis-projects.vercel.app"
    
    print("🚀" + "="*60 + "🚀")
    print("           ACTIVATING CLOUD SIGNAL GENERATORS")
    print("🚀" + "="*60 + "🚀")
    print()
    
    # Test cloud connection
    print("🧪 Testing cloud connection...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("✅ Cloud API is online!")
        else:
            print(f"⚠️ Cloud API response: {response.status_code}")
    except Exception as e:
        print(f"❌ Cloud connection error: {e}")
        return False
    
    print()
    print("🎯 ACTIVATION INSTRUCTIONS:")
    print("-" * 50)
    print("1. Open your browser")
    print("2. Visit these URLs to activate each generator:")
    print()
    print(f"🟢 3-Minute Generator:")
    print(f"   {base_url}/api/start-3min")
    print()
    print(f"🟡 5-Minute Generator:")
    print(f"   {base_url}/api/start-5min")
    print()
    print(f"🔵 15-Minute Generator:")
    print(f"   {base_url}/api/start-15min")
    print()
    print(f"🚀 ALL Generators (Recommended):")
    print(f"   {base_url}/api/start-all-live")
    print()
    print("-" * 50)
    print("✅ Once activated, signals will run 24/7 on cloud")
    print("💻 You can turn off your laptop safely!")
    print("📱 Check Telegram for live signals")
    print()
    
    # Send activation test to Telegram
    try:
        TELEGRAM_TOKEN = "8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro"
        chat_id = "5362504152"
        
        message = f"""🚀 CLOUD ACTIVATION READY!

☁️ Your signal generators are deployed to cloud!

🎯 TO ACTIVATE:
Visit: {base_url}/api/start-all-live

✅ Once activated:
🟢 3-minute signals every 3 minutes  
🟡 5-minute signals every 5 minutes
🔵 15-minute signals every 15 minutes

💻 Turn off laptop safely after activation!
📱 Signals will continue 24/7

⏰ {datetime.now().strftime('%H:%M:%S')}"""

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("📱 ✅ Activation instructions sent to Telegram!")
        else:
            print("📱 ❌ Failed to send Telegram message")
            
    except Exception as e:
        print(f"📱 Telegram error: {e}")
    
    print()
    print("🚀" + "="*60 + "🚀")
    print("           CLOUD DEPLOYMENT COMPLETE!")
    print("🚀" + "="*60 + "🚀")
    
    return True

if __name__ == "__main__":
    activate_cloud_signals()
