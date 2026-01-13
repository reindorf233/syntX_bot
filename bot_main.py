#!/usr/bin/env python3
"""
syntX_bot - Main Entry Point
Advanced Trading Bot with Multiple Strategies
"""
import asyncio
import logging
import os
from telegram_bot_handler import TelegramBotHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main bot function"""
    logger.info("🚀 Starting syntX Bot - Advanced Trading System")
    
    try:
        # Create and run bot
        bot_handler = TelegramBotHandler()
        await bot_handler.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
