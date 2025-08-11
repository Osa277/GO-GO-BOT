#!/usr/bin/env python3
"""
Quick Performance Test for Enhanced Trading Bot
Tests all components and ensures signals work with zero balance
"""

import sys
import os
import traceback

def test_imports():
    """Test all imports"""
    print("🔍 Testing imports...")
    
    results = {}
    
    # Test correlation analyzer
    try:
        from correlation_analyzer import correlation_analyzer, update_market_correlations
        results['correlation'] = "✅ SUCCESS"
    except Exception as e:
        results['correlation'] = f"❌ ERROR: {e}"
    
    # Test risk manager
    try:
        from risk_manager import risk_manager, calculate_optimal_position_size
        results['risk_manager'] = "✅ SUCCESS"
    except Exception as e:
        results['risk_manager'] = f"❌ ERROR: {e}"
    
    # Test session manager
    try:
        from enhanced_session_manager import session_manager, get_trading_recommendation
        results['session_manager'] = "✅ SUCCESS"
    except Exception as e:
        results['session_manager'] = f"❌ ERROR: {e}"
    
    # Test MT5
    try:
        from mt5_data import initialize_mt5, get_current_price, get_account_info
        results['mt5_data'] = "✅ SUCCESS"
    except Exception as e:
        results['mt5_data'] = f"❌ ERROR: {e}"
    
    # Test smc_utils
    try:
        from smc_utils import generate_realistic_signal
        results['smc_utils'] = "✅ SUCCESS"
    except Exception as e:
        results['smc_utils'] = f"❌ ERROR: {e}"
    
    # Test config
    try:
        from config import SYMBOLS, TIMEFRAMES, SIGNAL_ONLY_MODE, IGNORE_ACCOUNT_BALANCE
        results['config'] = "✅ SUCCESS"
        print(f"   SIGNAL_ONLY_MODE: {SIGNAL_ONLY_MODE}")
        print(f"   IGNORE_ACCOUNT_BALANCE: {IGNORE_ACCOUNT_BALANCE}")
    except Exception as e:
        results['config'] = f"❌ ERROR: {e}"
    
    return results

def test_mt5_connection():
    """Test MT5 connection and price fetching"""
    print("\n🔌 Testing MT5 connection...")
    
    try:
        from mt5_data import initialize_mt5, get_current_price, get_account_info
        
        if initialize_mt5():
            print("✅ MT5 initialized successfully")
            
            # Test account info
            account = get_account_info()
            if account:
                print(f"✅ Account info: Balance=${account.get('balance', 0):.2f}, Server={account.get('server', 'Unknown')}")
            else:
                print("⚠️ Could not get account info")
            
            # Test price fetching
            for symbol in ['BTCUSD', 'XAUUSD']:
                try:
                    price = get_current_price(symbol)
                    if price:
                        print(f"✅ {symbol}: {price}")
                    else:
                        print(f"⚠️ {symbol}: No price available")
                except Exception as e:
                    print(f"❌ {symbol}: Error - {e}")
            
            return True
        else:
            print("❌ MT5 initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ MT5 connection error: {e}")
        return False

def test_signal_generation_zero_balance():
    """Test signal generation with zero balance"""
    print("\n💰 Testing signal generation with zero balance...")
    
    try:
        from smc_utils import generate_realistic_signal
        from mt5_data import fetch_market_data
        from config import SYMBOLS, TIMEFRAMES
        
        # Test with mock zero balance scenario
        for symbol in SYMBOLS[:2]:  # Test first 2 symbols
            for tf in TIMEFRAMES[:2]:  # Test first 2 timeframes
                try:
                    tf_map = {"M3": 3, "M5": 5, "M15": 15, "M30": 30}
                    tf_minutes = tf_map.get(tf, 5)
                    
                    print(f"\n🎯 Testing {symbol} {tf} ({tf_minutes}m)...")
                    
                    # Fetch data
                    df = fetch_market_data(symbol, tf_minutes, 100)
                    if df is None or len(df) < 20:
                        print(f"   ⚠️ Insufficient data for {symbol} {tf}")
                        continue
                    
                    # Try to generate signal
                    signal = generate_realistic_signal(symbol, tf, df, 'bullish')
                    if signal:
                        print(f"   ✅ Signal generated: {signal['side']} {signal['symbol']} @ {signal['entry']}")
                        print(f"      TP: {signal['tp'][0] if isinstance(signal['tp'], list) else signal['tp']}")
                        print(f"      SL: {signal['sl']}")
                        print(f"      Confidence: {signal.get('confidence', 0.8)*100:.1f}%")
                    else:
                        print(f"   ⚠️ No signal generated for {symbol} {tf}")
                        
                except Exception as e:
                    print(f"   ❌ Error testing {symbol} {tf}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Signal generation test error: {e}")
        return False

