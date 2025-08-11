#!/usr/bin/env python3
"""
Simple Signal Performance Tracker
Tracks your Bitcoin trading signals and their outcomes
"""

import json
import os
from datetime import datetime

class SignalTracker:
    def __init__(self):
        self.signals_file = "signal_history.json"
        self.load_signals()
    
    def load_signals(self):
        """Load existing signals from file"""
        if os.path.exists(self.signals_file):
            with open(self.signals_file, 'r') as f:
                self.signals = json.load(f)
        else:
            self.signals = []
    
    def save_signals(self):
        """Save signals to file"""
        with open(self.signals_file, 'w') as f:
            json.dump(self.signals, f, indent=2)
    
    def add_signal(self, symbol, side, entry_price, sl, tp, timeframe):
        """Add a new signal"""
        signal = {
            'id': len(self.signals) + 1,
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'stop_loss': sl,
            'take_profit': tp,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'status': 'active',
            'outcome': None,
            'exit_price': None,
            'pnl_pips': None
        }
        self.signals.append(signal)
        self.save_signals()
        print(f"✅ Signal #{signal['id']} added: {side.upper()} {symbol} @ {entry_price}")
    
    def update_signal_outcome(self, signal_id, outcome, exit_price):
        """Update signal outcome (tp_hit, sl_hit, manual_close)"""
        for signal in self.signals:
            if signal['id'] == signal_id:
                signal['status'] = 'closed'
                signal['outcome'] = outcome
                signal['exit_price'] = exit_price
                
                # Calculate P&L in pips
                if signal['side'] == 'buy':
                    pnl = (exit_price - signal['entry_price']) * 10000
                else:
                    pnl = (signal['entry_price'] - exit_price) * 10000
                
                signal['pnl_pips'] = round(pnl, 1)
                self.save_signals()
                
                status_emoji = "🎯" if outcome == "tp_hit" else "❌" if outcome == "sl_hit" else "⏹️"
                print(f"{status_emoji} Signal #{signal_id} closed: {outcome} | P&L: {pnl:+.1f} pips")
                break
    
    def get_performance_stats(self):
        """Get overall performance statistics"""
        closed_signals = [s for s in self.signals if s['status'] == 'closed']
        
        if not closed_signals:
            return "No closed signals yet."
        
        total_signals = len(closed_signals)
        winners = len([s for s in closed_signals if s['outcome'] == 'tp_hit'])
        losers = len([s for s in closed_signals if s['outcome'] == 'sl_hit'])
        win_rate = (winners / total_signals) * 100
        
        total_pips = sum([s['pnl_pips'] for s in closed_signals if s['pnl_pips']])
        avg_pips = total_pips / total_signals
        
        return f"""
📊 PERFORMANCE STATS:
Total Signals: {total_signals}
Winners: {winners} | Losers: {losers}
Win Rate: {win_rate:.1f}%
Total P&L: {total_pips:+.1f} pips
Average per Signal: {avg_pips:+.1f} pips
        """
    
    def show_active_signals(self):
        """Show currently active signals"""
        active = [s for s in self.signals if s['status'] == 'active']
        
        if not active:
            print("No active signals.")
            return
        
        print("\n🔥 ACTIVE SIGNALS:")
        for signal in active:
            print(f"#{signal['id']}: {signal['side'].upper()} {signal['symbol']} @ {signal['entry_price']}")
            print(f"   SL: {signal['stop_loss']} | TP: {signal['take_profit']} | TF: {signal['timeframe']}")

def main():
    """Demo usage"""
    tracker = SignalTracker()
    
    print("🎯 Bitcoin Signal Tracker")
    print("========================")
    
    # Show current active signals
    tracker.show_active_signals()
    
    # Show performance stats
    print(tracker.get_performance_stats())
    
    print("\n📝 To use this tracker:")
    print("1. tracker.add_signal('BTCUSD', 'sell', 118006.70, 118100, 117900, 'M3')")
    print("2. tracker.update_signal_outcome(1, 'tp_hit', 117900)")
    print("3. tracker.get_performance_stats()")

if __name__ == "__main__":
    main()
