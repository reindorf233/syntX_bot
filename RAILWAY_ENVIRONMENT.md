# Railway Environment Variables - Complete Setup

## 🔧 **Required Environment Variables**

### 📱 **Telegram Bot Configuration**
```
TELEGRAM_BOT_TOKEN=8592086807:AAHfNHsBY4cuwDfvvFUMkmw5bZiC0ObJmCk
PUBLIC_CHANNEL_ID=@syntXSAFE
BOT_OWNER_ID=your_telegram_user_id
```

### 🌐 **Deriv API Configuration**
```
DERIV_APP_ID=120931
DERIV_TOKEN=RNaduc1QRp2NxMJ
```

### 🤖 **Bot Settings**
```
SIGNAL_STRENGTH_THRESHOLD=7.0
RISK_PERCENTAGE=1.0
MIN_ACCOUNT_BALANCE=5.0
MAX_ACCOUNT_BALANCE=10.0
```

### 📊 **Technical Analysis Settings**
```
BARS_COUNT=100
BB_PERIOD=20
BB_STD=2.0
RSI_PERIOD=14
EMA_FAST=20
EMA_SLOW=200
```

### 🧠 **AI Settings**
```
AI_ENABLED=true
AI_CONFIDENCE_THRESHOLD=0.7
AI_TRAINING_EPOCHS=20
```

### 🔄 **Auto Scanner Settings**
```
AUTO_SCAN_ENABLED=true
SCAN_INTERVAL=600
SCAN_INTERVAL_MINUTES=10
```

### 🌐 **Webhook & Hosting**
```
WEBHOOK_URL=https://your-app-url.onrender.com/webhook
PORT=8080
```

### ⏰ **Time Settings**
```
TIMEFRAME=M5
USER_RATE_LIMIT=5
```

## 🚀 **Railway Deployment Setup**

### 1. **Set Environment Variables**
- Copy all variables above to Railway dashboard
- Replace `your_telegram_user_id` with your actual Telegram user ID
- Replace `your-app-url` with your actual Railway app URL

### 2. **Webhook Configuration**
```
Webhook URL: https://your-app-url.onrender.com/webhook
Health Check: https://your-app-url.onrender.com/health
```

### 3. **Port Configuration**
```
Port: 8080 (Railway automatically assigns PORT)
```

## 📋 **Verification Checklist**

### ✅ **Before Deployment**
- [ ] All environment variables set in Railway
- [ ] Telegram Bot Token is valid
- [ ] Deriv credentials are correct
- [ ] Webhook URL updated with actual app URL

### ✅ **After Deployment**
- [ ] Bot starts without errors
- [ ] Webhook responds to POST requests
- [ ] Health check returns 200 OK
- [ ] Live prices show correct ranges (5698 for Vol 10)
- [ ] No "SIMULATED" tags appear

## 🔍 **Testing Endpoints**

### 🌐 **API Endpoints**
```
GET  /                    - Bot status
GET  /health              - Health check
POST /webhook            - Webhook handler
```

### 📱 **Telegram Commands**
```
/start                   - Start bot
/scan                    - Scan all symbols
/stats                   - Bot statistics
/help                    - Help menu
```

## 🎯 **Expected Results**

### ✅ **Correct Price Ranges**
- **Volatility 10**: ~5698 (not 100,000)
- **Step Index**: ~1500 (not 1000)
- **Boom 500**: ~1500 (not 100,000)

### ✅ **Live Data Indicators**
- **No "SIMULATED"** tags
- **Real-time Deriv API** prices
- **Correct symbol mappings**
- **Webhook responding** to requests

## 🌐 **GitHub Status**

All fixes have been pushed to GitHub:
```
ffdcc3e - Fix Deriv API connection and remove simulation fallback
```

Railway will automatically pull the latest changes and redeploy.