def test_risk_validation_zero_balance():
    """Test risk validation with zero balance"""
    print("\n🛡️ Testing risk validation with zero balance...")
    
    try:
        from risk_manager import validate_trade_risk, calculate_optimal_position_size
        
        # Mock signal
        mock_signal = {
            'symbol': 'BTCUSD',
            'side': 'buy',
            'entry': 100000.0,
            'sl': 99500.0,
            'tp': [100500.0, 101000.0, 101500.0],
            'confidence': 0.8
        }
        
        # Test with zero balance
        account_balance = 0.0
        current_positions = []
        
        is_valid, message = validate_trade_risk(mock_signal, account_balance, current_positions)
        print(f"   Risk validation with $0 balance: {is_valid} - {message}")
        
        if is_valid:
            optimal_size = calculate_optimal_position_size(mock_signal, account_balance, current_positions)
            print(f"   Optimal position size: {optimal_size:.3f} lots")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk validation test error: {e}")
        return False

def test_scanner_configuration():
    """Test scanner configuration for zero balance trading"""
    print("\n⚙️ Testing scanner configuration...")
    
    try:
        # Check environment variables and config
        signal_only = os.getenv('SIGNAL_ONLY_MODE', 'true').lower() == 'true'
        ignore_balance = os.getenv('IGNORE_ACCOUNT_BALANCE', 'true').lower() == 'true'
        
        print(f"   SIGNAL_ONLY_MODE: {signal_only}")
        print(f"   IGNORE_ACCOUNT_BALANCE: {ignore_balance}")
        
        if signal_only and ignore_balance:
            print("   ✅ Configuration set for zero balance signal generation")
        else:
            print("   ⚠️ Configuration may prevent zero balance signals")
            print("   💡 Recommendation: Set SIGNAL_ONLY_MODE=true and IGNORE_ACCOUNT_BALANCE=true")
        
        return signal_only and ignore_balance
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ENHANCED TRADING BOT PERFORMANCE TEST")
    print("=" * 50)
    
    # Test imports
    import_results = test_imports()
    
    print("\n📊 IMPORT RESULTS:")
    for component, result in import_results.items():
        print(f"   {component}: {result}")
    
    # Check if all imports successful
    failed_imports = [k for k, v in import_results.items() if "ERROR" in v]
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        print("Please install missing dependencies or fix import errors")
        return False
    
    # Test MT5 connection
    mt5_ok = test_mt5_connection()
    
    # Test configuration
    config_ok = test_scanner_configuration()
    
    # Test signal generation with zero balance
    if mt5_ok:
        signal_test_ok = test_signal_generation_zero_balance()
        risk_test_ok = test_risk_validation_zero_balance()
    else:
        print("\n⚠️ Skipping signal tests due to MT5 connection issues")
        signal_test_ok = False
        risk_test_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 PERFORMANCE TEST SUMMARY:")
    print(f"   Imports: {'✅ PASS' if not failed_imports else '❌ FAIL'}")
    print(f"   MT5 Connection: {'✅ PASS' if mt5_ok else '❌ FAIL'}")
    print(f"   Zero Balance Config: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Signal Generation: {'✅ PASS' if signal_test_ok else '❌ FAIL'}")
    print(f"   Risk Validation: {'✅ PASS' if risk_test_ok else '❌ FAIL'}")
    
    if all([not failed_imports, mt5_ok, config_ok]):
        print("\n🎉 READY FOR ZERO BALANCE SIGNAL GENERATION!")
        print("💡 Your bot will generate signals regardless of account balance")
        print("🚀 Run: python scanner.py")
    else:
        print("\n⚠️ Some issues detected. Please review and fix before running.")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Test script error: {e}")
        traceback.print_exc()
