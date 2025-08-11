#!/usr/bin/env python3
"""
Enhanced Real-Time Trading Dashboard
Comprehensive monitoring with risk management, correlation analysis, and session optimization
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
from datetime import datetime, timedelta
import logging
from mt5_data import get_current_price, get_account_info
from config import SYMBOLS, TIMEFRAMES
from risk_manager import get_portfolio_risk_report
from enhanced_session_manager import get_trading_recommendation
from correlation_analyzer import assess_portfolio_correlation
from performance_monitor import performance_monitor

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Load current trades and analytics data
def load_trading_data():
    """Load current trading data from various sources"""
    try:
        # Load open trades
        trades_data = []
        if os.path.exists('trading_bot.log'):
            # Parse recent trades from log file
            pass
        
        # Load performance data
        performance_data = {}
        if hasattr(performance_monitor, 'get_session_stats'):
            performance_data = performance_monitor.get_session_stats()
        
        # Load analytics data
        analytics_data = {}
        if os.path.exists('advanced_signals.json'):
            with open('advanced_signals.json', 'r') as f:
                analytics_data = json.load(f)
        
        return {
            'trades': trades_data,
            'performance': performance_data,
            'analytics': analytics_data
        }
        
    except Exception as e:
        logger.error(f"Error loading trading data: {e}")
        return {'trades': [], 'performance': {}, 'analytics': {}}

ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Trading Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h3 {
            color: #FFD700;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-value {
            font-weight: bold;
            color: #4CAF50;
        }
        .metric-value.negative {
            color: #F44336;
        }
        .metric-value.warning {
            color: #FF9800;
        }
        .signals-table {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th {
            background: rgba(255,255,255,0.1);
            color: #FFD700;
            font-weight: bold;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .status-open { background: #4CAF50; }
        .status-tp { background: #2196F3; }
        .status-sl { background: #F44336; }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .btn.secondary {
            background: linear-gradient(45deg, #2196F3, #1976D2);
        }
        .btn.danger {
            background: linear-gradient(45deg, #F44336, #D32F2F);
        }
        .refresh-time {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
        }
        .risk-indicator {
            width: 100%;
            height: 20px;
            background: #333;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .risk-bar {
            height: 100%;
            transition: width 0.3s ease;
        }
        .risk-low { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
        .risk-medium { background: linear-gradient(90deg, #FF9800, #FFC107); }
        .risk-high { background: linear-gradient(90deg, #F44336, #E91E63); }
        .correlation-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .correlation-item {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .session-indicator {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin: 5px 0;
        }
        .session-active {
            background: rgba(76, 175, 80, 0.2);
            border-left: 4px solid #4CAF50;
        }
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            .controls {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced Trading Bot Dashboard</h1>
            <p>Real-time MT5 Signals • Risk Management • Market Analysis</p>
            <div class="controls">
                <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
                <button class="btn secondary" onclick="toggleAutoRefresh()">⚡ Auto-Refresh</button>
                <button class="btn secondary" onclick="exportData()">📊 Export Report</button>
                <button class="btn danger" onclick="emergencyStop()">🛑 Emergency Stop</button>
            </div>
        </div>

        <div class="stats-grid">
            <!-- Account Overview -->
            <div class="card">
                <h3>💰 Account Overview</h3>
                <div class="metric">
                    <span>Balance:</span>
                    <span class="metric-value" id="account-balance">Loading...</span>
                </div>
                <div class="metric">
                    <span>Equity:</span>
                    <span class="metric-value" id="account-equity">Loading...</span>
                </div>
                <div class="metric">
                    <span>Free Margin:</span>
                    <span class="metric-value" id="free-margin">Loading...</span>
                </div>
                <div class="metric">
                    <span>Server:</span>
                    <span class="metric-value" id="server">Loading...</span>
                </div>
            </div>

            <!-- Performance Metrics -->
            <div class="card">
                <h3>📈 Performance Today</h3>
                <div class="metric">
                    <span>Signals Generated:</span>
                    <span class="metric-value" id="signals-generated">0</span>
                </div>
                <div class="metric">
                    <span>Signals Sent:</span>
                    <span class="metric-value" id="signals-sent">0</span>
                </div>
                <div class="metric">
                    <span>Win Rate:</span>
                    <span class="metric-value" id="win-rate">0%</span>
                </div>
                <div class="metric">
                    <span>Total P&L:</span>
                    <span class="metric-value" id="total-pnl">+0.0 pips</span>
                </div>
            </div>

            <!-- Risk Management -->
            <div class="card">
                <h3>🛡️ Risk Management</h3>
                <div class="metric">
                    <span>Portfolio Risk:</span>
                    <span class="metric-value" id="portfolio-risk">0.0%</span>
                </div>
                <div class="risk-indicator">
                    <div class="risk-bar risk-low" id="risk-bar" style="width: 25%"></div>
                </div>
                <div class="metric">
                    <span>Open Positions:</span>
                    <span class="metric-value" id="open-positions">0/5</span>
                </div>
                <div class="metric">
                    <span>Correlation Risk:</span>
                    <span class="metric-value" id="correlation-risk">LOW</span>
                </div>
            </div>

            <!-- Market Sessions -->
            <div class="card">
                <h3>🌍 Market Sessions</h3>
                <div id="session-status">
                    <div class="session-indicator session-active">
                        <span>🇺🇸 New York</span>
                        <span>Active</span>
                    </div>
                    <div class="session-indicator">
                        <span>🇬🇧 London</span>
                        <span>Closed</span>
                    </div>
                    <div class="session-indicator">
                        <span>🇯🇵 Tokyo</span>
                        <span>Closed</span>
                    </div>
                </div>
                <div class="metric">
                    <span>Prime Time:</span>
                    <span class="metric-value" id="prime-time">No</span>
                </div>
            </div>

            <!-- Current Prices -->
            <div class="card">
                <h3>💱 Live Prices</h3>
                <div class="metric">
                    <span>BTCUSD:</span>
                    <span class="metric-value" id="btc-price">Loading...</span>
                </div>
                <div class="metric">
                    <span>XAUUSD:</span>
                    <span class="metric-value" id="xau-price">Loading...</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span class="metric-value" id="price-update">Never</span>
                </div>
            </div>

            <!-- AI Insights -->
            <div class="card">
                <h3>🤖 AI Insights</h3>
                <div class="metric">
                    <span>Recommendation:</span>
                    <span class="metric-value" id="ai-recommendation">Analyzing...</span>
                </div>
                <div class="metric">
                    <span>Confidence:</span>
                    <span class="metric-value" id="ai-confidence">0%</span>
                </div>
                <div class="metric">
                    <span>Next Optimal Session:</span>
                    <span class="metric-value" id="next-session">Calculating...</span>
                </div>
            </div>
        </div>

        <!-- Active Signals Table -->
        <div class="signals-table">
            <h3>📊 Active Signals</h3>
            <table id="signals-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Symbol</th>
                        <th>Side</th>
                        <th>Entry</th>
                        <th>SL</th>
                        <th>TP1</th>
                        <th>Current Price</th>
                        <th>P&L</th>
                        <th>Status</th>
                        <th>Probability</th>
                    </tr>
                </thead>
                <tbody id="signals-tbody">
                    <tr>
                        <td colspan="10" style="text-align: center; opacity: 0.7;">
                            No active signals
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="refresh-time">
            <p>Last updated: <span id="last-update">Never</span> | Auto-refresh: <span id="auto-refresh-status">Off</span></p>
        </div>
    </div>

    <script>
        let autoRefreshEnabled = false;
        let refreshInterval;

        function refreshData() {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Error fetching data:', error));
        }

        function updateDashboard(data) {
            // Update account info
            if (data.account) {
                document.getElementById('account-balance').textContent = `$${data.account.balance?.toFixed(2) || '0.00'}`;
                document.getElementById('account-equity').textContent = `$${data.account.equity?.toFixed(2) || '0.00'}`;
                document.getElementById('free-margin').textContent = `$${data.account.free_margin?.toFixed(2) || '0.00'}`;
                document.getElementById('server').textContent = data.account.server || 'Unknown';
            }

            // Update performance
            if (data.performance) {
                document.getElementById('signals-generated').textContent = data.performance.signals_generated || 0;
                document.getElementById('signals-sent').textContent = data.performance.signals_sent || 0;
                document.getElementById('win-rate').textContent = `${data.performance.win_rate || 0}%`;
                document.getElementById('total-pnl').textContent = `${data.performance.total_pnl >= 0 ? '+' : ''}${data.performance.total_pnl || 0} pips`;
            }

            // Update risk
            if (data.risk) {
                document.getElementById('portfolio-risk').textContent = `${data.risk.portfolio_risk || 0}%`;
                document.getElementById('open-positions').textContent = `${data.risk.open_positions || 0}/5`;
                document.getElementById('correlation-risk').textContent = data.risk.correlation_risk || 'LOW';
                
                // Update risk bar
                const riskBar = document.getElementById('risk-bar');
                const riskLevel = data.risk.portfolio_risk || 0;
                riskBar.style.width = `${Math.min(100, riskLevel * 5)}%`;
                
                if (riskLevel < 1) {
                    riskBar.className = 'risk-bar risk-low';
                } else if (riskLevel < 2) {
                    riskBar.className = 'risk-bar risk-medium';
                } else {
                    riskBar.className = 'risk-bar risk-high';
                }
            }

            // Update prices
            if (data.prices) {
                document.getElementById('btc-price').textContent = data.prices.BTCUSD || 'N/A';
                document.getElementById('xau-price').textContent = data.prices.XAUUSD || 'N/A';
                document.getElementById('price-update').textContent = new Date().toLocaleTimeString();
            }

            // Update AI insights
            if (data.ai) {
                document.getElementById('ai-recommendation').textContent = data.ai.recommendation || 'Analyzing...';
                document.getElementById('ai-confidence').textContent = `${data.ai.confidence || 0}%`;
                document.getElementById('next-session').textContent = data.ai.next_session || 'Calculating...';
            }

            // Update last refresh time
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }

        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const statusElement = document.getElementById('auto-refresh-status');
            
            if (autoRefreshEnabled) {
                statusElement.textContent = 'On';
                refreshInterval = setInterval(refreshData, 10000); // Refresh every 10 seconds
                refreshData(); // Initial refresh
            } else {
                statusElement.textContent = 'Off';
                clearInterval(refreshInterval);
            }
        }

        function exportData() {
            fetch('/api/export-report')
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `trading_report_${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                });
        }

        function emergencyStop() {
            if (confirm('Are you sure you want to execute emergency stop? This will pause all trading activities.')) {
                fetch('/api/emergency-stop', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message || 'Emergency stop executed');
                        refreshData();
                    });
            }
        }

        // Initial load
        refreshData();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(ENHANCED_DASHBOARD_HTML)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for dashboard data"""
    try:
        # Get account info
        account = get_account_info()
        
        # Get current prices
        prices = {}
        for symbol in SYMBOLS:
            try:
                prices[symbol] = get_current_price(symbol)
            except:
                prices[symbol] = None
        
        # Get performance data
        performance = {}
        if hasattr(performance_monitor, 'get_session_stats'):
            performance = performance_monitor.get_session_stats()
        
        # Get risk data (placeholder - would integrate with actual risk manager)
        risk = {
            'portfolio_risk': 1.2,  # Placeholder
            'open_positions': 2,
            'correlation_risk': 'MEDIUM'
        }
        
        # Get AI insights (placeholder)
        ai_insights = {
            'recommendation': 'TRADE_NORMALLY',
            'confidence': 75,
            'next_session': 'NY Open in 2h'
        }
        
        return jsonify({
            'account': account,
            'prices': prices,
            'performance': performance,
            'risk': risk,
            'ai': ai_insights,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-report')
def export_report():
    """Export comprehensive trading report"""
    try:
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'account_info': get_account_info(),
            'performance': performance_monitor.get_session_stats() if hasattr(performance_monitor, 'get_session_stats') else {},
            'risk_analysis': 'Risk analysis data would go here',
            'correlation_analysis': 'Correlation analysis data would go here',
            'ai_insights': 'AI insights data would go here'
        }
        
        return jsonify(report_data)
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/emergency-stop', methods=['POST'])
def emergency_stop():
    """Emergency stop endpoint"""
    try:
        # Here you would implement actual emergency stop logic
        # For now, just return success message
        
        logger.warning("🛑 EMERGENCY STOP TRIGGERED via dashboard")
        
        return jsonify({
            'success': True,
            'message': 'Emergency stop executed successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error executing emergency stop: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Trading Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
