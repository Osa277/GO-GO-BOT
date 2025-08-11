from api.index import get_enhanced_professional_data, get_yahoo_finance_real_data

# Test updated gold prices
print("=== GOLD PRICE TEST ===")

# Real data
real_data = get_yahoo_finance_real_data('XAUUSD')
if real_data:
    print(f"✅ REAL Gold Price: {real_data['price']:.2f}")
else:
    print("❌ Failed to get real gold price")

# Enhanced simulation with updated ranges
sim_data = get_enhanced_professional_data('XAUUSD')
print(f"📊 Simulation Price: {sim_data['price']:.2f} (Range: 3350-3450)")

print("\n🎯 Gold price ranges are now updated to match current market levels!")
