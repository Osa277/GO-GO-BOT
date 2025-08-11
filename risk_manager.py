#!/usr/bin/env python3
"""
Advanced Risk Management System
Dynamic position sizing, correlation analysis, and portfolio risk management
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class AdvancedRiskManager:
    def __init__(self):
        self.risk_file = "risk_data.json"
        self.max_portfolio_risk = 0.02  # 2% max portfolio risk
        self.max_single_trade_risk = 0.005  # 0.5% max single trade risk
        self.max_correlation_risk = 0.015  # 1.5% max correlated positions
        self.load_risk_data()
        
    def load_risk_data(self):
        """Load historical risk data"""
        try:
            if os.path.exists(self.risk_file):
                with open(self.risk_file, 'r') as f:
                    self.risk_data = json.load(f)
            else:
                self.risk_data = {
                    'position_history': [],
                    'correlation_matrix': {},
                    'risk_metrics': {}
                }
        except Exception as e:
            logger.error(f"Error loading risk data: {e}")
            self.risk_data = {'position_history': [], 'correlation_matrix': {}, 'risk_metrics': {}}
    
    def save_risk_data(self):
        """Save risk data to file"""
        try:
            with open(self.risk_file, 'w') as f:
                json.dump(self.risk_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving risk data: {e}")
    
    def calculate_dynamic_position_size(self, signal: Dict, account_balance: float, 
                                      current_positions: List[Dict]) -> float:
        """Calculate optimal position size based on risk management"""
        try:
            # Handle zero balance case - use minimum position sizes for signal-only mode
            if account_balance <= 0:
                symbol = signal['symbol']
                if symbol == 'BTCUSD':
                    return 0.01  # Minimum BTC position
                elif symbol == 'XAUUSD':
                    return 0.01  # Minimum Gold position
                else:
                    return 0.01  # Default minimum
            
            # Base position size on account balance and risk tolerance
            risk_amount = account_balance * self.max_single_trade_risk
            
            # Calculate signal risk in account currency
            entry_price = signal['entry']
            sl_price = signal['sl']
            risk_per_unit = abs(entry_price - sl_price)
            
            if risk_per_unit == 0:
                return 0.01  # Minimum position size
            
            # Basic position size
            base_position_size = risk_amount / risk_per_unit
            
            # Adjust for symbol characteristics
            symbol = signal['symbol']
            if symbol == 'BTCUSD':
                # For BTC, use smaller position sizes due to volatility
                base_position_size *= 0.5
                min_size, max_size = 0.01, 0.5
            elif symbol == 'XAUUSD':
                # For Gold, moderate position sizes
                base_position_size *= 0.7
                min_size, max_size = 0.01, 1.0
            else:
                min_size, max_size = 0.01, 2.0
            
            # Check portfolio correlation risk
            correlation_factor = self.calculate_correlation_risk(signal, current_positions)
            base_position_size *= correlation_factor
            
            # Check current portfolio risk
            portfolio_risk_factor = self.calculate_portfolio_risk_factor(current_positions, account_balance)
            base_position_size *= portfolio_risk_factor
            
            # Apply timeframe-based adjustments
            tf_factor = self.get_timeframe_risk_factor(signal['tf'])
            base_position_size *= tf_factor
            
            # Ensure within limits
            position_size = max(min_size, min(base_position_size, max_size))
            
            logger.info(f"💰 POSITION SIZE: {symbol} {signal['side']} = {position_size:.3f} lots "
                       f"(Risk: ${risk_amount:.2f}, Correlation: {correlation_factor:.2f}x)")
            
            return round(position_size, 3)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.01  # Default minimal size
    
    def calculate_correlation_risk(self, signal: Dict, current_positions: List[Dict]) -> float:
        """Calculate correlation risk factor"""
        if not current_positions:
            return 1.0
        
        symbol = signal['symbol']
        side = signal['side']
        
        # Define correlation groups
        crypto_symbols = ['BTCUSD', 'ETHUSD', 'LTCUSD']
        precious_metals = ['XAUUSD', 'XAGUSD']
        forex_majors = ['EURUSD', 'GBPUSD', 'USDJPY']
        
        correlation_penalty = 0.0
        
        for pos in current_positions:
            if pos.get('status') != 'open':
                continue
                
            pos_symbol = pos['symbol']
            pos_side = pos['side']
            
            # High correlation penalty for same symbol
            if pos_symbol == symbol:
                if pos_side == side:
                    correlation_penalty += 0.5  # 50% reduction for same direction
                else:
                    correlation_penalty += 0.3  # 30% reduction for opposite direction
            
            # Medium correlation penalty for same asset class
            elif (symbol in crypto_symbols and pos_symbol in crypto_symbols) or \
                 (symbol in precious_metals and pos_symbol in precious_metals) or \
                 (symbol in forex_majors and pos_symbol in forex_majors):
                if pos_side == side:
                    correlation_penalty += 0.2  # 20% reduction
                else:
                    correlation_penalty += 0.1  # 10% reduction
        
        # Return correlation factor (1.0 = no penalty, 0.0 = maximum penalty)
        return max(0.1, 1.0 - correlation_penalty)
    
    def calculate_portfolio_risk_factor(self, current_positions: List[Dict], 
                                      account_balance: float) -> float:
        """Calculate portfolio-wide risk factor"""
        if not current_positions or account_balance <= 0:
            return 1.0
        
        total_risk = 0.0
        
        for pos in current_positions:
            if pos.get('status') != 'open':
                continue
            
            # Calculate risk for this position
            entry = pos.get('entry', 0)
            sl = pos.get('sl', 0)
            position_size = pos.get('position_size', 0.01)
            
            if entry and sl:
                risk_per_unit = abs(entry - sl)
                position_risk = risk_per_unit * position_size
                total_risk += position_risk
        
        # Calculate current portfolio risk percentage
        portfolio_risk_pct = total_risk / account_balance if account_balance > 0 else 0
        
        # Reduce position size if approaching risk limit
        if portfolio_risk_pct >= self.max_portfolio_risk:
            return 0.1  # Severely reduce position size
        elif portfolio_risk_pct >= self.max_portfolio_risk * 0.8:
            return 0.5  # Moderately reduce position size
        elif portfolio_risk_pct >= self.max_portfolio_risk * 0.6:
            return 0.8  # Slightly reduce position size
        
        return 1.0  # No reduction needed
    
    def get_timeframe_risk_factor(self, timeframe: str) -> float:
        """Get risk factor based on timeframe"""
        tf_factors = {
            'M3': 0.6,   # Higher risk due to noise
            'M5': 0.7,   # Moderate risk
            'M15': 0.8,  # Lower risk
            'M30': 1.0,  # Standard risk
            'H1': 1.2,   # Lower risk, higher confidence
            'H4': 1.5,   # Much lower risk
            'D1': 2.0    # Lowest risk
        }
        
        return tf_factors.get(timeframe, 1.0)
    
    def validate_signal_risk(self, signal: Dict, account_balance: float, 
                           current_positions: List[Dict]) -> Tuple[bool, str]:
        """Validate if signal meets risk criteria"""
        try:
            # Check if we're at position limit
            open_positions = [p for p in current_positions if p.get('status') == 'open']
            if len(open_positions) >= 5:  # Max 5 open positions
                return False, "Maximum open positions reached"
            
            # Allow signals with zero balance in signal-only mode
            # Check environment variables for signal-only mode
            import os
            signal_only_mode = os.getenv('SIGNAL_ONLY_MODE', 'true').lower() == 'true'
            ignore_balance = os.getenv('IGNORE_ACCOUNT_BALANCE', 'true').lower() == 'true'
            
            if account_balance <= 0 and not (signal_only_mode or ignore_balance):
                return False, "Insufficient account balance (set SIGNAL_ONLY_MODE=true to override)"
            
            # Check if signal has valid risk parameters
            if not signal.get('entry') or not signal.get('sl'):
                return False, "Invalid entry or stop loss"
            
            # Check if risk-reward ratio is acceptable
            entry = signal['entry']
            sl = signal['sl']
            tp = signal['tp'][0] if isinstance(signal['tp'], list) else signal['tp']
            
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            
            if risk <= 0:
                return False, "Invalid risk calculation"
            
            rr_ratio = reward / risk
            if rr_ratio < 1.2:  # Minimum 1:1.2 RR ratio
                return False, f"Poor risk-reward ratio: 1:{rr_ratio:.2f}"
            
            # Check maximum drawdown
            portfolio_risk = self.calculate_portfolio_risk_factor(current_positions, account_balance)
            if portfolio_risk < 0.5:
                return False, "Portfolio risk limit exceeded"
            
            return True, "Risk validation passed"
            
        except Exception as e:
            logger.error(f"Error validating signal risk: {e}")
            return False, f"Risk validation error: {e}"
    
    def get_risk_report(self, current_positions: List[Dict], account_balance: float) -> str:
        """Generate comprehensive risk report"""
        try:
            open_positions = [p for p in current_positions if p.get('status') == 'open']
            
            # Calculate total portfolio risk
            total_risk = 0.0
            for pos in open_positions:
                entry = pos.get('entry', 0)
                sl = pos.get('sl', 0)
                size = pos.get('position_size', 0.01)
                if entry and sl:
                    risk = abs(entry - sl) * size
                    total_risk += risk
            
            risk_pct = (total_risk / account_balance * 100) if account_balance > 0 else 0
            
            # Analyze correlation
            symbols = [p['symbol'] for p in open_positions]
            unique_symbols = len(set(symbols))
            correlation_risk = "HIGH" if len(symbols) - unique_symbols > 2 else "MEDIUM" if len(symbols) - unique_symbols > 0 else "LOW"
            
            report = f"""
