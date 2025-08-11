from api.index import get_yahoo_finance_real_data, get_enhanced_professional_data

# Test all currency pairs
symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'NZDUSD', 'USDCAD', 'BTCUSD', 'XAUUSD', 'US30']

print("=== CHECKING ALL CURRENCY PAIRS ===\n")

real_prices = {}
sim_prices = {}

for symbol in symbols:
    print(f"📊 Testing {symbol}:")
    
    # Get real data
    real_data = get_yahoo_finance_real_data(symbol)
    if real_data:
        real_price = real_data['price']
        real_prices[symbol] = real_price
        print(f"  ✅ REAL: {real_price}")
    else:
        print(f"  ❌ REAL: Failed")
        real_prices[symbol] = None
    
    # Get simulation data
    sim_data = get_enhanced_professional_data(symbol)
    sim_price = sim_data['price']
    sim_prices[symbol] = sim_price
    print(f"  📊 SIM:  {sim_price:.5f}")
    
    print()

print("\n=== SUMMARY: REAL vs SIMULATION ===")
for symbol in symbols:
    real = real_prices[symbol]
    sim = sim_prices[symbol]
    if real:
        difference = abs(real - sim) / real * 100
        status = "✅ CLOSE" if difference < 5 else "❌ FAR"
        print(f"{symbol:8} | Real: {real:8.5f} | Sim: {sim:8.5f} | Diff: {difference:5.1f}% {status}")
    else:
        print(f"{symbol:8} | Real: FAILED    | Sim: {sim:8.5f}")
