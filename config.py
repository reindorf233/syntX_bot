import os
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Telegram Bot Configuration
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.public_channel_id = os.getenv('PUBLIC_CHANNEL_ID')
        self.bot_owner_id = os.getenv('BOT_OWNER_ID')  # Admin control
        
        # Deriv API Configuration (Primary)
        self.deriv_app_id = os.getenv('DERIV_APP_ID')
        self.deriv_token = os.getenv('DERIV_TOKEN')
        
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
        
        # AI/ML Settings
        self.ai_enabled = os.getenv('AI_ENABLED', 'true').lower() == 'true'
        self.ai_confidence_threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', 0.7))
        self.ai_training_epochs = int(os.getenv('AI_TRAINING_EPOCHS', 20))
        
        # Webhook Settings (for hosting)
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.port = int(os.getenv('PORT', 8080))
        
        # Rate Limiting
        self.user_rate_limit = int(os.getenv('USER_RATE_LIMIT', 5))  # requests per minute
        
        # Validation
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        if not self.telegram_bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set - bot will not work")
        
        if not self.deriv_app_id or not self.deriv_token:
            logger.warning("Deriv API credentials not set - will use simulation mode")
        
        if self.signal_strength_threshold < 1 or self.signal_strength_threshold > 10:
            logger.warning("SIGNAL_STRENGTH_THRESHOLD should be between 1-10")
        
        if self.risk_percentage < 0.1 or self.risk_percentage > 5.0:
            logger.warning("RISK_PERCENTAGE should be between 0.1-5.0")

# Global config instance
config = Config()
