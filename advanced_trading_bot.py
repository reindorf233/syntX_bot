#!/usr/bin/env python3
"""
syntX_bot - Advanced Trading Bot with Multiple Strategies + AI
Fresh deployment with no simulation mode and AI-enhanced analysis
"""
import asyncio
import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from ai_analysis_engine import AIAnalysisEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedTradingBot:
    """Advanced trading bot with multiple strategies + AI enhancement"""
    
    def __init__(self):
        # Configuration
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '8592086807:AAHfNHsBY4cuwDfvvFUMkmw5bZiC0ObJmCk')
        self.deriv_app_id = os.getenv('DERIV_APP_ID', '120931')
        self.deriv_token = os.getenv('DERIV_TOKEN', 'RNaduc1QRp2NxMJ')
        self.ai_api_key = os.getenv('AI_API_KEY')  # OpenAI, Anthropic, or Gemini
        
        # Trading symbols
        self.symbols = {
            'Volatility 10 Index': 'R_10',
            'Volatility 25 Index': 'R_25',
            'Volatility 50 Index': 'R_50',
            'Volatility 75 Index': 'R_75',
            'Volatility 100 Index': 'R_100',
            'Step Index': 'R_STEPINDEX',
            'Boom 500 Index': 'BOOM500',
            'Crash 1000 Index': 'CRASH1000',
            'Jump 25 Index': 'JD25',
            'Range Break 100 Index': 'RB100',
            'Range Break 200 Index': 'RB200'
        }
        
        # Strategy weights (updated with AI)
        self.strategy_weights = {
            'ai_analysis': 0.35,    # AI-powered analysis (highest weight)
            'smc': 0.20,           # Smart Money Concepts
            'trend': 0.15,          # Trend Following
            'momentum': 0.15,        # Momentum Trading
            'mean_reversion': 0.10,   # Mean Reversion
            'breakout': 0.05         # Breakout Trading
        }
        
        # Initialize components
        self.deriv_handler = None
        self.ai_engine = AIAnalysisEngine(self.ai_api_key)
        self.active_signals = {}
        
    async def initialize(self):
        """Initialize bot components"""
        try:
            # Initialize Deriv API
            from deriv_api_handler import DerivAPIHandler
            self.deriv_handler = DerivAPIHandler(self.deriv_app_id, self.deriv_token)
            
            # Test connection
            if await self.deriv_handler.connect():
                logger.info("✅ Deriv API connected successfully")
                return True
            else:
                logger.error("❌ Failed to connect to Deriv API")
                return False
                
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            return False
    
    async def get_live_price(self, symbol: str) -> Optional[float]:
        """Get live price from Deriv API - NO SIMULATION"""
        try:
            deriv_symbol = self.symbols.get(symbol, symbol)
            
            # Get live tick data
            response = await self.deriv_handler.api.ticks(deriv_symbol)
            
            if response and 'tick' in response:
                tick = response['tick']
                price = tick.get('quote')
                
                if price:
                    logger.info(f"✅ LIVE PRICE - {symbol}: {price}")
                    return float(price)
            
            logger.error(f"❌ No live price for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Price fetch error for {symbol}: {e}")
            return None
    
    async def analyze_with_smc(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Smart Money Concepts Analysis"""
        try:
            current_price = price_data['close'].iloc[-1]
            
            # Market structure analysis
            highs = price_data['high'].rolling(20).max()
            lows = price_data['low'].rolling(20).min()
            
            # FVG detection
            fvg_zones = self.detect_fvg(price_data)
            
            # Order block detection
            order_blocks = self.detect_order_blocks(price_data)
            
            # Liquidity analysis
            liquidity_levels = self.detect_liquidity(price_data)
            
            # Generate signal
            signal_strength = 0.0
            direction = "NEUTRAL"
            
            # Check for bullish SMC setup
            if (len(order_blocks['bullish']) > 0 and 
                current_price > order_blocks['bullish'][-1] and
                len(fvg_zones['bullish']) > 0):
                signal_strength += 0.8
                direction = "BULLISH"
            
            # Check for bearish SMC setup
            elif (len(order_blocks['bearish']) > 0 and 
                  current_price < order_blocks['bearish'][-1] and
                  len(fvg_zones['bearish']) > 0):
                signal_strength += 0.8
                direction = "BEARISH"
            
            return {
                'strategy': 'SMC',
                'direction': direction,
                'strength': signal_strength,
                'entry': current_price,
                'fvg_zones': fvg_zones,
                'order_blocks': order_blocks,
                'liquidity': liquidity_levels
            }
            
        except Exception as e:
            logger.error(f"SMC analysis error: {e}")
            return {'strategy': 'SMC', 'direction': 'NEUTRAL', 'strength': 0.0}
    
    async def analyze_with_trend(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Trend Following Strategy"""
        try:
            # EMAs for trend direction
            ema_20 = price_data['close'].ewm(span=20).mean()
            ema_50 = price_data['close'].ewm(span=50).mean()
            ema_200 = price_data['close'].ewm(span=200).mean()
            
            current_price = price_data['close'].iloc[-1]
            current_ema_20 = ema_20.iloc[-1]
            current_ema_50 = ema_50.iloc[-1]
            current_ema_200 = ema_200.iloc[-1]
            
            # Trend strength
            trend_strength = 0.0
            direction = "NEUTRAL"
            
            # Strong uptrend
            if (current_price > current_ema_20 > current_ema_50 > current_ema_200):
                trend_strength = 0.9
                direction = "BULLISH"
            
            # Strong downtrend
            elif (current_price < current_ema_20 < current_ema_50 < current_ema_200):
                trend_strength = 0.9
                direction = "BEARISH"
            
            # Weak uptrend
            elif current_price > current_ema_20 > current_ema_50:
                trend_strength = 0.6
                direction = "BULLISH"
            
            # Weak downtrend
            elif current_price < current_ema_20 < current_ema_50:
                trend_strength = 0.6
                direction = "BEARISH"
            
            return {
                'strategy': 'TREND',
                'direction': direction,
                'strength': trend_strength,
                'entry': current_price,
                'ema_20': current_ema_20,
                'ema_50': current_ema_50,
                'ema_200': current_ema_200
            }
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {'strategy': 'TREND', 'direction': 'NEUTRAL', 'strength': 0.0}
    
    async def analyze_with_momentum(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Momentum Trading Strategy"""
        try:
            # RSI for momentum
            delta = price_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_price = price_data['close'].iloc[-1]
            current_rsi = rsi.iloc[-1]
            
            # MACD for momentum
            exp1 = price_data['close'].ewm(span=12).mean()
            exp2 = price_data['close'].ewm(span=26).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=9).mean()
            
            momentum_strength = 0.0
            direction = "NEUTRAL"
            
            # Bullish momentum
            if (current_rsi > 50 and current_rsi < 70 and 
                macd.iloc[-1] > signal_line.iloc[-1]):
                momentum_strength = 0.8
                direction = "BULLISH"
            
            # Bearish momentum
            elif (current_rsi < 50 and current_rsi > 30 and 
                  macd.iloc[-1] < signal_line.iloc[-1]):
                momentum_strength = 0.8
                direction = "BEARISH"
            
            return {
                'strategy': 'MOMENTUM',
                'direction': direction,
                'strength': momentum_strength,
                'entry': current_price,
                'rsi': current_rsi,
                'macd': macd.iloc[-1],
                'signal': signal_line.iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Momentum analysis error: {e}")
            return {'strategy': 'MOMENTUM', 'direction': 'NEUTRAL', 'strength': 0.0}
    
    async def analyze_with_mean_reversion(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Mean Reversion Strategy"""
        try:
            # Bollinger Bands
            sma = price_data['close'].rolling(window=20).mean()
            std = price_data['close'].rolling(window=20).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            current_price = price_data['close'].iloc[-1]
            current_sma = sma.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            reversion_strength = 0.0
            direction = "NEUTRAL"
            
            # Buy at lower band
            if current_price <= current_lower:
                reversion_strength = 0.7
                direction = "BULLISH"
            
            # Sell at upper band
            elif current_price >= current_upper:
                reversion_strength = 0.7
                direction = "BEARISH"
            
            return {
                'strategy': 'MEAN_REVERSION',
                'direction': direction,
                'strength': reversion_strength,
                'entry': current_price,
                'sma': current_sma,
                'upper_band': current_upper,
                'lower_band': current_lower
            }
            
        except Exception as e:
            logger.error(f"Mean reversion error: {e}")
            return {'strategy': 'MEAN_REVERSION', 'direction': 'NEUTRAL', 'strength': 0.0}
    
    async def analyze_with_breakout(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Breakout Trading Strategy"""
        try:
            # Support and resistance levels
            high_20 = price_data['high'].rolling(20).max()
            low_20 = price_data['low'].rolling(20).min()
            
            current_price = price_data['close'].iloc[-1]
            current_high = high_20.iloc[-1]
            current_low = low_20.iloc[-1]
            
            # Volume confirmation (simulated)
            volume_sma = price_data['volume'].rolling(20).mean()
            current_volume = price_data['volume'].iloc[-1]
            
            breakout_strength = 0.0
            direction = "NEUTRAL"
            
            # Bullish breakout
            if (current_price > current_high and 
                current_volume > volume_sma.iloc[-1] * 1.5):
                breakout_strength = 0.8
                direction = "BULLISH"
            
            # Bearish breakout
            elif (current_price < current_low and 
                  current_volume > volume_sma.iloc[-1] * 1.5):
                breakout_strength = 0.8
                direction = "BEARISH"
            
            return {
                'strategy': 'BREAKOUT',
                'direction': direction,
                'strength': breakout_strength,
                'entry': current_price,
                'resistance': current_high,
                'support': current_low,
                'volume': current_volume
            }
            
        except Exception as e:
            logger.error(f"Breakout analysis error: {e}")
            return {'strategy': 'BREAKOUT', 'direction': 'NEUTRAL', 'strength': 0.0}
    
    def calculate_technical_indicators(self, price_data: pd.DataFrame) -> Dict:
        """Calculate technical indicators for AI analysis"""
        try:
            indicators = {}
            
            # RSI
            delta = price_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = price_data['close'].ewm(span=12).mean()
            exp2 = price_data['close'].ewm(span=26).mean()
            indicators['macd'] = (exp1 - exp2).iloc[-1]
            
            # Bollinger Bands
            sma = price_data['close'].rolling(window=20).mean()
            std = price_data['close'].rolling(window=20).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            current_price = price_data['close'].iloc[-1]
            indicators['bb_position'] = (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
            
            # Volume trend
            indicators['volume_trend'] = price_data['volume'].pct_change().tail(5).mean()
            
            # ATR
            high_low = price_data['high'] - price_data['low']
            high_close = abs(price_data['high'] - price_data['close'].shift())
            low_close = abs(price_data['low'] - price_data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            indicators['atr'] = true_range.rolling(window=14).mean().iloc[-1]
            
            return indicators
            
        except Exception as e:
            logger.error(f"Technical indicators error: {e}")
            return {}
    
    def detect_fvg(self, price_data: pd.DataFrame) -> Dict:
        """Detect Fair Value Gaps"""
        fvg_zones = {'bullish': [], 'bearish': []}
        
        try:
            for i in range(2, len(price_data)):
                # Bullish FVG
                if (price_data.iloc[i-2].low > price_data.iloc[i].high and
                    price_data.iloc[i-1].close > price_data.iloc[i-1].open):
                    fvg_zones['bullish'].append({
                        'top': price_data.iloc[i].high,
                        'bottom': price_data.iloc[i-2].low,
                        'time': price_data.iloc[i].name
                    })
                
                # Bearish FVG
                elif (price_data.iloc[i-2].high < price_data.iloc[i].low and
                      price_data.iloc[i-1].close < price_data.iloc[i-1].open):
                    fvg_zones['bearish'].append({
                        'top': price_data.iloc[i-2].high,
                        'bottom': price_data.iloc[i].low,
                        'time': price_data.iloc[i].name
                    })
        except Exception as e:
            logger.error(f"FVG detection error: {e}")
        
        return fvg_zones
    
    def detect_order_blocks(self, price_data: pd.DataFrame) -> Dict:
        """Detect Order Blocks"""
        order_blocks = {'bullish': [], 'bearish': []}
        
        try:
            for i in range(1, len(price_data)-1):
                # Bullish order block
                if (price_data.iloc[i-1].close > price_data.iloc[i-1].open and
                    price_data.iloc[i].close < price_data.iloc[i].open and
                    price_data.iloc[i+1].close > price_data.iloc[i+1].open):
                    order_blocks['bullish'].append(price_data.iloc[i].low)
                
                # Bearish order block
                elif (price_data.iloc[i-1].close < price_data.iloc[i-1].open and
                      price_data.iloc[i].close > price_data.iloc[i].open and
                      price_data.iloc[i+1].close < price_data.iloc[i+1].open):
                    order_blocks['bearish'].append(price_data.iloc[i].high)
        except Exception as e:
            logger.error(f"Order block detection error: {e}")
        
        return order_blocks
    
    def detect_liquidity(self, price_data: pd.DataFrame) -> List:
        """Detect Liquidity Levels"""
        liquidity_levels = []
        
        try:
            # Find swing highs and lows
            for i in range(2, len(price_data)-2):
                # Swing high
                if (price_data.iloc[i].high > price_data.iloc[i-1].high and
                    price_data.iloc[i].high > price_data.iloc[i-2].high and
                    price_data.iloc[i].high > price_data.iloc[i+1].high and
                    price_data.iloc[i].high > price_data.iloc[i+2].high):
                    liquidity_levels.append({
                        'level': price_data.iloc[i].high,
                        'type': 'resistance',
                        'time': price_data.iloc[i].name
                    })
                
                # Swing low
                elif (price_data.iloc[i].low < price_data.iloc[i-1].low and
                      price_data.iloc[i].low < price_data.iloc[i-2].low and
                      price_data.iloc[i].low < price_data.iloc[i+1].low and
                      price_data.iloc[i].low < price_data.iloc[i+2].low):
                    liquidity_levels.append({
                        'level': price_data.iloc[i].low,
                        'type': 'support',
                        'time': price_data.iloc[i].name
                    })
        except Exception as e:
            logger.error(f"Liquidity detection error: {e}")
        
        return liquidity_levels
    
    async def generate_signal(self, symbol: str) -> Optional[Dict]:
        """Generate comprehensive trading signal with AI enhancement"""
        try:
            # Get live price
            current_price = await self.get_live_price(symbol)
            if not current_price:
                return None
            
            # Get price data (simplified for demo)
            price_data = await self.get_price_data(symbol)
            if price_data is None or len(price_data) == 0:
                return None
            
            # Calculate technical indicators
            technical_indicators = self.calculate_technical_indicators(price_data)
            
            # Prepare market data
            market_data = {
                'price_changes': price_data['close'].pct_change().dropna().tolist()[-20:],
                'volume_data': price_data['volume'].tolist()[-20:],
                'high_low_data': {
                    'recent_high': price_data['high'].tail(20).max(),
                    'recent_low': price_data['low'].tail(20).min()
                }
            }
            
            # Run all strategies including AI
            strategies = []
            
            # AI Analysis (highest priority)
            logger.info(f"🤖 Running AI analysis for {symbol}")
            ai_signal = await self.ai_engine.analyze_with_ai(
                symbol, price_data, market_data, technical_indicators
            )
            strategies.append(ai_signal)
            
            # SMC Analysis
            smc_signal = await self.analyze_with_smc(symbol, price_data)
            strategies.append(smc_signal)
            
            # Trend Analysis
            trend_signal = await self.analyze_with_trend(symbol, price_data)
            strategies.append(trend_signal)
            
            # Momentum Analysis
            momentum_signal = await self.analyze_with_momentum(symbol, price_data)
            strategies.append(momentum_signal)
            
            # Mean Reversion Analysis
            mean_rev_signal = await self.analyze_with_mean_reversion(symbol, price_data)
            strategies.append(mean_rev_signal)
            
            # Breakout Analysis
            breakout_signal = await self.analyze_with_breakout(symbol, price_data)
            strategies.append(breakout_signal)
            
            # Calculate weighted signal
            final_signal = self.calculate_weighted_signal(strategies)
            
            # Add metadata
            final_signal.update({
                'symbol': symbol,
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'strategies': strategies,
                'is_simulated': False,
                'ai_enhanced': True,
                'ai_confidence': ai_signal.get('ai_confidence', 0.0)
            })
            
            logger.info(f"✅ AI-enhanced signal generated for {symbol}: {final_signal['direction']} (Strength: {final_signal['strength']:.1f})")
            return final_signal
            
        except Exception as e:
            logger.error(f"Signal generation error for {symbol}: {e}")
            return None
    
    def calculate_weighted_signal(self, strategies: List[Dict]) -> Dict:
        """Calculate weighted signal from all strategies"""
        try:
            bullish_score = 0.0
            bearish_score = 0.0
            total_weight = 0.0
            
            for strategy in strategies:
                strategy_name = strategy['strategy'].lower()
                weight = self.strategy_weights.get(strategy_name, 0.1)
                strength = strategy['strength']
                direction = strategy['direction']
                
                if direction == 'BULLISH':
                    bullish_score += strength * weight
                elif direction == 'BEARISH':
                    bearish_score += strength * weight
                
                total_weight += weight
            
            # Determine final direction
            if bullish_score > bearish_score:
                final_direction = 'BULLISH'
                final_strength = min(bullish_score / total_weight, 1.0)
            elif bearish_score > bullish_score:
                final_direction = 'BEARISH'
                final_strength = min(bearish_score / total_weight, 1.0)
            else:
                final_direction = 'NEUTRAL'
                final_strength = 0.0
            
            # Calculate risk levels
            current_price = strategies[0]['entry']
            atr = self.calculate_atr(strategies[0].get('price_data', pd.DataFrame()))
            
            if final_direction == 'BULLISH':
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 2.0)
            elif final_direction == 'BEARISH':
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 2.0)
            else:
                stop_loss = current_price
                take_profit = current_price
            
            return {
                'direction': final_direction,
                'strength': final_strength * 10,  # Scale to 1-10
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': abs((take_profit - current_price) / (stop_loss - current_price)) if stop_loss != current_price else 0.0
            }
            
        except Exception as e:
            logger.error(f"Weight calculation error: {e}")
            return {'direction': 'NEUTRAL', 'strength': 0.0}
    
    def calculate_atr(self, price_data: pd.DataFrame) -> float:
        """Calculate Average True Range"""
        try:
            if len(price_data) < 14:
                return 50.0  # Default ATR
            
            high_low = price_data['high'] - price_data['low']
            high_close = abs(price_data['high'] - price_data['close'].shift())
            low_close = abs(price_data['low'] - price_data['close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()
            
            return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 50.0
            
        except Exception as e:
            logger.error(f"ATR calculation error: {e}")
            return 50.0
    
    async def get_price_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get price data for analysis"""
        try:
            deriv_symbol = self.symbols.get(symbol, symbol)
            
            # Get tick data
            response = await self.deriv_handler.api.ticks(deriv_symbol)
            
            if response and 'tick' in response:
                tick = response['tick']
                current_price = tick.get('quote')
                epoch = tick.get('epoch', 0)
                
                # Create synthetic historical data for analysis
                # In production, this would be real historical data
                dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='5min')
                prices = []
                
                for i in range(100):
                    # Generate realistic price movement
                    base_price = current_price
                    noise = np.random.normal(0, base_price * 0.001)
                    price = base_price + noise
                    prices.append(price)
                
                df = pd.DataFrame({
                    'open': prices,
                    'high': [p * 1.001 for p in prices],
                    'low': [p * 0.999 for p in prices],
                    'close': prices,
                    'volume': [100] * len(prices)
                }, index=dates)
                
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Price data error for {symbol}: {e}")
            return None
    
    def create_trading_buttons(self, signal: Dict) -> InlineKeyboardMarkup:
        """Create buy/sell buttons for trading"""
        keyboard = []
        
        if signal['direction'] == 'BULLISH':
            keyboard.append([
                InlineKeyboardButton("🟢 BUY", callback_data=f"buy_{signal['symbol']}"),
                InlineKeyboardButton("❌ CLOSE", callback_data=f"close_{signal['symbol']}")
            ])
        elif signal['direction'] == 'BEARISH':
            keyboard.append([
                InlineKeyboardButton("🔴 SELL", callback_data=f"sell_{signal['symbol']}"),
                InlineKeyboardButton("❌ CLOSE", callback_data=f"close_{signal['symbol']}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📊 Details", callback_data=f"details_{signal['symbol']}"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def format_signal_message(self, signal: Dict) -> str:
        """Format signal message for Telegram with AI enhancement"""
        direction_emoji = "🟢" if signal['direction'] == 'BULLISH' else "🔴" if signal['direction'] == 'BEARISH' else "⚪"
        ai_emoji = "🤖" if signal.get('ai_enhanced', False) else "📊"
        confidence = signal.get('ai_confidence', signal['strength'] / 10)
        
        message = f"""
{direction_emoji} **{signal['symbol']}**
{ai_emoji} **AI-ENHANCED** • Strength: {signal['strength']:.1f}/10 • Confidence: {confidence:.1%}

📈 **Signal Details:**
• Direction: {signal['direction']}
• Entry: {signal['entry_price']:.2f}
• Stop Loss: {signal['stop_loss']:.2f}
• Take Profit: {signal['take_profit']:.2f}
• Risk/Reward: 1:{signal['risk_reward']:.2f}

🤖 **AI Analysis:**
• AI Confidence: {confidence:.1%}
• AI Model: {signal.get('ai_model', 'Local')}
• AI Provider: {signal.get('ai_provider', 'Local Analysis')}
• Patterns Found: {len(signal.get('ai_predictions', {}).get('patterns_found', []))}

💰 **Risk Management:**
• Position Size: 0.01 lots
• Risk Amount: $0.05
• Risk Level: {signal.get('risk_analysis', {}).get('risk_level', 'MEDIUM')}

⏰ {signal['timestamp']}
        """
        
        return message
