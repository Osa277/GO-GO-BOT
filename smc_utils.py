def detect_smt_es(df, lookback=10):
    """Detect basic SMT (liquidity sweep) and ES (equilibrium zone) patterns."""
    # SMT: wick above/below recent highs/lows (liquidity sweep)
    # ES: price consolidates in a tight range (supply/demand balance)
    smt_signal = None
    es_zone = None
    if len(df) < lookback + 2:
        return smt_signal, es_zone
    recent_highs = df['high'].iloc[-lookback-2:-2]
    recent_lows = df['low'].iloc[-lookback-2:-2]
    last_high = df['high'].iloc[-2]
    last_low = df['low'].iloc[-2]
    curr_high = df['high'].iloc[-1]
    curr_low = df['low'].iloc[-1]
    # SMT: wick above previous highs (bullish sweep)
    if curr_high > max(recent_highs):
        smt_signal = 'bullish_sweep'
    # SMT: wick below previous lows (bearish sweep)
    elif curr_low < min(recent_lows):
        smt_signal = 'bearish_sweep'
    # ES: tight range in last N candles
    range_high = max(df['high'].iloc[-lookback:])
    range_low = min(df['low'].iloc[-lookback:])
    if (range_high - range_low) / df['close'].iloc[-1] < 0.01:
        es_zone = (range_low, range_high)
    return smt_signal, es_zone
def detect_fvg(df, lookback=3):
    """Detect Fair Value Gap (FVG) in the last `lookback` candles."""
    # FVG: gap between previous candle's low and next candle's high (for bullish), or high and next low (for bearish)
    fvg_signals = []
    for i in range(len(df) - lookback, len(df) - 1):
        prev_low = df['low'].iloc[i - 1]
        curr_high = df['high'].iloc[i]
        next_low = df['low'].iloc[i + 1]
        prev_high = df['high'].iloc[i - 1]
        curr_low = df['low'].iloc[i]
        next_high = df['high'].iloc[i + 1]
        # Bullish FVG: previous low < current high < next low
        if curr_high > prev_low and next_low > curr_high:
            fvg_signals.append({'type': 'bullish', 'index': i, 'price': curr_high})
        # Bearish FVG: previous high > current low > next high
        if curr_low < prev_high and next_high < curr_low:
            fvg_signals.append({'type': 'bearish', 'index': i, 'price': curr_low})
    return fvg_signals
import pandas as pd
import numpy as np
from pandas import DataFrame
from datetime import datetime
import logging
from config import SYMBOLS, TIMEFRAMES, EMA_PERIOD, RR_MULTIPLIERS, SYMBOL_SETTINGS

def calculate_realistic_tp_sl(symbol, entry_price, side, current_atr):
    """Calculate realistic TP and SL based on symbol-specific settings and ATR."""
    # Default settings if symbol not found
    default_config = {
        'max_sl_distance': 100,
        'min_tp_distance': 50,
        'atr_multiplier_sl': 1.0,
        'atr_multiplier_tp': 1.5
    }
    symbol_config = SYMBOL_SETTINGS.get(symbol, default_config)

    # Use ATR and timeframe to make TP/SL dynamic
    # Example: Increase TP/SL for higher timeframes
    # Assume timeframe is a string like 'M3', 'M5', 'H1', etc.
    tf_map = {'M3': 1, 'M5': 2, 'M15': 3, 'M30': 4, 'H1': 5, 'H4': 6}
    tf_factor = tf_map.get(str(symbol_config.get('tf', 'M3')), tf_map.get(str(symbol_config.get('tf', 'M3')), 1))
    # If tf not in config, fallback to passed timeframe if available
    if 'tf' not in symbol_config:
        tf_factor = tf_map.get(str(symbol_config.get('tf', 'M3')), 1)

    # If timeframe is passed as argument, use it
    import inspect
    frame = inspect.currentframe().f_back
    timeframe = frame.f_locals.get('timeframe', 'M3')
    tf_factor = tf_map.get(str(timeframe), 1)

    # Adjust ATR multipliers by timeframe factor
    atr_multiplier_sl = symbol_config['atr_multiplier_sl'] * (0.8 + 0.2 * tf_factor)
    atr_multiplier_tp = symbol_config['atr_multiplier_tp'] * (0.8 + 0.2 * tf_factor)

    if side == 'buy':
        atr_based_sl = entry_price - (current_atr * atr_multiplier_sl)
        point_value = 1.0 if symbol in ['BTCUSD', 'ETHUSD'] else 0.01
        max_sl_distance = symbol_config['max_sl_distance'] * point_value * (0.8 + 0.2 * tf_factor)
        max_sl = entry_price - max_sl_distance
        sl = max(atr_based_sl, max_sl)
    else:
        atr_based_sl = entry_price + (current_atr * atr_multiplier_sl)
        point_value = 1.0 if symbol in ['BTCUSD', 'ETHUSD'] else 0.01
        max_sl_distance = symbol_config['max_sl_distance'] * point_value * (0.8 + 0.2 * tf_factor)
        max_sl = entry_price + max_sl_distance
        sl = min(atr_based_sl, max_sl)

    risk = abs(entry_price - sl)
    tp_levels = []
    rr = RR_MULTIPLIERS.get(symbol, 1.5)
    # Generate up to 5 TP levels as multiples of RR and timeframe factor
    tp_multipliers = [1, 1.5, 2, 2.5, 3]
    for mult in tp_multipliers:
        if side == 'buy':
            tp = entry_price + (risk * rr * mult * (0.8 + 0.2 * tf_factor))
        else:
            tp = entry_price - (risk * rr * mult * (0.8 + 0.2 * tf_factor))
        tp_levels.append(round(tp, 5))
    return {'sl': round(sl, 5), 'tp_levels': tp_levels}

