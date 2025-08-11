"""
Real-Time TP Probability Calculator
Calculates dynamic TP hit probability based on current market conditions,
volatility, and historical performance
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

# Import MT5 data functions
try:
    from mt5_data import get_current_price, fetch_market_data
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MT5 not available - using mock data")

class RealTimeTPCalculator:
    def __init__(self):
        self.signals_file = "advanced_signals.json"
        self.load_historical_data()
        
    def load_historical_data(self):
        """Load historical signal performance data"""
        try:
            with open(self.signals_file, 'r') as f:
                self.historical_signals = json.load(f)
            print(f"✅ Loaded {len(self.historical_signals)} historical signals")
        except FileNotFoundError:
            self.historical_signals = []
            print("⚠️ No historical data found")
        except Exception as e:
            self.historical_signals = []
            print(f"❌ Error loading historical data: {e}")
    
    def calculate_market_volatility(self, symbol: str, timeframe_minutes: int = 60) -> float:
        """Calculate current market volatility for probability adjustment"""
        if not MT5_AVAILABLE:
            return 0.5  # Default moderate volatility
        
        try:
            # Get recent price data
            data = fetch_market_data(symbol, timeframe_minutes, 20)
            if data is None or len(data) < 10:
                return 0.5
            
            # Calculate price volatility (standard deviation of returns)
            prices = data['close'].values
            returns = []
            for i in range(1, len(prices)):
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(abs(ret))
            
            if len(returns) > 0:
                volatility = statistics.mean(returns)
                return min(1.0, volatility * 100)  # Normalize to 0-1 scale
            
        except Exception as e:
            print(f"⚠️ Volatility calculation error for {symbol}: {e}")
        
        return 0.5
    
    def get_symbol_historical_performance(self, symbol: str) -> Dict:
        """Get historical TP performance for specific symbol"""
        symbol_signals = [s for s in self.historical_signals 
                         if s.get('symbol') == symbol and s.get('status') == 'closed']
        
        if not symbol_signals:
            return {"tp_rate": 0.5, "total_trades": 0, "avg_duration": 0, "tp_hits": 0}
        
        tp_hits = len([s for s in symbol_signals if s.get('outcome') == 'tp_hit'])
        total = len(symbol_signals)
        tp_rate = tp_hits / total if total > 0 else 0.5
        
        # Calculate average duration to TP
        tp_durations = [s.get('duration_minutes', 0) for s in symbol_signals 
                       if s.get('outcome') == 'tp_hit' and s.get('duration_minutes')]
        avg_duration = statistics.mean(tp_durations) if tp_durations else 60
        
        return {
            "tp_rate": tp_rate,
            "total_trades": total,
            "avg_duration": avg_duration,
            "tp_hits": tp_hits
        }
    
    def calculate_distance_probability(self, symbol: str, entry_price: float, 
                                     tp_price: float, side: str) -> float:
        """Calculate probability based on TP distance from entry"""
        
        # Calculate distance
        distance = abs(tp_price - entry_price)
        
        # Symbol-specific pip calculations
        if symbol == 'BTCUSD':
            distance_pips = distance / 100  # BTC: 1 pip = $100
        elif symbol == 'ETHUSD':
            distance_pips = distance * 100  # ETH: 1 pip = $0.01
        elif symbol == 'XAUUSD':
            distance_pips = distance * 10   # XAU: 1 pip = $0.1
        else:
            distance_pips = distance * 10000  # Standard forex
        
        # Probability decreases with distance (exponential decay)
        # Base probability starts at 80% for very close TPs
        base_prob = 0.8
        decay_factor = 0.02  # How quickly probability decreases with distance
        
        distance_probability = base_prob * math.exp(-decay_factor * distance_pips)
        return max(0.1, min(0.9, distance_probability))  # Clamp between 10-90%
    
    def calculate_timeframe_probability(self, timeframe: str) -> float:
        """Calculate probability adjustment based on timeframe"""
        tf_multipliers = {
            "M1": 0.7,   # Very short term - more noise
            "M3": 0.75,  # Short term
            "M5": 0.8,   # Short-medium term
            "M15": 0.85, # Medium term - good balance
            "M30": 0.9,  # Medium-long term
            "H1": 0.95,  # Long term - more reliable
            "H4": 1.0,   # Very long term - most reliable
            "D1": 1.0    # Daily - most reliable
        }
        return tf_multipliers.get(timeframe, 0.8)
    
    def calculate_market_condition_probability(self, symbol: str) -> float:
        """Calculate probability based on current market conditions"""
        if not MT5_AVAILABLE:
            return 0.85  # Default neutral market
        
        try:
            current_price = get_current_price(symbol)
            if not current_price:
                return 0.85
            
            # Get recent data to determine trend strength
            data = fetch_market_data(symbol, 15, 20)  # 15-minute data
            if data is None or len(data) < 10:
                return 0.85
            
            # Simple trend strength calculation
            recent_prices = data['close'].tail(10).values
            trend_strength = abs((recent_prices[-1] - recent_prices[0]) / recent_prices[0])
            
            # Strong trend = higher TP probability
            if trend_strength > 0.02:  # Strong trend (>2% move)
                return 0.9
            elif trend_strength > 0.01:  # Moderate trend
                return 0.85
            else:  # Weak trend/consolidation
                return 0.75
            
        except Exception as e:
            print(f"⚠️ Market condition error for {symbol}: {e}")
            return 0.85
    
    def calculate_comprehensive_tp_probability(self, symbol: str, entry_price: float, 
                                             tp_price: float, sl_price: float, 
                                             side: str, timeframe: str, 
                                             confidence: float = 0.75) -> Dict:
        """Calculate comprehensive TP hit probability using all factors"""
        
        print(f"\n🎯 Calculating TP Probability for {symbol} {side.upper()}")
        print(f"   Entry: {entry_price}, TP: {tp_price}, SL: {sl_price}")
        
        # 1. Historical performance for this symbol
        historical = self.get_symbol_historical_performance(symbol)
        historical_prob = historical['tp_rate']
        print(f"   📊 Historical TP Rate: {historical_prob:.1%} ({historical['tp_hits']}/{historical['total_trades']} trades)")
        
        # 2. Distance-based probability
        distance_prob = self.calculate_distance_probability(symbol, entry_price, tp_price, side)
        print(f"   📏 Distance Probability: {distance_prob:.1%}")
        
        # 3. Timeframe probability
        timeframe_prob = self.calculate_timeframe_probability(timeframe)
        print(f"   ⏰ Timeframe Factor: {timeframe_prob:.1%}")
        
        # 4. Market volatility
        volatility = self.calculate_market_volatility(symbol)
        volatility_prob = 1.0 - (volatility * 0.3)  # High volatility reduces TP probability
        print(f"   📈 Volatility Factor: {volatility_prob:.1%} (volatility: {volatility:.1%})")
        
        # 5. Market condition
        market_condition_prob = self.calculate_market_condition_probability(symbol)
        print(f"   🌊 Market Condition: {market_condition_prob:.1%}")
        
        # 6. Risk-Reward ratio impact
        rr_distance = abs(tp_price - entry_price)
        sl_distance = abs(sl_price - entry_price)
        rr_ratio = rr_distance / sl_distance if sl_distance > 0 else 2.0
        
        # Higher RR = lower probability (but higher reward)
        rr_prob = 1.0 / (1.0 + (rr_ratio - 1.0) * 0.1)
        print(f"   ⚖️ Risk-Reward Impact: {rr_prob:.1%} (RR: 1:{rr_ratio:.1f})")
        
        # 7. Signal confidence
        confidence_prob = confidence
        print(f"   🎲 Signal Confidence: {confidence_prob:.1%}")
        
        # Weighted combination of all factors
        weights = {
            'historical': 0.25,
            'distance': 0.20,
            'timeframe': 0.15,
            'volatility': 0.10,
            'market_condition': 0.15,
            'rr_ratio': 0.10,
            'confidence': 0.05
        }
        
        final_probability = (
            historical_prob * weights['historical'] +
            distance_prob * weights['distance'] +
            timeframe_prob * weights['timeframe'] +
            volatility_prob * weights['volatility'] +
            market_condition_prob * weights['market_condition'] +
            rr_prob * weights['rr_ratio'] +
            confidence_prob * weights['confidence']
        )
        
        # Ensure probability is within reasonable bounds
        final_probability = max(0.15, min(0.90, final_probability))
        
        # Calculate expected value
        risk_amount = sl_distance
        reward_amount = rr_distance
        expected_value = (final_probability * reward_amount) - ((1 - final_probability) * risk_amount)
        
        print(f"\n   🎯 FINAL TP PROBABILITY: {final_probability:.1%}")
        print(f"   💰 Expected Value: {expected_value:.2f} points")
        
        return {
            "final_probability": final_probability,
            "probability_percent": round(final_probability * 100, 1),
            "expected_value": round(expected_value, 2),
            "risk_reward_ratio": round(rr_ratio, 2),
            "factors": {
                "historical_performance": round(historical_prob * 100, 1),
                "distance_factor": round(distance_prob * 100, 1),
                "timeframe_factor": round(timeframe_prob * 100, 1),
                "volatility_factor": round(volatility_prob * 100, 1),
                "market_condition": round(market_condition_prob * 100, 1),
                "rr_impact": round(rr_prob * 100, 1),
                "confidence": round(confidence_prob * 100, 1)
            },
            "recommendation": self.get_recommendation(final_probability, expected_value),
            "historical_data": historical
        }
    
    def get_recommendation(self, probability: float, expected_value: float) -> str:
        """Generate trading recommendation based on probability and expected value"""
        if probability >= 0.7 and expected_value > 0:
            return "🟢 STRONG BUY - High probability with positive expected value"
        elif probability >= 0.6 and expected_value > 0:
            return "🟡 MODERATE BUY - Good probability with positive expected value"
        elif probability >= 0.5 and expected_value > 0:
            return "🟠 WEAK BUY - Fair probability, monitor closely"
        elif probability >= 0.4:
            return "⚪ NEUTRAL - Low probability, high risk"
        else:
            return "🔴 AVOID - Very low probability of success"
    
    def analyze_active_signals(self):
        """Analyze all currently active signals with real-time probability"""
        active_signals = [s for s in self.historical_signals if s.get('status') == 'active']
        
        if not active_signals:
            print("📭 No active signals to analyze")
            return
        
        print("\n" + "="*80)
        print("🔄 REAL-TIME ACTIVE SIGNALS PROBABILITY ANALYSIS")
        print("="*80)
        
        for i, signal in enumerate(active_signals, 1):
            symbol = signal.get('symbol')
            entry = signal.get('entry_price')
            tp = signal.get('take_profit')
            sl = signal.get('stop_loss')
            side = signal.get('side')
            timeframe = signal.get('timeframe')
            confidence = signal.get('confidence', 0.75)
            
            print(f"\n📍 SIGNAL #{signal.get('id')} - {symbol} {side.upper()} ({timeframe})")
            
            if all([symbol, entry, tp, sl, side, timeframe]):
                analysis = self.calculate_comprehensive_tp_probability(
                    symbol, entry, tp, sl, side, timeframe, confidence
                )
                
                print(f"   💡 {analysis['recommendation']}")
            else:
                print("   ❌ Incomplete signal data")
        
        print("\n" + "="*80)

def main():
    """Main function to run real-time TP probability analysis"""
    calculator = RealTimeTPCalculator()
    calculator.analyze_active_signals()

if __name__ == "__main__":
    main()
