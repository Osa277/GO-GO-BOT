import time
import sys
import logging
import signal
import threading
from datetime import datetime, timedelta
from config import SYMBOLS, TIMEFRAMES, RR_MULTIPLIERS, MAX_OPEN_TRADES, DAILY_LOSS_LIMIT, trade_stats, LOG_LEVEL

# Enhanced logging setup with Unicode support
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
import requests

logger = logging.getLogger(__name__)


# --- Real-time price fetch for BTCUSD and XAUUSD using Binance API ---
def get_binance_price(symbol):
    symbol_map = {
        'BTCUSD': 'BTCUSDT',
        'XAUUSD': 'XAUUSDT'
    }
    binance_symbol = symbol_map.get(symbol, symbol)
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={binance_symbol}'
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        logger.error(f"Binance price fetch error for {symbol}: {e}")
        return None

# Dummy functions for MT5 compatibility (for other symbols)
import pandas as pd
def fetch_market_data(symbol, tf_minutes, bars):
    # Only support BTCUSD and XAUUSD for cloud
    symbol_map = {
        'BTCUSD': 'BTCUSDT',
        'XAUUSD': 'XAUUSDT'
    }
    if symbol not in symbol_map:
        return None
    binance_symbol = symbol_map[symbol]
    # Binance interval map
    interval_map = {1: '1m', 3: '3m', 5: '5m', 15: '15m', 30: '30m', 60: '1h', 240: '4h', 1440: '1d'}
    interval = interval_map.get(tf_minutes, '1m')
    url = f'https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval={interval}&limit={bars}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        # Format to pandas DataFrame
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception as e:
        logger.error(f"Binance OHLCV fetch error for {symbol}: {e}")
        return None
def get_current_price(symbol):
    if symbol in ['BTCUSD', 'XAUUSD']:
        return get_binance_price(symbol)
    return None
def get_account_info():
    return {'balance': 10000, 'equity': 10000, 'server': 'Binance', 'trade_mode': 2}
def get_symbol_info(symbol):
    return {}
def initialize_mt5():
    return True
def shutdown_mt5():
    pass

from smc_utils import generate_realistic_signal, calculate_realistic_tp_sl, atr
from telegram_utils import send_enhanced_alert, send_trade_update, send_performance_update, send_system_alert
import os

# Import advanced analytics
try:
    from advanced_analytics import AdvancedSignalAnalytics
    from price_monitor import BitcoinPriceMonitor
    from realtime_tp_calculator import RealTimeTPCalculator
    from smart_signal_filter import SmartSignalFilter
    from performance_monitor import performance_monitor
    from ai_signal_optimizer import record_signal_for_ai_learning, get_ai_probability_adjustments
    from automated_backtester import get_optimal_trading_parameters
    from pre_signal_alert import PreSignalAlertSystem
    from risk_manager import risk_manager, calculate_optimal_position_size, validate_trade_risk
    from enhanced_session_manager import session_manager, get_session_multipliers, get_trading_recommendation
    from correlation_analyzer import correlation_analyzer, get_correlation_advice, update_market_correlations
    ADVANCED_FEATURES = True
    print("✅ Advanced analytics loaded")
    print("🎯 Real-time TP probability calculator loaded")
    print("🔍 Smart signal quality filter loaded")
    print("📊 Performance monitor loaded")
    print("🤖 AI signal optimizer loaded")
    print("📈 Automated backtester loaded")
    print("⚡ Pre-signal alert system loaded")
    print("🛡️ Advanced risk manager loaded")
    print("🌍 Enhanced session manager loaded")
    print("🔗 Market correlation analyzer loaded")
except ImportError as e:
    ADVANCED_FEATURES = False
    print(f"⚠️ Advanced features not available: {e}")

# Real-time configuration
TF_MAP = {"M1": 1, "M3": 3, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 10))
COOLDOWN_SECONDS = 60

# Signal-only mode configuration
SIGNAL_ONLY_MODE = os.getenv('SIGNAL_ONLY_MODE', 'true').lower() == 'true'
IGNORE_ACCOUNT_BALANCE = os.getenv('IGNORE_ACCOUNT_BALANCE', 'true').lower() == 'true'

