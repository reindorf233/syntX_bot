import asyncio
import logging
import signal
import sys
from telegram_bot import telegram_bot
from auto_scanner import auto_scanner, scheduled_tasks
from deriv_api_handler import DerivAPIHandler
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SyntheticsPublicBot:
    def __init__(self):
        self.running = False
        self.deriv_handler = None
        
    async def start(self):
        """Start bot and all background tasks"""
        try:
            logger.info("Starting Deriv SyntX Public Bot...")
            
            # Initialize Deriv API connection
            try:
                self.deriv_handler = DerivAPIHandler(
                    config.deriv_app_id, 
                    config.deriv_token
                )
                if await self.deriv_handler.connect():
                    logger.info("Deriv API connection established")
                else:
                    logger.warning("Deriv API connection failed - will use simulation mode")
            except Exception as e:
                logger.error(f"Deriv initialization error: {e}")
            
            # Start auto-scanner
            await auto_scanner.start_scanner()
            
            # Start scheduled tasks
            await scheduled_tasks.start_tasks()
            
            self.running = True
            logger.info("Bot started successfully!")
            
            # Send startup message to channel if configured
            if config.public_channel_id:
                try:
                    await telegram_bot.broadcast_to_channel(
                        "🚀 *Deriv SyntX Bot is now online!*\n\n"
                        "📊 24/7 automated scanning active\n"
                        "🔍 Real-time signal analysis\n"
                        "💥 Synthetic indices alerts\n\n"
                        "Use /start to begin!"
                    )
                except Exception as e:
                    logger.error(f"Failed to send startup message: {e}")
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self, signum=None, frame=None):
        """Stop bot gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping bot...")
        
        try:
            # Stop auto-scanner
            await auto_scanner.stop_scanner()
            
            # Stop scheduled tasks
            await scheduled_tasks.stop_tasks()
            
            # Disconnect Deriv API
            if self.deriv_handler:
                await self.deriv_handler.disconnect()
            
            # Send shutdown message to channel if configured
            if config.public_channel_id:
                try:
                    await telegram_bot.broadcast_to_channel(
                        "🔴 *Deriv SyntX Bot is shutting down for maintenance*\n\n"
                        "We'll be back online shortly!"
                    )
                except Exception as e:
                    logger.error(f"Failed to send shutdown message: {e}")
            
            self.running = False
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def run(self):
        """Main bot run method"""
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self.stop(s, f)))
        signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self.stop(s, f)))
        
        try:
            # Start the bot
            asyncio.run(self.start())
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

# Global bot instance
bot = SyntheticsPublicBot()

if __name__ == "__main__":
    bot.run()
