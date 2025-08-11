"""
Take Profit (TP) Accuracy & Probability Analysis Tool
Analyzes the accuracy, probability, and performance of TP levels
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import statistics
from typing import Dict, List, Tuple
import math

class TPAccuracyAnalyzer:
    def __init__(self):
        self.signals_file = "advanced_signals.json"
        self.load_signals()
    
    def load_signals(self):
        """Load signal data from JSON file"""
        try:
            with open(self.signals_file, 'r') as f:
                self.signals = json.load(f)
            print(f"✅ Loaded {len(self.signals)} signals for analysis")
        except FileNotFoundError:
            print("⚠️ No signals file found - starting with empty data")
            self.signals = []
        except Exception as e:
            print(f"❌ Error loading signals: {e}")
            self.signals = []
    
    def calculate_tp_accuracy(self) -> Dict:
        """Calculate TP hit accuracy across all signals"""
        if not self.signals:
            return {"error": "No signals data available"}
        
        # Filter completed signals only
        completed_signals = [s for s in self.signals if s.get('status') == 'closed']
        
        if not completed_signals:
            return {"error": "No completed signals for analysis", "total_signals": len(self.signals)}
        
        # Count TP hits vs SL hits
        tp_hits = len([s for s in completed_signals if s.get('outcome') == 'tp_hit'])
        sl_hits = len([s for s in completed_signals if s.get('outcome') == 'sl_hit'])
        
        total_completed = len(completed_signals)
        tp_accuracy = (tp_hits / total_completed * 100) if total_completed > 0 else 0
        
        return {
            "total_signals": len(self.signals),
            "completed_signals": total_completed,
            "active_signals": len(self.signals) - total_completed,
            "tp_hits": tp_hits,
            "sl_hits": sl_hits,
            "tp_accuracy_percent": round(tp_accuracy, 2),
            "win_rate": round(tp_accuracy, 2),
            "loss_rate": round(100 - tp_accuracy, 2)
        }
    
    def analyze_by_symbol(self) -> Dict:
        """Analyze TP accuracy by trading symbol"""
        completed_signals = [s for s in self.signals if s.get('status') == 'closed']
        
        if not completed_signals:
            return {"error": "No completed signals for symbol analysis"}
        
        symbols = {}
        for signal in completed_signals:
            symbol = signal.get('symbol', 'Unknown')
            if symbol not in symbols:
                symbols[symbol] = {"tp_hits": 0, "sl_hits": 0, "total": 0}
            
            symbols[symbol]["total"] += 1
            if signal.get('outcome') == 'tp_hit':
                symbols[symbol]["tp_hits"] += 1
            elif signal.get('outcome') == 'sl_hit':
                symbols[symbol]["sl_hits"] += 1
        
        # Calculate accuracy for each symbol
        for symbol in symbols:
            total = symbols[symbol]["total"]
            tp_hits = symbols[symbol]["tp_hits"]
            symbols[symbol]["accuracy_percent"] = round((tp_hits / total * 100), 2) if total > 0 else 0
        
        return symbols
    
    def analyze_by_timeframe(self) -> Dict:
        """Analyze TP accuracy by timeframe"""
        completed_signals = [s for s in self.signals if s.get('status') == 'closed']
        
        if not completed_signals:
            return {"error": "No completed signals for timeframe analysis"}
        
        timeframes = {}
        for signal in completed_signals:
            tf = signal.get('timeframe', 'Unknown')
            if tf not in timeframes:
                timeframes[tf] = {"tp_hits": 0, "sl_hits": 0, "total": 0}
            
            timeframes[tf]["total"] += 1
            if signal.get('outcome') == 'tp_hit':
                timeframes[tf]["tp_hits"] += 1
            elif signal.get('outcome') == 'sl_hit':
                timeframes[tf]["sl_hits"] += 1
        
        # Calculate accuracy for each timeframe
        for tf in timeframes:
            total = timeframes[tf]["total"]
            tp_hits = timeframes[tf]["tp_hits"]
            timeframes[tf]["accuracy_percent"] = round((tp_hits / total * 100), 2) if total > 0 else 0
        
        return timeframes
    
    def calculate_risk_reward_performance(self) -> Dict:
        """Analyze risk-reward performance"""
        completed_signals = [s for s in self.signals if s.get('status') == 'closed']
        
        if not completed_signals:
            return {"error": "No completed signals for RR analysis"}
        
        total_risk = 0
        total_reward = 0
        profitable_trades = 0
        
        for signal in completed_signals:
            entry = signal.get('entry_price', 0)
            sl = signal.get('stop_loss', 0)
            tp = signal.get('take_profit', 0)
            
            if entry and sl and tp:
                # Calculate risk and reward distances
                if signal.get('side') == 'buy':
                    risk_distance = abs(entry - sl)
                    reward_distance = abs(tp - entry)
                else:  # sell
                    risk_distance = abs(sl - entry)
                    reward_distance = abs(entry - tp)
                
                total_risk += risk_distance
                
                if signal.get('outcome') == 'tp_hit':
                    total_reward += reward_distance
                    profitable_trades += 1
                # If SL hit, we lose the risk amount (no reward)
        
        total_trades = len(completed_signals)
        expected_reward_per_trade = total_reward / total_trades if total_trades > 0 else 0
        expected_risk_per_trade = total_risk / total_trades if total_trades > 0 else 0
        profit_factor = total_reward / total_risk if total_risk > 0 else 0
        
        return {
            "total_trades": total_trades,
            "profitable_trades": profitable_trades,
            "profit_factor": round(profit_factor, 3),
            "expected_reward_per_trade": round(expected_reward_per_trade, 2),
            "expected_risk_per_trade": round(expected_risk_per_trade, 2),
            "risk_reward_efficiency": round(profit_factor, 3)
        }
    
    def calculate_tp_probability_by_distance(self) -> Dict:
        """Calculate TP hit probability based on distance from entry"""
        completed_signals = [s for s in self.signals if s.get('status') == 'closed']
        
        if not completed_signals:
            return {"error": "No completed signals for distance analysis"}
        
        # Group by TP distance ranges
        distance_ranges = {
            "0-50_pips": {"tp_hits": 0, "total": 0},
            "50-100_pips": {"tp_hits": 0, "total": 0},
            "100-200_pips": {"tp_hits": 0, "total": 0},
            "200+_pips": {"tp_hits": 0, "total": 0}
        }
        
        for signal in completed_signals:
            entry = signal.get('entry_price', 0)
            tp = signal.get('take_profit', 0)
            
            if entry and tp:
                # Calculate distance in pips (approximation)
                if signal.get('symbol') == 'BTCUSD':
                    distance_pips = abs(tp - entry) / 100  # BTC: 1 pip = $100
                elif signal.get('symbol') == 'ETHUSD':
                    distance_pips = abs(tp - entry) * 100  # ETH: 1 pip = $0.01
                elif signal.get('symbol') == 'XAUUSD':
                    distance_pips = abs(tp - entry) * 10   # XAU: 1 pip = $0.1
                else:
                    distance_pips = abs(tp - entry) * 10000  # Standard forex
                
                # Categorize by distance
                if distance_pips <= 50:
                    range_key = "0-50_pips"
                elif distance_pips <= 100:
                    range_key = "50-100_pips"
                elif distance_pips <= 200:
                    range_key = "100-200_pips"
                else:
                    range_key = "200+_pips"
                
                distance_ranges[range_key]["total"] += 1
                if signal.get('outcome') == 'tp_hit':
                    distance_ranges[range_key]["tp_hits"] += 1
        
        # Calculate probabilities
        for range_key in distance_ranges:
            total = distance_ranges[range_key]["total"]
            tp_hits = distance_ranges[range_key]["tp_hits"]
            distance_ranges[range_key]["probability_percent"] = round((tp_hits / total * 100), 2) if total > 0 else 0
        
        return distance_ranges
    
    def get_current_active_signals_analysis(self) -> Dict:
        """Analyze currently active signals and their TP probability"""
        active_signals = [s for s in self.signals if s.get('status') == 'active']
        
        if not active_signals:
            return {"message": "No active signals to analyze"}
        
        # Get overall TP accuracy for probability estimation
        overall_stats = self.calculate_tp_accuracy()
        base_probability = overall_stats.get('tp_accuracy_percent', 50)  # Default 50% if no data
        
        active_analysis = []
        for signal in active_signals:
            symbol = signal.get('symbol')
            entry = signal.get('entry_price')
            tp = signal.get('take_profit')
            sl = signal.get('stop_loss')
            confidence = signal.get('confidence', 0.75) * 100
            
            # Calculate distance to TP and SL
            if entry and tp and sl:
                if signal.get('side') == 'buy':
                    tp_distance = tp - entry
                    sl_distance = entry - sl
                else:  # sell
                    tp_distance = entry - tp
                    sl_distance = sl - entry
                
                # Calculate risk-reward ratio
                rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
                
                # Estimate probability based on historical data + confidence
                estimated_probability = min(95, base_probability * (confidence / 75) * 1.1)
                
                active_analysis.append({
                    "id": signal.get('id'),
                    "symbol": symbol,
                    "side": signal.get('side'),
                    "entry_price": entry,
                    "tp_price": tp,
                    "sl_price": sl,
                    "tp_distance": round(tp_distance, 2),
                    "sl_distance": round(sl_distance, 2),
                    "risk_reward_ratio": round(rr_ratio, 2),
                    "confidence_percent": round(confidence, 1),
                    "estimated_tp_probability": round(estimated_probability, 1),
                    "timeframe": signal.get('timeframe'),
                    "timestamp": signal.get('timestamp')
                })
        
        return {
            "active_signals_count": len(active_signals),
            "base_tp_probability": round(base_probability, 1),
            "signals": active_analysis
        }
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive TP accuracy and probability report"""
        print("\n" + "="*80)
        print("🎯 TAKE PROFIT (TP) ACCURACY & PROBABILITY ANALYSIS")
        print("="*80)
        
        # Overall accuracy
        overall = self.calculate_tp_accuracy()
        print(f"\n📊 OVERALL PERFORMANCE:")
        if 'error' not in overall:
            print(f"   Total Signals Generated: {overall['total_signals']}")
            print(f"   Completed Signals: {overall['completed_signals']}")
            print(f"   Active Signals: {overall['active_signals']}")
            print(f"   🎯 TP Hit Rate: {overall['tp_accuracy_percent']}%")
            print(f"   🛑 SL Hit Rate: {overall['loss_rate']}%")
            print(f"   ✅ Win Rate: {overall['win_rate']}%")
        else:
            print(f"   ⚠️ {overall.get('error', 'No data available')}")
        
        # Symbol analysis
        print(f"\n📈 PERFORMANCE BY SYMBOL:")
        symbol_stats = self.analyze_by_symbol()
        if 'error' not in symbol_stats:
            for symbol, stats in symbol_stats.items():
                print(f"   {symbol}: {stats['accuracy_percent']}% TP hit rate "
                      f"({stats['tp_hits']}/{stats['total']} trades)")
        else:
            print(f"   ⚠️ {symbol_stats.get('error')}")
        
        # Timeframe analysis
        print(f"\n⏰ PERFORMANCE BY TIMEFRAME:")
        tf_stats = self.analyze_by_timeframe()
        if 'error' not in tf_stats:
            for tf, stats in tf_stats.items():
                print(f"   {tf}: {stats['accuracy_percent']}% TP hit rate "
                      f"({stats['tp_hits']}/{stats['total']} trades)")
        else:
            print(f"   ⚠️ {tf_stats.get('error')}")
        
        # Risk-Reward analysis
        print(f"\n💰 RISK-REWARD PERFORMANCE:")
        rr_stats = self.calculate_risk_reward_performance()
        if 'error' not in rr_stats:
            print(f"   Profit Factor: {rr_stats['profit_factor']}")
            print(f"   Profitable Trades: {rr_stats['profitable_trades']}/{rr_stats['total_trades']}")
            print(f"   Risk-Reward Efficiency: {rr_stats['risk_reward_efficiency']}")
        else:
            print(f"   ⚠️ {rr_stats.get('error')}")
        
        # TP Distance probability
        print(f"\n📏 TP PROBABILITY BY DISTANCE:")
        distance_stats = self.calculate_tp_probability_by_distance()
        if 'error' not in distance_stats:
            for distance, stats in distance_stats.items():
                if stats['total'] > 0:
                    print(f"   {distance}: {stats['probability_percent']}% success rate "
                          f"({stats['tp_hits']}/{stats['total']} trades)")
        else:
            print(f"   ⚠️ {distance_stats.get('error')}")
        
        # Current active signals
        print(f"\n🔄 ACTIVE SIGNALS ANALYSIS:")
        active_stats = self.get_current_active_signals_analysis()
        if 'message' not in active_stats:
            print(f"   Active Signals: {active_stats['active_signals_count']}")
            print(f"   Base TP Probability: {active_stats['base_tp_probability']}%")
            print("\n   Current Active Trades:")
            for signal in active_stats['signals']:
                prob = signal['estimated_tp_probability']
                rr = signal['risk_reward_ratio']
                print(f"   📍 #{signal['id']} {signal['symbol']} {signal['side'].upper()}")
                print(f"      Entry: {signal['entry_price']} | TP: {signal['tp_price']}")
                print(f"      Estimated TP Probability: {prob}% | RR: 1:{rr}")
                print(f"      Timeframe: {signal['timeframe']} | Confidence: {signal['confidence_percent']}%")
                print()
        else:
            print(f"   {active_stats['message']}")
        
        # Probability assessment
        print(f"\n🎲 PROBABILITY ASSESSMENT:")
        if 'error' not in overall:
            accuracy = overall['tp_accuracy_percent']
            if accuracy >= 70:
                assessment = "🟢 HIGH PROBABILITY - TPs are highly accurate"
            elif accuracy >= 50:
                assessment = "🟡 MODERATE PROBABILITY - TPs show decent accuracy"
            elif accuracy >= 30:
                assessment = "🟠 LOW PROBABILITY - TP accuracy needs improvement"
            else:
                assessment = "🔴 VERY LOW PROBABILITY - Major TP calibration needed"
            
            print(f"   Current TP Accuracy: {accuracy}%")
            print(f"   Assessment: {assessment}")
        
        print(f"\n📝 RECOMMENDATIONS:")
        if 'error' not in overall and overall['completed_signals'] > 0:
            accuracy = overall['tp_accuracy_percent']
            if accuracy < 50:
                print("   • Consider reducing TP distances for higher hit rate")
                print("   • Analyze market conditions causing SL hits")
                print("   • Review entry timing and market volatility")
            elif accuracy < 70:
                print("   • Fine-tune TP levels based on symbol-specific performance")
                print("   • Consider dynamic TP adjustment based on market conditions")
            else:
                print("   • Maintain current TP strategy - performing well")
                print("   • Consider slightly increasing TP targets for higher rewards")
        else:
            print("   • Collect more signal data for accurate analysis")
            print("   • Monitor upcoming signals closely for pattern recognition")
        
        print("\n" + "="*80)
        
        return "Analysis complete"

def main():
    """Main function to run TP accuracy analysis"""
    analyzer = TPAccuracyAnalyzer()
    analyzer.generate_comprehensive_report()

if __name__ == "__main__":
    main()
