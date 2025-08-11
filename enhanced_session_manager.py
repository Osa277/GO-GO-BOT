#!/usr/bin/env python3
"""
Enhanced Market Session Manager
Optimizes trading based on market sessions, volatility patterns, and economic events
"""

import logging
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import json
import os

logger = logging.getLogger(__name__)

class EnhancedSessionManager:
    def __init__(self):
        self.session_file = "session_data.json"
        self.load_session_data()
        
        # Define market sessions (UTC times)
        self.sessions = {
            'tokyo': {'start': 0, 'end': 9},      # 00:00-09:00 UTC
            'london': {'start': 8, 'end': 17},    # 08:00-17:00 UTC  
            'new_york': {'start': 13, 'end': 22}, # 13:00-22:00 UTC
            'sydney': {'start': 22, 'end': 7}     # 22:00-07:00 UTC (next day)
        }
        
        # Session characteristics for different symbols
        self.session_characteristics = {
            'BTCUSD': {
                'best_sessions': ['new_york', 'london'],
                'high_volatility': ['new_york'],
                'low_volatility': ['tokyo'],
                'overlap_boost': {'london_ny': 1.3, 'tokyo_london': 1.1}
            },
            'XAUUSD': {
                'best_sessions': ['london', 'new_york'],
                'high_volatility': ['london', 'new_york'],
                'low_volatility': ['tokyo'],
                'overlap_boost': {'london_ny': 1.4, 'tokyo_london': 1.2}
            }
        }
    
    def load_session_data(self):
        """Load historical session performance data"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    self.session_data = json.load(f)
            else:
                self.session_data = {
                    'session_performance': {},
                    'hourly_stats': {},
                    'volatility_patterns': {}
                }
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
            self.session_data = {'session_performance': {}, 'hourly_stats': {}, 'volatility_patterns': {}}
    
    def save_session_data(self):
        """Save session data to file"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
    
    def get_current_session_info(self) -> Dict:
        """Get detailed current session information"""
        now_utc = datetime.utcnow()
        current_hour = now_utc.hour
        
        active_sessions = []
        overlaps = []
        
        # Check which sessions are active
        for session_name, times in self.sessions.items():
            start, end = times['start'], times['end']
            
            # Handle sessions that cross midnight
            if start > end:  # Like Sydney: 22:00-07:00
                if current_hour >= start or current_hour <= end:
                    active_sessions.append(session_name)
            else:
                if start <= current_hour <= end:
                    active_sessions.append(session_name)
        
        # Check for overlaps
        if 'london' in active_sessions and 'new_york' in active_sessions:
            overlaps.append('london_ny')
        if 'tokyo' in active_sessions and 'london' in active_sessions:
            overlaps.append('tokyo_london')
        if 'new_york' in active_sessions and 'sydney' in active_sessions:
            overlaps.append('ny_sydney')
        
        # Determine session priority
        priority_score = 0.5  # Base score
        
        if 'london_ny' in overlaps:
            priority_score = 1.0  # Highest priority
        elif 'new_york' in active_sessions:
            priority_score = 0.9
        elif 'london' in active_sessions:
            priority_score = 0.8
        elif 'tokyo_london' in overlaps:
            priority_score = 0.7
        elif 'tokyo' in active_sessions:
            priority_score = 0.6
        
        return {
            'current_hour_utc': current_hour,
            'active_sessions': active_sessions,
            'overlaps': overlaps,
            'priority_score': priority_score,
            'is_prime_time': priority_score >= 0.8,
            'volatility_expected': 'new_york' in active_sessions or 'london' in active_sessions
        }
    
    def get_symbol_session_multiplier(self, symbol: str) -> Dict:
        """Get session-based multipliers for a specific symbol"""
        session_info = self.get_current_session_info()
        characteristics = self.session_characteristics.get(symbol, {})
        
        # Base multipliers
        multipliers = {
            'probability_multiplier': 1.0,
            'confidence_boost': 0.0,
            'position_size_factor': 1.0,
            'take_profit_adjustment': 1.0
        }
        
        recommendations = []
        
        # Apply session-specific adjustments
        active_sessions = session_info['active_sessions']
        overlaps = session_info['overlaps']
        
        # Check if in best sessions for this symbol
        best_sessions = characteristics.get('best_sessions', [])
        if any(session in active_sessions for session in best_sessions):
            multipliers['probability_multiplier'] *= 1.2
            multipliers['confidence_boost'] += 0.05
            recommendations.append(f"✅ {symbol} performs well during current session")
        
        # Apply overlap bonuses
        overlap_boosts = characteristics.get('overlap_boost', {})
        for overlap in overlaps:
            if overlap in overlap_boosts:
                boost = overlap_boosts[overlap]
                multipliers['probability_multiplier'] *= boost
                multipliers['position_size_factor'] *= min(1.5, boost)
                recommendations.append(f"🚀 {overlap.replace('_', '-').upper()} overlap active (+{(boost-1)*100:.0f}% boost)")
        
        # Volatility adjustments
        if session_info['volatility_expected']:
            high_vol_sessions = characteristics.get('high_volatility', [])
            if any(session in active_sessions for session in high_vol_sessions):
                multipliers['take_profit_adjustment'] *= 1.3  # Wider TPs in high volatility
                recommendations.append("⚡ High volatility expected - TPs adjusted")
            else:
                multipliers['probability_multiplier'] *= 0.9  # Slightly reduce probability in unexpected volatility
                recommendations.append("⚠️ Volatility expected but not in optimal session")
        
        # Prime time bonus
        if session_info['is_prime_time']:
            multipliers['confidence_boost'] += 0.03
            recommendations.append("⭐ Prime trading time - confidence boosted")
        
        # Low activity penalty
        if session_info['priority_score'] < 0.6:
            multipliers['probability_multiplier'] *= 0.8
            multipliers['position_size_factor'] *= 0.7
            recommendations.append("😴 Low activity period - reduced exposure")
        
        return {
            'multipliers': multipliers,
            'session_info': session_info,
            'recommendations': recommendations,
            'optimal_for_symbol': any(session in active_sessions for session in best_sessions)
        }
    
    def get_hourly_performance_factor(self, symbol: str) -> float:
        """Get performance factor based on historical hourly data"""
        current_hour = datetime.utcnow().hour
        hour_key = f"hour_{current_hour}"
        
        # Get historical performance for this hour
        hourly_stats = self.session_data.get('hourly_stats', {})
        symbol_stats = hourly_stats.get(symbol, {})
        hour_stats = symbol_stats.get(hour_key, {'win_rate': 50, 'avg_pips': 0, 'signals': 0})
        
        win_rate = hour_stats.get('win_rate', 50)
        signal_count = hour_stats.get('signals', 0)
        
        # Calculate factor based on historical performance
        if signal_count >= 5:  # Enough data
            if win_rate >= 70:
                return 1.3  # Strong performance
            elif win_rate >= 60:
                return 1.1  # Good performance
            elif win_rate <= 30:
                return 0.7  # Poor performance
            elif win_rate <= 40:
                return 0.9  # Below average
        
        return 1.0  # Neutral/insufficient data
    
    def record_session_performance(self, signal: Dict, outcome: str):
        """Record performance data for session analysis"""
        try:
            session_info = self.get_current_session_info()
            symbol = signal['symbol']
            current_hour = session_info['current_hour_utc']
            
            # Initialize structures if needed
            if 'session_performance' not in self.session_data:
                self.session_data['session_performance'] = {}
            if 'hourly_stats' not in self.session_data:
                self.session_data['hourly_stats'] = {}
            
            # Record session performance
            for session in session_info['active_sessions']:
                session_key = f"{symbol}_{session}"
                if session_key not in self.session_data['session_performance']:
                    self.session_data['session_performance'][session_key] = {
                        'total_signals': 0, 'wins': 0, 'losses': 0, 'total_pips': 0
                    }
                
                perf = self.session_data['session_performance'][session_key]
                perf['total_signals'] += 1
                
                if outcome in ['tp_hit', 'tp1_hit', 'tp2_hit', 'tp3_hit']:
                    perf['wins'] += 1
                    perf['total_pips'] += signal.get('pnl_pips', 0)
                else:
                    perf['losses'] += 1
                    perf['total_pips'] += signal.get('pnl_pips', 0)
            
            # Record hourly stats
            if symbol not in self.session_data['hourly_stats']:
                self.session_data['hourly_stats'][symbol] = {}
            
            hour_key = f"hour_{current_hour}"
            if hour_key not in self.session_data['hourly_stats'][symbol]:
                self.session_data['hourly_stats'][symbol][hour_key] = {
                    'signals': 0, 'wins': 0, 'total_pips': 0
                }
            
            hour_stats = self.session_data['hourly_stats'][symbol][hour_key]
            hour_stats['signals'] += 1
            
            if outcome in ['tp_hit', 'tp1_hit', 'tp2_hit', 'tp3_hit']:
                hour_stats['wins'] += 1
            
            hour_stats['total_pips'] += signal.get('pnl_pips', 0)
            hour_stats['win_rate'] = (hour_stats['wins'] / hour_stats['signals']) * 100
            hour_stats['avg_pips'] = hour_stats['total_pips'] / hour_stats['signals']
            
            self.save_session_data()
            
        except Exception as e:
            logger.error(f"Error recording session performance: {e}")
    
    def get_session_recommendation(self, symbol: str) -> Dict:
        """Get comprehensive session-based trading recommendation"""
        try:
            session_analysis = self.get_symbol_session_multiplier(symbol)
            hourly_factor = self.get_hourly_performance_factor(symbol)
            session_info = session_analysis['session_info']
            
            # Overall recommendation score
            overall_score = (session_info['priority_score'] * 0.6 + 
                           (session_analysis['multipliers']['probability_multiplier'] - 1) * 0.4)
            
            if overall_score >= 0.8:
                recommendation = "🟢 EXCELLENT - Optimal trading conditions"
                action = "TRADE_AGGRESSIVELY"
            elif overall_score >= 0.6:
                recommendation = "🟡 GOOD - Favorable conditions"
                action = "TRADE_NORMALLY"
            elif overall_score >= 0.4:
                recommendation = "🟠 FAIR - Proceed with caution"
                action = "TRADE_CONSERVATIVELY"
            else:
                recommendation = "🔴 POOR - Consider avoiding"
                action = "AVOID_TRADING"
            
            return {
                'recommendation': recommendation,
                'action': action,
                'overall_score': overall_score,
                'session_analysis': session_analysis,
                'hourly_factor': hourly_factor,
                'next_optimal_session': self.get_next_optimal_session(symbol)
            }
            
        except Exception as e:
            logger.error(f"Error getting session recommendation: {e}")
            return {'recommendation': '❌ Error', 'action': 'TRADE_NORMALLY', 'overall_score': 0.5}
    
    def get_next_optimal_session(self, symbol: str) -> Dict:
        """Find when the next optimal trading session begins"""
        characteristics = self.session_characteristics.get(symbol, {})
        best_sessions = characteristics.get('best_sessions', ['london', 'new_york'])
        
        now_utc = datetime.utcnow()
        current_hour = now_utc.hour
        
        # Find next optimal session
        hours_until_optimal = 24  # Maximum hours to check
        
        for session in best_sessions:
            session_start = self.sessions[session]['start']
            
            if session_start > current_hour:
                hours_until = session_start - current_hour
            else:
                hours_until = (24 - current_hour) + session_start
            
            if hours_until < hours_until_optimal:
                hours_until_optimal = hours_until
                next_session = session
        
        return {
            'session': next_session,
            'hours_until': hours_until_optimal,
            'start_time_utc': (now_utc + timedelta(hours=hours_until_optimal)).strftime('%H:%M UTC')
        }

# Global session manager instance
session_manager = EnhancedSessionManager()

def get_session_multipliers(symbol: str) -> Dict:
    """Helper function to get session multipliers"""
    return session_manager.get_symbol_session_multiplier(symbol)

def get_trading_recommendation(symbol: str) -> Dict:
    """Helper function to get trading recommendation"""
    return session_manager.get_session_recommendation(symbol)

def record_session_outcome(signal: Dict, outcome: str):
    """Helper function to record session performance"""
    session_manager.record_session_performance(signal, outcome)
