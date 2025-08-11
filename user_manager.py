#!/usr/bin/env python3
"""
Telegram User Management Script
Helps you add and manage users for your trading bot
"""

import requests
from config import TELEGRAM_TOKEN

def get_user_chat_id():
    """Get chat ID for new users"""
    print("🔍 HOW TO GET USER CHAT ID:")
    print("=" * 50)
    print("1. Ask the user to send '/start' to your bot")
    print("2. Run this function to see recent messages")
    print("3. Find their chat_id in the results")
    print()
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['result']:
                print("📱 RECENT MESSAGES:")
                print("-" * 30)
                
                for update in data['result'][-10:]:  # Last 10 messages
                    if 'message' in update:
                        message = update['message']
                        chat = message['chat']
                        user = message.get('from', {})
                        
                        print(f"User: {user.get('first_name', '')} {user.get('last_name', '')}")
                        print(f"Username: @{user.get('username', 'No username')}")
                        print(f"Chat ID: {chat['id']}")
                        print(f"Message: {message.get('text', 'No text')}")
                        print("-" * 30)
            else:
                print("❌ No recent messages found")
                print("💡 Ask users to send '/start' to your bot first")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def send_welcome_message(chat_id, user_name="User"):
    """Send welcome message to new user"""
    message = f"""👋 Welcome {user_name}!

🤖 You've been added to the Trading Bot signals!

📊 You will receive:
✅ Real-time trading signals
✅ Entry, Stop Loss, Take Profit levels
✅ Probability analysis
✅ Risk management info

🎯 Supported symbols: BTCUSD, XAUUSD, US30

Happy Trading! 🚀"""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"✅ Welcome message sent to {user_name}")
            return True
        else:
            print(f"❌ Failed to send welcome message: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending welcome message: {e}")
        return False

def add_new_user_interactive():
    """Interactive function to add a new user"""
    print("🆕 ADD NEW USER")
    print("=" * 30)
    
    print("\n📱 Step 1: Get Chat ID")
    print("Have the user send '/start' to your bot, then run get_user_chat_id()")
    
    chat_id = input("\nEnter user's chat ID: ").strip()
    if not chat_id:
        print("❌ Chat ID is required")
        return
    
    user_name = input("Enter user's name: ").strip() or "User"
    
    print("\n👑 Is this a premium user? (y/n)")
    premium = input().strip().lower() == 'y'
    
    print("\n📊 Select symbols (comma-separated):")
    print("Available: BTCUSD, XAUUSD, US30")
    symbols_input = input("Symbols: ").strip() or "BTCUSD"
    symbols = [s.strip().upper() for s in symbols_input.split(',')]
    
    # Generate config entry
    user_config = f"""    {{
        'chat_id': '{chat_id}',
        'name': '{user_name}',
        'premium': {premium},
        'symbols': {symbols}
    }}"""
    
    print("\n✅ USER CONFIGURATION:")
    print("=" * 40)
    print(user_config)
    print("\n📝 ADD THIS TO config.py in TELEGRAM_USERS list:")
    print("1. Open config.py")
    print("2. Find TELEGRAM_USERS = [")
    print("3. Add the configuration above")
    print("4. Restart your bot")
    
    # Send welcome message
    if input("\nSend welcome message? (y/n): ").strip().lower() == 'y':
        send_welcome_message(chat_id, user_name)

def test_user_message(chat_id):
    """Send test message to specific user"""
    message = f"""🧪 TEST MESSAGE

✅ Your Telegram is working!
🤖 You're connected to the Trading Bot
🕐 {requests.get('http://worldtimeapi.org/api/timezone/UTC').json()['datetime'][:19]}

This is a test signal to verify your connection."""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"✅ Test message sent to {chat_id}")
            return True
        else:
            print(f"❌ Failed to send test message: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

if __name__ == "__main__":
    print("🤖 TELEGRAM USER MANAGER")
    print("=" * 40)
    print("1. Get user chat IDs: get_user_chat_id()")
    print("2. Add new user: add_new_user_interactive()")
    print("3. Test user: test_user_message('CHAT_ID')")
    print("4. Send welcome: send_welcome_message('CHAT_ID', 'Name')")
    print()
    
    while True:
        action = input("Choose action (1-4) or 'q' to quit: ").strip()
        
        if action == 'q':
            break
        elif action == '1':
            get_user_chat_id()
        elif action == '2':
            add_new_user_interactive()
        elif action == '3':
            chat_id = input("Enter chat ID to test: ").strip()
            if chat_id:
                test_user_message(chat_id)
        elif action == '4':
            chat_id = input("Enter chat ID: ").strip()
            name = input("Enter name: ").strip() or "User"
            if chat_id:
                send_welcome_message(chat_id, name)
        else:
            print("Invalid choice")
