"""
Enhanced Performance Monitor
Monitors bot performance with probability analytics, filter effectiveness,
and real-time quality metrics
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_file = "performance_stats.json"
        self.load_performance_data()
        
        # Real-time counters
        self.signals_generated = 0
        self.signals_filtered = 0
        self.signals_sent = 0
        self.tp_hits = 0
        self.sl_hits = 0
        
        # Probability tracking
        self.probability_predictions = []
        self.actual_outcomes = []
        
        # Filter effectiveness
        self.filter_stats = {
            'probability_filter': {'stopped': 0, 'passed': 0},
            'confidence_filter': {'stopped': 0, 'passed': 0},
            'timeframe_filter': {'stopped': 0, 'passed': 0},
            'price_accuracy_filter': {'stopped': 0, 'passed': 0}
        }
        
        self.session_start = datetime.now()
    
    def load_performance_data(self):
        """Load historical performance data"""
        try:
            with open(self.performance_file, 'r') as f:
                self.performance_data = json.load(f)
        except FileNotFoundError:
            self.performance_data = {
                'total_signals': 0,
                'total_filtered': 0,
                'total_sent': 0,
                'total_tp_hits': 0,
                'total_sl_hits': 0,
                'probability_accuracy': [],
                'sessions': []
            }
        except Exception as e:
            self.logger.error(f"Error loading performance data: {e}")
            self.performance_data = {}
    
    def save_performance_data(self):
        """Save performance data to file"""
        try:
            with open(self.performance_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving performance data: {e}")
    
    def record_signal_generated(self, signal: Dict):
        """Record a new signal generated"""
        self.signals_generated += 1
        self.logger.debug(f"Signal generated: {signal.get('symbol')} {signal.get('side')}")
    
    def record_signal_filtered(self, signal: Dict, reason: str):
        """Record a signal that was filtered out"""
        self.signals_filtered += 1
        symbol = signal.get('symbol', 'Unknown')
        self.logger.info(f"📊 Signal filtered: {symbol} - {reason}")
        
        # Track which filter stopped it
        if 'probability' in reason.lower():
            self.filter_stats['probability_filter']['stopped'] += 1
        elif 'confidence' in reason.lower():
            self.filter_stats['confidence_filter']['stopped'] += 1
        elif 'timeframe' in reason.lower():
            self.filter_stats['timeframe_filter']['stopped'] += 1
        elif 'price' in reason.lower():
            self.filter_stats['price_accuracy_filter']['stopped'] += 1
    
    def record_signal_sent(self, signal: Dict):
        """Record a signal that was sent to users"""
        self.signals_sent += 1
        
        # Record probability prediction for later accuracy check
        if 'tp_probability' in signal:
            self.probability_predictions.append({
                'signal_id': signal.get('id', len(self.probability_predictions)),
                'symbol': signal.get('symbol'),
                'predicted_probability': signal['tp_probability'],
                'timestamp': datetime.now().isoformat(),
                'outcome': None  # Will be updated when trade closes
            })
        
        self.logger.info(f"📊 Signal sent: {signal.get('symbol')} {signal.get('side')}")
    
    def record_trade_outcome(self, signal_id: int, outcome: str, exit_price: float):
        """Record the actual outcome of a trade"""
        if outcome == 'tp_hit':
            self.tp_hits += 1
        elif outcome == 'sl_hit':
            self.sl_hits += 1
        
        # Update probability prediction accuracy
        for prediction in self.probability_predictions:
            if prediction['signal_id'] == signal_id and prediction['outcome'] is None:
                prediction['outcome'] = outcome
                prediction['exit_price'] = exit_price
                prediction['outcome_timestamp'] = datetime.now().isoformat()
                
                # Calculate if probability prediction was accurate
                predicted_success = prediction['predicted_probability'] > 50
                actual_success = outcome == 'tp_hit'
                prediction['prediction_accurate'] = predicted_success == actual_success
                
                self.logger.info(f"📊 Trade outcome recorded: Signal {signal_id} - {outcome}")
                break
    
    def calculate_probability_accuracy(self) -> float:
        """Calculate how accurate our probability predictions are"""
        completed_predictions = [p for p in self.probability_predictions if p['outcome'] is not None]
        
        if not completed_predictions:
            return 0.0
        
        accurate_predictions = sum(1 for p in completed_predictions if p.get('prediction_accurate', False))
        accuracy = accurate_predictions / len(completed_predictions) * 100
        
        return round(accuracy, 2)
    
    def calculate_filter_effectiveness(self) -> Dict:
        """Calculate how effective each filter is"""
        effectiveness = {}
        
        for filter_name, stats in self.filter_stats.items():
            total = stats['stopped'] + stats['passed']
            if total > 0:
                filter_rate = stats['stopped'] / total * 100
                effectiveness[filter_name] = {
                    'filter_rate_percent': round(filter_rate, 1),
                    'signals_stopped': stats['stopped'],
                    'signals_passed': stats['passed'],
                    'total_checked': total
                }
            else:
                effectiveness[filter_name] = {
                    'filter_rate_percent': 0,
                    'signals_stopped': 0,
                    'signals_passed': 0,
                    'total_checked': 0
                }
        
        return effectiveness
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        session_duration = datetime.now() - self.session_start
        hours = session_duration.total_seconds() / 3600
        
        # Calculate rates
        generation_rate = self.signals_generated / hours if hours > 0 else 0
        filter_rate = (self.signals_filtered / self.signals_generated * 100) if self.signals_generated > 0 else 0
        send_rate = (self.signals_sent / self.signals_generated * 100) if self.signals_generated > 0 else 0
        
        # Calculate win rate
        total_completed = self.tp_hits + self.sl_hits
        win_rate = (self.tp_hits / total_completed * 100) if total_completed > 0 else 0
        
        return {
            'session_duration_hours': round(hours, 2),
            'signals_generated': self.signals_generated,
            'signals_filtered': self.signals_filtered,
            'signals_sent': self.signals_sent,
            'filter_rate_percent': round(filter_rate, 1),
            'send_rate_percent': round(send_rate, 1),
            'generation_rate_per_hour': round(generation_rate, 1),
            'tp_hits': self.tp_hits,
            'sl_hits': self.sl_hits,
            'win_rate_percent': round(win_rate, 1),
            'probability_accuracy_percent': self.calculate_probability_accuracy()
        }
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        stats = self.get_session_stats()
        filter_effectiveness = self.calculate_filter_effectiveness()
        
        report = f"""