# Global state
open_trades = []
last_alert_time = {}
last_performance_update = datetime.now().date()
bot_start_time = datetime.now()
account_info = None

def is_market_open():
    """Check if market is open - Bitcoin trades 24/7, Forex has specific hours"""
    from config import SYMBOLS
    
    # Check if any crypto symbols are in the list
    crypto_symbols = ['BTCUSD', 'ETHUSD', 'LTCUSD', 'XRPUSD', 'ADAUSD', 'DOTUSD']
    has_crypto = any(symbol in SYMBOLS for symbol in crypto_symbols)
    
    # If we have crypto symbols, market is always open (24/7)
    if has_crypto:
        logger.info("CRYPTO MARKET: Always open (24/7)")
        return True
    
    # For forex only - traditional market hours
    current_hour = datetime.now().hour
    weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
    
    # Forex market hours (UTC): Sunday 22:00 - Friday 22:00
    if weekday == 6:  # Sunday
        return current_hour >= 22  # Sunday 22:00 onwards
    elif weekday == 5:  # Saturday
        return current_hour < 22   # Until Friday 22:00
    else:  # Monday-Friday
        return True

def manage_trade(trade, current_price):
    """Enhanced trade management for MT5 signals"""
    try:
        # Calculate current P&L in pips
        if trade['side'] == 'buy':
            pnl_pips = (current_price - trade['entry']) * 10000  # For 5-digit quotes
        else:
            pnl_pips = (trade['entry'] - current_price) * 10000
        
        trade['current_pnl_pips'] = pnl_pips
        
        # Trail stop logic (basic)
        if pnl_pips > 20:  # If in profit by 20+ pips
            if trade['side'] == 'buy':
                new_sl = max(trade['sl'], current_price - (20 * 0.0001))  # Trail 20 pips
            else:
                new_sl = min(trade['sl'], current_price + (20 * 0.0001))
            
            if new_sl != trade['sl']:
                logger.info(f"TRAIL STOP: {trade['symbol']} SL moved to {new_sl:.5f}")
                trade['sl'] = new_sl
        
    except Exception as e:
        logger.error(f"Trade management error: {e}")

