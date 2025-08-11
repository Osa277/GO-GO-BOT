#!/usr/bin/env python3
"""
Real-Time Trading Bot with Realistic TP/SL System
Clean startup script for the optimized trading system
"""

import os
import sys
import time
import logging
from datetime import datetime

def main():
    print("🚀 STARTING REALISTIC TP/SL TRADING SYSTEM")
    print("=" * 50)
    
    try:
        # Test imports first
        print("🔧 Testing imports...")
        
        from config import SYMBOLS, TIMEFRAMES
        print("✅ Config imported")
        
        from smc_utils import generate_realistic_signal
        print("✅ SMC Utils imported")
        
        from scanner import MT5SignalBot
        print("✅ Scanner imported")
        
        print(f"📊 Trading symbols: {SYMBOLS}")
        print(f"⏰ Timeframes: {TIMEFRAMES}")
        print(f"🎯 Using realistic TP/SL with conservative RR ratios")
        print()
        
        # Initialize scanner
        bot = MT5SignalBot()
        print("✅ Trading bot initialized")
        
        # Start the main trading loop
        print("🔄 Starting real-time trading with realistic levels...")
        print("💡 Press Ctrl+C to stop")
        print()
        
        bot.scan_realtime()
        
    except KeyboardInterrupt:
        print("\n⏹️  Trading stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("📊 Trading session ended")

if __name__ == "__main__":
    main()
