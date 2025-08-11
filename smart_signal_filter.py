"""
Smart Signal Quality Filter
Filters signals based on multiple quality criteria including TP probability,
market conditions, historical performance, and New York trading sessions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Import trading sessions manager
try:
    from trading_sessions import session_manager, should_trade_now, get_session_multipliers
    SESSIONS_AVAILABLE = True
except ImportError:
    SESSIONS_AVAILABLE = False
    logging.warning("Trading sessions module not available")

class SmartSignalFilter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.min_tp_probability = 45.0  # Minimum TP probability %
        self.min_confidence = 65.0      # Minimum signal confidence %
        self.min_expected_value = 0.0   # Minimum expected value
        self.max_price_diff = 0.015     # Max 1.5% price difference
        
        # Symbol-specific filters
        self.symbol_filters = {
            'BTCUSD': {'min_prob': 50.0, 'preferred_tf': ['M3', 'M15', 'M30', 'H1']},
            'ETHUSD': {'min_prob': 40.0, 'preferred_tf': ['M3', 'M15', 'M30']},
            'XAUUSD': {'min_prob': 45.0, 'preferred_tf': ['M3', 'M5', 'M15', 'M30']}
        }
        
        # Time-based filters
        self.avoid_hours = []  # Hours to avoid trading (24h format)
        self.preferred_sessions = ['london', 'newyork', 'overlap']
        
        self.filtered_count = 0
        self.passed_count = 0
    
    def check_probability_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if signal meets probability requirements"""
        tp_prob = signal.get('tp_probability', 50.0)
        symbol = signal.get('symbol', '')
        
        # Get symbol-specific minimum probability
        symbol_min = self.symbol_filters.get(symbol, {}).get('min_prob', self.min_tp_probability)
        
        if tp_prob < symbol_min:
            return False, f"TP probability {tp_prob}% below {symbol_min}% threshold for {symbol}"
        
        return True, f"TP probability {tp_prob}% meets {symbol_min}% threshold"
    
    def check_confidence_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if signal meets confidence requirements"""
        confidence = signal.get('confidence', 0.75) * 100
        
        if confidence < self.min_confidence:
            return False, f"Signal confidence {confidence:.1f}% below {self.min_confidence}% threshold"
        
        return True, f"Signal confidence {confidence:.1f}% meets threshold"
    
    def check_expected_value_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if signal has positive expected value"""
        expected_value = signal.get('expected_value', 0)
        
        if expected_value < self.min_expected_value:
            return False, f"Expected value {expected_value:.2f} below {self.min_expected_value} threshold"
        
        return True, f"Expected value {expected_value:.2f} meets threshold"
    
    def check_price_accuracy_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if signal entry price is close to current market price"""
        entry_price = signal.get('entry', 0)
        current_price = signal.get('current_price', entry_price)
        
        if entry_price == 0 or current_price == 0:
            return True, "Price accuracy check skipped - no price data"
        
        price_diff = abs(entry_price - current_price) / current_price
        
        if price_diff > self.max_price_diff:
            return False, f"Price difference {price_diff*100:.2f}% exceeds {self.max_price_diff*100}% threshold"
        
        return True, f"Price difference {price_diff*100:.2f}% within threshold"
    
    def check_timeframe_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if timeframe is preferred for the symbol"""
        symbol = signal.get('symbol', '')
        timeframe = signal.get('tf', '')
        
        preferred_tfs = self.symbol_filters.get(symbol, {}).get('preferred_tf', [])
        
        if preferred_tfs and timeframe not in preferred_tfs:
            return False, f"Timeframe {timeframe} not in preferred list {preferred_tfs} for {symbol}"
        
        return True, f"Timeframe {timeframe} is acceptable for {symbol}"
    
    def check_realistic_signal_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if signal uses the new realistic TP/SL system"""
        is_realistic = signal.get('realistic_levels', False)
        
        if is_realistic:
            # Validate realistic signal structure
            required_fields = ['risk', 'rr_ratio', 'atr']
            missing_fields = [field for field in required_fields if field not in signal]
            
            if missing_fields:
                return False, f"Realistic signal missing fields: {missing_fields}"
            
            # Check if risk is reasonable
            risk = signal.get('risk', 0)
            if risk <= 0 or risk > 10000:  # Max $10k risk per trade
                return False, f"Unrealistic risk amount: ${risk:,.2f}"
            
            # Check if RR ratio is reasonable
            rr_ratio = signal.get('rr_ratio', 0)
            if rr_ratio < 1.0 or rr_ratio > 5.0:  # Between 1:1 and 5:1
                return False, f"Unrealistic RR ratio: {rr_ratio:.2f}"
            
            return True, f"✅ REALISTIC signal validated: Risk ${risk:.2f}, RR {rr_ratio:.2f}"
        else:
            # Legacy signal - apply stricter filtering
            return True, "Legacy signal - basic validation applied"

    def check_time_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if current time is suitable for trading with NY session focus"""
        # First check traditional avoid hours
        current_hour = datetime.now().hour
        
        if current_hour in self.avoid_hours:
            return False, f"Current hour {current_hour} is in avoid list {self.avoid_hours}"
        
        # If sessions are available, use session-based filtering
        if SESSIONS_AVAILABLE:
            should_trade, session_reason = should_trade_now(signal.get('symbol', ''))
            
            if not should_trade:
                return False, f"Session filter: {session_reason}"
            
            # Get session info for logging
            session_info = session_manager.get_session_info()
            
            # Log NY session status
            if session_info['ny_session_active']:
                self.logger.info(f"🇺🇸 NY SESSION ACTIVE - Enhanced signal quality expected")
            
            if session_info['overlap_session_active']:
                self.logger.info(f"🔥 NY-LONDON OVERLAP - Maximum volatility period!")
            
            return True, f"✅ {session_reason} | NY Time: {session_info['ny_time']}"
        
        # Fallback to basic time check
        return True, f"Current hour {current_hour} is acceptable for trading"
    
    def apply_session_multipliers(self, signal: Dict) -> Dict:
        """Apply New York session-based multipliers to signal"""
        if not SESSIONS_AVAILABLE:
            return signal
        
        try:
            # Get session analysis
            session_analysis = get_session_multipliers(signal.get('symbol', ''))
            multipliers = session_analysis['multipliers']
            session_info = session_analysis['session_info']
            
            # Apply probability multiplier
            if 'tp_probability' in signal:
                original_prob = signal['tp_probability']
                adjusted_prob = original_prob * multipliers['probability_multiplier']
                signal['tp_probability'] = min(99, max(1, adjusted_prob))
                
                if adjusted_prob != original_prob:
                    self.logger.info(f"🎯 SESSION ADJUSTMENT: {signal.get('symbol')} TP probability: "
                                   f"{original_prob:.1f}% → {signal['tp_probability']:.1f}% "
                                   f"({multipliers['probability_multiplier']:.2f}x)")
            
            # Apply confidence boost
            if 'confidence' in signal:
                original_conf = signal['confidence']
                signal['confidence'] = min(1.0, max(0.1, original_conf + multipliers['confidence_boost']))
                
                if multipliers['confidence_boost'] != 0:
                    self.logger.info(f"💪 CONFIDENCE BOOST: {signal.get('symbol')} confidence: "
                                   f"{original_conf:.2f} → {signal['confidence']:.2f}")
            
            # Add session metadata
            signal['session_active'] = session_info['ny_session_active']
            signal['overlap_active'] = session_info['overlap_session_active']
            signal['session_priority'] = session_info['priority_score']
            
            # Log session recommendations
            for rec in session_analysis['recommendations']:
                self.logger.info(f"📋 SESSION TIP: {rec}")
                
        except Exception as e:
            self.logger.error(f"Error applying session multipliers: {e}")
        
        return signal
    
    def check_recommendation_filter(self, signal: Dict) -> Tuple[bool, str]:
        """Check if signal has a positive recommendation"""
        recommendation = signal.get('recommendation', '')
        
        # Filter out signals with negative recommendations
        negative_keywords = ['AVOID', 'VERY LOW', 'HIGH RISK']
        
        for keyword in negative_keywords:
            if keyword in recommendation.upper():
                return False, f"Negative recommendation: {recommendation}"
        
        return True, f"Recommendation acceptable: {recommendation}"
    
    def apply_quality_filters(self, signal: Dict) -> Tuple[bool, List[str]]:
        """Apply all quality filters to a signal"""
        filters = [
            self.check_realistic_signal_filter,  # New realistic signal check
            self.check_probability_filter,
            self.check_confidence_filter,
            self.check_expected_value_filter,
            self.check_price_accuracy_filter,
            # self.check_timeframe_filter,  # Disabled: allow all timeframes
            self.check_time_filter,
            self.check_recommendation_filter
        ]
        
        results = []
        passed = True
        
        for filter_func in filters:
            try:
                filter_passed, message = filter_func(signal)
                results.append(f"{'✅' if filter_passed else '❌'} {message}")
                
                if not filter_passed:
                    passed = False
                    
            except Exception as e:
                results.append(f"⚠️ Filter error: {e}")
                self.logger.warning(f"Filter error in {filter_func.__name__}: {e}")
        
        return passed, results
    
    def filter_signal(self, signal: Dict) -> Tuple[bool, str]:
        """Main signal filtering function with NY session optimization"""
        symbol = signal.get('symbol', 'Unknown')
        side = signal.get('side', 'unknown').upper()
        tf = signal.get('tf', 'Unknown')
        
        self.logger.info(f"🔍 Filtering signal: {symbol} {side} {tf}")
        
        # Apply New York session multipliers first
        signal = self.apply_session_multipliers(signal)
        
        # Apply all quality filters
        passed, filter_results = self.apply_quality_filters(signal)
        
        # Log detailed results
        for result in filter_results:
            self.logger.info(f"   {result}")
        
        if passed:
            self.passed_count += 1
            
            # Add session info to success message
            session_note = ""
            if SESSIONS_AVAILABLE:
                if signal.get('overlap_active', False):
                    session_note = " [NY-LONDON OVERLAP ⚡]"
                elif signal.get('session_active', False):
                    session_note = " [NY SESSION 🇺🇸]"
            
            self.logger.info(f"✅ SIGNAL PASSED: {symbol} {side} {tf} - All filters passed{session_note}")
            return True, f"Signal passed all quality filters{session_note}"
        else:
            self.filtered_count += 1
            failed_filters = [r for r in filter_results if '❌' in r]
            self.logger.warning(f"🚫 SIGNAL FILTERED: {symbol} {side} {tf} - {len(failed_filters)} filters failed")
            return False, f"Signal filtered: {len(failed_filters)} quality checks failed"
    
    def get_filter_stats(self) -> Dict:
        """Get filtering statistics"""
        total = self.passed_count + self.filtered_count
        pass_rate = (self.passed_count / total * 100) if total > 0 else 0
        
        return {
            'total_signals': total,
            'passed_signals': self.passed_count,
            'filtered_signals': self.filtered_count,
            'pass_rate_percent': round(pass_rate, 1),
            'filter_rate_percent': round(100 - pass_rate, 1)
        }
    
    def update_filter_settings(self, **kwargs):
        """Update filter settings dynamically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"Updated filter setting: {key} = {value}")
    
    def get_symbol_performance_adjustment(self, symbol: str, historical_performance: float) -> float:
        """Adjust probability threshold based on symbol's historical performance"""
        base_threshold = self.symbol_filters.get(symbol, {}).get('min_prob', self.min_tp_probability)
        
        # If historical performance is poor, raise the threshold
        if historical_performance < 0.3:  # Less than 30% TP hit rate
            return base_threshold + 10  # Require 10% higher probability
        elif historical_performance < 0.5:  # Less than 50% TP hit rate
            return base_threshold + 5   # Require 5% higher probability
        elif historical_performance > 0.7:  # Greater than 70% TP hit rate
            return base_threshold - 5   # Allow 5% lower probability
        
        return base_threshold
