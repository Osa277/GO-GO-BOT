from api.index import get_yahoo_finance_real_data

# Test current gold price
result = get_yahoo_finance_real_data('XAUUSD')
if result:
    print(f"Current Gold (XAUUSD): {result['price']}")
    print(f"Source: {result['source']}")
else:
    print("Failed to get gold price")
