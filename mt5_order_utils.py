import MetaTrader5 as mt5
import logging

def place_mt5_order(symbol, side, volume, price, sl, tp):
    """Place a live order on MetaTrader5."""
    if not mt5.initialize():
        logging.error(f"MT5 initialize() failed: {mt5.last_error()}")
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
        logging.error(f"Order send failed: {result.retcode} {result.comment}")
        return False
    logging.info(f"Order placed: {result}")
    return True
