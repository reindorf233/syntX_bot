# Deriv SyntX Public Telegram Bot

A comprehensive Telegram bot for synthetic indices signals focused on Deriv SyntX style indices with Smart Money Concepts (SMC) analysis.

## Features

- 🚀 **Multi-Asset Support**: Volatility, Boom/Crash, Step, and Jump indices
- 📊 **Smart Money Concepts**: FVGs, Order Blocks, Liquidity Sweeps
- 📈 **Technical Analysis**: RSI, Bollinger Bands, MACD, EMAs
- 🔄 **Dual Data Sources**: MT5 connection + price simulation fallback
- 🤖 **24/7 Auto-Scanner**: Background scanning with channel broadcasts
- 💰 **Risk Management**: ATR-based SL/TP, position sizing for $5-10 accounts
- 📱 **Interactive Interface**: Inline keyboards, real-time analysis
- 🗄️ **User Management**: SQLite database for users and signals

## Supported Indices

### Volatility Indices
- Volatility 10 Index
- Volatility 25 Index  
- Volatility 50 Index
- Volatility 75 Index
- Volatility 100 Index

### Boom/Crash Indices
- Boom 500 Index
- Boom 1000 Index
- Crash 500 Index
- Crash 1000 Index

### Other Indices
- Step Index
- Jump 25/50/75/100 Indices

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd syntX_bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Create Telegram Bot**
- Contact @BotFather on Telegram
- Create a new bot with `/newbot`
- Get your bot token and add to `.env`

5. **Create Public Channel** (Optional)
- Create a public channel
- Add your bot as administrator
- Add channel ID to `.env`

## Configuration

### Environment Variables (.env)

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
PUBLIC_CHANNEL_ID=@your_public_channel

# MT5 Configuration (Deriv Demo)
MT5_LOGIN=your_deriv_demo_account
MT5_PASSWORD=your_deriv_demo_password
MT5_SERVER=Deriv-Demo

# Bot Settings
SCAN_INTERVAL_MINUTES=10
SIGNAL_STRENGTH_THRESHOLD=7
RISK_PERCENTAGE=1.0
MIN_ACCOUNT_BALANCE=5.0
MAX_ACCOUNT_BALANCE=10.0

# Analysis Settings
TIMEFRAME=M5
BARS_COUNT=100
RSI_PERIOD=14
BB_PERIOD=20
BB_STD=2
EMA_FAST=20
EMA_SLOW=200
```

## Usage

### Starting the Bot

```bash
python main.py
```

### Bot Commands

- `/start` - Show main menu
- `/scan` - Scan all symbols for signals
- `/stats` - Show bot statistics
- `/subscribe` - Subscription information
- `/help` - Show help message

### Signal Strength

- **8-10/10**: Strong signal ⭐⭐⭐
- **6-7/10**: Good signal ⭐⭐  
- **4-5/10**: Weak signal ⭐
- **0-3/10**: No signal

### Risk Management

- Always use provided stop loss
- Risk only 1% per trade
- Follow suggested position sizes
- Use appropriate lot sizes for account balance

## Architecture

### Core Components

1. **Main Bot** (`main.py`)
   - Application entry point
   - Graceful startup/shutdown
   - Signal handlers

2. **Telegram Interface** (`telegram_bot.py`)
   - Command handlers
   - Inline keyboards
   - Message formatting

3. **Signal Generation** (`signal_generator.py`)
   - MT5 data fetching
   - Price simulation fallback
   - Signal analysis

4. **Technical Analysis** (`technical_analyzer.py`)
   - SMC analysis
   - Technical indicators
   - Signal strength scoring

5. **MT5 Handler** (`mt5_handler.py`)
   - Connection management
   - Data fetching
   - Retry logic

6. **Price Simulator** (`price_simulator.py`)
   - GBM-based simulation
   - Symbol-specific parameters
   - Realistic price generation

7. **Auto Scanner** (`auto_scanner.py`)
   - Background scanning
   - Channel broadcasting
   - Scheduled tasks

8. **Database** (`database.py`)
   - User management
   - Signal storage
   - Statistics

## Data Sources

### Primary: MT5 Connection
- Real-time data from Deriv MT5
- Accurate OHLC prices
- Live market conditions

### Fallback: Price Simulation
- Geometric Brownian Motion
- Symbol-specific volatility
- Jump patterns for Boom/Crash
- Labeled as "Simulated"

## Deployment

### Local Development
```bash
python main.py
```

### Production (Render/Railway)
1. Set environment variables in platform
2. Use webhook instead of polling
3. Configure persistent storage for database
4. Set up monitoring

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## Monitoring

### Logs
- Console output
- `bot.log` file
- Error tracking

### Database Statistics
- Total signals generated
- User interactions
- Signal performance

### Health Checks
- MT5 connection status
- Bot responsiveness
- Scanner activity

## Security

- Environment variables for sensitive data
- Input validation
- Error handling
- Rate limiting considerations

## Troubleshooting

### Common Issues

1. **MT5 Connection Failed**
   - Check credentials in `.env`
   - Verify Deriv demo account
   - Check network connectivity

2. **Bot Token Invalid**
   - Verify token from BotFather
   - Check token format

3. **No Signals Generated**
   - Check signal strength threshold
   - Verify data source connection
   - Review analysis parameters

4. **Channel Broadcasting Fails**
   - Check bot is channel admin
   - Verify channel ID format
   - Check channel privacy settings

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create GitHub issue
- Contact bot administrator
- Review documentation

## Disclaimer

This bot is for educational and informational purposes only. Trading synthetic indices involves significant risk. Always:
- Do your own research
- Use proper risk management
- Start with demo accounts
- Never risk more than you can afford to lose

The bot provides signals based on technical analysis but cannot guarantee profits. Past performance does not indicate future results.
