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
        
        # Symbol mapping for Deriv API - CORRECTED SYMBOLS
        self.deriv_symbols = {
            # Volatility Indices (standard)
            'Volatility 10 Index': 'R_10',
            'Volatility 25 Index': 'R_25',
            'Volatility 50 Index': 'R_50',
            'Volatility 75 Index': 'R_75',
            'Volatility 100 Index': 'R_100',
            
            # Volatility Indices (1 second)
            'Volatility 10 Index (1s)': 'R_10_1S',
            'Volatility 25 Index (1s)': 'R_25_1S',
            'Volatility 50 Index (1s)': 'R_50_1S',
            'Volatility 75 Index (1s)': 'R_75_1S',
            'Volatility 100 Index (1s)': 'R_100_1S',
            
            # Boom/Crash Indices
            'Boom 300 Index': 'BOOM300',
            'Boom 500 Index': 'BOOM500',
            'Boom 1000 Index': 'BOOM1000',
            'Crash 300 Index': 'CRASH300',
            'Crash 500 Index': 'CRASH500',
            'Crash 1000 Index': 'CRASH1000',
            
            # Jump Indices
            'Jump 10 Index': 'JD10',
            'Jump 25 Index': 'JD25',
            'Jump 50 Index': 'JD50',
            'Jump 75 Index': 'JD75',
            'Jump 100 Index': 'JD100',
            
            # Range Break Indices
            'Range Break 100 Index': 'RB100',
            'Range Break 200 Index': 'RB200',
            
            # Step Index
            'Step Index': 'R_STEPINDEX'
        }
    
    async def fetch_data(self, symbol: str, timeframe: str = None, count: int = None) -> Optional[pd.DataFrame]:
        """Fetch data from Deriv API - NO SIMULATION FALLBACK"""
        if timeframe is None:
            timeframe = config.timeframe
        if count is None:
            count = config.bars_count
        
        # Get Deriv symbol name
        deriv_symbol = self.deriv_symbols.get(symbol, symbol)
        
        logging.info(f"DATA FETCH - Attempting LIVE data for {symbol} -> {deriv_symbol}")
        
        # ONLY use Deriv API - NO simulation fallback
        try:
            if await self.deriv_handler.connect():
                logging.info(f"DATA FETCH - Connected to Deriv API for {deriv_symbol}")
                
                data = await self.deriv_handler.get_ohlc(deriv_symbol, timeframe, count)
                if data is not None and len(data) > 0:
                    logging.info(f"DATA FETCH - Successfully fetched LIVE data for {symbol}: {len(data)} candles")
                    
                    # Verify data is not simulated
                    if data.attrs.get('simulated', False):
                        logging.error(f"DATA FETCH - FAILED: Received simulated data for {symbol}")
                        return None
                    
                    return data
                else:
                    logging.error(f"DATA FETCH - FAILED: Deriv API returned no data for {symbol}")
            else:
                logging.error(f"DATA FETCH - FAILED: Could not connect to Deriv API for {symbol}")
                
        except Exception as e:
            logging.error(f"DATA FETCH - ERROR: Deriv API failed for {symbol}: {e}")
        
        # NO SIMULATION FALLBACK - Return None if live data fails
        logging.error(f"DATA FETCH - FAILED: No live data available for {symbol} - NO SIMULATION FALLBACK")
        return None
    
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
    
    def validate_and_log_price(self, raw_price: float, symbol: str) -> float:
        """Validate price is within expected range and log details"""
        try:
            # Expected price ranges for different symbol types
            expected_ranges = {
                # Volatility indices (standard)
                'R_10': (4000, 8000),
                'R_25': (4000, 8000),
                'R_50': (4000, 8000),
                'R_75': (4000, 8000),
                'R_100': (4000, 8000),
                
                # Volatility indices (1s)
                'R_10_1S': (4000, 8000),
                'R_25_1S': (4000, 8000),
                'R_50_1S': (4000, 8000),
                'R_75_1S': (4000, 8000),
                'R_100_1S': (4000, 8000),
                
                # Boom/Crash indices
                'BOOM300': (1000, 3000),
                'BOOM500': (1000, 3000),
                'BOOM1000': (1000, 3000),
                'CRASH300': (1000, 3000),
                'CRASH500': (1000, 3000),
                'CRASH1000': (1000, 3000),
                
                # Jump indices
                'JD10': (4000, 8000),
                'JD25': (4000, 8000),
                'JD50': (4000, 8000),
                'JD75': (4000, 8000),
                'JD100': (4000, 8000),
                
                # Range Break indices
                'RB100': (1000, 3000),
                'RB200': (1000, 3000),
                
                # Step Index
                'R_STEPINDEX': (1000, 3000)
            }
            
            # Get expected range for this symbol
            min_expected, max_expected = expected_ranges.get(symbol, (100, 10000))
            
            # Log detailed information
            logging.info(f"PRICE VALIDATION - Symbol: {symbol}")
            logging.info(f"PRICE VALIDATION - Raw Price: {raw_price}")
            logging.info(f"PRICE VALIDATION - Expected Range: {min_expected} - {max_expected}")
            logging.info(f"PRICE VALIDATION - App ID: {config.deriv_app_id}")
            logging.info(f"PRICE VALIDATION - Timestamp: {pd.Timestamp.now().isoformat()}")
            
            # Validate price is within reasonable range
            if min_expected <= raw_price <= max_expected:
                logging.info(f"PRICE VALIDATION - ✅ Price within expected range: {raw_price}")
                return round(raw_price, 2)
            else:
                logging.error(f"PRICE VALIDATION - ❌ Price OUT OF RANGE: {raw_price} (expected {min_expected}-{max_expected})")
                # Return the price anyway but flag it
                return round(raw_price, 2)
                
        except Exception as e:
            logging.error(f"PRICE VALIDATION - Error validating price for {symbol}: {e}")
            return round(raw_price, 2)
    
    def normalize_deriv_price(self, raw_price: float, symbol: str) -> float:
        """NO SCALING - Use Deriv API prices directly as they are already correctly scaled"""
        try:
            # Deriv API returns prices already correctly scaled
            # DO NOT apply any scaling factors
            # DO NOT multiply by pip/point/contract size
            # Use the price exactly as received from Deriv
            
            logging.info(f"PRICE NORMALIZATION - Symbol: {symbol}")
            logging.info(f"PRICE NORMALIZATION - Raw API Price: {raw_price}")
            
            # Validate and log the price
            validated_price = self.validate_and_log_price(raw_price, symbol)
            
            logging.info(f"PRICE NORMALIZATION - Final Price (NO SCALING): {validated_price}")
            return validated_price
            
        except Exception as e:
            logging.error(f"PRICE NORMALIZATION - Error processing price for {symbol}: {e}")
            return round(raw_price, 2)
    
    async def get_current_price(self, symbol: str) -> Optional[Tuple[float, float, bool]]:
        """Get current price from LIVE Deriv API - NO SIMULATION FALLBACK"""
        # Get Deriv symbol name
        deriv_symbol = self.deriv_symbols.get(symbol, symbol)
        
        logging.info(f"PRICE FETCH - Attempting LIVE price for {symbol} -> {deriv_symbol}")
        
        # ONLY use live Deriv API - NO simulation fallback
        try:
            if await self.deriv_handler.connect():
                logging.info(f"PRICE FETCH - Connected to Deriv API for {deriv_symbol}")
                
                ticks = await self.deriv_handler.get_ticks_history(deriv_symbol, 1)
                if ticks is not None and len(ticks) > 0:
                    raw_price = ticks.iloc[-1]['close']
                    
                    # Log the raw tick data
                    logging.info(f"PRICE FETCH - Raw tick data for {deriv_symbol}: {ticks.iloc[-1].to_dict()}")
                    
                    # NO SCALING - Use price exactly as received
                    normalized_price = self.normalize_deriv_price(raw_price, deriv_symbol)
                    
                    # Calculate realistic spread
                    spread = normalized_price * 0.0001  # Small spread for synthetic indices
                    
                    bid = round(normalized_price - spread, 2)
                    ask = round(normalized_price + spread, 2)
                    
                    logging.info(f"PRICE FETCH - LIVE price for {symbol}: Bid={bid}, Ask={ask}, Simulated=FALSE")
                    
                    return bid, ask, False  # bid, ask, NOT_SIMULATED
                else:
                    logging.error(f"PRICE FETCH - No tick data received for {deriv_symbol}")
            else:
                logging.error(f"PRICE FETCH - Failed to connect to Deriv API for {deriv_symbol}")
                
        except Exception as e:
            logging.error(f"PRICE FETCH - Deriv API error for {symbol}: {e}")
        
        # NO SIMULATION FALLBACK - Return None if live data fails
        logging.error(f"PRICE FETCH - FAILED to get LIVE price for {symbol} - NO SIMULATION FALLBACK")
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
            
            # Get current price - MUST be live data
            current_price_info = await self.get_current_price(symbol)
            if current_price_info is None:
                logging.error(f"ANALYSIS - FAILED: No live price available for {symbol}")
                return None
            
            bid, ask, is_simulated = current_price_info
            current_price = (bid + ask) / 2
            
            # Verify this is live data, not simulated
            if is_simulated:
                logging.error(f"ANALYSIS - FAILED: Received simulated data for {symbol} - expected live data")
                return None
            
            logging.info(f"ANALYSIS - Using LIVE price for {symbol}: {current_price}")
            
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
            
            # Normalize all prices for display consistency (NO SCALING)
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
            
            # Verify data is not simulated
            data_simulated = data.attrs.get('simulated', False)
            if data_simulated:
                logging.error(f"ANALYSIS - FAILED: Historical data is simulated for {symbol}")
                return None
            
            logging.info(f"ANALYSIS - SUCCESS: Generated LIVE signal for {symbol} at {current_price}")
            
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
                'is_simulated': False,  # FORCE to False - this is LIVE data
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
