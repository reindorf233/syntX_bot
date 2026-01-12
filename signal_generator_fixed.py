import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from config import config
from deriv_api_handler import DerivAPIHandler
from technical_analyzer import technical_analyzer

class SignalGenerator:
    def __init__(self):
        self.symbols = {
            'Volatility': [
                'Volatility 10 Index',
                'Volatility 25 Index', 
                'Volatility 50 Index',
                'Volatility 75 Index',
                'Volatility 100 Index'
            ],
            'Boom/Crash': [
                'Boom 500 Index',
                'Boom 1000 Index',
                'Crash 500 Index', 
                'Crash 1000 Index'
            ],
            'Step': [
                'Step Index'
            ],
            'Jump': [
                'Jump 25 Index',
                'Jump 50 Index',
                'Jump 75 Index', 
                'Jump 100 Index'
            ]
        }
        
        # Initialize Deriv API handler
        self.deriv_handler = DerivAPIHandler(
            config.deriv_app_id, 
            config.deriv_token
        )
        
        # Symbol mapping for Deriv API
        self.deriv_symbols = {
            'Volatility 10 Index': 'R_10',
            'Volatility 25 Index': 'R_25',
            'Volatility 50 Index': 'R_50',
            'Volatility 75 Index': 'R_75',
            'Volatility 100 Index': 'R_100',
            'Boom 500 Index': 'BOOM500',
            'Boom 1000 Index': 'BOOM1000',
            'Crash 500 Index': 'CRASH500',
            'Crash 1000 Index': 'CRASH1000',
            'Step Index': 'R_STEPINDEX',  # Fixed: Use R_ prefix for Deriv API
            'Jump 25 Index': 'R_JUMPM25',
            'Jump 50 Index': 'R_JUMPM50',
            'Jump 75 Index': 'R_JUMPM75',
            'Jump 100 Index': 'R_JUMPM100'
        }
    
    async def fetch_data(self, symbol: str, timeframe: str = None, count: int = None) -> Optional[pd.DataFrame]:
        """Fetch data from Deriv API with fallback to simulation"""
        if timeframe is None:
            timeframe = config.timeframe
        if count is None:
            count = config.bars_count
        
        # Get Deriv symbol name
        deriv_symbol = self.deriv_symbols.get(symbol, symbol)
        
        # Try Deriv API first
        try:
            if await self.deriv_handler.connect():
                data = await self.deriv_handler.get_ohlc(deriv_symbol, timeframe, count)
                if data is not None and len(data) > 0:
                    logging.info(f"Successfully fetched Deriv data for {symbol}")
                    return data
                else:
                    logging.warning(f"Deriv API returned no data for {symbol}")
            else:
                logging.warning("Deriv API connection failed")
        except Exception as e:
            logging.error(f"Deriv API data fetch failed for {symbol}: {e}")
        
        # Fallback to simulation
        return await self.simulate_data(symbol, count)
    
    async def simulate_data(self, symbol: str, count: int = 100) -> Optional[pd.DataFrame]:
        """Generate simulated data when API is unavailable"""
        try:
            # Get realistic base prices for each symbol type
            base_prices = {
                # Volatility indices - realistic ranges
                'Volatility 10 Index': 5750,
                'Volatility 25 Index': 5750,
                'Volatility 50 Index': 5750,
                'Volatility 75 Index': 5750,
                'Volatility 100 Index': 5750,
                
                # Boom/Crash indices - realistic ranges
                'Boom 500 Index': 1500,
                'Boom 1000 Index': 1500,
                'Crash 500 Index': 1500,
                'Crash 1000 Index': 1500,
                
                # Step Index - realistic range
                'Step Index': 1500,
                
                # Jump indices - realistic ranges
                'Jump 25 Index': 5750,
                'Jump 50 Index': 5750,
                'Jump 75 Index': 5750,
                'Jump 100 Index': 5750
            }
            
            base_price = base_prices.get(symbol, 1000)
            
            # Generate realistic price movement
            np.random.seed(42)  # For consistent testing
            
            # Different volatility for different symbol types
            if 'Volatility' in symbol:
                volatility = base_price * 0.02  # 2% volatility
            elif 'Boom' in symbol or 'Crash' in symbol:
                volatility = base_price * 0.05  # 5% volatility (more volatile)
            elif 'Step' in symbol:
                volatility = base_price * 0.01  # 1% volatility (less volatile)
            elif 'Jump' in symbol:
                volatility = base_price * 0.03  # 3% volatility
            else:
                volatility = base_price * 0.02  # Default 2%
            
            # Generate price series
            dates = pd.date_range(end=pd.Timestamp.now(), periods=count, freq='5min')
            
            # Random walk with trend
            returns = np.random.normal(0, volatility / base_price, count)
            prices = [base_price]
            
            for i in range(1, count):
                new_price = prices[-1] * (1 + returns[i])
                prices.append(max(new_price, base_price * 0.5))  # Prevent negative prices
            
            # Create OHLC data
            data = []
            for i in range(len(prices)):
                high = prices[i] * (1 + abs(np.random.normal(0, 0.005)))
                low = prices[i] * (1 - abs(np.random.normal(0, 0.005)))
                close = prices[i]
                open_price = prices[i-1] if i > 0 else close
                
                data.append({
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close, 2),
                    'volume': np.random.randint(1000, 5000)
                })
            
            data = pd.DataFrame(data, index=dates)
            data.attrs['simulated'] = True
            return data
            
        except Exception as e:
            logging.error(f"Simulation failed for {symbol}: {e}")
        
        return None
    
    def normalize_deriv_price(self, raw_price: float, symbol: str) -> float:
        """Normalize Deriv API price to standard display range"""
        try:
            # Debug logging
            logging.info(f"Raw price for {symbol}: {raw_price}")
            
            # Step Index special handling - typically trades 1000-2000 range
            if symbol == 'R_STEPINDEX':
                # Step Index usually doesn't need scaling, but check for obvious errors
                if raw_price > 10000:
                    # If price is way too high, scale it down
                    normalized = raw_price / 10
                    logging.info(f"Step Index normalization: {raw_price} -> {normalized}")
                    return round(normalized, 2)
                elif raw_price < 100:
                    # If price is way too low, scale it up
                    normalized = raw_price * 10
                    logging.info(f"Step Index normalization: {raw_price} -> {normalized}")
                    return round(normalized, 2)
                else:
                    # Step Index is in correct range
                    logging.info(f"Step Index no normalization needed: {raw_price}")
                    return round(raw_price, 2)
            
            # Volatility indices often have scaling issues
            if symbol.startswith('R_') and symbol not in ['R_75', 'R_STEPINDEX']:
                # Common scaling factors based on typical ranges
                if raw_price > 90000:
                    # Price is likely scaled up, normalize down
                    scaling_factors = {
                        'R_10': 17.36,   # Volatility 10
                        'R_25': 17.36,   # Volatility 25  
                        'R_50': 17.36,   # Volatility 50
                        'R_100': 17.36,  # Volatility 100
                        'R_JUMPM25': 17.36,  # Jump 25
                        'R_JUMPM50': 17.36,  # Jump 50
                        'R_JUMPM75': 17.36,  # Jump 75
                        'R_JUMPM100': 17.36, # Jump 100
                    }
                    factor = scaling_factors.get(symbol, 17.36)
                    normalized = raw_price / factor
                    logging.info(f"Normalized {symbol} price: {raw_price} -> {normalized} (factor: {factor})")
                    return round(normalized, 2)
            
            # Boom/Crash indices typically don't need normalization
            # But check for obvious scaling issues
            if symbol.startswith(('BOOM', 'CRASH')):
                if raw_price > 10000:
                    # Boom/Crash typically in 1000-2000 range
                    normalized = raw_price / 10
                    logging.info(f"Boom/Crash normalization: {raw_price} -> {normalized}")
                    return round(normalized, 2)
            
            # For other symbols, check if they need normalization
            if raw_price > 90000:
                # Apply general normalization for any symbol with inflated prices
                factor = 17.36  # Default factor
                normalized = raw_price / factor
                logging.info(f"General normalization for {symbol}: {raw_price} -> {normalized}")
                return round(normalized, 2)
            
            normalized_price = round(raw_price, 2)
            logging.info(f"No normalization needed for {symbol}: {raw_price} -> {normalized_price}")
            return normalized_price
            
        except Exception as e:
            logging.error(f"Error normalizing price for {symbol}: {e}")
            return round(raw_price, 2)
    
    async def get_current_price(self, symbol: str) -> Optional[Tuple[float, float, bool]]:
        """Get current price with indication if simulated"""
        # Get Deriv symbol name
        deriv_symbol = self.deriv_symbols.get(symbol, symbol)
        
        # Try Deriv API first
        try:
            if await self.deriv_handler.connect():
                ticks = await self.deriv_handler.get_ticks_history(deriv_symbol, 1)
                if ticks is not None and len(ticks) > 0:
                    raw_price = ticks.iloc[-1]['close']
                    # Normalize price if needed
                    normalized_price = self.normalize_deriv_price(raw_price, deriv_symbol)
                    
                    # For synthetic indices, bid/ask are usually close to each other
                    spread = normalized_price * 0.0001  # Small spread
                    return normalized_price - spread, normalized_price + spread, False  # bid, ask, not_simulated
        except Exception as e:
            logging.error(f"Deriv API price fetch failed for {symbol}: {e}")
        
        # Fallback to simulation
        try:
            # Use realistic base price for simulation
            base_prices = {
                'Step Index': 1500,
                'Volatility 10 Index': 5750,
                'Volatility 25 Index': 5750,
                'Volatility 50 Index': 5750,
                'Volatility 75 Index': 5750,
                'Volatility 100 Index': 5750,
                'Boom 500 Index': 1500,
                'Boom 1000 Index': 1500,
                'Crash 500 Index': 1500,
                'Crash 1000 Index': 1500,
                'Jump 25 Index': 5750,
                'Jump 50 Index': 5750,
                'Jump 75 Index': 5750,
                'Jump 100 Index': 5750
            }
            
            base_price = base_prices.get(symbol, 1000)
            spread = base_price * 0.0001
            return base_price - spread, base_price + spread, True  # bid, ask, simulated
        except Exception as e:
            logging.error(f"Simulated price failed for {symbol}: {e}")
        
        return None
    
    async def analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze a single symbol and generate signal"""
        try:
            # Fetch data
            data = await self.fetch_data(symbol)
            if data is None or len(data) < 50:
                logging.warning(f"Insufficient data for {symbol}")
                return None
            
            # Calculate indicators
            data = technical_analyzer.calculate_indicators(data)
            
            # Get signal strength
            signal_strength = technical_analyzer.get_signal_strength(data)
            
            # Get current price
            current_price_info = await self.get_current_price(symbol)
            if current_price_info is None:
                return None
            
            bid, ask, is_simulated = current_price_info
            current_price = (bid + ask) / 2
            
            # Calculate risk levels
            atr = data['atr'].iloc[-1] if not pd.isna(data['atr'].iloc[-1]) else current_price * 0.01
            
            # Determine entry, SL, TP based on signal direction
            if signal_strength['direction'] == 'bullish':
                entry_price = ask
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 2.5)
            elif signal_strength['direction'] == 'bearish':
                entry_price = bid
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 2.5)
            else:
                entry_price = current_price
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 2.5)
            
            # Normalize all prices for display consistency
            deriv_symbol = self.deriv_symbols.get(symbol, symbol)
            entry_price = self.normalize_deriv_price(entry_price, deriv_symbol)
            stop_loss = self.normalize_deriv_price(stop_loss, deriv_symbol)
            take_profit = self.normalize_deriv_price(take_profit, deriv_symbol)
            current_price = self.normalize_deriv_price(current_price, deriv_symbol)
            
            # Calculate position size for risk management
            risk_amount = config.min_account_balance * (config.risk_percentage / 100)
            position_size = self.calculate_position_size(risk_amount, entry_price, stop_loss)
            
            # Get additional analysis
            fvgs = technical_analyzer.identify_fvg(data.tail(20))
            order_blocks = technical_analyzer.identify_order_blocks(data.tail(20))
            sweeps = technical_analyzer.identify_liquidity_sweeps(data.tail(20))
            price_action = technical_analyzer.analyze_price_action(data.tail(10))
            
            return {
                'symbol': symbol,
                'direction': signal_strength['direction'],
                'strength': signal_strength['strength'],
                'entry_price': round(entry_price, 2),
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
                'position_size': round(position_size, 2),
                'risk_reward_ratio': round(abs(take_profit - entry_price) / abs(stop_loss - entry_price), 2),
                'current_price': round(current_price, 2),
                'atr': round(atr, 2),
                'is_simulated': is_simulated or data.attrs.get('simulated', False),
                'factors': signal_strength.get('factors', {}),
                'smc_analysis': {
                    'fvgs': len(fvgs),
                    'order_blocks': len(order_blocks),
                    'sweeps': len(sweeps)
                },
                'price_action': price_action,
                'timestamp': pd.Timestamp.now()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def calculate_position_size(self, risk_amount: float, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management"""
        try:
            risk_per_unit = abs(entry_price - stop_loss)
            if risk_per_unit == 0:
                return 0.01  # Minimum position
            
            position_size = risk_amount / risk_per_unit
            
            # Limit position size for synthetic indices
            max_position = 0.1  # Maximum 0.1 lots
            min_position = 0.01  # Minimum 0.01 lots
            
            return max(min_position, min(position_size, max_position))
            
        except Exception as e:
            logging.error(f"Error calculating position size: {e}")
            return 0.01
    
    async def scan_all_symbols(self) -> Dict[str, Dict]:
        """Scan all configured symbols and return signals"""
        signals = {}
        
        for category, symbol_list in self.symbols.items():
            for symbol in symbol_list:
                try:
                    signal = await self.analyze_symbol(symbol)
                    if signal and signal['strength'] >= config.signal_strength_threshold:
                        signals[symbol] = signal
                        logging.info(f"Strong signal found: {symbol} {signal['direction']} {signal['strength']}/10")
                except Exception as e:
                    logging.error(f"Error scanning {symbol}: {e}")
        
        return signals
    
    async def get_best_signals(self, min_strength: float = None) -> Dict[str, Dict]:
        """Get best signals above threshold"""
        if min_strength is None:
            min_strength = config.signal_strength_threshold
        
        all_signals = await self.scan_all_symbols()
        
        # Filter by strength and sort
        strong_signals = {
            symbol: signal for symbol, signal in all_signals.items()
            if signal['strength'] >= min_strength
        }
        
        # Sort by strength (descending)
        sorted_signals = dict(sorted(
            strong_signals.items(),
            key=lambda x: x[1]['strength'],
            reverse=True
        ))
        
        return sorted_signals
    
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

# Global instance
signal_generator = SignalGenerator()