class MT5SignalBot:
    def __init__(self):
        self.running = False
        self.setup_signal_handlers()
        self.performance_lock = threading.Lock()
        self.trade_lock = threading.Lock()
        self.initialize_mt5_connection()
        self.update_account_info()
        
        # Initialize advanced features
        if ADVANCED_FEATURES:
            self.analytics = AdvancedSignalAnalytics()
            self.price_monitor = BitcoinPriceMonitor()
            self.tp_calculator = RealTimeTPCalculator()
            self.signal_filter = SmartSignalFilter()
            self.pre_signal_alert = PreSignalAlertSystem()
            self.price_monitor.start_monitoring()
            print("🚀 Advanced analytics and price monitoring activated")
            print("🎯 TP probability calculator activated")
            print("🔍 Smart signal quality filter activated")
            print("⏰ Pre-signal alert system activated - You will receive 1-minute advance warnings!")
        else:
            self.analytics = None
            self.price_monitor = None
            self.tp_calculator = None
            self.signal_filter = None
            self.pre_signal_alert = None
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
        # Stop advanced features
        if ADVANCED_FEATURES and self.price_monitor:
            self.price_monitor.stop_monitoring()
        
        shutdown_mt5()
        send_system_alert("STOP: MT5 Signal Bot shutting down gracefully", "INFO")
        sys.exit(0)
    
    def initialize_mt5_connection(self):
        """Initialize MT5 connection"""
        try:
            if initialize_mt5():
                logger.info("SUCCESS: MT5 initialized successfully")
                
                # Test connection with a sample price request
                test_price = get_current_price('EURUSD')
                if test_price:
                    logger.info(f"MT5 CONNECTION TEST: EURUSD = {test_price:.5f}")
                    return True
                else:
                    logger.warning("WARNING: MT5 connected but cannot get prices")
                    return False
            else:
                logger.error("ERROR: Failed to initialize MT5")
                return False
        except Exception as e:
            logger.error(f"MT5 initialization error: {e}")
            return False
    
    def update_account_info(self):
        """Update MT5 account information"""
        global account_info
        try:
            account_info = get_account_info()
            if account_info:
                trade_mode = "REAL" if account_info.get('trade_mode') == 2 else "DEMO"
                logger.info(f"MT5 ACCOUNT ({trade_mode}): Login: {account_info['login']}, "
                          f"Balance: ${account_info['balance']:.2f}, "
                          f"Equity: ${account_info['equity']:.2f}, "
                          f"Server: {account_info['server']}")
                
                trade_stats['account_balance'] = account_info['balance']
            else:
                logger.warning("WARNING: Could not retrieve MT5 account info")
                
        except Exception as e:
            logger.error(f"MT5 account info error: {e}")
    
    def safe_fetch_mt5_data(self, symbol, tf_minutes, retries=0):
        """Safely fetch REAL MT5 market data with retry logic"""
        try:
            data = fetch_market_data(symbol, tf_minutes, 100)
            if data is None or len(data) < 30:
                if retries < 3:
                    logger.warning(f"MT5 data retry {retries + 1} for {symbol} {tf_minutes}m")
                    time.sleep(2)
                    return self.safe_fetch_mt5_data(symbol, tf_minutes, retries + 1)
                logger.error(f"ERROR: Insufficient MT5 data for {symbol} {tf_minutes}m")
                return None
            
            # Log latest real price from MT5
            latest_price = data['close'].iloc[-1]
            logger.info(f"MT5 DATA: {symbol} {tf_minutes}m - {len(data)} bars "
                       f"(Latest: {latest_price:.5f})")
            
            return data
        except Exception as e:
            if retries < 2:
                logger.warning(f"MT5 data retry {retries + 1} for {symbol}: {e}")
                time.sleep(3)
                return self.safe_fetch_mt5_data(symbol, tf_minutes, retries + 1)
            logger.error(f"ERROR: MT5 data fetch failed for {symbol}: {e}")
            return None
    
    def check_signal_limits(self):
        """Enhanced risk management for MT5 signals"""
        try:
            # Always allow signal generation if in signal-only mode
            if SIGNAL_ONLY_MODE or IGNORE_ACCOUNT_BALANCE:
                return True, "MT5 Signal-only mode active"
            
            with self.trade_lock:
                self.update_account_info()
                
                current_balance = account_info['balance'] if account_info else 0
                current_equity = account_info['equity'] if account_info else current_balance
                
                # Allow signals even with zero balance in signal mode
                if current_balance <= 0 and IGNORE_ACCOUNT_BALANCE:
                    return True, "MT5 Zero balance - signals only"
                
                # Max open signals
                if len(open_trades) >= MAX_OPEN_TRADES:
                    return False, f"Max open MT5 signals reached ({len(open_trades)}/{MAX_OPEN_TRADES})"
                
                # Daily loss limit (only if tracking balance)
                if current_balance > 0:
                    daily_loss_limit = DAILY_LOSS_LIMIT * current_balance
                    if trade_stats['daily_pnl'] <= -daily_loss_limit:
                        return False, f"Daily loss limit reached: ${trade_stats['daily_pnl']:.2f}"
                
                # Equity protection
                if current_equity < current_balance * 0.8:
                    return False, f"High drawdown detected - Equity: ${current_equity:.2f}"
                
                return True, "MT5 OK"
                
        except Exception as e:
            logger.error(f"MT5 signal check error: {e}")
            return True, f"MT5 signal check error (allowing): {e}"
    
    def check_trades_realtime(self, symbol):
        """Real-time MT5 signal monitoring with live prices"""
        try:
            # Get REAL current price from MT5
            current_price = get_current_price(symbol)
            if current_price is None:
                logger.warning(f"Could not get MT5 price for {symbol}")
                return
            
            with self.trade_lock:
                for trade in open_trades[:]:
                    if trade.get('status', 'open') != 'open' or trade['symbol'] != symbol:
                        continue
                    
                    # Check signal outcomes with REAL MT5 prices
                    if trade['side'] == 'buy':
                        if current_price <= trade['sl']:
                            pnl_pips = (current_price - trade['entry']) * 10000
                            logger.info(f"MT5 SIGNAL SL HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"({pnl_pips:.1f} pips)")
                            trade['status'] = 'sl_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'sl_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'sl_hit', current_price
                                )
                                trade_copy = trade.copy()
                                trade_copy['status'] = 'sl_hit'
                                trade_copy['exit_price'] = current_price
                                record_signal_for_ai_learning(trade_copy)
                        # TP1
                        elif current_price >= trade['tp'][0] and trade.get('status', 'open') == 'open':
                            pnl_pips = (current_price - trade['entry']) * 10000
                            logger.info(f"MT5 SIGNAL TP1 HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"(+{pnl_pips:.1f} pips)")
                            trade['status'] = 'tp1_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp1_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp1_hit', current_price
                                )
                                trade_copy = trade.copy()
                                trade_copy['status'] = 'tp1_hit'
                                trade_copy['exit_price'] = current_price
                                record_signal_for_ai_learning(trade_copy)
                        # TP2
                        elif len(trade['tp']) > 1 and current_price >= trade['tp'][1] and trade.get('status', 'open') in ['open', 'tp1_hit']:
                            pnl_pips = (current_price - trade['entry']) * 10000
                            logger.info(f"MT5 SIGNAL TP2 HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"(+{pnl_pips:.1f} pips)")
                            trade['status'] = 'tp2_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp2_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp2_hit', current_price
                                )
                                trade_copy = trade.copy()
                                trade_copy['status'] = 'tp2_hit'
                                trade_copy['exit_price'] = current_price
                                record_signal_for_ai_learning(trade_copy)
                        # TP3
                        elif len(trade['tp']) > 2 and current_price >= trade['tp'][2] and trade.get('status', 'open') in ['open', 'tp1_hit', 'tp2_hit']:
                            pnl_pips = (current_price - trade['entry']) * 10000
                            logger.info(f"MT5 SIGNAL TP3 HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"(+{pnl_pips:.1f} pips)")
                            trade['status'] = 'tp3_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp3_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp3_hit', current_price
                                )
                                trade_copy = trade.copy()
                                trade_copy['status'] = 'tp3_hit'
                                trade_copy['exit_price'] = current_price
                                record_signal_for_ai_learning(trade_copy)
                    elif trade['side'] == 'sell':
                        if current_price >= trade['sl']:
                            pnl_pips = (trade['entry'] - current_price) * 10000
                            logger.info(f"MT5 SIGNAL SL HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"({pnl_pips:.1f} pips)")
                            trade['status'] = 'sl_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'sl_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'sl_hit', current_price
                                )
                        # TP1
                        elif current_price <= trade['tp'][0] and trade.get('status', 'open') == 'open':
                            pnl_pips = (trade['entry'] - current_price) * 10000
                            logger.info(f"MT5 SIGNAL TP1 HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"(+{pnl_pips:.1f} pips)")
                            trade['status'] = 'tp1_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp1_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp1_hit', current_price
                                )
                        # TP2
                        elif len(trade['tp']) > 1 and current_price <= trade['tp'][1] and trade.get('status', 'open') in ['open', 'tp1_hit']:
                            pnl_pips = (trade['entry'] - current_price) * 10000
                            logger.info(f"MT5 SIGNAL TP2 HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"(+{pnl_pips:.1f} pips)")
                            trade['status'] = 'tp2_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp2_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp2_hit', current_price
                                )
                        # TP3
                        elif len(trade['tp']) > 2 and current_price <= trade['tp'][2] and trade.get('status', 'open') in ['open', 'tp1_hit', 'tp2_hit']:
                            pnl_pips = (trade['entry'] - current_price) * 10000
                            logger.info(f"MT5 SIGNAL TP3 HIT: {trade['symbol']} at {current_price:.5f} "
                                        f"(+{pnl_pips:.1f} pips)")
                            trade['status'] = 'tp3_hit'
                            trade['exit_price'] = current_price
                            trade['exit_time'] = datetime.now()
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp3_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp3_hit', current_price
                                )
                            if ADVANCED_FEATURES and self.analytics and 'analytics_id' in trade:
                                self.analytics.update_signal_outcome(
                                    trade['analytics_id'], 'tp_hit', current_price
                                )
                                performance_monitor.record_trade_outcome(
                                    trade['analytics_id'], 'tp_hit', current_price
                                )
                        
        except Exception as e:
            logger.error(f"Real-time MT5 signal check error for {symbol}: {e}")
    
    def generate_and_process_signals(self, df, symbol, tf):
        """Generate and process MT5-based signals with comprehensive analysis and validation"""
        try:
            ema_20 = df['close'].rolling(20).mean().iloc[-1]
            ema_50 = df['close'].rolling(50).mean().iloc[-1]
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 1e-9)
            rsi = 100 - (100 / (1 + rs))
            rsi_last = rsi.iloc[-1]
            current_price = df['close'].iloc[-1]
            logger.debug(f"[SignalGen] Checking for signal: {symbol} {tf} | Price: {current_price}, EMA20: {ema_20}, EMA50: {ema_50}, RSI: {rsi_last}")

            # --- Support/Resistance Detection ---
            def detect_support_resistance(df, window=20):
                support = df['low'].rolling(window).min().iloc[-1]
                resistance = df['high'].rolling(window).max().iloc[-1]
                return support, resistance

            support, resistance = detect_support_resistance(df, window=20)
            logger.debug(f"[SignalGen] Support: {support}, Resistance: {resistance}")

            signals = []
            # Process BTCUSD and XAUUSD for all timeframes in TIMEFRAMES
            if symbol in ['BTCUSD', 'XAUUSD'] and tf in TIMEFRAMES:
                # Use 3% proximity for both symbols
                proximity = 0.03
                # Bullish if price near support and EMA/RSI bullish (relaxed RSI > 50)
                if ema_20 > ema_50 and rsi_last > 50 and abs(current_price - support) < (current_price * proximity):
                    bullish_signal = generate_realistic_signal(symbol, tf, df, 'bullish')
                    if bullish_signal:
                        bullish_signal['support'] = support
                        bullish_signal['resistance'] = resistance
                        signals.append(bullish_signal)
                # Bearish if price near resistance and EMA/RSI bearish (relaxed RSI < 50)
                elif ema_20 < ema_50 and rsi_last < 50 and abs(current_price - resistance) < (current_price * proximity):
                    bearish_signal = generate_realistic_signal(symbol, tf, df, 'bearish')
                    if bearish_signal:
                        bearish_signal['support'] = support
                        bearish_signal['resistance'] = resistance
                        signals.append(bearish_signal)
            
            if not signals:
                logger.debug(f"[SignalGen] No signals to process for {symbol} {tf}")
                return

            key = (symbol, tf)
            now = time.time()

            if key in last_alert_time and now - last_alert_time[key] < COOLDOWN_SECONDS:
                return

            current_mt5_price = get_current_price(symbol)

            for signal in signals:
                # === ENHANCED SIGNAL VALIDATION & OPTIMIZATION ===
                
                if ADVANCED_FEATURES:
                    performance_monitor.record_signal_generated(signal)

                signal['generated_at'] = datetime.now()
                signal['bot_version'] = "5.0-MT5-Enhanced-RiskManagement"
                signal['data_source'] = "MetaTrader5"
                signal['current_price'] = current_mt5_price or df['close'].iloc[-1]
                signal['signal_only'] = SIGNAL_ONLY_MODE
                signal['account_balance'] = account_info['balance'] if account_info else 0
                signal['server'] = account_info['server'] if account_info else 'Unknown'

                # === 1. CORRELATION ANALYSIS ===
                if ADVANCED_FEATURES:
                    correlation_advice = get_correlation_advice(signal, open_trades)
                    signal['correlation_advice'] = correlation_advice
                    
                    if correlation_advice['advice'] == 'AVOID':
                        logger.warning(f"🚫 CORRELATION BLOCK: {symbol} - {correlation_advice['reason']}")
                        performance_monitor.record_signal_filtered(signal, f"Correlation: {correlation_advice['reason']}")
                        continue
                    
                    # Apply correlation adjustments
                    if 'adjustments' in correlation_advice:
                        adjustments = correlation_advice['adjustments']
                        if 'confidence_adjustment' in adjustments:
                            original_conf = signal.get('confidence', 0.8)
                            signal['confidence'] = max(0.1, original_conf + adjustments['confidence_adjustment'])

                # === 2. SESSION ANALYSIS ===
                if ADVANCED_FEATURES:
                    session_recommendation = get_trading_recommendation(symbol)
                    signal['session_analysis'] = session_recommendation
                    
                    # Only block trading in CRITICAL conditions, allow all others in signal-only mode
                    if session_recommendation['action'] == 'AVOID_TRADING' and 'CRITICAL' in session_recommendation.get('recommendation', ''):
                        logger.warning(f"🚫 SESSION BLOCK: {symbol} - {session_recommendation['recommendation']}")
                        performance_monitor.record_signal_filtered(signal, f"Session: {session_recommendation['recommendation']}")
                        continue
                    elif session_recommendation['action'] == 'AVOID_TRADING':
                        # In signal-only mode, still send signals but with session warning
                        logger.info(f"⚠️ SESSION WARNING: {symbol} - {session_recommendation['recommendation']} (Signal still sent)")
                    
                    # Apply session multipliers
                    session_multipliers = get_session_multipliers(symbol)
                    signal['session_multipliers'] = session_multipliers
                    
                    if 'tp_probability' in signal:
                        original_prob = signal['tp_probability']
                        signal['tp_probability'] = min(99, max(1, original_prob * session_multipliers['multipliers']['probability_multiplier']))
                    
                    if 'confidence' in signal:
                        boost = session_multipliers['multipliers']['confidence_boost']
                        signal['confidence'] = min(1.0, signal['confidence'] + boost)

                # === 3. RISK VALIDATION ===
                if ADVANCED_FEATURES:
                    risk_valid, risk_message = validate_trade_risk(signal, account_info['balance'] if account_info else 0, open_trades)
                    signal['risk_validation'] = {'valid': risk_valid, 'message': risk_message}
                    
                    if not risk_valid:
                        logger.warning(f"🚫 RISK BLOCK: {symbol} - {risk_message}")
                        performance_monitor.record_signal_filtered(signal, f"Risk: {risk_message}")
                        continue
                    
                    # Calculate optimal position size
                    optimal_size = calculate_optimal_position_size(signal, account_info['balance'] if account_info else 1000, open_trades)
                    signal['position_size'] = optimal_size
                    
                    # Apply correlation position size adjustment
                    if 'correlation_advice' in signal and 'adjustments' in signal['correlation_advice']:
                        pos_multiplier = signal['correlation_advice']['adjustments'].get('position_size_multiplier', 1.0)
                        signal['position_size'] *= pos_multiplier

                price_diff = abs(signal['entry'] - signal['current_price']) / signal['current_price']
                if price_diff > 0.01:
                    logger.warning(f"Large price difference detected for {symbol}: "
                                 f"Signal: {signal['entry']:.5f}, Current: {signal['current_price']:.5f}")

                tp_probability = 0.75
                probability_analysis = None

                # === 4. TP PROBABILITY CALCULATION ===
                if ADVANCED_FEATURES and self.tp_calculator:
                    try:
                        tp_price = signal['tp'][0] if isinstance(signal['tp'], list) else signal['tp']
                        probability_analysis = self.tp_calculator.calculate_comprehensive_tp_probability(
                            symbol, signal['entry'], tp_price, signal['sl'],
                            signal['side'], tf, signal.get('confidence', 0.75)
                        )
                        tp_probability = probability_analysis['final_probability']
                        signal['tp_probability'] = probability_analysis['probability_percent']
                        signal['expected_value'] = probability_analysis['expected_value']
                        signal['recommendation'] = probability_analysis['recommendation']

                        # === 5. AI ADJUSTMENTS ===
                        ai_adjustments = get_ai_probability_adjustments(symbol, tf)
                        if ai_adjustments:
                            adjusted_prob = probability_analysis['probability_percent'] * ai_adjustments.get('probability_multiplier', 1.0)
                            signal['tp_probability'] = max(1, min(99, adjusted_prob))
                            signal['ai_adjusted'] = True
                            logger.info(f"🤖 AI ADJUSTMENT: {symbol} probability adjusted from {probability_analysis['probability_percent']:.1f}% to {signal['tp_probability']:.1f}%")

                        logger.info(f"🎯 TP PROBABILITY: {signal['tp_probability']}% for {symbol} {signal['side'].upper()}")
                        logger.info(f"💡 RECOMMENDATION: {signal['recommendation']}")

                    except Exception as e:
                        logger.warning(f"TP probability calculation error: {e}")

                # === 6. SMART SIGNAL FILTERING ===
                if ADVANCED_FEATURES and self.signal_filter:
                    try:
                        filter_passed, filter_message = self.signal_filter.filter_signal(signal)
                        if not filter_passed:
                            logger.warning(f"🚫 SIGNAL FILTERED: {symbol} - {filter_message}")
                            performance_monitor.record_signal_filtered(signal, filter_message)
                            continue
                        else:
                            logger.info(f"✅ SIGNAL QUALITY CHECK PASSED: {symbol}")
                    except Exception as e:
                        logger.warning(f"Signal filter error: {e}")

                # === 7. FINAL SIGNAL VALIDATION ===
                logger.info(f"NEW ENHANCED SIGNAL: {signal['order_type']} {signal['symbol']} {signal['tf']} "
                          f"at {signal['entry']:.5f} (MT5: {signal['current_price']:.5f}) "
                          f"[TP Probability: {tp_probability*100:.1f}%] "
                          f"[Position Size: {signal.get('position_size', 0.01):.3f}] "
                          f"[Session: {signal.get('session_analysis', {}).get('action', 'N/A')}] "
                          f"[Correlation: {signal.get('correlation_advice', {}).get('correlation_risk', 'N/A')}]")

                if send_enhanced_alert(signal):
                    if ADVANCED_FEATURES:
                        performance_monitor.record_signal_sent(signal)

                    with self.trade_lock:
                        open_trades.append(signal)

                    if ADVANCED_FEATURES and self.analytics:
                        tp_price = signal['tp'][0] if isinstance(signal['tp'], list) else signal['tp']
                        signal_id = self.analytics.add_signal(
                            signal['symbol'],
                            signal['side'],
                            signal['entry'],
                            signal['sl'],
                            tp_price,
                            signal['tf'],
                            signal.get('confidence', 0.8)
                        )
                        signal['analytics_id'] = signal_id

                    logger.info(f"ENHANCED SIGNAL SENT: {signal['order_type']} {signal['symbol']} {signal['tf']}")

            last_alert_time[key] = now

        except Exception as e:
            logger.error(f"MT5 signal processing error for {symbol} {tf}: {e}")
    
    def scan_realtime(self):
        """Main MT5 real-time scanning loop"""
        self.running = True
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        logger.info("SUCCESS: MT5 Signal Bot Started (REAL-TIME DATA)")
        send_system_alert("SUCCESS: MT5 Signal Bot Started - Real Market Data + Pre-Signal Alerts Active", "SUCCESS")
        
        # Performance reporting timer
        last_performance_report = time.time()
        performance_report_interval = 3600  # Report every hour
        
        # Correlation update timer
        last_correlation_update = time.time()
        correlation_update_interval = 7200  # Update every 2 hours
        
        while self.running:
            loop_start_time = time.time()
            try:
                # Market hours check
                if not is_market_open():
                    if consecutive_errors == 0:
                        logger.info("INFO: Forex market closed, monitoring mode...")
                    time.sleep(60)
                    continue

                # Signal generation check
                can_generate, check_msg = self.check_signal_limits()
                if not can_generate and not SIGNAL_ONLY_MODE:
                    logger.warning(f"WARNING: MT5 signal generation paused: {check_msg}")
                    time.sleep(60)
                    continue

                # Main MT5 scanning loop
                for symbol in SYMBOLS:
                    logger.info(f"[DEBUG] Scanning symbol: {symbol}")
                    # Real-time signal monitoring with MT5 prices
                    self.check_trades_realtime(symbol)

                    # Pre-signal alert monitoring (1-minute advance warning)
                    if ADVANCED_FEATURES and self.pre_signal_alert:
                        try:
                            self.pre_signal_alert.check_pre_signal_conditions(symbol)
                        except Exception as e:
                            logger.warning(f"Pre-signal alert error for {symbol}: {e}")

                    # Data analysis and signal generation with MT5 data
                    for tf in TIMEFRAMES:
                        logger.info(f"[DEBUG]   Timeframe: {tf}")
                        tf_minutes = TF_MAP.get(tf)
                        if tf_minutes is None:
                            continue

                        # Fetch REAL MT5 data
                        df = self.safe_fetch_mt5_data(symbol, tf_minutes)
                        if df is None:
                            logger.warning(f"[DEBUG]     No data for {symbol} {tf}")
                            continue

                        logger.info(f"[DEBUG]     Generating signals for {symbol} {tf}")
                        # Generate signals using MT5 data
                        self.generate_and_process_signals(df, symbol, tf)

                # Reset error counter
                consecutive_errors = 0

                # Periodic performance reporting
                current_time = time.time()
                if ADVANCED_FEATURES and current_time - last_performance_report > performance_report_interval:
                    try:
                        report = performance_monitor.generate_performance_report()
                        logger.info(report)
                        last_performance_report = current_time
                    except Exception as e:
                        logger.warning(f"Performance report error: {e}")

                # Periodic correlation matrix update
                if ADVANCED_FEATURES and current_time - last_correlation_update > correlation_update_interval:
                    try:
                        logger.info("🔗 Updating market correlation matrix...")
                        update_market_correlations()
                        correlation_report = correlation_analyzer.get_correlation_report()
                        logger.info(f"📊 CORRELATION UPDATE:\n{correlation_report}")
                        last_correlation_update = current_time
                    except Exception as e:
                        logger.warning(f"Correlation update error: {e}")

                # Sleep
                loop_duration = time.time() - loop_start_time
                sleep_time = max(1, SCAN_INTERVAL - loop_duration)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("KEYBOARD: Interrupt received, shutting down MT5 bot...")
                break
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"ERROR: MT5 scanner error (attempt {consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    error_msg = f"CRITICAL: Max MT5 errors reached ({max_consecutive_errors})"
                    logger.critical(error_msg)
                    send_system_alert(error_msg, "ERROR")
                    break
                
                time.sleep(min(60, 10 * consecutive_errors))
        
        logger.info("STOP: MT5 Signal Bot Stopped")
        
        # Save performance data before shutdown
        if ADVANCED_FEATURES:
            try:
                performance_monitor.save_session_data()
                final_report = performance_monitor.generate_performance_report()
                logger.info(f"📊 FINAL SESSION REPORT:\n{final_report}")
            except Exception as e:
                logger.error(f"Error saving performance data: {e}")
        
        shutdown_mt5()
        send_system_alert("STOP: MT5 Signal Bot Stopped", "INFO")

def main():
    """Main entry point for MT5 Signal Bot"""
    try:
        logger.info("STARTUP: MT5 REAL-TIME MODE - Using MetaTrader5 for accurate signals")
        
        bot = MT5SignalBot()
        bot.scan_realtime()
        
    except Exception as e:
        logger.critical(f"CRITICAL MT5 ERROR: {e}")
        send_system_alert(f"CRITICAL MT5 ERROR: {e}", "ERROR")
        shutdown_mt5()
        sys.exit(1)

if __name__ == "__main__":
    main()