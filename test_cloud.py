#!/usr/bin/env python3
"""
Cloud Signal Generator Test
Test the Vercel deployment directly
"""
import requests
import json
from datetime import datetime

# Your cloud URL
CLOUD_URL = "https://go-go-nfoxqvmeb-asiyanbis-projects.vercel.app"

def test_cloud_endpoints():
    """Test all cloud endpoints"""
    
    endpoints = [
        "",  # Main endpoint
        "/api/status",
        "/api/signal",
        "/api/signal?symbol=BTCUSD",
        "/api/send-signal?symbol=BTCUSD",
        "/api/users",
        "/api/test-users"
    ]
    
    print("🧪 Testing Cloud Signal Generator...")
    print(f"📍 URL: {CLOUD_URL}")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{CLOUD_URL}{endpoint}"
        try:
            print(f"\n🔗 Testing: {endpoint or '/'}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.status_code}")
                try:
                    data = response.json()
                    print(f"📊 Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"📄 Response: {response.text[:200]}...")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"📄 Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"🚫 ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Testing signal generation...")
    
    # Test specific signal generation
    try:
        response = requests.get(f"{CLOUD_URL}/api/send-signal?symbol=BTCUSD", timeout=15)
        if response.status_code == 200:
            print("✅ Signal generation working!")
            data = response.json()
            print(f"📊 Signal: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Signal generation failed: {response.status_code}")
    except Exception as e:
        print(f"🚫 Signal test error: {e}")

if __name__ == "__main__":
    test_cloud_endpoints()
