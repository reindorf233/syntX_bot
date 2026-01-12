import os
import logging
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.public_channel_id = os.getenv('PUBLIC_CHANNEL_ID')
        
        # MT5 Configuration
        try:
            self.mt5_login = int(os.getenv('MT5_LOGIN', 0))
        except ValueError:
            self.mt5_login = 0
            logging.warning("Invalid MT5_LOGIN format, using 0")
        
        self.mt5_password = os.getenv('MT5_PASSWORD')
        self.mt5_server = os.getenv('MT5_SERVER')
        
        # Bot Settings
        self.scan_interval_minutes = int(os.getenv('SCAN_INTERVAL_MINUTES', 10))
        self.signal_strength_threshold = float(os.getenv('SIGNAL_STRENGTH_THRESHOLD', 7.0))
        self.risk_percentage = float(os.getenv('RISK_PERCENTAGE', 1.0))
        self.min_account_balance = float(os.getenv('MIN_ACCOUNT_BALANCE', 5.0))
        self.max_account_balance = float(os.getenv('MAX_ACCOUNT_BALANCE', 10.0))
        
        # Analysis Settings
        self.timeframe = os.getenv('TIMEFRAME', 'M5')
        self.bars_count = int(os.getenv('BARS_COUNT', 100))
        self.rsi_period = int(os.getenv('RSI_PERIOD', 14))
        self.bb_period = int(os.getenv('BB_PERIOD', 20))
        self.bb_std = float(os.getenv('BB_STD', 2.0))
        self.ema_fast = int(os.getenv('EMA_FAST', 20))
        self.ema_slow = int(os.getenv('EMA_SLOW', 200))
        self.macd_fast = int(os.getenv('MACD_FAST', 12))
        self.macd_slow = int(os.getenv('MACD_SLOW', 26))
        self.macd_signal = int(os.getenv('MACD_SIGNAL', 9))
        
        # Validate required settings
        self.validate()
    
    def validate(self):
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        if not self.public_channel_id:
            logging.warning("PUBLIC_CHANNEL_ID not set - broadcast alerts disabled")
            
        if self.mt5_login == 0 or not self.mt5_password or not self.mt5_server:
            logging.warning("MT5 credentials incomplete - will use simulation mode only")

# Global config instance
config = Config()
