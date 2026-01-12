import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from typing import Dict, List
from signal_generator import signal_generator
from database import db_manager
from config import config

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(config.telegram_bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("scan", self.handle_scan))
        self.application.add_handler(CommandHandler("stats", self.handle_stats))
        self.application.add_handler(CommandHandler("subscribe", self.handle_subscribe))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        db_manager.add_user(user.id, user.username, user.first_name, user.last_name)
        db_manager.log_interaction(user.id, "start")
        
        welcome_message = """
🚀 *Welcome to Deriv SyntX Signals Bot!*

📊 *Real-time synthetic indices signals with SMC analysis*

🔹 *Features:*
• Volatility Indices (10, 25, 50, 75, 100)
• Boom & Crash Indices (500, 1000)
• Step Index
• Jump Indices (25, 50, 75, 100)
• Smart Money Concepts (SMC)
• Risk management included
• 24/7 automated scanning

📈 *Choose an option below to get started:*
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Volatility Indices", callback_data="menu_volatility")],
            [InlineKeyboardButton("💥 Boom/Crash Indices", callback_data="menu_boom_crash")],
            [InlineKeyboardButton("📈 Step Index", callback_data="menu_step")],
            [InlineKeyboardButton("🚀 Jump Indices", callback_data="menu_jump")],
            [InlineKeyboardButton("🔍 Scan All Signals", callback_data="scan_all")],
            [InlineKeyboardButton("📊 Bot Statistics", callback_data="show_stats")],
            [InlineKeyboardButton("❓ Help", callback_data="show_help")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user = update.effective_user
        db_manager.log_interaction(user.id, "help")
        
        help_message = """
📖 *Bot Help & Commands*

🔹 *Available Commands:*
• /start - Show main menu
• /scan - Scan all symbols for signals
• /stats - Show bot statistics
• /subscribe - Subscribe to notifications
• /help - Show this help message

🔹 *How to Use:*
1. Choose an asset category from the menu
2. Select a specific symbol
3. Get detailed signal analysis
4. Follow risk management guidelines

🔹 *Signal Strength:*
• 8-10/10: Strong signal ⭐⭐⭐
• 6-7/10: Good signal ⭐⭐
• 4-5/10: Weak signal ⭐
• 0-3/10: No signal

🔹 *Risk Management:*
• Always use stop loss
• Risk only 1% per trade
• Follow suggested position sizes

🔹 *Data Sources:*
• 📈 Live: Deriv MT5 connection
• 📊 Simulated: When MT5 unavailable

