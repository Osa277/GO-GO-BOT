# GO-GO-BOT Trading System

🤖 **Advanced MT5 Trading Bot with Multi-User Telegram Support**

## Features

✅ **Multi-User Telegram Notifications**
- Send signals to multiple users simultaneously
- Simple chat ID management system
- Welcome messages for new users

✅ **Optimized Timeframes** 
- M3, M5, M15 timeframes only (removed 1hr, 30m, 1m for performance)
- Enhanced signal accuracy

✅ **Advanced Analytics**
- Real-time probability analysis
- Risk management
- Performance tracking

✅ **Vercel Deployment Ready**
- Web API endpoints
- Webhook support
- Cloud hosting compatible

## Quick Start

### Local Development
```bash
python scanner.py  # Start optimized scanner
python simple_user_manager.py  # Manage Telegram users
```

### Web API (Vercel)
- `/api/status` - Health check
- `/api/signal` - Get trading signal
- `/api/send-signal` - Send signal to all users
- `/api/users` - View user list
- `/api/add-user` - Add new user (POST)

## User Management

### Add New Telegram Users
1. User sends `/start` to your bot
2. Run `python simple_user_manager.py` to get chat IDs
3. Add chat IDs to `TELEGRAM_USERS` list in `telegram_utils.py`

### Supported Symbols
- BTCUSD (Bitcoin)
- XAUUSD (Gold)  
- US30 (Dow Jones)

## Deployment

### GitHub
```bash
git add .
git commit -m "Deploy MT5 trading bot"
git push origin main
```

### Vercel
```bash
vercel deploy --prod
```

## Configuration

Update environment variables in `vercel.json`:
- `TELEGRAM_TOKEN` - Your bot token
- `TELEGRAM_CHAT_ID` - Primary chat ID

## Architecture

- **scanner.py** - Main trading engine
- **telegram_utils.py** - Multi-user messaging
- **api/index.py** - Web API endpoints
- **mt5_data.py** - Optimized data handling

---

🚀 **Ready for production deployment!**
