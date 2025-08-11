#!/usr/bin/env python3
"""
Advanced Bitcoin Signal Analytics Dashboard
Real-time performance tracking for your trading bot
"""

import json
import os
from datetime import datetime, timedelta
import threading
import time

class AdvancedSignalAnalytics:
    def __init__(self):
        self.signals_file = "advanced_signals.json"
        self.performance_file = "performance_stats.json"
        self.load_data()
        self.lock = threading.Lock()
        
    def load_data(self):
        """Load existing data"""
        # Load signals
        if os.path.exists(self.signals_file):
            with open(self.signals_file, 'r') as f:
                self.signals = json.load(f)
        else:
            self.signals = []
            
        # Load performance stats
        if os.path.exists(self.performance_file):
            with open(self.performance_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                'total_signals': 0,
                'winning_signals': 0,
                'losing_signals': 0,
                'total_pips': 0.0,
                'best_trade_pips': 0.0,
                'worst_trade_pips': 0.0,
                'avg_pips_per_trade': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'last_updated': datetime.now().isoformat()
            }
    
    def save_data(self):
        """Save all data"""
        with open(self.signals_file, 'w') as f:
            json.dump(self.signals, f, indent=2)
        with open(self.performance_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def add_signal(self, symbol, side, entry_price, sl, tp, timeframe, confidence=0.8):
        """Add a new signal with enhanced data"""
        with self.lock:
            signal = {
                'id': len(self.signals) + 1,
                'symbol': symbol,
                'side': side.lower(),
                'entry_price': float(entry_price),
                'stop_loss': float(sl),
                'take_profit': float(tp) if isinstance(tp, (int, float)) else float(tp[0]),
                'timeframe': timeframe,
                'confidence': float(confidence),
                'timestamp': datetime.now().isoformat(),
                'status': 'active',
                'outcome': None,
                'exit_price': None,
                'pnl_pips': None,
                'duration_minutes': None,
                'risk_reward_ratio': None,
                'market_condition': self._analyze_market_condition(symbol, entry_price)
            }
            
            # Calculate risk-reward ratio
            if signal['side'] == 'buy':
                risk_pips = abs(signal['entry_price'] - signal['stop_loss']) * 10000
                reward_pips = abs(signal['take_profit'] - signal['entry_price']) * 10000
            else:
                risk_pips = abs(signal['stop_loss'] - signal['entry_price']) * 10000
                reward_pips = abs(signal['entry_price'] - signal['take_profit']) * 10000
            
            signal['risk_reward_ratio'] = round(reward_pips / risk_pips, 2) if risk_pips > 0 else 0
            
            self.signals.append(signal)
            self.stats['total_signals'] += 1
            self.save_data()
            
            print(f"🎯 ENHANCED SIGNAL #{signal['id']}: {side.upper()} {symbol}")
            print(f"   Entry: {entry_price} | SL: {sl} | TP: {tp}")
            print(f"   RR: 1:{signal['risk_reward_ratio']} | Confidence: {confidence*100:.0f}%")
            
            return signal['id']
    
    def _analyze_market_condition(self, symbol, price):
        """Analyze current market condition"""
        # Simple market condition analysis
        if 'BTC' in symbol:
            if price > 115000:
                return "high_momentum"
            elif price > 110000:
                return "bullish"
            elif price > 100000:
                return "neutral"
            else:
                return "bearish"
        return "unknown"
    
    def update_signal_outcome(self, signal_id, outcome, exit_price, current_price=None):
        """Update signal outcome with enhanced analytics"""
        with self.lock:
            for signal in self.signals:
                if signal['id'] == signal_id and signal['status'] == 'active':
                    signal['status'] = 'closed'
                    signal['outcome'] = outcome
                    signal['exit_price'] = float(exit_price)
                    
                    # Calculate duration
                    start_time = datetime.fromisoformat(signal['timestamp'])
                    signal['duration_minutes'] = int((datetime.now() - start_time).total_seconds() / 60)
                    
                    # Calculate P&L in pips
                    if signal['side'] == 'buy':
                        pnl = (signal['exit_price'] - signal['entry_price']) * 10000
                    else:
                        pnl = (signal['entry_price'] - signal['exit_price']) * 10000
                    
                    signal['pnl_pips'] = round(pnl, 1)
                    
                    # Update global stats
                    if outcome in ['tp_hit', 'manual_profit']:
                        self.stats['winning_signals'] += 1
                        if signal['pnl_pips'] > self.stats['best_trade_pips']:
                            self.stats['best_trade_pips'] = signal['pnl_pips']
                    else:
                        self.stats['losing_signals'] += 1
                        if signal['pnl_pips'] < self.stats['worst_trade_pips']:
                            self.stats['worst_trade_pips'] = signal['pnl_pips']
                    
                    self.stats['total_pips'] += signal['pnl_pips']
                    self._update_performance_metrics()
                    self.save_data()
                    
                    # Print outcome
                    status_emoji = {
                        'tp_hit': '🎯',
                        'sl_hit': '❌', 
                        'manual_profit': '💰',
                        'manual_loss': '⏹️'
                    }.get(outcome, '📊')
                    
                    print(f"{status_emoji} SIGNAL #{signal_id} CLOSED:")
                    print(f"   Outcome: {outcome.upper()} | P&L: {pnl:+.1f} pips")
                    print(f"   Duration: {signal['duration_minutes']} minutes")
                    print(f"   Updated Win Rate: {self.stats['win_rate']:.1f}%")
                    
                    return signal
            
            print(f"❌ Signal #{signal_id} not found or already closed")
            return None
    
    def _update_performance_metrics(self):
        """Update calculated performance metrics"""
        total = self.stats['total_signals']
        closed = self.stats['winning_signals'] + self.stats['losing_signals']
        
        if closed > 0:
            self.stats['win_rate'] = (self.stats['winning_signals'] / closed) * 100
            self.stats['avg_pips_per_trade'] = self.stats['total_pips'] / closed
        
        # Calculate profit factor
        winning_pips = sum([s['pnl_pips'] for s in self.signals 
                           if s.get('pnl_pips', 0) > 0 and s['status'] == 'closed'])
        losing_pips = abs(sum([s['pnl_pips'] for s in self.signals 
                              if s.get('pnl_pips', 0) < 0 and s['status'] == 'closed']))
        
        self.stats['profit_factor'] = (winning_pips / losing_pips) if losing_pips > 0 else 0
        self.stats['last_updated'] = datetime.now().isoformat()
    
    def get_performance_report(self):
        """Generate comprehensive performance report"""
        closed_signals = [s for s in self.signals if s['status'] == 'closed']
        active_signals = [s for s in self.signals if s['status'] == 'active']
        
        # Recent performance (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_signals = [s for s in closed_signals 
                         if datetime.fromisoformat(s['timestamp']) > recent_cutoff]
        
        report = f"""
🎯 BITCOIN SIGNAL ANALYTICS REPORT
=====================================

📊 OVERALL PERFORMANCE:
• Total Signals Generated: {self.stats['total_signals']}
• Closed Signals: {len(closed_signals)}
• Active Signals: {len(active_signals)}
• Win Rate: {self.stats['win_rate']:.1f}%
• Total P&L: {self.stats['total_pips']:+.1f} pips
• Average per Trade: {self.stats['avg_pips_per_trade']:+.1f} pips
• Profit Factor: {self.stats['profit_factor']:.2f}

🏆 BEST & WORST:
• Best Trade: +{self.stats['best_trade_pips']:.1f} pips
• Worst Trade: {self.stats['worst_trade_pips']:+.1f} pips

⚡ RECENT PERFORMANCE (24h):
• Recent Signals: {len(recent_signals)}
• Recent P&L: {sum([s.get('pnl_pips', 0) for s in recent_signals]):+.1f} pips

🔥 ACTIVE SIGNALS:
"""
        
        for signal in active_signals[-5:]:  # Show last 5 active
            report += f"• #{signal['id']}: {signal['side'].upper()} {signal['symbol']} @ {signal['entry_price']}\n"
        
        return report
    
    def get_signal_by_entry_price(self, symbol, entry_price, tolerance=0.1):
        """Find signal by entry price (for automated tracking)"""
        for signal in self.signals:
            if (signal['symbol'] == symbol and 
                signal['status'] == 'active' and
                abs(signal['entry_price'] - entry_price) < tolerance):
                return signal['id']
        return None

# Demo usage function
def demo_usage():
    """Demonstrate analytics usage"""
    analytics = AdvancedSignalAnalytics()
    
    print("🚀 BITCOIN SIGNAL ANALYTICS INITIALIZED")
    print("========================================")
    
    # Show current performance
    print(analytics.get_performance_report())
    
    print("\n📝 USAGE EXAMPLES:")
    print("1. analytics.add_signal('BTCUSD', 'sell', 118006.70, 118100, 117900, 'M3', 0.85)")
    print("2. analytics.update_signal_outcome(1, 'tp_hit', 117900)")
    print("3. analytics.get_performance_report()")
    
    return analytics

if __name__ == "__main__":
    demo_usage()