def generate_realistic_signal(symbol, timeframe, df, trend='bullish'):
    """Generate trading signal with realistic TP/SL levels"""
    # Robust signal generation with explicit structure and logging

    # Support both BTCUSD and XAUUSD
    if symbol not in ['BTCUSD', 'XAUUSD']:
        logging.info(f"[SignalGen] Skipping unsupported symbol: {symbol}")
        return None

    # Minimal data check for faster signals
    if df is None or len(df) < 20:
        logging.debug(f"[SignalGen] DataFrame is None or too short for {symbol} {timeframe}")
        return None

    current_price = float(df['close'].iloc[-1])
    current_atr = float(atr(df))

    # Use EMA and RSI to determine bullish or bearish
    ema_20 = df['close'].rolling(20).mean().iloc[-1]
    ema_50 = df['close'].rolling(50).mean().iloc[-1]
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    rsi_last = rsi.iloc[-1]

    if ema_20 > ema_50 and rsi_last > 55:
        side = 'buy'
        trend = 'bullish'
    elif ema_20 < ema_50 and rsi_last < 45:
        side = 'sell'
        trend = 'bearish'
    else:
        logging.info(f"[SignalGen] No strong bullish or bearish signal for BTCUSD.")
        return None

    entry = current_price
    tp_sl_data = calculate_realistic_tp_sl(symbol, entry, side, current_atr)
    if not tp_sl_data or 'tp_levels' not in tp_sl_data or len(tp_sl_data['tp_levels']) < 5:
        logging.error(f"[SignalGen] Invalid TP/SL data for {symbol} {timeframe}: {tp_sl_data}")
        return None

    # Build the signal dictionary with high confidence
    signal = {
        'symbol': symbol,
        'timeframe': timeframe,
        'tf': timeframe,
        'side': side,
        'order_type': side,
        'entry': round(entry, 5),
        'sl': tp_sl_data['sl'],
        'tp.1': tp_sl_data['tp_levels'][0],
        'tp.2': tp_sl_data['tp_levels'][1],
        'tp.3': tp_sl_data['tp_levels'][2],
        'tp.4': tp_sl_data['tp_levels'][3],
        'tp.5': tp_sl_data['tp_levels'][4],
        'tp': tp_sl_data['tp_levels'],
        'confidence': 99.0,
        'rr_ratio': 2.0,
        'atr': round(current_atr, 5),
        'risk': round(abs(entry - tp_sl_data['sl']), 2),
        'trend': trend,
        'timestamp': datetime.now().isoformat(),
        'realistic_levels': True,
        'fvg_type': None,
        'fvg_price': None,
        'smt_signal': None,
        'es_zone': None,
        'extra1': None,
        'extra2': None
    }
    logging.info(f"[SignalGen] BTCUSD 99% {trend} signal generated: {signal}")
    try:
        from mt5_data import execute_signal_mt5
        execute_signal_mt5(signal, volume=0.01)
    except Exception as e:
        logging.error(f"[SignalGen] Could not place live MT5 order: {e}")
    return signal

def generate_signal(df, symbol, timeframe, rr_multipliers):
    """Legacy wrapper for backward compatibility - uses realistic signal generation"""
    if df is None or len(df) < 50:
        return []

    ema_20 = df['close'].rolling(20).mean().iloc[-1]
    ema_50 = df['close'].rolling(50).mean().iloc[-1]
    current_price = df['close'].iloc[-1]

    # Calculate RSI for confirmation
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    rsi_last = rsi.iloc[-1]

    # Bullish: EMA20 > EMA50 and RSI > 55
    if ema_20 > ema_50 and rsi_last > 55:
        signal = generate_realistic_signal(symbol, timeframe, df, 'bullish')
    # Bearish: EMA20 < EMA50 and RSI < 45
    elif ema_20 < ema_50 and rsi_last < 45:
        signal = generate_realistic_signal(symbol, timeframe, df, 'bearish')
    else:
        signal = None

    return [signal] if signal else []

def atr(df, period=14):
    """Calculate ATR for dynamic TP/SL."""
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean().iloc[-1]

print(" smc_utils loaded with realistic TP/SL system")
