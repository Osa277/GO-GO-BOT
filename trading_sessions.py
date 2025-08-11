#!/usr/bin/env python3
"""
Trading Sessions Manager
Advanced session-based trading optimization with New York session focus.
"""

from datetime import datetime, timezone, timedelta
import logging
from config import TRADING_SESSIONS, ENABLE_SESSION_FILTERING, PREFERRED_SESSIONS, AVOID_LOW_VOLATILITY_HOURS

logger = logging.getLogger(__name__)

class TradingSessionManager:
    def __init__(self):
        self.sessions = TRADING_SESSIONS
        self.preferred_sessions = PREFERRED_SESSIONS
        self.avoid_hours = AVOID_LOW_VOLATILITY_HOURS
        self.enable_filtering = ENABLE_SESSION_FILTERING
        
        # Time zones (UTC offsets)
        self.utc_offset = 0
        self.ny_offset = -5  # EST (UTC-5) / -4 for EDT (UTC-4)
        self.london_offset = 0  # GMT (UTC+0) / +1 for BST (UTC+1)
        
    def get_current_utc_hour(self):
        """Get current UTC hour"""
        return datetime.now(timezone.utc).hour
    
    def get_ny_time_string(self):
        """Get current New York time as string"""
        utc_now = datetime.now(timezone.utc)
        # Simple EST calculation (adjust for EDT if needed)
        ny_time = utc_now + timedelta(hours=self.ny_offset)
        return ny_time.strftime("%H:%M EST")
    
    def is_ny_session_active(self):
        """Check if New York session is currently active"""
        current_hour = self.get_current_utc_hour()
        ny_session = self.sessions.get("NEW_YORK", {})
        
        if not ny_session.get("enabled", False):
            return False
        
        start_hour = ny_session.get("start", 13)
        end_hour = ny_session.get("end", 22)
        
        # Handle session that crosses midnight
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:
            return current_hour >= start_hour or current_hour <= end_hour
    
    def is_overlap_session_active(self):
        """Check if NY-London overlap session is active (highest volatility)"""
        current_hour = self.get_current_utc_hour()
        overlap_session = self.sessions.get("OVERLAP_NY_LONDON", {})
        
        if not overlap_session.get("enabled", False):
            return False
        
        start_hour = overlap_session.get("start", 13)
        end_hour = overlap_session.get("end", 17)
        
        return start_hour <= current_hour <= end_hour
    
    def get_active_sessions(self):
        """Get list of currently active sessions"""
        current_hour = self.get_current_utc_hour()
        active_sessions = []
        
        for session_name, session_config in self.sessions.items():
            if not session_config.get("enabled", False):
                continue
                
            start_hour = session_config.get("start", 0)
            end_hour = session_config.get("end", 23)
            
            # Check if current hour is within session
            if start_hour <= end_hour:
                if start_hour <= current_hour <= end_hour:
                    active_sessions.append({
                        "name": session_name,
                        "display_name": session_config.get("name", session_name),
                        "priority": session_config.get("priority", "medium"),
                        "start": start_hour,
                        "end": end_hour
                    })
            else:  # Session crosses midnight
                if current_hour >= start_hour or current_hour <= end_hour:
                    active_sessions.append({
                        "name": session_name,
                        "display_name": session_config.get("name", session_name),
                        "priority": session_config.get("priority", "medium"),
                        "start": start_hour,
                        "end": end_hour
                    })
        
        return active_sessions
    
    def get_session_priority_score(self):
        """Get priority score for current time (higher = better for trading)"""
        active_sessions = self.get_active_sessions()
        
        if not active_sessions:
            return 0
        
        # Priority mapping
        priority_scores = {
            "very_high": 10,
            "high": 7,
            "medium": 5,
            "low": 3,
            "very_low": 1
        }
        
        max_score = 0
        for session in active_sessions:
            score = priority_scores.get(session["priority"], 5)
            max_score = max(max_score, score)
        
        return max_score
    
    def should_trade_now(self, symbol=""):
        """Determine if trading should be allowed at current time"""
        if not self.enable_filtering:
            return True, "Session filtering disabled"
        
        current_hour = self.get_current_utc_hour()
        
        # Check if in avoid hours
        if current_hour in self.avoid_hours:
            return False, f"Current hour {current_hour} UTC is in low volatility period"
        
        # Check if any preferred session is active
        active_sessions = self.get_active_sessions()
        
        if not active_sessions:
            return False, "No trading sessions currently active"
        
        # Check if any active session is in preferred list
        for session in active_sessions:
            if session["name"] in self.preferred_sessions:
                return True, f"✅ {session['display_name']} active (Priority: {session['priority']})"
        
        # If no preferred session is active, check priority
        priority_score = self.get_session_priority_score()
        if priority_score >= 5:  # Medium priority or higher
            session_names = [s["display_name"] for s in active_sessions]
            return True, f"📊 Active sessions: {', '.join(session_names)} (Score: {priority_score})"
        
        return False, f"Current sessions have low priority (Score: {priority_score})"
    
    def get_next_ny_session(self):
        """Get time until next New York session starts"""
        current_hour = self.get_current_utc_hour()
        ny_start = self.sessions["NEW_YORK"]["start"]
        
        if current_hour < ny_start:
            hours_until = ny_start - current_hour
        else:
            hours_until = (24 - current_hour) + ny_start
        
        return hours_until
    
    def get_session_info(self):
        """Get comprehensive session information"""
        current_hour = self.get_current_utc_hour()
        active_sessions = self.get_active_sessions()
        ny_active = self.is_ny_session_active()
        overlap_active = self.is_overlap_session_active()
        
        info = {
            "current_utc_hour": current_hour,
            "ny_time": self.get_ny_time_string(),
            "ny_session_active": ny_active,
            "overlap_session_active": overlap_active,
            "active_sessions": active_sessions,
            "priority_score": self.get_session_priority_score(),
            "should_trade": self.should_trade_now()[0],
            "trade_reason": self.should_trade_now()[1],
            "hours_until_ny": self.get_next_ny_session() if not ny_active else 0
        }
        
        return info
    
    def get_session_analysis_for_ai(self, symbol):
        """Get session analysis data for AI optimization"""
        session_info = self.get_session_info()
        
        # Calculate session-based multipliers
        multipliers = {
            "probability_multiplier": 1.0,
            "confidence_boost": 0.0,
            "risk_adjustment": 0.0
        }
        
        # NY session gets priority
        if session_info["ny_session_active"]:
            multipliers["probability_multiplier"] = 1.15  # 15% boost
            multipliers["confidence_boost"] = 0.1
            
        # Overlap session gets highest priority
        if session_info["overlap_session_active"]:
            multipliers["probability_multiplier"] = 1.25  # 25% boost
            multipliers["confidence_boost"] = 0.15
            multipliers["risk_adjustment"] = 0.05  # Can take slightly more risk
        
        # Low priority hours
        if session_info["priority_score"] < 5:
            multipliers["probability_multiplier"] = 0.85  # 15% reduction
            multipliers["confidence_boost"] = -0.1
        
        return {
            "session_info": session_info,
            "multipliers": multipliers,
            "recommendations": self._get_session_recommendations(session_info)
        }
    
    def _get_session_recommendations(self, session_info):
        """Generate session-based trading recommendations"""
        recommendations = []
        
        if session_info["overlap_session_active"]:
            recommendations.append("🔥 NY-London Overlap - Highest volatility period active!")
            
        elif session_info["ny_session_active"]:
            recommendations.append("🇺🇸 New York Session - High volatility expected")
            
        elif session_info["priority_score"] < 5:
            recommendations.append("⚠️ Low volatility period - Consider reducing position sizes")
            
        if session_info["hours_until_ny"] > 0 and session_info["hours_until_ny"] <= 2:
            recommendations.append(f"⏰ NY session starts in {session_info['hours_until_ny']} hours")
        
        return recommendations

# Global session manager instance
session_manager = TradingSessionManager()

def is_ny_session_active():
    """Quick check if NY session is active"""
    return session_manager.is_ny_session_active()

def should_trade_now(symbol=""):
    """Quick check if trading should be allowed"""
    return session_manager.should_trade_now(symbol)

def get_session_info():
    """Get current session information"""
    return session_manager.get_session_info()

def get_session_multipliers(symbol):
    """Get session-based multipliers for AI"""
    return session_manager.get_session_analysis_for_ai(symbol)

if __name__ == "__main__":
    # Test the session manager
    sm = TradingSessionManager()
    info = sm.get_session_info()
    print(f"Session Info: {info}")
    
    should_trade, reason = sm.should_trade_now()
    print(f"Should Trade: {should_trade} - {reason}")