🏆 ENHANCED BOT PERFORMANCE REPORT
{'='*50}

📊 SESSION STATISTICS:
   Duration: {stats['session_duration_hours']} hours
   Signals Generated: {stats['signals_generated']}
   Signals Filtered: {stats['signals_filtered']} ({stats['filter_rate_percent']}%)
   Signals Sent: {stats['signals_sent']} ({stats['send_rate_percent']}%)
   Generation Rate: {stats['generation_rate_per_hour']} signals/hour

🎯 TRADING PERFORMANCE:
   TP Hits: {stats['tp_hits']}
   SL Hits: {stats['sl_hits']}
   Win Rate: {stats['win_rate_percent']}%
   Probability Accuracy: {stats['probability_accuracy_percent']}%

🔍 FILTER EFFECTIVENESS:"""
        
        for filter_name, effectiveness in filter_effectiveness.items():
            clean_name = filter_name.replace('_filter', '').replace('_', ' ').title()
            report += f"""
   {clean_name}: {effectiveness['filter_rate_percent']}% filtered ({effectiveness['signals_stopped']}/{effectiveness['total_checked']})"""
        
        # Quality assessment
        if stats['win_rate_percent'] >= 60:
            quality = "🟢 EXCELLENT"
        elif stats['win_rate_percent'] >= 50:
            quality = "🟡 GOOD"
        elif stats['win_rate_percent'] >= 40:
            quality = "🟠 FAIR"
        else:
            quality = "🔴 NEEDS IMPROVEMENT"
        
        report += f"""

🏅 OVERALL QUALITY: {quality}

📈 IMPROVEMENTS:"""
        
        if stats['probability_accuracy_percent'] < 70:
            report += "\n   • Calibrate probability calculations"
        if stats['filter_rate_percent'] > 80:
            report += "\n   • Consider relaxing filter thresholds"
        if stats['filter_rate_percent'] < 30:
            report += "\n   • Consider tightening filter criteria"
        if stats['win_rate_percent'] < 50:
            report += "\n   • Review signal generation logic"
        
        report += f"\n\n{'='*50}"
        
        return report
    
    def save_session_data(self):
        """Save current session data to historical records"""
        session_data = self.get_session_stats()
        session_data['timestamp'] = datetime.now().isoformat()
        session_data['filter_effectiveness'] = self.calculate_filter_effectiveness()
        
        if 'sessions' not in self.performance_data:
            self.performance_data['sessions'] = []
        
        self.performance_data['sessions'].append(session_data)
        
        # Update totals
        self.performance_data['total_signals'] += self.signals_generated
        self.performance_data['total_filtered'] += self.signals_filtered
        self.performance_data['total_sent'] += self.signals_sent
        self.performance_data['total_tp_hits'] += self.tp_hits
        self.performance_data['total_sl_hits'] += self.sl_hits
        
        self.save_performance_data()
        self.logger.info("📊 Session data saved to performance history")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
