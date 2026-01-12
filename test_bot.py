import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
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
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        self.running = False
        
    async def start(self):
        """Start the bot"""
        try:
            # Initialize MT5 connection (optional)
            try:
                if mt5_handler.connect():
                    logger.info("MT5 connection established")
                else:
                    logger.warning("MT5 connection failed - will use simulation mode")
            except Exception as e:
                logger.error(f"MT5 initialization error: {e}")
            
            # Setup handlers
            application = Application.builder().token(config.telegram_bot_token).build()
            
            # Command handlers
            application.add_handler(CommandHandler("start", self.handle_start))
            application.add_handler(CommandHandler("help", self.handle_help))
            application.add_handler(CommandHandler("scan", self.handle_scan))
            
            # Callback query handlers
            application.add_handler(CallbackQueryHandler(self.handle_callback))
            
            # Message handlers
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            self.running = True
            logger.info("Bot started successfully!")
            
            # Run the bot
            await application.run_polling()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        if not self.running:
            return
        
        logger.info("Stopping bot...")
        self.running = False
    
    async def handle_start(self, update: Update, context):
        """Handle /start command"""
        user = update.effective_user
        await update.message.reply_text(
            "🚀 *Deriv SyntX Bot is Working!*\n\n"
            "📊 *Features:*\n"
            "• Volatility Indices (10, 25, 50, 75, 100)\n"
            "• Boom/Crash Indices (500, 1000)\n"
            "• Step Index\n"
            "• Jump Indices (25, 50, 75, 100)\n\n"
            "📱 *Commands:*\n"
            "• /start - Show this menu\n"
            "• /scan - Scan all symbols\n"
            "• /help - Show help\n\n"
            "🔍 *Bot is running in simulation mode*\n"
            "Use /scan to test signals!"
        )
    
    async def handle_help(self, update: Update, context):
        """Handle /help command"""
        await update.message.reply_text(
            "📖 *Bot Help*\n\n"
            "📊 *Supported Assets:*\n"
            "• Volatility: 10, 25, 50, 75, 100\n"
            "• Boom/Crash: 500, 1000\n"
            "• Step: Step Index\n"
            "• Jump: 25, 50, 75, 100\n\n"
            "🔍 *Commands:*\n"
            "• /start - Main menu\n"
            "• /scan - Quick scan\n"
            "• /help - This help\n\n"
            "💡 *Note: Bot uses simulation mode*\n"
            "All features work perfectly!"
        )
    
    async def handle_scan(self, update: Update, context):
        """Handle /scan command"""
        await update.message.reply_text("🔍 *Scanning all symbols...*\n\nThis may take a moment...")
        
        # Import signal generator here to avoid circular imports
        from signal_generator import signal_generator
        
        try:
            signals = signal_generator.scan_all_symbols()
            if signals:
                message = "🚀 *Strong Signals Found:*\n\n"
                for symbol, signal in list(signals.items())[:5]:  # Top 5 signals
                    direction_emoji = "🟢" if signal['direction'] == 'bullish' else "🔴"
                    message += f"{direction_emoji} *{symbol}*\n"
                    message += f"   {signal['direction'].upper()} {signal['strength']}/10\n"
                    message += f"   Entry: {signal['entry_price']}\n"
                    message += f"   SL: {signal['stop_loss']}\n"
                    message += f"   TP: {signal['take_profit']}\n\n"
            else:
                message = "📊 *No strong signals found*\n\n"
                message += "Try individual symbols via /start menu\n"
                message += "Signals below threshold may not be shown"
        except Exception as e:
            message = f"❌ *Scan error:*\n{e}"
        
        await update.message.reply_text(message)
    
    async def handle_callback(self, update: Update, context):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        # Simple callback handling
        if query.data == "back_to_main":
            await self.handle_start(update, context)
        else:
            await update.callback_query.edit_message_text(
                f"🔍 *Feature: {query.data}*\n\n"
                "This feature is being developed!\n"
                "Use /start for main menu"
            )
    
    async def handle_message(self, update: Update, context):
        """Handle regular messages"""
        text = update.message.text.lower()
        
        if "hello" in text or "hi" in text:
            await update.message.reply_text("👋 Hello! Use /start to see the main menu")
        elif "signal" in text:
            await self.handle_scan(update, context)
        else:
            await update.message.reply_text("🤔 Use /start for main menu or /help for assistance")
    
    def run(self):
        """Run the bot"""
        asyncio.run(self.start())

# Global bot instance
bot = SimpleBot()

if __name__ == "__main__":
    bot.run()
