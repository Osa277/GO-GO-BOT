#!/usr/bin/env python3
"""
Simple MT5 Telegram User Manager
Add users to your MT5 trading bot signals
"""

import requests
from config import TELEGRAM_TOKEN

def get_user_chat_ids():
    """Get chat IDs from recent messages - Ask users to send /start first"""
    print("🔍 GETTING USER CHAT IDs")
    print("=" * 40)
    print("📱 Ask new users to send '/start' to your bot first!")
    print()
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['result']:
                print("📱 RECENT MESSAGES:")
                print("-" * 30)
                
                chat_ids = []
                for update in data['result'][-20:]:  # Last 20 messages
                    if 'message' in update:
                        message = update['message']
                        chat = message['chat']
                        user = message.get('from', {})
                        
                        chat_id = str(chat['id'])
                        if chat_id not in chat_ids:
                            chat_ids.append(chat_id)
                        
                        print(f"👤 {user.get('first_name', '')} {user.get('last_name', '')}")
                        print(f"📧 @{user.get('username', 'No username')}")
                        print(f"🆔 Chat ID: {chat_id}")
                        print(f"💬 Message: {message.get('text', 'No text')[:30]}...")
                        print("-" * 30)
                
                print(f"\n✅ Found {len(set(chat_ids))} unique users")
                return list(set(chat_ids))
            else:
                print("❌ No recent messages found")
                print("💡 Ask users to send '/start' to your bot first")
                return []
        else:
            print(f"❌ API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def add_users_to_telegram_utils():
    """Guide user to add chat IDs to telegram_utils.py"""
    chat_ids = get_user_chat_ids()
    
    if not chat_ids:
        print("❌ No users found. Ask them to message your bot first.")
        return
    
    print(f"\n🔧 HOW TO ADD {len(chat_ids)} USERS:")
    print("=" * 50)
    print("1. Open telegram_utils.py")
    print("2. Find the TELEGRAM_USERS list (around line 15)")
    print("3. Add these chat IDs:")
    print()
    
    print("TELEGRAM_USERS = [")
    print("    '5362504152',  # Samuel (original user)")
    for chat_id in chat_ids:
        if chat_id != '5362504152':  # Don't duplicate original user
            print(f"    '{chat_id}',  # New user")
    print("]")
    
    print(f"\n4. Save the file")
    print(f"5. Restart your scanner: python scanner.py")
    print(f"\n✅ All {len(chat_ids)} users will receive signals!")

def send_test_message_to_user(chat_id):
    """Send test message to verify user can receive signals"""
    message = f"""🧪 TEST SIGNAL

✅ Your Telegram is connected!
🤖 You're now part of the MT5 Trading Bot
🕐 {requests.get('http://worldtimeapi.org/api/timezone/UTC').json()['datetime'][:19]}

You will receive:
📊 Real-time MT5 signals
💰 Entry/Exit points
🎯 Take Profit levels
🛑 Stop Loss levels

Ready for trading! 🚀"""
    
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

def test_current_users():
    """Test sending messages to users currently in telegram_utils.py"""
    try:
        from telegram_utils import TELEGRAM_USERS, send_telegram_message_to_users
        
        print(f"🧪 TESTING {len(TELEGRAM_USERS)} CURRENT USERS")
        print("=" * 40)
        
        test_message = f"🧪 Multi-User Test - {requests.get('http://worldtimeapi.org/api/timezone/UTC').json()['datetime'][:19]}"
        
        result = send_telegram_message_to_users(test_message)
        
        if result:
            print("✅ Multi-user system working!")
        else:
            print("❌ Multi-user system failed")
            
        return result
        
    except Exception as e:
        print(f"❌ Error testing users: {e}")
        return False

if __name__ == "__main__":
    print("🤖 MT5 TELEGRAM USER MANAGER")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Get user chat IDs")
        print("2. Add users to system")
        print("3. Test specific user")
        print("4. Test all current users")
        print("5. Quit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            get_user_chat_ids()
        elif choice == '2':
            add_users_to_telegram_utils()
        elif choice == '3':
            chat_id = input("Enter chat ID to test: ").strip()
            if chat_id:
                send_test_message_to_user(chat_id)
        elif choice == '4':
            test_current_users()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")
