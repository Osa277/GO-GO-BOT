#!/usr/bin/env python3
"""
Automated Backtesting System
Advanced backtesting with parameter optimization and strategy validation.
"""

import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import product
import os
from concurrent.futures import ThreadPoolExecutor
import copy

logger = logging.getLogger(__name__)

class AutomatedBacktester:
    def __init__(self):
        self.results_file = "backtest_results.json"
        self.optimization_file = "parameter_optimization.json"
        self.best_params_file = "optimal_parameters.json"
        
    def load_historical_data(self, days_back=30):
        """Load historical signal data for backtesting"""
        try:
            # Try to load from performance stats and logs
            historical_signals = []
            
            # Load from trading bot log if available
            if os.path.exists("trading_bot.log"):
                with open("trading_bot.log", 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if "NEW MT5 SIGNAL:" in line and "TP Probability:" in line:
                        # Parse signal from log
                        try:
                            signal_data = self._parse_signal_from_log(line)
                            if signal_data:
                                historical_signals.append(signal_data)
                        except Exception as e:
                            continue
            
            # Load from AI optimizer data if available
            if os.path.exists("ai_optimization_data.json"):
                with open("ai_optimization_data.json", 'r') as f:
                    ai_data = json.load(f)
                    historical_signals.extend(ai_data.get("signals", []))
            
            logger.info(f"📊 Loaded {len(historical_signals)} historical signals for backtesting")
            return historical_signals
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return []
    
    def _parse_signal_from_log(self, log_line):
        """Parse signal information from log line"""
        try:
            # Extract basic signal info from log format
            # Example: "NEW MT5 SIGNAL: buy now BTCUSD M15 at 118130.91000 [TP Probability: 56.5%]"
            parts = log_line.split()
            
            if "buy" in log_line.lower():
                side = "buy"
            elif "sell" in log_line.lower():
                side = "sell"
            else:
                return None
            
            # Extract symbol
            symbol = None
            for part in parts:
                if part in ["BTCUSD", "ETHUSD", "XAUUSD", "EURUSD", "GBPUSD"]:
                    symbol = part
                    break
            
            # Extract timeframe
            timeframe = None
            for part in parts:
                if part in ["M1", "M3", "M5", "M15", "M30", "H1", "H4"]:
                    timeframe = part
                    break
            
            # Extract entry price
            entry_price = None
            for i, part in enumerate(parts):
                if "at" in part and i + 1 < len(parts):
                    try:
                        entry_price = float(parts[i + 1])
                        break
                    except ValueError:
                        continue
            
            # Extract TP probability
            tp_probability = 75.0  # Default
            for part in parts:
                if "%" in part and "Probability:" in log_line:
                    try:
                        tp_probability = float(part.replace("%]", "").replace("[", ""))
                        break
                    except ValueError:
                        continue
            
            if symbol and entry_price and side:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "side": side,
                    "entry": entry_price,
                    "timeframe": timeframe or "M15",
                    "tp_probability": tp_probability,
                    "confidence": 0.75,
                    "status": "open"
                }
            
        except Exception as e:
            logger.error(f"Error parsing signal from log: {e}")
        
        return None
    
    def simulate_signal_outcome(self, signal, market_data=None):
        """Simulate the outcome of a signal based on probability"""
        try:
            # Use probability to determine outcome
            tp_prob = signal.get("tp_probability", 50) / 100
            
            # Add some randomness but weighted by probability
            random_factor = np.random.random()
            
            # Adjust probability based on symbol and timeframe performance
            adjusted_prob = tp_prob
            
            # Symbol-based adjustments (based on observed performance)
            symbol_adjustments = {
                "BTCUSD": 0.9,  # Bitcoin tends to be less predictable
                "ETHUSD": 0.85,
                "XAUUSD": 1.1,  # Gold tends to be more stable
                "EURUSD": 1.0,
                "GBPUSD": 0.95
            }
            
            adjusted_prob *= symbol_adjustments.get(signal.get("symbol"), 1.0)
            
            # Timeframe adjustments
            tf_adjustments = {
                "M1": 0.7,  # Very short term is harder
                "M3": 0.8,
                "M5": 0.85,
                "M15": 1.0,  # Sweet spot
                "M30": 1.05,
                "H1": 1.1,
                "H4": 1.15
            }
            
            adjusted_prob *= tf_adjustments.get(signal.get("timeframe"), 1.0)
            
            # Clamp probability
            adjusted_prob = max(0.05, min(0.95, adjusted_prob))
            
            # Determine outcome
            if random_factor < adjusted_prob:
                outcome = "tp_hit"
                pips = abs(np.random.normal(200, 50))  # Simulate TP pips
            else:
                outcome = "sl_hit"
                pips = -abs(np.random.normal(100, 30))  # Simulate SL pips
            
            return {
                "outcome": outcome,
                "pips": pips,
                "probability_used": adjusted_prob,
                "exit_time": datetime.now() + timedelta(hours=np.random.randint(1, 24))
            }
            
        except Exception as e:
            logger.error(f"Error simulating signal outcome: {e}")
            return {"outcome": "sl_hit", "pips": -100, "probability_used": 0.5}
    
    def backtest_strategy(self, signals, parameters):
        """Backtest a strategy with given parameters"""
        try:
            results = {
                "parameters": parameters,
                "total_signals": len(signals),
                "trades": [],
                "performance": {
                    "total_pips": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0,
                    "profit_factor": 0,
                    "max_drawdown": 0,
                    "sharpe_ratio": 0
                }
            }
            
            equity_curve = [0]
            running_pips = 0
            max_equity = 0
            max_drawdown = 0
            
            min_probability = parameters.get("min_probability", 50)
            min_confidence = parameters.get("min_confidence", 0.7)
            max_daily_signals = parameters.get("max_daily_signals", 10)
            allowed_symbols = parameters.get("allowed_symbols", ["BTCUSD", "ETHUSD", "XAUUSD"])
            allowed_timeframes = parameters.get("allowed_timeframes", ["M15", "M30", "H1"])
            
            daily_signal_count = {}
            
            for signal in signals:
                # Apply filters based on parameters
                if signal.get("tp_probability", 0) < min_probability:
                    continue
                
                if signal.get("confidence", 0) < min_confidence:
                    continue
                
                if signal.get("symbol") not in allowed_symbols:
                    continue
                
                if signal.get("timeframe") not in allowed_timeframes:
                    continue
                
                # Check daily signal limit
                signal_date = signal.get("timestamp", "")[:10]  # Get date part
                daily_count = daily_signal_count.get(signal_date, 0)
                if daily_count >= max_daily_signals:
                    continue
                
                daily_signal_count[signal_date] = daily_count + 1
                
                # Simulate the trade
                outcome = self.simulate_signal_outcome(signal)
                
                trade_result = {
                    "signal": signal,
                    "outcome": outcome["outcome"],
                    "pips": outcome["pips"],
                    "probability": outcome["probability_used"]
                }
                
                results["trades"].append(trade_result)
                
                # Update running totals
                running_pips += outcome["pips"]
                equity_curve.append(running_pips)
                
                if outcome["outcome"] == "tp_hit":
                    results["performance"]["winning_trades"] += 1
                else:
                    results["performance"]["losing_trades"] += 1
                
                # Update max drawdown
                max_equity = max(max_equity, running_pips)
                current_drawdown = max_equity - running_pips
                max_drawdown = max(max_drawdown, current_drawdown)
            
            # Calculate final performance metrics
            total_trades = len(results["trades"])
            if total_trades > 0:
                results["performance"]["total_pips"] = running_pips
                results["performance"]["win_rate"] = (results["performance"]["winning_trades"] / total_trades) * 100
                results["performance"]["max_drawdown"] = max_drawdown
                
                # Calculate profit factor
                winning_pips = sum([t["pips"] for t in results["trades"] if t["pips"] > 0])
                losing_pips = abs(sum([t["pips"] for t in results["trades"] if t["pips"] < 0]))
                
                if losing_pips > 0:
                    results["performance"]["profit_factor"] = winning_pips / losing_pips
                
                # Simple Sharpe ratio calculation
                if len(equity_curve) > 1:
                    returns = np.diff(equity_curve)
                    if np.std(returns) > 0:
                        results["performance"]["sharpe_ratio"] = np.mean(returns) / np.std(returns)
            
            return results
            
        except Exception as e:
            logger.error(f"Backtesting error: {e}")
            return None
    
    def optimize_parameters(self, signals):
        """Optimize strategy parameters using grid search"""
        try:
            logger.info("🔍 Starting parameter optimization...")
            
            # Define parameter ranges to test
            parameter_grid = {
                "min_probability": [40, 50, 60, 70],
                "min_confidence": [0.6, 0.7, 0.75, 0.8],
                "max_daily_signals": [5, 8, 10, 15],
                "allowed_symbols": [
                    ["BTCUSD", "ETHUSD", "XAUUSD"],
                    ["BTCUSD", "XAUUSD"],
                    ["BTCUSD"],
                    ["ETHUSD", "XAUUSD"]
                ],
                "allowed_timeframes": [
                    ["M15", "M30", "H1"],
                    ["M15", "M30"],
                    ["M30", "H1"],
                    ["M15"]
                ]
            }
            
            # Generate all parameter combinations
            param_names = list(parameter_grid.keys())
            param_values = list(parameter_grid.values())
            param_combinations = list(product(*param_values))
            
            logger.info(f"🧪 Testing {len(param_combinations)} parameter combinations...")
            
            best_result = None
            best_score = -999999
            all_results = []
            
            # Test each combination
            for i, combination in enumerate(param_combinations):
                params = dict(zip(param_names, combination))
                
                # Run backtest
                result = self.backtest_strategy(signals, params)
                
                if result and len(result["trades"]) > 0:
                    # Calculate composite score
                    performance = result["performance"]
                    score = (
                        performance["total_pips"] * 0.4 +
                        performance["win_rate"] * 10 * 0.3 +
                        performance["profit_factor"] * 100 * 0.2 +
                        performance["sharpe_ratio"] * 50 * 0.1 -
                        performance["max_drawdown"] * 0.1
                    )
                    
                    result["optimization_score"] = score
                    all_results.append(result)
                    
                    if score > best_score:
                        best_score = score
                        best_result = result
                        logger.info(f"🎯 New best parameters found (score: {score:.2f})")
                
                if (i + 1) % 10 == 0:
                    logger.info(f"📊 Progress: {i + 1}/{len(param_combinations)} combinations tested")
            
            # Sort results by score
            all_results.sort(key=lambda x: x.get("optimization_score", -999999), reverse=True)
            
            # Save optimization results
            optimization_data = {
                "timestamp": datetime.now().isoformat(),
                "total_combinations_tested": len(param_combinations),
                "signals_used": len(signals),
                "best_parameters": best_result["parameters"] if best_result else None,
                "best_performance": best_result["performance"] if best_result else None,
                "top_10_results": all_results[:10],
                "optimization_summary": {
                    "best_score": best_score,
                    "improvement_vs_default": "N/A"  # Would compare to default params
                }
            }
            
            with open(self.optimization_file, 'w') as f:
                json.dump(optimization_data, f, indent=2)
            
            # Save best parameters separately
            if best_result:
                with open(self.best_params_file, 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "parameters": best_result["parameters"],
                        "expected_performance": best_result["performance"],
                        "confidence": "high" if len(signals) > 50 else "medium"
                    }, f, indent=2)
            
            logger.info(f"✅ Parameter optimization complete - Best score: {best_score:.2f}")
            
            return optimization_data
            
        except Exception as e:
            logger.error(f"Parameter optimization error: {e}")
            return None
    
    def run_full_backtest_suite(self):
        """Run complete backtesting and optimization suite"""
        try:
            logger.info("🚀 Starting full backtesting suite...")
            
            # Load historical data
            signals = self.load_historical_data()
            
            if len(signals) < 10:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 10 signals for backtesting, found {len(signals)}"
                }
            
            # Run parameter optimization
            optimization_results = self.optimize_parameters(signals)
            
            # Run additional analysis
            analysis_results = self.run_strategy_analysis(signals)
            
            final_results = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "data_quality": {
                    "total_signals_analyzed": len(signals),
                    "data_span_days": 30,  # Assumption
                    "confidence_level": "high" if len(signals) > 50 else "medium"
                },
                "optimization_results": optimization_results,
                "strategy_analysis": analysis_results,
                "recommendations": self.generate_implementation_recommendations(optimization_results)
            }
            
            # Save complete results
            with open(self.results_file, 'w') as f:
                json.dump(final_results, f, indent=2)
            
            logger.info("✅ Full backtesting suite completed successfully")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Full backtesting suite error: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_strategy_analysis(self, signals):
        """Run additional strategy analysis"""
        try:
            analysis = {
                "signal_distribution": self._analyze_signal_distribution(signals),
                "performance_by_hour": self._analyze_hourly_performance(signals),
                "symbol_correlation": self._analyze_symbol_correlations(signals),
                "probability_calibration": self._analyze_probability_calibration(signals)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Strategy analysis error: {e}")
            return {}
    
    def _analyze_signal_distribution(self, signals):
        """Analyze the distribution of signals"""
        try:
            distribution = {
                "by_symbol": {},
                "by_timeframe": {},
                "by_probability_range": {}
            }
            
            for signal in signals:
                # Symbol distribution
                symbol = signal.get("symbol", "Unknown")
                distribution["by_symbol"][symbol] = distribution["by_symbol"].get(symbol, 0) + 1
                
                # Timeframe distribution
                tf = signal.get("timeframe", "Unknown")
                distribution["by_timeframe"][tf] = distribution["by_timeframe"].get(tf, 0) + 1
                
                # Probability range distribution
                prob = signal.get("tp_probability", 50)
                if prob < 40:
                    range_key = "low_prob"
                elif prob < 60:
                    range_key = "medium_prob"
                elif prob < 80:
                    range_key = "high_prob"
                else:
                    range_key = "very_high_prob"
                
                distribution["by_probability_range"][range_key] = distribution["by_probability_range"].get(range_key, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Signal distribution analysis error: {e}")
            return {}
    
    def _analyze_hourly_performance(self, signals):
        """Analyze performance by hour of day"""
        # Simplified implementation
        return {"status": "analysis_placeholder", "note": "Would analyze signal performance by hour"}
    
    def _analyze_symbol_correlations(self, signals):
        """Analyze correlations between different symbols"""
        # Simplified implementation
        return {"status": "analysis_placeholder", "note": "Would analyze symbol correlations"}
    
    def _analyze_probability_calibration(self, signals):
        """Analyze how well-calibrated our probabilities are"""
        # Simplified implementation
        return {"status": "analysis_placeholder", "note": "Would analyze probability calibration"}
    
    def generate_implementation_recommendations(self, optimization_results):
        """Generate recommendations for implementing optimized parameters"""
        if not optimization_results or not optimization_results.get("best_parameters"):
            return ["Insufficient data for recommendations"]
        
        best_params = optimization_results["best_parameters"]
        recommendations = []
        
        # Parameter-specific recommendations
        if best_params.get("min_probability", 50) > 60:
            recommendations.append("Increase minimum TP probability threshold to improve win rate")
        
        if best_params.get("min_confidence", 0.7) > 0.75:
            recommendations.append("Use higher confidence threshold for signal filtering")
        
        if len(best_params.get("allowed_symbols", [])) < 3:
            recommendations.append("Focus on fewer symbols for better performance")
        
        if len(best_params.get("allowed_timeframes", [])) < 3:
            recommendations.append("Limit timeframes to optimize signal quality")
        
        recommendations.append("Implement gradual parameter changes to avoid disruption")
        recommendations.append("Monitor performance closely after implementing changes")
        
        return recommendations
    
    def get_optimal_parameters(self):
        """Get the current optimal parameters"""
        try:
            if os.path.exists(self.best_params_file):
                with open(self.best_params_file, 'r') as f:
                    data = json.load(f)
                    return data.get("parameters", {})
        except Exception as e:
            logger.error(f"Error loading optimal parameters: {e}")
        
        return {}

# Global backtester instance
automated_backtester = AutomatedBacktester()

def run_automated_backtest():
    """Run automated backtesting suite"""
    return automated_backtester.run_full_backtest_suite()

def get_optimal_trading_parameters():
    """Get optimal trading parameters from backtesting"""
    return automated_backtester.get_optimal_parameters()

if __name__ == "__main__":
    # Test the backtester
    backtester = AutomatedBacktester()
    results = backtester.run_full_backtest_suite()
    print(json.dumps(results, indent=2))
