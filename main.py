import asyncio
import logging
import signal
import sys
from telegram_bot import telegram_bot
from auto_scanner import auto_scanner, scheduled_tasks
from mt5_handler import mt5_handler
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
        
    async def start(self):
        """Start the bot and all background tasks"""
        try:
            logger.info("Starting Deriv SyntX Public Bot...")
            
            # Initialize MT5 connection (optional)
            try:
                if mt5_handler.connect():
                    logger.info("MT5 connection established")
                else:
                    logger.warning("MT5 connection failed - will use simulation mode")
            except Exception as e:
                logger.error(f"MT5 initialization error: {e}")
            
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
                        "💥 Boom/Crash & Volatility alerts\n\n"
                        "Use /start to begin!"
                    )
                except Exception as e:
                    logger.error(f"Failed to send startup message: {e}")
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self, signum=None, frame=None):
        """Stop the bot gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping bot...")
        
        try:
            # Stop auto-scanner
            await auto_scanner.stop_scanner()
            
            # Stop scheduled tasks
            await scheduled_tasks.stop_tasks()
            
            # Disconnect MT5
            mt5_handler.disconnect()
            
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
    
    async def run(self):
        """Main bot run method"""
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self.stop(s, f)))
        signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self.stop(s, f)))
        
        try:
            # Start the bot
            await self.start()
            
            # Run the Telegram bot (this is blocking)
            telegram_bot.run()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.stop()

# Global bot instance
bot = SyntheticsPublicBot()

def main():
    """Main entry point"""
    try:
        # Run the bot
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
