# config.py - Trading Bot Configuration

SYMBOLS = [
    'BTCUSD', 'XAUUSD', 'US30'
]

TIMEFRAMES = [
    'M3', 'M5', 'M15'
]

RR_MULTIPLIERS = {
    'BTCUSD': 2.0,
    'ETHUSD': 2.0,
    'EURUSD': 1.5,
    'GBPUSD': 1.5,
    'USDJPY': 1.2,
    'XAUUSD': 1.8,
    'US30': 1.5,
    'NAS100': 1.6
}

MAX_OPEN_TRADES = 5
DAILY_LOSS_LIMIT = 0.05

trade_stats = {
    'account_balance': 0,
    'daily_pnl': 0,
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0
}

LOG_LEVEL = 'INFO'

# Additional config for smc_utils.py compatibility
EMA_PERIOD = 20
SYMBOL_SETTINGS = {
    'BTCUSD': {'min_tp': 200, 'min_sl': 50, 'atr_multiplier_sl': 2.0, 'atr_multiplier_tp': 4.0, 'max_sl_distance': 300, 'min_tp_distance': 200},
    'ETHUSD': {'min_tp': 80, 'min_sl': 40, 'atr_multiplier_sl': 2.0, 'atr_multiplier_tp': 3.0, 'max_sl_distance': 160, 'min_tp_distance': 80},
    'EURUSD': {'min_tp': 30, 'min_sl': 15, 'atr_multiplier_sl': 1.5, 'atr_multiplier_tp': 2.0, 'max_sl_distance': 60, 'min_tp_distance': 30},
    'GBPUSD': {'min_tp': 30, 'min_sl': 15, 'atr_multiplier_sl': 1.5, 'atr_multiplier_tp': 2.0, 'max_sl_distance': 60, 'min_tp_distance': 30},
    'USDJPY': {'min_tp': 20, 'min_sl': 10, 'atr_multiplier_sl': 1.2, 'atr_multiplier_tp': 1.8, 'max_sl_distance': 40, 'min_tp_distance': 20},
    'XAUUSD': {'min_tp': 100, 'min_sl': 25, 'atr_multiplier_sl': 1.8, 'atr_multiplier_tp': 3.5, 'max_sl_distance': 200, 'min_tp_distance': 100}
}

# Telegram configuration for telegram_utils.py
TELEGRAM_TOKEN = '8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro'
TELEGRAM_CHAT_ID = '5362504152'

# Multiple users support - Add chat IDs directly in telegram_utils.py TELEGRAM_USERS list

# Signal-only mode configuration - IMPORTANT for zero balance trading
SIGNAL_ONLY_MODE = True  # Set to True to generate signals regardless of balance
IGNORE_ACCOUNT_BALANCE = True  # Set to True to ignore account balance checks
