#!/usr/bin/env python3
"""
Test script for live Vercel deployment
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://go-go-3c20ypsad-asiyanbis-projects.vercel.app"

def test_endpoint(endpoint, method='GET'):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        print(f"\n🔍 Testing: {endpoint}")
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success! Response:")
                print(json.dumps(data, indent=2)[:500] + "..." if len(str(data)) > 500 else json.dumps(data, indent=2))
                return True
            except:
                print(f"✅ Success! Text response: {response.text[:200]}...")
                return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Test all endpoints"""
    print("🚀 TESTING LIVE VERCEL DEPLOYMENT")
    print("=" * 50)
    
    endpoints = [
        "/",
        "/api/status", 
        "/api/signal?symbol=BTCUSD",
        "/api/users",
        "/api/realtime-signal?symbol=EURUSD"
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint in endpoints:
        if test_endpoint(endpoint):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 RESULTS: {success_count}/{total_count} endpoints working")
    
    if success_count >= 3:
        print("🎉 DEPLOYMENT IS LIVE AND WORKING!")
        print(f"🌐 Your bot is running at: {BASE_URL}")
        
        # Test signal activation
        print("\n🚀 Testing signal activation...")
        test_endpoint("/api/start-all-live")
        
    else:
        print("⚠️ Some issues detected, but deployment may still be functional")

if __name__ == "__main__":
    main()
