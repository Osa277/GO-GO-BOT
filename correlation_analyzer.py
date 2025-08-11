#!/usr/bin/env python3
"""
Market Correlation Analyzer
Analyzes correlations between symbols to optimize signal generation and risk management
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from mt5_data import fetch_market_data

logger = logging.getLogger(__name__)

class MarketCorrelationAnalyzer:
    def __init__(self):
        self.correlation_file = "correlation_data.json"
        self.symbols = ['BTCUSD', 'XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30']
        self.timeframes = [3, 5, 15]  # Minutes
        self.correlation_threshold = 0.7  # High correlation threshold
        self.load_correlation_data()
        
    def load_correlation_data(self):
        """Load historical correlation data"""
        try:
            if os.path.exists(self.correlation_file):
                with open(self.correlation_file, 'r') as f:
                    self.correlation_data = json.load(f)
            else:
                self.correlation_data = {
                    'correlation_matrix': {},
                    'last_updated': None,
                    'historical_correlations': []
                }
        except Exception as e:
            logger.error(f"Error loading correlation data: {e}")
            self.correlation_data = {'correlation_matrix': {}, 'last_updated': None, 'historical_correlations': []}
    
    def save_correlation_data(self):
        """Save correlation data to file"""
        try:
            self.correlation_data['last_updated'] = datetime.now().isoformat()
            with open(self.correlation_file, 'w') as f:
                json.dump(self.correlation_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving correlation data: {e}")
    
    def calculate_symbol_correlation(self, symbol1: str, symbol2: str, 
                                   timeframe: int = 30, periods: int = 100) -> Optional[float]:
        """Calculate correlation between two symbols"""
        try:
            # Fetch data for both symbols
            df1 = fetch_market_data(symbol1, timeframe, periods)
            df2 = fetch_market_data(symbol2, timeframe, periods)
            
            if df1 is None or df2 is None or len(df1) < 20 or len(df2) < 20:
                return None
            
            # Align the data by timestamp (ensure same length)
            min_length = min(len(df1), len(df2))
            prices1 = df1['close'].tail(min_length).values
            prices2 = df2['close'].tail(min_length).values
            
            # Calculate price changes (returns)
            returns1 = np.diff(prices1) / prices1[:-1]
            returns2 = np.diff(prices2) / prices2[:-1]
            
            # Calculate correlation
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            
            return correlation if not np.isnan(correlation) else None
            
        except Exception as e:
            logger.error(f"Error calculating correlation between {symbol1} and {symbol2}: {e}")
            return None
    
    def update_correlation_matrix(self) -> Dict:
        """Update correlation matrix for all symbol pairs"""
        try:
            correlation_matrix = {}
            
            for i, symbol1 in enumerate(self.symbols):
                correlation_matrix[symbol1] = {}
                
                for j, symbol2 in enumerate(self.symbols):
                    if i == j:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    elif symbol2 in correlation_matrix and symbol1 in correlation_matrix[symbol2]:
                        # Use already calculated correlation (symmetric)
                        correlation_matrix[symbol1][symbol2] = correlation_matrix[symbol2][symbol1]
                    else:
                        # Calculate new correlation
                        corr = self.calculate_symbol_correlation(symbol1, symbol2)
                        correlation_matrix[symbol1][symbol2] = corr
            
            # Store the matrix
            self.correlation_data['correlation_matrix'] = correlation_matrix
            
            # Store historical correlation for trending analysis
            historical_entry = {
                'timestamp': datetime.now().isoformat(),
                'matrix': correlation_matrix
            }
            
            if 'historical_correlations' not in self.correlation_data:
                self.correlation_data['historical_correlations'] = []
            
            self.correlation_data['historical_correlations'].append(historical_entry)
            
            # Keep only last 100 entries
            if len(self.correlation_data['historical_correlations']) > 100:
                self.correlation_data['historical_correlations'] = self.correlation_data['historical_correlations'][-100:]
            
            self.save_correlation_data()
            
            logger.info("📊 Correlation matrix updated successfully")
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Error updating correlation matrix: {e}")
            return {}
    
    def get_correlated_symbols(self, target_symbol: str, 
                             correlation_threshold: float = None) -> List[Dict]:
        """Get symbols highly correlated with target symbol"""
        if correlation_threshold is None:
            correlation_threshold = self.correlation_threshold
        
        correlation_matrix = self.correlation_data.get('correlation_matrix', {})
        
        if target_symbol not in correlation_matrix:
            return []
        
        correlated_symbols = []
        
        for symbol, correlation in correlation_matrix[target_symbol].items():
            if symbol != target_symbol and correlation is not None:
                abs_correlation = abs(correlation)
                
                if abs_correlation >= correlation_threshold:
                    correlated_symbols.append({
                        'symbol': symbol,
                        'correlation': correlation,
                        'abs_correlation': abs_correlation,
                        'relationship': 'positive' if correlation > 0 else 'negative'
                    })
        
        # Sort by absolute correlation (highest first)
        correlated_symbols.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        return correlated_symbols
    
    def assess_portfolio_correlation_risk(self, current_positions: List[Dict]) -> Dict:
        """Assess correlation risk in current portfolio"""
        try:
            if len(current_positions) < 2:
                return {'risk_level': 'LOW', 'risk_score': 0.0, 'details': 'Insufficient positions for correlation analysis'}
            
            correlation_matrix = self.correlation_data.get('correlation_matrix', {})
            
            if not correlation_matrix:
                return {'risk_level': 'UNKNOWN', 'risk_score': 0.5, 'details': 'Correlation data not available'}
            
            # Extract position symbols and directions
            position_data = []
            for pos in current_positions:
                if pos.get('status') == 'open':
                    position_data.append({
                        'symbol': pos['symbol'],
                        'side': pos['side'],
                        'size': pos.get('position_size', 0.01)
                    })
            
            if len(position_data) < 2:
                return {'risk_level': 'LOW', 'risk_score': 0.0, 'details': 'Insufficient open positions'}
            
            # Calculate correlation risk
            total_risk_score = 0.0
            risk_pairs = []
            
            for i, pos1 in enumerate(position_data):
                for j, pos2 in enumerate(position_data[i+1:], i+1):
                    symbol1, symbol2 = pos1['symbol'], pos2['symbol']
                    
                    if symbol1 in correlation_matrix and symbol2 in correlation_matrix[symbol1]:
                        correlation = correlation_matrix[symbol1][symbol2]
                        
                        if correlation is not None:
                            # Calculate risk based on correlation and position directions
                            if pos1['side'] == pos2['side']:  # Same direction
                                risk_contribution = abs(correlation) * min(pos1['size'], pos2['size'])
                            else:  # Opposite directions
                                risk_contribution = abs(correlation) * 0.5 * min(pos1['size'], pos2['size'])
                            
                            total_risk_score += risk_contribution
                            
                            if abs(correlation) > self.correlation_threshold:
                                risk_pairs.append({
                                    'pair': f"{symbol1}-{symbol2}",
                                    'correlation': correlation,
                                    'same_direction': pos1['side'] == pos2['side'],
                                    'risk_contribution': risk_contribution
                                })
            
            # Normalize risk score
            normalized_risk = min(1.0, total_risk_score / len(position_data))
            
            # Determine risk level
            if normalized_risk >= 0.8:
                risk_level = 'CRITICAL'
            elif normalized_risk >= 0.6:
                risk_level = 'HIGH'
            elif normalized_risk >= 0.4:
                risk_level = 'MEDIUM'
            elif normalized_risk >= 0.2:
                risk_level = 'LOW'
            else:
                risk_level = 'MINIMAL'
            
            return {
                'risk_level': risk_level,
                'risk_score': normalized_risk,
                'risky_pairs': risk_pairs,
                'total_positions': len(position_data),
                'details': f"Portfolio correlation risk: {risk_level} ({normalized_risk:.2f})"
            }
            
        except Exception as e:
            logger.error(f"Error assessing portfolio correlation risk: {e}")
            return {'risk_level': 'ERROR', 'risk_score': 0.5, 'details': f"Error: {e}"}
    
    def get_signal_correlation_advice(self, signal: Dict, current_positions: List[Dict]) -> Dict:
        """Get advice about taking a signal based on correlation with current positions"""
        try:
            signal_symbol = signal['symbol']
            signal_side = signal['side']
            
            if not current_positions:
                return {
                    'advice': 'TAKE',
                    'reason': 'No current positions to correlate with',
                    'correlation_risk': 'NONE',
                    'adjustments': {}
                }
            
            correlation_matrix = self.correlation_data.get('correlation_matrix', {})
            
            if signal_symbol not in correlation_matrix:
                return {
                    'advice': 'TAKE',
                    'reason': 'Correlation data not available for this symbol',
                    'correlation_risk': 'UNKNOWN',
                    'adjustments': {}
                }
            
            # Analyze correlation with existing positions
            correlation_conflicts = []
            position_size_adjustment = 1.0
            
            for pos in current_positions:
                if pos.get('status') != 'open':
                    continue
                
                pos_symbol = pos['symbol']
                pos_side = pos['side']
                
                if pos_symbol in correlation_matrix[signal_symbol]:
                    correlation = correlation_matrix[signal_symbol][pos_symbol]
                    
                    if correlation is not None and abs(correlation) > self.correlation_threshold:
                        # High correlation detected
                        if signal_side == pos_side and correlation > 0:
                            # Same direction, positive correlation - high risk
                            correlation_conflicts.append({
                                'symbol': pos_symbol,
                                'correlation': correlation,
                                'conflict_type': 'SAME_DIRECTION_POSITIVE',
                                'risk_level': 'HIGH'
                            })
                            position_size_adjustment *= 0.6  # Reduce position size
                            
                        elif signal_side != pos_side and correlation > 0:
                            # Opposite direction, positive correlation - medium risk
                            correlation_conflicts.append({
                                'symbol': pos_symbol,
                                'correlation': correlation,
                                'conflict_type': 'OPPOSITE_DIRECTION_POSITIVE',
                                'risk_level': 'MEDIUM'
                            })
                            position_size_adjustment *= 0.8
                            
                        elif signal_side == pos_side and correlation < 0:
                            # Same direction, negative correlation - low risk (diversification)
                            correlation_conflicts.append({
                                'symbol': pos_symbol,
                                'correlation': correlation,
                                'conflict_type': 'SAME_DIRECTION_NEGATIVE',
                                'risk_level': 'LOW'
                            })
                            # No position size adjustment needed
                            
                        elif signal_side != pos_side and correlation < 0:
                            # Opposite direction, negative correlation - beneficial
                            correlation_conflicts.append({
                                'symbol': pos_symbol,
                                'correlation': correlation,
                                'conflict_type': 'OPPOSITE_DIRECTION_NEGATIVE',
                                'risk_level': 'BENEFICIAL'
                            })
                            position_size_adjustment *= 1.1  # Slightly increase position size
            
            # Determine overall advice
            high_risk_conflicts = [c for c in correlation_conflicts if c['risk_level'] == 'HIGH']
            
            if len(high_risk_conflicts) >= 2:
                advice = 'AVOID'
                reason = f"Multiple high correlation conflicts with {len(high_risk_conflicts)} positions"
                correlation_risk = 'CRITICAL'
            elif len(high_risk_conflicts) == 1:
                advice = 'TAKE_REDUCED'
                reason = f"High correlation with {high_risk_conflicts[0]['symbol']} ({high_risk_conflicts[0]['correlation']:.2f})"
                correlation_risk = 'HIGH'
            elif len(correlation_conflicts) >= 3:
                advice = 'TAKE_REDUCED'
                reason = f"Multiple moderate correlations detected"
                correlation_risk = 'MEDIUM'
            else:
                advice = 'TAKE'
                reason = "Acceptable correlation risk"
                correlation_risk = 'LOW'
            
            return {
                'advice': advice,
                'reason': reason,
                'correlation_risk': correlation_risk,
                'conflicts': correlation_conflicts,
                'adjustments': {
                    'position_size_multiplier': max(0.2, min(1.5, position_size_adjustment)),
                    'confidence_adjustment': -0.05 * len(high_risk_conflicts)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting signal correlation advice: {e}")
            return {
                'advice': 'TAKE',
                'reason': f'Error analyzing correlation: {e}',
                'correlation_risk': 'ERROR',
                'adjustments': {}
            }
    
    def get_correlation_report(self) -> str:
        """Generate comprehensive correlation report"""
        try:
            correlation_matrix = self.correlation_data.get('correlation_matrix', {})
            
            if not correlation_matrix:
                return "❌ No correlation data available. Run update_correlation_matrix() first."
            
            report = "📊 MARKET CORRELATION ANALYSIS\n"
            report += "=" * 35 + "\n\n"
            
            # High correlation pairs
            high_corr_pairs = []
            for symbol1 in correlation_matrix:
                for symbol2, correlation in correlation_matrix[symbol1].items():
                    if symbol1 != symbol2 and correlation is not None and abs(correlation) > self.correlation_threshold:
                        pair_key = tuple(sorted([symbol1, symbol2]))
                        if pair_key not in [tuple(sorted([p['symbol1'], p['symbol2']])) for p in high_corr_pairs]:
                            high_corr_pairs.append({
                                'symbol1': symbol1,
                                'symbol2': symbol2,
                                'correlation': correlation,
                                'type': 'Positive' if correlation > 0 else 'Negative'
                            })
            
            if high_corr_pairs:
                report += "🔗 HIGH CORRELATION PAIRS:\n"
                for pair in sorted(high_corr_pairs, key=lambda x: abs(x['correlation']), reverse=True):
                    report += f"   {pair['symbol1']} ↔ {pair['symbol2']}: {pair['correlation']:.3f} ({pair['type']})\n"
            else:
                report += "✅ No high correlation pairs detected\n"
            
            report += "\n📈 DIVERSIFICATION OPPORTUNITIES:\n"
            
            # Find low correlation pairs for diversification
            for symbol in ['BTCUSD', 'XAUUSD']:
                if symbol in correlation_matrix:
                    low_corr_symbols = []
                    for other_symbol, correlation in correlation_matrix[symbol].items():
                        if other_symbol != symbol and correlation is not None and abs(correlation) < 0.3:
                            low_corr_symbols.append(f"{other_symbol} ({correlation:.2f})")
                    
                    if low_corr_symbols:
                        report += f"   {symbol}: {', '.join(low_corr_symbols[:3])}\n"
            
            last_updated = self.correlation_data.get('last_updated')
            if last_updated:
                report += f"\n🕒 Last Updated: {last_updated[:19].replace('T', ' ')}"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating correlation report: {e}")
            return f"❌ Error generating correlation report: {e}"

# Global correlation analyzer instance
correlation_analyzer = MarketCorrelationAnalyzer()

def update_market_correlations():
    """Helper function to update market correlations"""
    return correlation_analyzer.update_correlation_matrix()

def get_correlation_advice(signal: Dict, current_positions: List[Dict]) -> Dict:
    """Helper function to get correlation advice for a signal"""
    return correlation_analyzer.get_signal_correlation_advice(signal, current_positions)

def assess_portfolio_correlation(current_positions: List[Dict]) -> Dict:
    """Helper function to assess portfolio correlation risk"""
    return correlation_analyzer.assess_portfolio_correlation_risk(current_positions)
