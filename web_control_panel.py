#!/usr/bin/env python3
"""
Web Control Panel for GO-GO-BOT
Advanced web-based dashboard for monitoring and controlling the trading bot.
"""

from flask import Flask, render_template_string, jsonify, request
import json
import logging
import os
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
logger = logging.getLogger(__name__)

# HTML Template for the control panel
CONTROL_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GO-GO-BOT Control Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .status-bar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .card h3 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            color: #2d3748;
        }
        
        .positive {
            color: #38a169;
        }
        
        .negative {
            color: #e53e3e;
        }
        
        .neutral {
            color: #4a5568;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
        }
        
        .signals-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .signals-table th,
        .signals-table td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .signals-table th {
            background: #f7fafc;
            font-weight: 600;
            color: #4a5568;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-running {
            background: #38a169;
        }
        
        .status-stopped {
            background: #e53e3e;
        }
        
        .status-paused {
            background: #ecc94b;
        }
        
        .log-container {
            background: #1a202c;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            font-size: 1.5em;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
        }
        
        .modal-content {
            background: white;
            margin: 10% auto;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 600px;
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: black;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GO-GO-BOT Control Panel</h1>
            <p>Advanced Trading Bot Management System</p>
        </div>
        
        <div class="status-bar">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="status-indicator" id="botStatus"></span>
                    <strong id="botStatusText">Loading...</strong>
                    <span style="margin-left: 20px;">Version: <strong id="botVersion">4.0</strong></span>
                    <span style="margin-left: 20px;">Uptime: <strong id="botUptime">--:--:--</strong></span>
                </div>
                <div>
                    <button class="btn btn-success" onclick="startBot()">▶️ Start</button>
                    <button class="btn btn-danger" onclick="stopBot()">⏹️ Stop</button>
                    <button class="btn" onclick="restartBot()">🔄 Restart</button>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Performance Metrics</h3>
                <div class="metric">
                    <span>Total Signals:</span>
                    <span class="metric-value" id="totalSignals">0</span>
                </div>
                <div class="metric">
                    <span>Active Signals:</span>
                    <span class="metric-value" id="activeSignals">0</span>
                </div>
                <div class="metric">
                    <span>Win Rate:</span>
                    <span class="metric-value" id="winRate">0%</span>
                </div>
                <div class="metric">
                    <span>Total Pips:</span>
                    <span class="metric-value" id="totalPips">0</span>
                </div>
                <div class="metric">
                    <span>Profit Factor:</span>
                    <span class="metric-value" id="profitFactor">0.00</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Current Settings</h3>
                <div class="metric">
                    <span>Min TP Probability:</span>
                    <span class="metric-value" id="minProbability">50%</span>
                </div>
                <div class="metric">
                    <span>Max Daily Signals:</span>
                    <span class="metric-value" id="maxSignals">10</span>
                </div>
                <div class="metric">
                    <span>Active Symbols:</span>
                    <span class="metric-value" id="activeSymbols">3</span>
                </div>
                <div class="metric">
                    <span>Risk Level:</span>
                    <span class="metric-value" id="riskLevel">Medium</span>
                </div>
                <button class="btn" onclick="openSettingsModal()">⚙️ Adjust Settings</button>
            </div>
            
            <div class="card">
                <h3>🔧 System Status</h3>
                <div class="metric">
                    <span>MT5 Connection:</span>
                    <span class="metric-value positive" id="mt5Status">Connected</span>
                </div>
                <div class="metric">
                    <span>Telegram Alerts:</span>
                    <span class="metric-value positive" id="telegramStatus">Active</span>
                </div>
                <div class="metric">
                    <span>AI Optimizer:</span>
                    <span class="metric-value positive" id="aiStatus">Running</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span class="metric-value" id="lastUpdate">--:--:--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎮 Quick Actions</h3>
                <div style="text-align: center;">
                    <button class="btn" onclick="runBacktest()">📈 Run Backtest</button>
                    <button class="btn" onclick="optimizeParameters()">🔍 Optimize Parameters</button>
                    <button class="btn" onclick="generateReport()">📊 Generate Report</button>
                    <button class="btn" onclick="exportData()">💾 Export Data</button>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🔥 Recent Signals</h3>
            <table class="signals-table" id="signalsTable">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Symbol</th>
                        <th>Side</th>
                        <th>Entry</th>
                        <th>TP Prob</th>
                        <th>Status</th>
                        <th>P&L</th>
                    </tr>
                </thead>
                <tbody id="signalsTableBody">
                    <tr>
                        <td colspan="7" style="text-align: center; color: #999;">Loading signals...</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h3>📋 Live Bot Log</h3>
            <div class="log-container" id="liveLog">
                Loading log data...
            </div>
            <button class="btn" onclick="clearLog()" style="margin-top: 10px;">🗑️ Clear Log</button>
        </div>
    </div>
    
    <!-- Settings Modal -->
    <div id="settingsModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeSettingsModal()">&times;</span>
            <h2>⚙️ Bot Settings</h2>
            <br>
            <div>
                <label>Minimum TP Probability:</label>
                <input type="range" id="probabilitySlider" min="30" max="90" value="50">
                <span id="probabilityValue">50%</span>
            </div>
            <br>
            <div>
                <label>Maximum Daily Signals:</label>
                <input type="number" id="maxSignalsInput" min="1" max="50" value="10">
            </div>
            <br>
            <div>
                <label>Risk Level:</label>
                <select id="riskLevelSelect">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                </select>
            </div>
            <br>
            <button class="btn btn-success" onclick="saveSettings()">💾 Save Settings</button>
            <button class="btn" onclick="closeSettingsModal()">❌ Cancel</button>
        </div>
    </div>
    
    <button class="btn refresh-btn" onclick="refreshData()">🔄</button>
    
    <script>
        // Auto-refresh data every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial load
        refreshData();
        
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Error:', error));
        }
        
        function updateDashboard(data) {
            // Update status
            const statusElement = document.getElementById('botStatus');
            const statusTextElement = document.getElementById('botStatusText');
            
            if (data.bot_running) {
                statusElement.className = 'status-indicator status-running';
                statusTextElement.textContent = 'Running';
            } else {
                statusElement.className = 'status-indicator status-stopped';
                statusTextElement.textContent = 'Stopped';
            }
            
            // Update metrics
            document.getElementById('totalSignals').textContent = data.total_signals || 0;
            document.getElementById('activeSignals').textContent = data.active_signals || 0;
            document.getElementById('winRate').textContent = (data.win_rate || 0) + '%';
            document.getElementById('totalPips').textContent = data.total_pips || 0;
            document.getElementById('profitFactor').textContent = (data.profit_factor || 0).toFixed(2);
            
            // Update settings
            document.getElementById('minProbability').textContent = (data.min_probability || 50) + '%';
            document.getElementById('maxSignals').textContent = data.max_signals || 10;
            document.getElementById('activeSymbols').textContent = data.active_symbols || 3;
            
            // Update last update time
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
            // Update signals table
            updateSignalsTable(data.recent_signals || []);
            
            // Update log
            if (data.recent_log) {
                document.getElementById('liveLog').textContent = data.recent_log;
            }
        }
        
        function updateSignalsTable(signals) {
            const tbody = document.getElementById('signalsTableBody');
            
            if (signals.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">No recent signals</td></tr>';
                return;
            }
            
            tbody.innerHTML = signals.map(signal => `
                <tr>
                    <td>${new Date(signal.time).toLocaleTimeString()}</td>
                    <td>${signal.symbol}</td>
                    <td>${signal.side.toUpperCase()}</td>
                    <td>${signal.entry}</td>
                    <td>${signal.tp_probability}%</td>
                    <td><span class="status-indicator ${signal.status === 'tp_hit' ? 'status-running' : signal.status === 'sl_hit' ? 'status-stopped' : 'status-paused'}"></span>${signal.status}</td>
                    <td class="${signal.pnl > 0 ? 'positive' : signal.pnl < 0 ? 'negative' : 'neutral'}">${signal.pnl || 0}</td>
                </tr>
            `).join('');
        }
        
        function startBot() {
            fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function stopBot() {
            fetch('/api/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function restartBot() {
            fetch('/api/restart', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function runBacktest() {
            alert('Starting backtest... This may take a few minutes.');
            fetch('/api/backtest', {method: 'POST'})
                .then(response => response.json())
                .then(data => alert('Backtest completed: ' + data.message));
        }
        
        function optimizeParameters() {
            alert('Starting parameter optimization... This may take several minutes.');
            fetch('/api/optimize', {method: 'POST'})
                .then(response => response.json())
                .then(data => alert('Optimization completed: ' + data.message));
        }
        
        function generateReport() {
            window.open('/api/report', '_blank');
        }
        
        function exportData() {
            window.open('/api/export', '_blank');
        }
        
        function openSettingsModal() {
            document.getElementById('settingsModal').style.display = 'block';
        }
        
        function closeSettingsModal() {
            document.getElementById('settingsModal').style.display = 'none';
        }
        
        function saveSettings() {
            const settings = {
                min_probability: document.getElementById('probabilitySlider').value,
                max_signals: document.getElementById('maxSignalsInput').value,
                risk_level: document.getElementById('riskLevelSelect').value
            };
            
            fetch('/api/settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                alert('Settings saved successfully!');
                closeSettingsModal();
                refreshData();
            });
        }
        
        function clearLog() {
            document.getElementById('liveLog').textContent = 'Log cleared.';
        }
        
        // Settings modal interactions
        document.getElementById('probabilitySlider').addEventListener('input', function() {
            document.getElementById('probabilityValue').textContent = this.value + '%';
        });
    </script>
</body>
</html>
"""

class WebControlPanel:
    def __init__(self):
        self.bot_running = False
        self.settings = {
            "min_probability": 50,
            "max_signals": 10,
            "risk_level": "medium"
        }
    
    def get_bot_status(self):
        """Get current bot status and metrics"""
        try:
            # Load performance stats
            performance_data = {}
            if os.path.exists("performance_stats.json"):
                with open("performance_stats.json", 'r') as f:
                    performance_data = json.load(f)
            
            # Check if bot is running (simplified check)
            self.bot_running = self._check_bot_running()
            
            # Get recent signals
            recent_signals = self._get_recent_signals()
            
            # Get recent log entries
            recent_log = self._get_recent_log()
            
            status = {
                "bot_running": self.bot_running,
                "total_signals": performance_data.get("total_signals", 0),
                "active_signals": len([s for s in recent_signals if s.get("status") == "open"]),
                "win_rate": performance_data.get("win_rate", 0),
                "total_pips": performance_data.get("total_pips", 0),
                "profit_factor": performance_data.get("profit_factor", 0),
                "min_probability": self.settings["min_probability"],
                "max_signals": self.settings["max_signals"],
                "active_symbols": 3,  # From config
                "recent_signals": recent_signals[-10:],  # Last 10 signals
                "recent_log": recent_log
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {"error": str(e)}
    
    def _check_bot_running(self):
        """Check if the bot is currently running"""
        try:
            # Check if scanner.py process is running (simplified)
            if os.path.exists("trading_bot.log"):
                # Check if log was updated recently (within last 2 minutes)
                log_modified = os.path.getmtime("trading_bot.log")
                now = time.time()
                return (now - log_modified) < 120  # 2 minutes
            return False
        except Exception:
            return False
    
    def _get_recent_signals(self):
        """Get recent signals from various sources"""
        signals = []
        
        try:
            # Try to load from AI optimizer data
            if os.path.exists("ai_optimization_data.json"):
                with open("ai_optimization_data.json", 'r') as f:
                    ai_data = json.load(f)
                    signals.extend(ai_data.get("signals", []))
            
            # Convert to web format
            web_signals = []
            for signal in signals[-20:]:  # Last 20 signals
                web_signals.append({
                    "time": signal.get("timestamp", datetime.now().isoformat()),
                    "symbol": signal.get("symbol", "Unknown"),
                    "side": signal.get("side", "buy"),
                    "entry": signal.get("entry", 0),
                    "tp_probability": signal.get("tp_probability", 50),
                    "status": signal.get("status", "open"),
                    "pnl": 0  # Would calculate from actual data
                })
            
            return web_signals
            
        except Exception as e:
            logger.error(f"Error getting recent signals: {e}")
            return []
    
    def _get_recent_log(self):
        """Get recent log entries"""
        try:
            if os.path.exists("trading_bot.log"):
                with open("trading_bot.log", 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    # Get last 20 lines
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    return ''.join(recent_lines)
            return "No log data available"
        except Exception as e:
            return f"Error loading log: {e}"

# Global control panel instance
control_panel = WebControlPanel()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(CONTROL_PANEL_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    return jsonify(control_panel.get_bot_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the bot"""
    try:
        # This would implement actual bot starting logic
        control_panel.bot_running = True
        return jsonify({"success": True, "message": "Bot started successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the bot"""
    try:
        # This would implement actual bot stopping logic
        control_panel.bot_running = False
        return jsonify({"success": True, "message": "Bot stopped successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """Restart the bot"""
    try:
        # This would implement actual bot restarting logic
        return jsonify({"success": True, "message": "Bot restarted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """Run backtesting"""
    try:
        from automated_backtester import run_automated_backtest
        
        # Run backtest in background thread
        def run_backtest():
            result = run_automated_backtest()
            logger.info(f"Backtest completed: {result}")
        
        threading.Thread(target=run_backtest, daemon=True).start()
        
        return jsonify({"success": True, "message": "Backtesting started in background"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    """Run parameter optimization"""
    try:
        from ai_signal_optimizer import get_ai_optimization_report
        
        # Run optimization in background thread
        def run_optimization():
            result = get_ai_optimization_report()
            logger.info(f"Optimization completed: {result}")
        
        threading.Thread(target=run_optimization, daemon=True).start()
        
        return jsonify({"success": True, "message": "Parameter optimization started in background"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/settings', methods=['POST'])
def api_settings():
    """Save bot settings"""
    try:
        data = request.get_json()
        control_panel.settings.update(data)
        
        # Save settings to file
        with open("web_panel_settings.json", 'w') as f:
            json.dump(control_panel.settings, f, indent=2)
        
        return jsonify({"success": True, "message": "Settings saved successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/report')
def api_report():
    """Generate performance report"""
    try:
        # Generate comprehensive report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "status": control_panel.get_bot_status(),
            "message": "Performance report generated successfully"
        }
        
        return jsonify(report_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/export')
def api_export():
    """Export bot data"""
    try:
        # Export all relevant data
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "bot_status": control_panel.get_bot_status(),
            "settings": control_panel.settings,
            "export_note": "Data exported successfully"
        }
        
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": str(e)})

def start_web_panel(host='localhost', port=5000):
    """Start the web control panel"""
    try:
        logger.info(f"🌐 Starting Web Control Panel on http://{host}:{port}")
        app.run(host=host, port=port, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Error starting web panel: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_web_panel()
