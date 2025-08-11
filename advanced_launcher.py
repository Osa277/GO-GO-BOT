#!/usr/bin/env python3
"""
Advanced GO-GO-BOT Launcher
Comprehensive launcher with all enhanced features and management options.
"""

import os
import sys
import time
import logging
import threading
import signal
import subprocess
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_launcher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AdvancedBotLauncher:
    def __init__(self):
        self.running = False
        self.processes = {}
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down all processes...")
        self.shutdown_all()
        sys.exit(0)
    
    def print_banner(self):
        """Print startup banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                            🚀 GO-GO-BOT ADVANCED LAUNCHER                    ║
║                           Enhanced Trading Bot System                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Version: 5.0-AI-Enhanced                                                    ║
║  Features: AI Optimization, Automated Backtesting, Web Control Panel        ║
║  Data Source: MetaTrader5 (Real-time)                                        ║
║  Status: Ready for Advanced Trading                                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_dependencies(self):
        """Check if all required files and dependencies are available"""
        required_files = [
            'scanner.py',
            'config.py',
            'mt5_data.py',
            'smc_utils.py',
            'telegram_utils.py',
            'advanced_analytics.py',
            'realtime_tp_calculator.py',
            'smart_signal_filter.py',
            'performance_monitor.py',
            'ai_signal_optimizer.py',
            'automated_backtester.py',
            'web_control_panel.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"❌ Missing required files: {missing_files}")
            return False
        
        logger.info("✅ All required files found")
        return True
    
    def show_menu(self):
        """Show interactive menu"""
        menu = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🎮 LAUNCHER MENU                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. 🚀 Start Full Trading Bot (All Features)                               │
│  2. 📊 Start Simple Dashboard Only                                         │
│  3. 🌐 Start Web Control Panel Only                                        │
│  4. 🤖 Run AI Optimization Analysis                                        │
│  5. 📈 Run Automated Backtesting                                           │
│  6. 🔍 View Current Bot Status                                             │
│  7. 📋 View Performance Report                                             │
│  8. ⚙️  Configure Bot Settings                                              │
│  9. 🛠️  System Diagnostics                                                 │
│  0. ❌ Exit Launcher                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
        """
        print(menu)
        
    def start_trading_bot(self):
        """Start the full trading bot with all features"""
        try:
            logger.info("🚀 Starting full trading bot with all advanced features...")
            
            # Start main scanner
            scanner_process = subprocess.Popen(
                [sys.executable, 'scanner.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['scanner'] = scanner_process
            logger.info("✅ Trading bot scanner started")
            
            # Start web control panel in background
            try:
                web_process = subprocess.Popen(
                    [sys.executable, 'web_control_panel.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                self.processes['web_panel'] = web_process
                logger.info("✅ Web control panel started on http://localhost:5000")
            except Exception as e:
                logger.warning(f"⚠️ Could not start web panel: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting trading bot: {e}")
            return False
    
    def start_dashboard_only(self):
        """Start simple dashboard only"""
        try:
            logger.info("📊 Starting simple dashboard...")
            os.system(f"{sys.executable} simple_dashboard.py")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting dashboard: {e}")
            return False
    
    def start_web_panel_only(self):
        """Start web control panel only"""
        try:
            logger.info("🌐 Starting web control panel...")
            
            web_process = subprocess.Popen(
                [sys.executable, 'web_control_panel.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            self.processes['web_panel'] = web_process
            logger.info("✅ Web control panel started on http://localhost:5000")
            logger.info("💡 Open your browser and go to http://localhost:5000")
            
            # Keep process running
            web_process.wait()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting web panel: {e}")
            return False
    
    def run_ai_optimization(self):
        """Run AI optimization analysis"""
        try:
            logger.info("🤖 Running AI optimization analysis...")
            
            from ai_signal_optimizer import get_ai_optimization_report
            result = get_ai_optimization_report()
            
            if result.get('status') == 'success':
                logger.info("✅ AI optimization completed successfully")
                print("\n🤖 AI OPTIMIZATION RESULTS:")
                print(f"   Status: {result.get('status')}")
                if 'recommendations' in result:
                    print(f"   Recommendations Generated: {len(result['recommendations'].get('recommendations', []))}")
                
                # Save detailed results
                with open('ai_optimization_results.json', 'w') as f:
                    json.dump(result, f, indent=2)
                
                print("   📁 Detailed results saved to: ai_optimization_results.json")
                
            else:
                logger.warning(f"⚠️ AI optimization: {result.get('message', 'Unknown status')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running AI optimization: {e}")
            return False
    
    def run_automated_backtest(self):
        """Run automated backtesting"""
        try:
            logger.info("📈 Running automated backtesting suite...")
            
            from automated_backtester import run_automated_backtest
            result = run_automated_backtest()
            
            if result.get('status') == 'success':
                logger.info("✅ Automated backtesting completed successfully")
                print("\n📈 BACKTESTING RESULTS:")
                print(f"   Status: {result.get('status')}")
                
                data_quality = result.get('data_quality', {})
                print(f"   Signals Analyzed: {data_quality.get('total_signals_analyzed', 0)}")
                print(f"   Confidence Level: {data_quality.get('confidence_level', 'Unknown')}")
                
                # Save detailed results
                with open('backtest_results_detailed.json', 'w') as f:
                    json.dump(result, f, indent=2)
                
                print("   📁 Detailed results saved to: backtest_results_detailed.json")
                
            else:
                logger.warning(f"⚠️ Backtesting: {result.get('message', 'Unknown status')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running backtesting: {e}")
            return False
    
    def view_bot_status(self):
        """View current bot status"""
        try:
            logger.info("🔍 Checking bot status...")
            
            status_info = {
                "timestamp": datetime.now().isoformat(),
                "processes": {},
                "files": {}
            }
            
            # Check running processes
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    status_info["processes"][name] = "Running"
                else:
                    status_info["processes"][name] = "Stopped"
            
            # Check important files
            important_files = [
                'trading_bot.log',
                'performance_stats.json',
                'ai_optimization_data.json',
                'backtest_results.json'
            ]
            
            for file in important_files:
                if os.path.exists(file):
                    mod_time = os.path.getmtime(file)
                    status_info["files"][file] = {
                        "exists": True,
                        "last_modified": datetime.fromtimestamp(mod_time).isoformat(),
                        "size_kb": round(os.path.getsize(file) / 1024, 2)
                    }
                else:
                    status_info["files"][file] = {"exists": False}
            
            print("\n🔍 CURRENT BOT STATUS:")
            print("=" * 50)
            
            print("\n📋 Running Processes:")
            for name, status in status_info["processes"].items():
                status_icon = "✅" if status == "Running" else "❌"
                print(f"   {status_icon} {name}: {status}")
            
            print("\n📁 Important Files:")
            for file, info in status_info["files"].items():
                if info["exists"]:
                    print(f"   ✅ {file} ({info['size_kb']} KB, modified: {info['last_modified'][:19]})")
                else:
                    print(f"   ❌ {file} (missing)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking bot status: {e}")
            return False
    
    def view_performance_report(self):
        """View performance report"""
        try:
            logger.info("📋 Generating performance report...")
            
            # Try to run simple dashboard to get current stats
            os.system(f"{sys.executable} simple_dashboard.py")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating performance report: {e}")
            return False
    
    def configure_settings(self):
        """Configure bot settings"""
        try:
            print("\n⚙️ BOT CONFIGURATION")
            print("=" * 30)
            
            # Load current config
            current_config = {}
            try:
                if os.path.exists('config.py'):
                    import config
                    current_config = {
                        'symbols': getattr(config, 'SYMBOLS', []),
                        'timeframes': getattr(config, 'TIMEFRAMES', []),
                        'risk': getattr(config, 'RR_MULTIPLIERS', {})
                    }
                    print(f"📊 Current Symbols: {current_config['symbols']}")
                    print(f"⏰ Current Timeframes: {current_config['timeframes']}")
            except Exception as e:
                logger.warning(f"Could not load current config: {e}")
            
            print("\n💡 Configuration options:")
            print("   1. View current configuration")
            print("   2. Edit configuration file manually")
            print("   3. Reset to default configuration")
            print("   4. Back to main menu")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print(f"\n📋 Current Configuration:")
                print(f"   Symbols: {current_config.get('symbols', 'Unknown')}")
                print(f"   Timeframes: {current_config.get('timeframes', 'Unknown')}")
                print(f"   Risk Settings: {current_config.get('risk', 'Unknown')}")
            
            elif choice == "2":
                print("💡 Please edit config.py manually with your preferred text editor")
                print("   Example: notepad config.py")
            
            elif choice == "3":
                print("⚠️ This will reset all settings to default values")
                confirm = input("Are you sure? (y/N): ").strip().lower()
                if confirm == 'y':
                    print("🔄 Configuration reset functionality would be implemented here")
                else:
                    print("❌ Configuration reset cancelled")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in configuration: {e}")
            return False
    
    def run_diagnostics(self):
        """Run system diagnostics"""
        try:
            print("\n🛠️ SYSTEM DIAGNOSTICS")
            print("=" * 30)
            
            # Check Python version
            python_version = sys.version.split()[0]
            print(f"🐍 Python Version: {python_version}")
            
            # Check required modules
            required_modules = [
                'MetaTrader5', 'pandas', 'numpy', 'requests', 
                'flask', 'logging', 'threading', 'json'
            ]
            
            print("\n📦 Module Dependencies:")
            for module in required_modules:
                try:
                    __import__(module)
                    print(f"   ✅ {module}: Available")
                except ImportError:
                    print(f"   ❌ {module}: Missing")
            
            # Check file permissions
            print("\n📁 File Permissions:")
            test_files = ['config.py', 'scanner.py', 'trading_bot.log']
            for file in test_files:
                if os.path.exists(file):
                    readable = os.access(file, os.R_OK)
                    writable = os.access(file, os.W_OK)
                    print(f"   📄 {file}: R{'✅' if readable else '❌'} W{'✅' if writable else '❌'}")
                else:
                    print(f"   📄 {file}: Missing")
            
            # Check disk space
            try:
                import shutil
                total, used, free = shutil.disk_usage('.')
                free_gb = free // (1024**3)
                print(f"\n💾 Free Disk Space: {free_gb} GB")
            except Exception:
                print("\n💾 Could not check disk space")
            
            print("\n🔍 Diagnostic complete!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running diagnostics: {e}")
            return False
    
    def shutdown_all(self):
        """Shutdown all running processes"""
        logger.info("🛑 Shutting down all processes...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {name}...")
                    process.kill()
        
        self.processes.clear()
        logger.info("✅ All processes stopped")
    
    def run_interactive_mode(self):
        """Run interactive launcher mode"""
        self.running = True
        
        while self.running:
            try:
                self.show_menu()
                choice = input("Enter your choice (0-9): ").strip()
                
                if choice == "1":
                    self.start_trading_bot()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "2":
                    self.start_dashboard_only()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "3":
                    self.start_web_panel_only()
                
                elif choice == "4":
                    self.run_ai_optimization()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "5":
                    self.run_automated_backtest()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "6":
                    self.view_bot_status()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "7":
                    self.view_performance_report()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "8":
                    self.configure_settings()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "9":
                    self.run_diagnostics()
                    input("\nPress Enter to return to menu...")
                
                elif choice == "0":
                    print("👋 Goodbye! Shutting down launcher...")
                    self.shutdown_all()
                    self.running = False
                
                else:
                    print("❌ Invalid choice. Please enter a number between 0-9.")
                    time.sleep(1)
                
                # Clear screen between operations
                os.system('cls' if os.name == 'nt' else 'clear')
                
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupt received. Shutting down...")
                self.shutdown_all()
                break
            except Exception as e:
                logger.error(f"❌ Menu error: {e}")
                input("Press Enter to continue...")

def main():
    """Main launcher function"""
    try:
        launcher = AdvancedBotLauncher()
        
        # Clear screen and show banner
        os.system('cls' if os.name == 'nt' else 'clear')
        launcher.print_banner()
        
        # Check dependencies
        if not launcher.check_dependencies():
            print("❌ Dependency check failed. Please ensure all files are present.")
            input("Press Enter to exit...")
            return
        
        print("✅ All dependencies checked successfully!")
        print("🚀 Starting interactive launcher...")
        time.sleep(2)
        
        # Clear screen again and start interactive mode
        os.system('cls' if os.name == 'nt' else 'clear')
        launcher.run_interactive_mode()
        
    except Exception as e:
        logger.critical(f"❌ CRITICAL LAUNCHER ERROR: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
