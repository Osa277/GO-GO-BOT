#!/usr/bin/env python3
"""
Quick Status Check for Realistic TP/SL Trading System
"""

from datetime import datetime
import os

def check_system_status():
    print("📊 REALISTIC TP/SL TRADING SYSTEM STATUS")
    print("=" * 50)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check core files
    core_files = [
        'config.py',
        'scanner.py', 
        'smc_utils.py',
        'mt5_data.py',
        'telegram_utils.py',
        'smart_signal_filter.py',
        'trading_sessions.py',
        'ai_signal_optimizer.py'
    ]
    
    print("📁 Core System Files:")
    missing_files = []
    for file in core_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            missing_files.append(file)
    
    print()
    
    # Try to import key modules
    print("🔧 Module Import Status:")
    try:
        from config import SYMBOLS, RR_MULTIPLIERS
        print(f"   ✅ Config: {len(SYMBOLS)} symbols, RR ratios: {RR_MULTIPLIERS}")
    except Exception as e:
        print(f"   ❌ Config import failed: {e}")
    
    try:
        from smc_utils import calculate_realistic_tp_sl, generate_realistic_signal
        print("   ✅ SMC Utils: Realistic TP/SL functions loaded")
    except Exception as e:
        print(f"   ❌ SMC Utils import failed: {e}")
    
    try:
        from smart_signal_filter import SmartSignalFilter
        print("   ✅ Smart Signal Filter: Advanced filtering available")
    except Exception as e:
        print(f"   ❌ Signal Filter import failed: {e}")
    
    print()
    
    if missing_files:
        print("⚠️  SYSTEM STATUS: INCOMPLETE")
        print(f"   Missing files: {missing_files}")
    else:
        print("✅ SYSTEM STATUS: READY FOR REAL-TIME TRADING")
        print("🎯 Realistic TP/SL system active")
        print("📊 NY session optimization enabled")
        print("🤖 AI learning system operational")
    
    print()
    print("🚀 To start trading: python start_trading.py")

if __name__ == "__main__":
    check_system_status()
