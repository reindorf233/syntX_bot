import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from config import config
from mt5_handler import mt5_handler
from price_simulator import price_simulator
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
    
    def fetch_data(self, symbol: str, timeframe: str = None, count: int = None) -> Optional[pd.DataFrame]:
        """Fetch data from MT5 with fallback to simulation"""
        if timeframe is None:
            timeframe = config.timeframe
        if count is None:
            count = config.bars_count
        
        # Try MT5 first
        try:
            if mt5_handler.connect():
                data = mt5_handler.fetch_ohlc_data(symbol, timeframe, count)
                if data is not None and len(data) > 0:
                    logging.info(f"Successfully fetched MT5 data for {symbol}")
                    return data
                else:
                    logging.warning(f"MT5 returned no data for {symbol}")
            else:
                logging.warning("MT5 connection failed, using simulation")
        except Exception as e:
            logging.error(f"MT5 data fetch failed for {symbol}: {e}")
        
        # Fallback to simulation
        try:
            simulated_data = price_simulator.simulate_prices(symbol, timeframe, count)
            if simulated_data is not None:
                logging.info(f"Using simulated data for {symbol}")
                # Add a flag to indicate simulated data
                simulated_data.attrs['simulated'] = True
                return simulated_data
        except Exception as e:
            logging.error(f"Simulation failed for {symbol}: {e}")
        
        return None
    
    def get_current_price(self, symbol: str) -> Optional[Tuple[float, float, bool]]:
        """Get current price with indication if simulated"""
        # Try MT5 first
        try:
            if mt5_handler.connect():
                price = mt5_handler.get_current_price(symbol)
                if price:
                    return price[0], price[1], False  # bid, ask, not_simulated
        except Exception as e:
            logging.error(f"MT5 price fetch failed for {symbol}: {e}")
        
        # Fallback to simulation
        try:
            price = price_simulator.get_current_price(symbol)
            if price:
                return price[0], price[1], True  # bid, ask, simulated
        except Exception as e:
            logging.error(f"Simulated price failed for {symbol}: {e}")
        
        return None
    
    def analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze a single symbol and generate signal"""
        try:
            # Fetch data
            data = self.fetch_data(symbol)
            if data is None or len(data) < 50:
                logging.warning(f"Insufficient data for {symbol}")
                return None
            
            # Calculate indicators
            data = technical_analyzer.calculate_indicators(data)
            
            # Get signal strength
            signal_strength = technical_analyzer.get_signal_strength(data)
            
            # Get current price
            current_price_info = self.get_current_price(symbol)
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
    
    def scan_all_symbols(self) -> Dict[str, Dict]:
        """Scan all configured symbols and return signals"""
        signals = {}
        
        for category, symbol_list in self.symbols.items():
            for symbol in symbol_list:
                try:
                    signal = self.analyze_symbol(symbol)
                    if signal and signal['strength'] >= config.signal_strength_threshold:
                        signals[symbol] = signal
                        logging.info(f"Strong signal found: {symbol} {signal['direction']} {signal['strength']}/10")
                except Exception as e:
                    logging.error(f"Error scanning {symbol}: {e}")
        
        return signals
    
    def get_best_signals(self, min_strength: float = None) -> Dict[str, Dict]:
        """Get best signals above threshold"""
        if min_strength is None:
            min_strength = config.signal_strength_threshold
        
        all_signals = self.scan_all_symbols()
        
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

🔍 *Technical Analysis:*
• Current Price: {signal['current_price']}
• ATR: {signal['atr']}
• FVGs: {signal['smc_analysis']['fvgs']}
• Order Blocks: {signal['smc_analysis']['order_blocks']}
• Liquidity Sweeps: {signal['smc_analysis']['sweeps']}

⏰ {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}
            """
            
            return message.strip()
            
        except Exception as e:
            logging.error(f"Error formatting signal message: {e}")
            return f"Error formatting signal for {signal.get('symbol', 'Unknown')}"

# Global signal generator instance
signal_generator = SignalGenerator()
