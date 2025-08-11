# mt5_data.py - MetaTrader5 Data Interface (real integration template)

import MetaTrader5 as mt5
import pandas as pd

def initialize_mt5():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() failed: {mt5.last_error()}")
    return True

def shutdown_mt5():
    mt5.shutdown()

def fetch_market_data(symbol, tf_minutes, bars):
    timeframe_map = {
        3: mt5.TIMEFRAME_M3,
        5: mt5.TIMEFRAME_M5,
        15: mt5.TIMEFRAME_M15,
        240: mt5.TIMEFRAME_H4,
        1440: mt5.TIMEFRAME_D1
    }
    tf = timeframe_map.get(tf_minutes)
    if tf is None:
        raise ValueError(f"Unsupported timeframe: {tf_minutes}")
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No data for {symbol} {tf_minutes}m")
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"No tick data for {symbol}")
    return tick.ask if tick.ask > 0 else tick.bid

def get_account_info():
    info = mt5.account_info()
    if info is None:
        raise RuntimeError("MT5 account_info() failed")
    return {
        'login': info.login,
        'balance': info.balance,
        'equity': info.equity,
        'server': info.server,
        'trade_mode': info.trade_mode
    }

def get_symbol_info(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        raise RuntimeError(f"No info for symbol {symbol}")
    return info._asdict()

def place_mt5_order(symbol, side, volume, price, sl, tp):
    """Place a live order on MetaTrader5."""
    if not mt5.initialize():
        print(f"MT5 initialize() failed: {mt5.last_error()}")
        return False
    order_type = mt5.ORDER_TYPE_BUY if side == 'buy' else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "AutoTrade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order send failed: {result.retcode} {result.comment}")
        return False
    print(f"Order placed: {result}")
    return True

def execute_signal_mt5(signal, volume=0.01):
    """Execute a signal dict as a live MT5 order. Call this from your signal logic."""
    print("[MT5 DEBUG] Incoming signal:", signal)
    tf_val = signal.get('tf', None)
    print(f"[MT5 DEBUG] Signal tf value: {tf_val}")
    
    # Check if we're in signal-only mode
    from config import SIGNAL_ONLY_MODE, IGNORE_ACCOUNT_BALANCE
    
    if SIGNAL_ONLY_MODE or IGNORE_ACCOUNT_BALANCE:
        print("[MT5 DEBUG] Signal-only mode enabled. Signal will be sent via Telegram only.")
        return True  # Return True to indicate signal was "processed"
    
    # Execute for any timeframe if live trading is enabled
    if tf_val in [3, 5, 15, '3', '5', '15', '3m', '5m', '15m', 'M3', 'M5', 'M15']:
        print(f"[MT5 DEBUG] Signal is {tf_val}. Proceeding with order.")
        return place_mt5_order(
            symbol=signal['symbol'],
            side=signal['side'],
            volume=volume,
            price=signal['entry'],
            sl=signal['sl'],
            tp=signal['tp.1']  # Or use any TP level you want
        )
    else:
        print(f"[MT5 DEBUG] Signal timeframe {tf_val} not supported. Skipping order execution.")
        return False
