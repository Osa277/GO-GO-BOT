#!/usr/bin/env python3
"""
AI-Powered Signal Optimizer
Advanced machine learning system for optimizing trading signals based on historical performance.
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import os

logger = logging.getLogger(__name__)

class AISignalOptimizer:
    def __init__(self):
        self.performance_file = "ai_optimization_data.json"
        self.recommendations_file = "ai_recommendations.json"
        self.learning_data = self.load_learning_data()
        self.min_samples_for_learning = 10
        
    def load_learning_data(self):
        """Load historical learning data"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
        
        return {
            "signals": [],
            "performance_patterns": {},
            "optimization_history": [],
            "last_optimization": None
        }
    
    def save_learning_data(self):
        """Save learning data to file"""
        try:
            self.learning_data["last_updated"] = datetime.now().isoformat()
            
            # Convert numpy types to Python native types for JSON serialization
            def convert_numpy_types(obj):
                if hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(v) for v in obj]
                return obj
            
            serializable_data = convert_numpy_types(self.learning_data)
            
            with open(self.performance_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def analyze_signal_patterns(self):
        """Advanced pattern analysis using machine learning concepts"""
        signals = self.learning_data.get("signals", [])
        if len(signals) < self.min_samples_for_learning:
            return {"status": "insufficient_data", "samples": len(signals)}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(signals)
        
        patterns = {
            "symbol_performance": self._analyze_symbol_patterns(df),
            "timeframe_effectiveness": self._analyze_timeframe_patterns(df),
            "probability_accuracy": self._analyze_probability_accuracy(df),
            "market_condition_impact": self._analyze_market_conditions(df),
            "signal_strength_correlation": self._analyze_signal_strength(df),
            "time_based_patterns": self._analyze_time_patterns(df)
        }
        
        return patterns
    
    def _analyze_symbol_patterns(self, df):
        """Analyze performance patterns by symbol"""
        symbol_stats = {}
        
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol]
            completed = symbol_df[symbol_df['status'].isin(['tp_hit', 'sl_hit'])]
            
            if len(completed) > 0:
                win_rate = len(completed[completed['status'] == 'tp_hit']) / len(completed)
                avg_probability = completed['tp_probability'].mean() if 'tp_probability' in completed.columns else 0
                avg_actual_performance = win_rate
                
                # Calculate probability accuracy
                prob_accuracy = 1 - abs(avg_probability/100 - win_rate) if avg_probability > 0 else 0
                
                symbol_stats[symbol] = {
                    "win_rate": round(win_rate * 100, 2),
                    "total_signals": len(symbol_df),
                    "completed_signals": len(completed),
                    "avg_predicted_probability": round(avg_probability, 2),
                    "probability_accuracy": round(prob_accuracy * 100, 2),
                    "recommendation": self._get_symbol_recommendation(win_rate, prob_accuracy)
                }
        
        return symbol_stats
    
    def _analyze_timeframe_patterns(self, df):
        """Analyze performance patterns by timeframe"""
        timeframe_stats = {}
        
        for tf in df['timeframe'].unique():
            tf_df = df[df['timeframe'] == tf]
            completed = tf_df[tf_df['status'].isin(['tp_hit', 'sl_hit'])]
            
            if len(completed) > 0:
                win_rate = len(completed[completed['status'] == 'tp_hit']) / len(completed)
                
                timeframe_stats[tf] = {
                    "win_rate": round(win_rate * 100, 2),
                    "total_signals": len(tf_df),
                    "completed_signals": len(completed),
                    "effectiveness_rating": self._rate_effectiveness(win_rate),
                    "recommendation": "increase_weight" if win_rate > 0.4 else "decrease_weight"
                }
        
        return timeframe_stats
    
    def _analyze_probability_accuracy(self, df):
        """Analyze how accurate our probability predictions are"""
        completed = df[df['status'].isin(['tp_hit', 'sl_hit'])]
        if len(completed) == 0:
            return {"status": "no_completed_signals"}
        
        # Calculate actual vs predicted accuracy
        accuracy_data = []
        
        for _, signal in completed.iterrows():
            if 'tp_probability' in signal and pd.notna(signal['tp_probability']):
                predicted_prob = signal['tp_probability'] / 100
                actual_outcome = 1 if signal['status'] == 'tp_hit' else 0
                accuracy = 1 - abs(predicted_prob - actual_outcome)
                accuracy_data.append({
                    "predicted": predicted_prob,
                    "actual": actual_outcome,
                    "accuracy": accuracy
                })
        
        if accuracy_data:
            avg_accuracy = np.mean([d['accuracy'] for d in accuracy_data])
            return {
                "average_accuracy": round(avg_accuracy * 100, 2),
                "total_predictions": len(accuracy_data),
                "calibration_needed": avg_accuracy < 0.7,
                "recommendation": self._get_calibration_recommendation(avg_accuracy)
            }
        
        return {"status": "no_probability_data"}
    
    def _analyze_market_conditions(self, df):
        """Analyze performance under different market conditions"""
        # This would analyze volatility, time of day, market trends, etc.
        conditions = {
            "high_volatility": {"win_rate": 0, "signals": 0},
            "low_volatility": {"win_rate": 0, "signals": 0},
            "trending_market": {"win_rate": 0, "signals": 0},
            "ranging_market": {"win_rate": 0, "signals": 0}
        }
        
        # Simple implementation - would be enhanced with actual market data
        completed = df[df['status'].isin(['tp_hit', 'sl_hit'])]
        if len(completed) > 0:
            overall_win_rate = len(completed[completed['status'] == 'tp_hit']) / len(completed)
            
            for condition in conditions:
                conditions[condition] = {
                    "win_rate": round(overall_win_rate * 100, 2),
                    "signals": len(completed),
                    "recommendation": "optimize" if overall_win_rate < 0.3 else "maintain"
                }
        
        return conditions
    
    def _analyze_signal_strength(self, df):
        """Analyze correlation between signal strength and outcomes"""
        completed = df[df['status'].isin(['tp_hit', 'sl_hit'])]
        if len(completed) == 0:
            return {"status": "no_data"}
        
        # Analyze confidence levels
        if 'confidence' in completed.columns:
            high_conf = completed[completed['confidence'] > 0.8]
            med_conf = completed[(completed['confidence'] > 0.6) & (completed['confidence'] <= 0.8)]
            low_conf = completed[completed['confidence'] <= 0.6]
            
            stats = {}
            for name, subset in [("high", high_conf), ("medium", med_conf), ("low", low_conf)]:
                if len(subset) > 0:
                    win_rate = len(subset[subset['status'] == 'tp_hit']) / len(subset)
                    stats[f"{name}_confidence"] = {
                        "win_rate": round(win_rate * 100, 2),
                        "signals": len(subset),
                        "should_focus": win_rate > 0.4
                    }
            
            return stats
        
        return {"status": "no_confidence_data"}
    
    def _analyze_time_patterns(self, df):
        """Analyze performance patterns based on time and New York sessions"""
        completed = df[df['status'].isin(['tp_hit', 'sl_hit'])]
        if len(completed) == 0:
            return {"status": "no_data"}
        
        patterns = {}
        
        # Convert timestamps and analyze by hour
        if 'generated_at' in completed.columns:
            completed['hour'] = pd.to_datetime(completed['generated_at']).dt.hour
            
            # Standard hourly analysis
            hourly_stats = {}
            for hour in range(24):
                hour_data = completed[completed['hour'] == hour]
                if len(hour_data) > 0:
                    win_rate = len(hour_data[hour_data['status'] == 'tp_hit']) / len(hour_data)
                    hourly_stats[f"hour_{hour}"] = {
                        "win_rate": round(win_rate * 100, 2),
                        "signals": len(hour_data),
                        "recommendation": "focus" if win_rate > 0.5 else "avoid" if win_rate < 0.2 else "normal"
                    }
            
            patterns["hourly_performance"] = hourly_stats
            
            # New York session analysis (13-22 UTC)
            ny_session_data = completed[completed['hour'].between(13, 22)]
            other_hours_data = completed[~completed['hour'].between(13, 22)]
            
            if len(ny_session_data) > 0 and len(other_hours_data) > 0:
                ny_win_rate = len(ny_session_data[ny_session_data['status'] == 'tp_hit']) / len(ny_session_data)
                other_win_rate = len(other_hours_data[other_hours_data['status'] == 'tp_hit']) / len(other_hours_data)
                
                patterns["session_analysis"] = {
                    "ny_session": {
                        "win_rate": round(ny_win_rate * 100, 2),
                        "signals": len(ny_session_data),
                        "hours": "13-22 UTC (8AM-5PM EST)"
                    },
                    "other_hours": {
                        "win_rate": round(other_win_rate * 100, 2),
                        "signals": len(other_hours_data),
                        "hours": "0-12, 23 UTC"
                    },
                    "ny_advantage": round((ny_win_rate - other_win_rate) * 100, 2),
                    "recommendation": "focus_on_ny" if ny_win_rate > other_win_rate + 0.1 else "session_neutral"
                }
            
            # Overlap session analysis (13-17 UTC - NY-London overlap)
            overlap_data = completed[completed['hour'].between(13, 17)]
            if len(overlap_data) > 0:
                overlap_win_rate = len(overlap_data[overlap_data['status'] == 'tp_hit']) / len(overlap_data)
                patterns["overlap_session"] = {
                    "win_rate": round(overlap_win_rate * 100, 2),
                    "signals": len(overlap_data),
                    "hours": "13-17 UTC (NY-London Overlap)",
                    "performance_rating": "excellent" if overlap_win_rate > 0.7 else "good" if overlap_win_rate > 0.5 else "average"
                }
        
        return patterns if patterns else {"status": "no_time_data"}
    
    def _get_symbol_recommendation(self, win_rate, prob_accuracy):
        """Get recommendation for symbol trading"""
        if win_rate > 0.6 and prob_accuracy > 0.8:
            return "increase_allocation"
        elif win_rate > 0.4 and prob_accuracy > 0.6:
            return "maintain"
        elif win_rate < 0.3 or prob_accuracy < 0.4:
            return "reduce_allocation"
        else:
            return "monitor_closely"
    
    def _rate_effectiveness(self, win_rate):
        """Rate the effectiveness of a strategy component"""
        if win_rate > 0.7:
            return "excellent"
        elif win_rate > 0.5:
            return "good"
        elif win_rate > 0.4:
            return "fair"
        elif win_rate > 0.3:
            return "poor"
        else:
            return "very_poor"
    
    def _get_calibration_recommendation(self, accuracy):
        """Get recommendation for probability calibration"""
        if accuracy > 0.8:
            return "well_calibrated"
        elif accuracy > 0.6:
            return "minor_adjustment_needed"
        elif accuracy > 0.4:
            return "significant_recalibration_needed"
        else:
            return "major_overhaul_required"
    
    def generate_optimization_recommendations(self, patterns):
        """Generate AI-powered optimization recommendations"""
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "confidence_level": "high",
            "recommendations": []
        }
        
        # Symbol-based recommendations
        if "symbol_performance" in patterns:
            for symbol, stats in patterns["symbol_performance"].items():
                if stats["win_rate"] < 20:
                    recommendations["recommendations"].append({
                        "type": "symbol_filter",
                        "action": f"Consider reducing {symbol} signals or increasing minimum probability threshold",
                        "priority": "high",
                        "expected_impact": "reduce_losses",
                        "data": stats
                    })
                elif stats["win_rate"] > 60:
                    recommendations["recommendations"].append({
                        "type": "symbol_optimization",
                        "action": f"Increase {symbol} signal weight - showing strong performance",
                        "priority": "medium",
                        "expected_impact": "increase_profits",
                        "data": stats
                    })
        
        # Timeframe optimization
        if "timeframe_effectiveness" in patterns:
            best_tf = max(patterns["timeframe_effectiveness"].items(), 
                         key=lambda x: x[1]["win_rate"], default=None)
            worst_tf = min(patterns["timeframe_effectiveness"].items(), 
                          key=lambda x: x[1]["win_rate"], default=None)
            
            if best_tf and best_tf[1]["win_rate"] > 50:
                recommendations["recommendations"].append({
                    "type": "timeframe_focus",
                    "action": f"Focus more on {best_tf[0]} timeframe - {best_tf[1]['win_rate']}% win rate",
                    "priority": "medium",
                    "expected_impact": "improve_accuracy"
                })
            
            if worst_tf and worst_tf[1]["win_rate"] < 20:
                recommendations["recommendations"].append({
                    "type": "timeframe_filter",
                    "action": f"Consider filtering out {worst_tf[0]} signals - only {worst_tf[1]['win_rate']}% win rate",
                    "priority": "high",
                    "expected_impact": "reduce_losses"
                })
        
        # Probability calibration
        if "probability_accuracy" in patterns and "average_accuracy" in patterns["probability_accuracy"]:
            accuracy = patterns["probability_accuracy"]["average_accuracy"]
            if accuracy < 70:
                recommendations["recommendations"].append({
                    "type": "probability_calibration",
                    "action": f"Recalibrate probability model - current accuracy: {accuracy}%",
                    "priority": "high",
                    "expected_impact": "improve_predictions",
                    "suggestion": "Adjust probability calculation weights and add more market factors"
                })
        
        # Time-based and session optimization
        if "time_based_patterns" in patterns:
            time_patterns = patterns["time_based_patterns"]
            
            # NY session-specific recommendations
            if "session_analysis" in time_patterns:
                session_data = time_patterns["session_analysis"]
                ny_advantage = session_data.get("ny_advantage", 0)
                
                if ny_advantage > 10:  # NY session is 10%+ better
                    recommendations["recommendations"].append({
                        "type": "session_optimization",
                        "action": f"Focus on New York session (13-22 UTC) - {ny_advantage:.1f}% better performance",
                        "priority": "high",
                        "expected_impact": "improve_accuracy",
                        "data": session_data["ny_session"]
                    })
                elif ny_advantage < -10:  # NY session is 10%+ worse
                    recommendations["recommendations"].append({
                        "type": "session_filter",
                        "action": f"Consider avoiding NY session - {abs(ny_advantage):.1f}% worse performance",
                        "priority": "medium",
                        "expected_impact": "reduce_losses",
                        "data": session_data
                    })
            
            # Overlap session recommendations
            if "overlap_session" in time_patterns:
                overlap_data = time_patterns["overlap_session"]
                if overlap_data["win_rate"] > 60:
                    recommendations["recommendations"].append({
                        "type": "overlap_focus",
                        "action": f"Prioritize NY-London overlap (13-17 UTC) - {overlap_data['win_rate']}% win rate",
                        "priority": "high",
                        "expected_impact": "maximize_profits",
                        "data": overlap_data
                    })
            
            # Hourly performance recommendations
            if "hourly_performance" in time_patterns:
                hourly_data = time_patterns["hourly_performance"]
                
                # Find best and worst performing hours
                best_hours = [(hour, data) for hour, data in hourly_data.items() 
                             if data["win_rate"] > 70 and data["signals"] >= 3]
                worst_hours = [(hour, data) for hour, data in hourly_data.items() 
                              if data["win_rate"] < 20 and data["signals"] >= 3]
                
                if best_hours:
                    best_hour_info = max(best_hours, key=lambda x: x[1]["win_rate"])
                    hour = int(best_hour_info[0].split('_')[1])
                    recommendations["recommendations"].append({
                        "type": "hour_focus",
                        "action": f"Focus on hour {hour}:00 UTC - {best_hour_info[1]['win_rate']}% win rate",
                        "priority": "medium",
                        "expected_impact": "improve_timing"
                    })
                
                if worst_hours:
                    worst_hour_info = min(worst_hours, key=lambda x: x[1]["win_rate"])
                    hour = int(worst_hour_info[0].split('_')[1])
                    recommendations["recommendations"].append({
                        "type": "hour_avoidance",
                        "action": f"Avoid trading at hour {hour}:00 UTC - only {worst_hour_info[1]['win_rate']}% win rate",
                        "priority": "medium",
                        "expected_impact": "reduce_losses"
                    })
        
        # Signal strength optimization
        if "signal_strength_correlation" in patterns:
            for strength, data in patterns["signal_strength_correlation"].items():
                if "should_focus" in data and data["should_focus"]:
                    recommendations["recommendations"].append({
                        "type": "signal_filtering",
                        "action": f"Focus on {strength} signals - {data['win_rate']}% win rate",
                        "priority": "medium",
                        "expected_impact": "improve_quality"
                    })
        
        return recommendations
    
    def record_signal_outcome(self, signal_data):
        """Record a signal outcome for learning"""
        try:
            # Ensure signal has required fields
            signal_record = {
                "timestamp": datetime.now().isoformat(),
                "symbol": signal_data.get("symbol"),
                "side": signal_data.get("side"),
                "entry": signal_data.get("entry"),
                "tp": signal_data.get("tp"),
                "sl": signal_data.get("sl"),
                "timeframe": signal_data.get("tf"),
                "status": signal_data.get("status", "open"),
                "tp_probability": signal_data.get("tp_probability", 0),
                "confidence": signal_data.get("confidence", 0.75),
                "generated_at": signal_data.get("generated_at", datetime.now().isoformat()),
                "exit_price": signal_data.get("exit_price"),
                "exit_time": signal_data.get("exit_time")
            }
            
            self.learning_data["signals"].append(signal_record)
            
            # Keep only recent signals (last 1000)
            if len(self.learning_data["signals"]) > 1000:
                self.learning_data["signals"] = self.learning_data["signals"][-1000:]
            
            self.save_learning_data()
            logger.info(f"🤖 AI: Recorded signal outcome for {signal_data.get('symbol')} - {signal_data.get('status')}")
            
        except Exception as e:
            logger.error(f"Error recording signal outcome: {e}")
    
    def run_optimization_analysis(self):
        """Run complete AI optimization analysis"""
        try:
            logger.info("🤖 AI: Starting optimization analysis...")
            
            # Analyze patterns
            patterns = self.analyze_signal_patterns()
            
            if patterns.get("status") == "insufficient_data":
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least {self.min_samples_for_learning} signals for analysis",
                    "current_samples": patterns.get("samples", 0)
                }
            
            # Generate recommendations
            recommendations = self.generate_optimization_recommendations(patterns)
            
            # Save recommendations
            def convert_numpy_types(obj):
                if hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(v) for v in obj]
                return obj
            
            analysis_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "patterns": patterns,
                "recommendations": recommendations,
                "data_quality": {
                    "total_signals": len(self.learning_data["signals"]),
                    "analysis_confidence": "high" if len(self.learning_data["signals"]) > 50 else "medium"
                }
            }
            
            with open(self.recommendations_file, 'w') as f:
                json.dump(convert_numpy_types(analysis_data), f, indent=2)
            
            logger.info(f"🤖 AI: Analysis complete - {len(recommendations['recommendations'])} recommendations generated")
            
            return {
                "status": "success",
                "patterns": patterns,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"AI optimization analysis error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_dynamic_probability_adjustments(self, symbol, timeframe):
        """Get dynamic probability adjustments based on learning"""
        try:
            # Load latest patterns
            if os.path.exists(self.recommendations_file):
                with open(self.recommendations_file, 'r') as f:
                    data = json.load(f)
                    patterns = data.get("patterns", {})
                    
                    adjustments = {"probability_multiplier": 1.0, "confidence_adjustment": 0.0}
                    
                    # Symbol-based adjustment
                    symbol_data = patterns.get("symbol_performance", {}).get(symbol, {})
                    if symbol_data:
                        win_rate = symbol_data.get("win_rate", 50) / 100
                        if win_rate > 0.6:
                            adjustments["probability_multiplier"] *= 1.1
                        elif win_rate < 0.3:
                            adjustments["probability_multiplier"] *= 0.9
                    
                    # Timeframe-based adjustment
                    tf_data = patterns.get("timeframe_effectiveness", {}).get(timeframe, {})
                    if tf_data:
                        tf_win_rate = tf_data.get("win_rate", 50) / 100
                        if tf_win_rate > 0.5:
                            adjustments["confidence_adjustment"] += 0.05
                        elif tf_win_rate < 0.3:
                            adjustments["confidence_adjustment"] -= 0.05
                    
                    return adjustments
            
            return {"probability_multiplier": 1.0, "confidence_adjustment": 0.0}
            
        except Exception as e:
            logger.error(f"Error getting dynamic adjustments: {e}")
            return {"probability_multiplier": 1.0, "confidence_adjustment": 0.0}

# Global optimizer instance
ai_optimizer = AISignalOptimizer()

def record_signal_for_ai_learning(signal_data):
    """Helper function to record signal outcomes for AI learning"""
    ai_optimizer.record_signal_outcome(signal_data)

def get_ai_optimization_report():
    """Generate AI optimization report"""
    return ai_optimizer.run_optimization_analysis()

def get_ai_probability_adjustments(symbol, timeframe):
    """Get AI-based probability adjustments"""
    return ai_optimizer.get_dynamic_probability_adjustments(symbol, timeframe)

if __name__ == "__main__":
    # Test the AI optimizer
    optimizer = AISignalOptimizer()
    result = optimizer.run_optimization_analysis()
    print(json.dumps(result, indent=2))