❓ *Need more help? Contact admin*
        """
        
        await update.message.reply_text(help_message, parse_mode="Markdown")
    
    async def handle_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command"""
        user = update.effective_user
        db_manager.log_interaction(user.id, "scan_all")
        
        await update.message.reply_text("🔍 *Scanning all symbols for strong signals...*", parse_mode="Markdown")
        
        try:
            signals = await signal_generator.get_best_signals()
            
            if not signals:
                await update.message.reply_text("📊 *No strong signals found at the moment.*\n\nTry again in a few minutes!", parse_mode="Markdown")
                return
            
            message = "🚀 *Strong Signals Found:*\n\n"
            
            for symbol, signal in list(signals.items())[:5]:  # Limit to top 5
                direction_emoji = "🟢" if signal['direction'] == 'bullish' else "🔴"
                simulated_tag = "📊" if signal['is_simulated'] else "📈"
                
                message += f"{direction_emoji} *{symbol}*\n"
                message += f"{simulated_tag} {signal['direction'].upper()} • {signal['strength']}/10\n"
                message += f"Entry: {signal['entry_price']} | SL: {signal['stop_loss']} | TP: {signal['take_profit']}\n"
                message += f"R:R 1:{signal['risk_reward_ratio']} | Size: {signal['position_size']} lots\n\n"
            
            message += "📊 *Use the menu for detailed analysis of any signal.*"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logging.error(f"Error in scan command: {e}")
            await update.message.reply_text("❌ *Error scanning signals. Please try again.*", parse_mode="Markdown")
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user = update.effective_user
        db_manager.log_interaction(user.id, "stats")
        
        try:
            stats = db_manager.get_signal_stats()
            user_stats = db_manager.get_user_stats(user.id)
            
            message = "📊 *Bot Statistics*\n\n"
            
            if stats:
                message += f"📈 *Total Signals:* {stats['total_signals']}\n"
                message += f"📊 *Live Signals:* {stats['live_signals']}\n"
                message += f"📈 *Simulated Signals:* {stats['simulated_signals']}\n"
                message += f"⭐ *Average Strength:* {stats['average_strength']}/10\n\n"
                
                if stats['direction_distribution']:
                    message += "📊 *Direction Distribution:*\n"
                    for direction, count in stats['direction_distribution'].items():
                        emoji = "🟢" if direction == 'bullish' else "🔴" if direction == 'bearish' else "🟡"
                        message += f"{emoji} {direction.title()}: {count}\n"
            
            if user_stats:
                message += f"\n👤 *Your Stats:*\n"
                message += f"🔍 *Interactions:* {user_stats['interaction_count']}\n"
                message += f"📅 *Last Active:* {user_stats['last_active'][:10] if user_stats['last_active'] else 'Never'}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logging.error(f"Error in stats command: {e}")
            await update.message.reply_text("❌ *Error loading statistics.*", parse_mode="Markdown")
    
    async def handle_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user = update.effective_user
        db_manager.log_interaction(user.id, "subscribe")
        
        message = """
📢 *Subscription Information*

🔹 *Free Features:*
• All signal analysis
• Manual scanning
• Bot statistics
• Risk management tools

🔹 *Premium Features (Coming Soon):*
• Real-time alerts
• Custom signal filters
• Advanced analytics
• Priority support

🔹 *Channel Alerts:*
Join our public channel for automatic 10/10 signal alerts!
📢 [Channel Link](https://t.me/your_channel)

💡 *Currently all features are FREE!*
        """
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        callback_data = query.data
        
        # Log interaction
        db_manager.log_interaction(user.id, "callback", callback_data)
        
        if callback_data == "menu_volatility":
            await self.show_volatility_menu(query)
        elif callback_data == "menu_boom_crash":
            await self.show_boom_crash_menu(query)
        elif callback_data == "menu_step":
            await self.show_step_menu(query)
        elif callback_data == "menu_jump":
            await self.show_jump_menu(query)
        elif callback_data == "scan_all":
            await self.handle_scan(update, context)
        elif callback_data == "show_stats":
            await self.handle_stats(update, context)
        elif callback_data == "show_help":
            await self.handle_help(update, context)
        elif callback_data.startswith("analyze_"):
            symbol = callback_data.replace("analyze_", "")
            await self.analyze_symbol(query, symbol)
        elif callback_data == "back_to_main":
            await self.handle_start(update, context)
    
    async def show_volatility_menu(self, query):
        """Show volatility indices menu"""
        symbols = signal_generator.symbols['Volatility']
        
        keyboard = []
        for symbol in symbols:
            keyboard.append([InlineKeyboardButton(symbol, callback_data=f"analyze_{symbol}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📊 *Volatility Indices*\n\nSelect a symbol to analyze:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def show_boom_crash_menu(self, query):
        """Show boom/crash indices menu"""
        symbols = signal_generator.symbols['Boom/Crash']
        
        keyboard = []
        for symbol in symbols:
            keyboard.append([InlineKeyboardButton(symbol, callback_data=f"analyze_{symbol}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💥 *Boom & Crash Indices*\n\nSelect a symbol to analyze:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def show_step_menu(self, query):
        """Show step index menu"""
        symbols = signal_generator.symbols['Step']
        
        keyboard = []
        for symbol in symbols:
            keyboard.append([InlineKeyboardButton(symbol, callback_data=f"analyze_{symbol}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📈 *Step Index*\n\nSelect a symbol to analyze:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def show_jump_menu(self, query):
        """Show jump indices menu"""
        symbols = signal_generator.symbols['Jump']
        
        keyboard = []
        for symbol in symbols:
            keyboard.append([InlineKeyboardButton(symbol, callback_data=f"analyze_{symbol}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🚀 *Jump Indices*\n\nSelect a symbol to analyze:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def analyze_symbol(self, query, symbol: str):
        """Analyze specific symbol"""
        await query.edit_message_text(f"🔍 *Analyzing {symbol}...*", parse_mode="Markdown")
        
        try:
            signal = await signal_generator.analyze_symbol(symbol)
            
            if not signal:
                await query.edit_message_text(
                    f"❌ *Unable to analyze {symbol}*\n\nPlease try again in a moment.",
                    parse_mode="Markdown"
                )
                return
            
            message = signal_generator.format_signal_message(signal)
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Save signal to database
            db_manager.save_signal(signal)
            
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            await query.edit_message_text(
                f"❌ *Error analyzing {symbol}*\n\nPlease try again later.",
                parse_mode="Markdown"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user = update.effective_user
        message_text = update.message.text.lower()
        
        db_manager.log_interaction(user.id, "message", details=message_text)
        
        # Simple responses
        if "hello" in message_text or "hi" in message_text:
            await update.message.reply_text("👋 Hello! Use /start to see the main menu.")
        elif "signal" in message_text:
            await self.handle_scan(update, context)
        elif "help" in message_text:
            await self.handle_help(update, context)
        else:
            await update.message.reply_text("🤔 Use /start to see available options.")
    
    def format_signal_message(self, signal: Dict) -> str:
        """Format signal for Telegram message"""
        try:
            direction_emoji = "🟢" if signal['direction'] == 'bullish' else "🔴" if signal['direction'] == 'bearish' else "🟡"
            simulated_tag = "📊 SIMULATED" if signal['is_simulated'] else "📈 LIVE"
            
            message = f"""
{direction_emoji} *{signal['symbol']}*
{simulated_tag} • Strength: {signal['strength']}/10

📊 *Signal Details:*
• Direction: {signal['direction'].upper()}
• Entry: {signal['entry_price']}
• Stop Loss: {signal['stop_loss']}
• Take Profit: {signal['take_profit']}
• Risk/Reward: 1:{signal['risk_reward_ratio']}

💰 *Risk Management:*
• Position Size: {signal['position_size']} lots
• Risk Amount: ${config.min_account_balance * (config.risk_percentage / 100):.2f}

📈 *Technical Analysis:*
• SMC FVGs: {signal['smc_analysis']['fvgs']}
• Order Blocks: {signal['smc_analysis']['order_blocks']}
• Liquidity Sweeps: {signal['smc_analysis']['sweeps']}
• ATR: {signal['atr']}

⏰ *Time: {signal['timestamp'].strftime('%H:%M:%S')}*
"""
            return message
            
        except Exception as e:
            logging.error(f"Error formatting signal message: {e}")
            return "❌ Error formatting signal message"
    
    async def broadcast_to_channel(self, message: str):
        """Broadcast message to public channel"""
        if not config.public_channel_id:
            logging.warning("No public channel ID configured")
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=config.public_channel_id,
                text=message,
                parse_mode="Markdown"
            )
            logging.info(f"Message broadcasted to channel: {config.public_channel_id}")
        except Exception as e:
            logging.error(f"Error broadcasting to channel: {e}")
    
    async def run(self):
        """Run the bot"""
        await self.application.initialize()
        await self.application.start()
        logging.info("Telegram bot started successfully")

# Global bot instance
telegram_bot = TelegramBot()
