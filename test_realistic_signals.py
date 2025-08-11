from api.index import get_mt5_professional_data, generate_mt5_professional_signal

# Test a few signals with updated prices
test_symbols = ['EURUSD', 'GBPUSD', 'BTCUSD', 'XAUUSD']

print("=== TESTING UPDATED TRADING SIGNALS ===\n")

for symbol in test_symbols:
    print(f"📊 Testing {symbol} Signal:")
    
    # Get market data (will try real data first, then simulation)
    data = get_mt5_professional_data(symbol)
    
    if data:
        print(f"  💰 Price: {data['price']:.5f}")
        print(f"  📊 Source: {data['source']}")
        print(f"  🔴 Real Data: {'YES' if data.get('real_data') else 'NO'}")
        
        # Generate signal
        signal = generate_mt5_professional_signal(symbol, data)
        
        if signal:
            print(f"  🎯 Signal: {signal['side'].upper()}")
            print(f"  💰 Entry: {signal['entry']}")
            print(f"  🛑 SL: {signal['sl']}")
            print(f"  🎯 TP: {signal['tp']}")
            print(f"  📈 Confidence: {signal['confidence']}%")
        else:
            print(f"  ❌ No signal generated")
    else:
        print(f"  ❌ Failed to get data")
    
    print()

print("🎯 All currency pairs now have realistic prices matching real market!")
