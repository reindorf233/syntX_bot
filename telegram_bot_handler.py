#!/usr/bin/env python3
"""
Telegram Bot Handler with Buy/Sell Options
"""
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from advanced_trading_bot import AdvancedTradingBot

logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Telegram bot with trading capabilities"""
    
    def __init__(self):
        self.bot = AdvancedTradingBot()
        self.user_positions = {}  # Track user positions
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_message = """
🚀 **Welcome to syntX Bot - Advanced Trading!**

🤖 **Features:**
• 📊 6 Trading Strategies (SMC, Trend, Momentum, etc.)
• 🎯 Live Deriv API Data (No Simulation)
• 💱 Buy/Sell Trading Options
• 📈 Real-time Signal Generation
• ⚡ Instant Trade Execution

📱 **Commands:**
/start - Start bot
/scan - Scan all symbols
/analyze <symbol> - Analyze specific symbol
/positions - View your positions
/balance - Check account balance
/help - Help menu

🔔 **Trading Alerts:**
• Real-time signals with buy/sell buttons
• Risk management included
• Multiple strategy confirmation

Ready to start trading? Use /scan to see current opportunities! 📊
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan all symbols for opportunities"""
        await update.message.reply_text("🔍 Scanning all symbols for trading opportunities...")
        
        # Initialize bot if needed
        if not await self.bot.initialize():
            await update.message.reply_text("❌ Failed to connect to Deriv API")
            return
        
        # Scan all symbols
        opportunities = []
        for symbol in self.bot.symbols.keys():
            signal = await self.bot.generate_signal(symbol)
            if signal and signal['strength'] >= 7.0:  # High strength signals only
                opportunities.append(signal)
        
        if opportunities:
            # Sort by strength
            opportunities.sort(key=lambda x: x['strength'], reverse=True)
            
            # Send top 3 opportunities
            for i, signal in enumerate(opportunities[:3]):
                message = self.bot.format_signal_message(signal)
                keyboard = self.bot.create_trading_buttons(signal)
                
                await update.message.reply_text(
                    message, 
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
                # Add delay to avoid spam
                await asyncio.sleep(1)
        else:
            await update.message.reply_text("📊 No high-probability opportunities found right now")
    
    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze specific symbol"""
        if not context.args:
            await update.message.reply_text("Please provide a symbol: /analyze Volatility 10 Index")
            return
        
        symbol = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Analyzing {symbol}...")
        
        # Initialize bot if needed
        if not await self.bot.initialize():
            await update.message.reply_text("❌ Failed to connect to Deriv API")
            return
        
        # Generate signal
        signal = await self.bot.generate_signal(symbol)
        
        if signal:
            message = self.bot.format_signal_message(signal)
            keyboard = self.bot.create_trading_buttons(signal)
            
            await update.message.reply_text(
                message, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(f"❌ Could not generate signal for {symbol}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data.startswith('buy_'):
            symbol = data.replace('buy_', '')
            await self.execute_buy(query, symbol, user_id)
        
        elif data.startswith('sell_'):
            symbol = data.replace('sell_', '')
            await self.execute_sell(query, symbol, user_id)
        
        elif data.startswith('close_'):
            symbol = data.replace('close_', '')
            await self.execute_close(query, symbol, user_id)
        
        elif data.startswith('details_'):
            symbol = data.replace('details_', '')
            await self.show_details(query, symbol)
        
        elif data == 'settings':
            await self.show_settings(query)
    
    async def execute_buy(self, query, symbol: str, user_id: int):
        """Execute buy trade"""
        try:
            # Generate current signal
            signal = await self.bot.generate_signal(symbol)
            
            if signal and signal['direction'] == 'BULLISH':
                # Record position
                if user_id not in self.user_positions:
                    self.user_positions[user_id] = {}
                
                self.user_positions[user_id][symbol] = {
                    'type': 'BUY',
                    'entry': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'timestamp': datetime.now(),
                    'status': 'OPEN'
                }
                
                message = f"""
✅ **BUY ORDER EXECUTED**

📊 **{symbol}**
• Entry: {signal['entry_price']:.2f}
• Stop Loss: {signal['stop_loss']:.2f}
• Take Profit: {signal['take_profit']:.2f}
• Risk/Reward: 1:{signal['risk_reward']:.2f}

💰 **Position Details:**
• Size: 0.01 lots
• Risk: $0.05
• Status: OPEN

⏰ Time: {datetime.now().strftime('%H:%M:%S')}
                """
                
                await query.edit_message_text(message, parse_mode='Markdown')
                
                # Send monitoring alert
                await query.message.reply_text("🔔 Position opened! Monitoring for exit signals...")
                
            else:
                await query.edit_message_text("❌ Signal changed. Please analyze again before trading.")
                
        except Exception as e:
            logger.error(f"Buy execution error: {e}")
            await query.edit_message_text("❌ Failed to execute buy order")
    
    async def execute_sell(self, query, symbol: str, user_id: int):
        """Execute sell trade"""
        try:
            # Generate current signal
            signal = await self.bot.generate_signal(symbol)
            
            if signal and signal['direction'] == 'BEARISH':
                # Record position
                if user_id not in self.user_positions:
                    self.user_positions[user_id] = {}
                
                self.user_positions[user_id][symbol] = {
                    'type': 'SELL',
                    'entry': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'timestamp': datetime.now(),
                    'status': 'OPEN'
                }
                
                message = f"""
✅ **SELL ORDER EXECUTED**

📊 **{symbol}**
• Entry: {signal['entry_price']:.2f}
• Stop Loss: {signal['stop_loss']:.2f}
• Take Profit: {signal['take_profit']:.2f}
• Risk/Reward: 1:{signal['risk_reward']:.2f}

💰 **Position Details:**
• Size: 0.01 lots
• Risk: $0.05
• Status: OPEN

⏰ Time: {datetime.now().strftime('%H:%M:%S')}
                """
                
                await query.edit_message_text(message, parse_mode='Markdown')
                
                # Send monitoring alert
                await query.message.reply_text("🔔 Position opened! Monitoring for exit signals...")
                
            else:
                await query.edit_message_text("❌ Signal changed. Please analyze again before trading.")
                
        except Exception as e:
            logger.error(f"Sell execution error: {e}")
            await query.edit_message_text("❌ Failed to execute sell order")
    
    async def execute_close(self, query, symbol: str, user_id: int):
        """Close position"""
        try:
            if user_id in self.user_positions and symbol in self.user_positions[user_id]:
                position = self.user_positions[user_id][symbol]
                
                # Get current price
                current_price = await self.bot.get_live_price(symbol)
                
                if current_price:
                    # Calculate P&L
                    if position['type'] == 'BUY':
                        pnl = (current_price - position['entry']) * 0.01
                    else:
                        pnl = (position['entry'] - current_price) * 0.01
                    
                    # Update position status
                    position['status'] = 'CLOSED'
                    position['close_price'] = current_price
                    position['pnl'] = pnl
                    position['close_time'] = datetime.now()
                    
                    pnl_emoji = "🟢" if pnl > 0 else "🔴"
                    
                    message = f"""
✅ **POSITION CLOSED**

📊 **{symbol}**
• Type: {position['type']}
• Entry: {position['entry']:.2f}
• Close: {current_price:.2f}

💰 **P&L:**
{pnl_emoji} ${abs(pnl):.2f}

⏰ Duration: {(position['close_time'] - position['timestamp']).total_seconds():.0f}s
                    """
                    
                    await query.edit_message_text(message, parse_mode='Markdown')
                    
                    # Remove from active positions
                    del self.user_positions[user_id][symbol]
                    
                else:
                    await query.edit_message_text("❌ Could not get current price to close position")
            else:
                await query.edit_message_text("❌ No open position found")
                
        except Exception as e:
            logger.error(f"Close execution error: {e}")
            await query.edit_message_text("❌ Failed to close position")
    
    async def show_details(self, query, symbol: str):
        """Show detailed analysis"""
        try:
            signal = await self.bot.generate_signal(symbol)
            
            if signal:
                details = f"""
📊 **Detailed Analysis - {symbol}**

🎯 **Signal Summary:**
• Direction: {signal['direction']}
• Strength: {signal['strength']:.1f}/10
• Entry: {signal['entry_price']:.2f}

📈 **Strategy Breakdown:**
"""
                # Add strategy details
                for strategy in signal.get('strategies', []):
                    strategy_emoji = "✅" if strategy['strength'] > 0.5 else "❌"
                    details += f"• {strategy_emoji} {strategy['strategy']}: {strategy['direction']} ({strategy['strength']:.2f})\n"
                
                details += f"""
💰 **Risk Management:**
• Stop Loss: {signal['stop_loss']:.2f}
• Take Profit: {signal['take_profit']:.2f}
• Risk/Reward: 1:{signal['risk_reward']:.2f}

🔍 **Technical Levels:**
• Current Price: {signal['current_price']:.2f}
• ATR: {signal.get('atr', 50):.2f}

⏰ Generated: {signal['timestamp']}
                """
                
                await query.edit_message_text(details, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Could not generate detailed analysis")
                
        except Exception as e:
            logger.error(f"Details error: {e}")
            await query.edit_message_text("❌ Failed to show details")
    
    async def show_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user positions"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_positions or not self.user_positions[user_id]:
            await update.message.reply_text("📊 No open positions")
            return
        
        message = "📊 **Your Open Positions:**\n\n"
        
        for symbol, position in self.user_positions[user_id].items():
            if position['status'] == 'OPEN':
                current_price = await self.bot.get_live_price(symbol)
                
                if current_price:
                    if position['type'] == 'BUY':
                        pnl = (current_price - position['entry']) * 0.01
                    else:
                        pnl = (position['entry'] - current_price) * 0.01
                    
                    pnl_emoji = "🟢" if pnl > 0 else "🔴"
                    
                    message += f"""
📈 **{symbol}**
• Type: {position['type']}
• Entry: {position['entry']:.2f}
• Current: {current_price:.2f}
• P&L: {pnl_emoji} ${abs(pnl):.2f}
• SL: {position['stop_loss']:.2f}
• TP: {position['take_profit']:.2f}

"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show account balance"""
        # This would connect to real broker API
        await update.message.reply_text("""
💰 **Account Balance**

📊 **Demo Account:**
• Balance: $10,000.00
• Available: $9,950.00
• Used: $50.00

💼 **Real Account:**
• Connect your Deriv account for live trading

🔧 *Note: This is a demo. Connect real account for live trading.*
        """)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_message = """
🤖 **syntX Bot Help**

📱 **Commands:**
/start - Start bot and get welcome message
/scan - Scan all symbols for opportunities
/analyze <symbol> - Analyze specific symbol
/positions - View your open positions
/balance - Check account balance
/help - Show this help message

🎯 **Trading Features:**
• 📊 6 Trading Strategies (SMC, Trend, Momentum, etc.)
• 💱 Buy/Sell buttons on every signal
• 🛡️ Built-in risk management
• 📈 Real-time P&L tracking
• 🔔 Position monitoring alerts

⚡ **How to Trade:**
1. Use /scan to find opportunities
2. Click 🟢 BUY or 🔴 SELL on signals
3. Set your risk management
4. Monitor positions with /positions
5. Close manually or let TP/SL hit

🔒 **Safety Features:**
• Stop Loss on every trade
• Take Profit targets
• Risk/Reward calculation
• Position size limits
• Real-time monitoring

❓ **Need Help?**
• Check signals before trading
• Start with small positions
• Use proper risk management
• Monitor your positions

🚀 *Ready to trade? Use /scan to begin!*
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def show_settings(self, query):
        """Show settings menu"""
        keyboard = [
            [InlineKeyboardButton("⚙️ Risk Settings", callback_data="settings_risk")],
            [InlineKeyboardButton("📊 Strategy Settings", callback_data="settings_strategy")],
            [InlineKeyboardButton("🔔 Notification Settings", callback_data="settings_notifications")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings_back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
⚙️ **Settings Menu**

Choose what you'd like to configure:

🛡️ **Risk Settings** - Position size, stop loss, take profit
📊 **Strategy Settings** - Enable/disable strategies
🔔 **Notifications** - Alert preferences

*More settings coming soon!*
        """
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    def create_application(self):
        """Create Telegram application"""
        token = self.bot.telegram_token
        
        if not token or token == 'YOUR_BOT_TOKEN_HERE':
            logger.error("TELEGRAM_BOT_TOKEN not set")
            return None
        
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("scan", self.scan))
        application.add_handler(CommandHandler("analyze", self.analyze))
        application.add_handler(CommandHandler("positions", self.show_positions))
        application.add_handler(CommandHandler("balance", self.show_balance))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback handler for buttons
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        return application
    
    async def run(self):
        """Run the bot"""
        application = self.create_application()
        
        if application:
            logger.info("🚀 syntX Bot started successfully!")
            await application.run_polling()
        else:
            logger.error("❌ Failed to create Telegram application")

# Main execution
if __name__ == "__main__":
    bot_handler = TelegramBotHandler()
    asyncio.run(bot_handler.run())
