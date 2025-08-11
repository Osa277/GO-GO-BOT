# 🚀 Vercel Deployment Guide

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: For code repository
3. **Telegram Bot Token**: Already configured in vercel.json

## 🛠️ Deployment Methods

### Method 1: GitHub + Vercel (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - MT5 Trading Bot"
   git branch -M main
   git remote add origin https://github.com/your-username/mt5-trading-bot.git
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the configuration from `vercel.json`

### Method 2: Vercel CLI (Direct Upload)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

## 🔧 Configuration

### Environment Variables (Already in vercel.json):
- `TELEGRAM_TOKEN`: 8120881444:AAEDiMtf02xlqPjFQ1cJPhMZf3XkAIUutro
- `TELEGRAM_CHAT_ID`: 5362504152

### Additional Users:
- Edit `api/index.py` line 11-15 to add more chat IDs:
```python
TELEGRAM_USERS = [
    '5362504152',  # Samuel (original user)
    '1234567890',  # User 2
    '0987654321',  # User 3
]
```

## 📡 API Endpoints

After deployment, your bot will have these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Health check |
| `/api/signal?symbol=BTCUSD` | GET | Generate signal |
| `/api/send-signal?symbol=BTCUSD` | GET | Generate & send signal |
| `/api/webhook` | POST | Receive external signals |
| `/api/users` | GET | List current users |
| `/api/add-user` | POST | Add new user |
| `/api/test-users` | GET | Test message to all users |

## 🧪 Testing Your Deployment

1. **Health Check**:
   ```
   GET https://your-app.vercel.app/api/status
   ```

2. **Test Users**:
   ```
   GET https://your-app.vercel.app/api/test-users
   ```

3. **Generate Signal**:
   ```
   GET https://your-app.vercel.app/api/send-signal?symbol=BTCUSD
   ```

## 👥 Adding New Users

### Method 1: Via API
```bash
curl -X POST https://your-app.vercel.app/api/add-user \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "1234567890"}'
```

### Method 2: Manual Edit
1. Edit `api/index.py`
2. Add chat ID to `TELEGRAM_USERS` list
3. Redeploy with `vercel --prod`

## 🔧 Webhook Integration

Use your Vercel URL as webhook endpoint:
```
POST https://your-app.vercel.app/api/webhook
Content-Type: application/json

{
  "symbol": "BTCUSD",
  "action": "buy",
  "price": 45000
}
```

## 📊 Supported Features

✅ Multi-user Telegram notifications
✅ Yahoo Finance data (free alternative to MT5)
✅ Real-time signal generation
✅ Webhook support for external signals
✅ Simple moving average + RSI strategy
✅ Automatic user management

## 🚨 Important Notes

1. **Free Tier Limits**: Vercel free tier has function execution limits
2. **Market Data**: Uses Yahoo Finance (free) instead of MT5
3. **Persistence**: User list resets on redeploy (use database for production)
4. **Security**: Consider adding authentication for production use

## 🎯 Next Steps

1. Deploy to Vercel
2. Test with `/api/test-users`
3. Add more users via `/api/add-user`
4. Set up webhooks if needed
5. Monitor with `/api/status`

Happy Trading! 🚀