🛡️ RISK MANAGEMENT REPORT
========================
Portfolio Risk: {risk_pct:.2f}% (Limit: {self.max_portfolio_risk*100:.1f}%)
Open Positions: {len(open_positions)}/5
Unique Symbols: {unique_symbols}
Correlation Risk: {correlation_risk}

Risk Utilization: {"🔴 HIGH" if risk_pct > 1.5 else "🟡 MEDIUM" if risk_pct > 1.0 else "🟢 LOW"}
Available Risk: {max(0, self.max_portfolio_risk*100 - risk_pct):.2f}%
            """
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return "❌ Error generating risk report"

# Global risk manager instance
risk_manager = AdvancedRiskManager()

def calculate_optimal_position_size(signal: Dict, account_balance: float, 
                                  current_positions: List[Dict]) -> float:
    """Helper function for position size calculation"""
    return risk_manager.calculate_dynamic_position_size(signal, account_balance, current_positions)

def validate_trade_risk(signal: Dict, account_balance: float, 
                       current_positions: List[Dict]) -> Tuple[bool, str]:
    """Helper function for risk validation"""
    return risk_manager.validate_signal_risk(signal, account_balance, current_positions)

def get_portfolio_risk_report(current_positions: List[Dict], account_balance: float) -> str:
    """Helper function for risk reporting"""
    return risk_manager.get_risk_report(current_positions, account_balance)
