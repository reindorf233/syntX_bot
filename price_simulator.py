import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import config

class PriceSimulator:
    def __init__(self):
        # Symbol-specific parameters for realistic simulation
        self.symbol_params = {
            # Volatility Indices
            'Volatility 75 Index': {
                'volatility': 0.75,  # High volatility
                'drift': 0.0001,
                'jump_prob': 0.02,
                'jump_size': 0.005,
                'base_price': 100000
            },
            'Volatility 100 Index': {
                'volatility': 1.0,
                'drift': 0.0001,
                'jump_prob': 0.025,
                'jump_size': 0.007,
                'base_price': 100000
            },
            'Volatility 50 Index': {
                'volatility': 0.5,
                'drift': 0.0001,
                'jump_prob': 0.015,
                'jump_size': 0.003,
                'base_price': 100000
            },
            'Volatility 25 Index': {
                'volatility': 0.25,
                'drift': 0.0001,
                'jump_prob': 0.01,
                'jump_size': 0.002,
                'base_price': 100000
            },
            'Volatility 10 Index': {
                'volatility': 0.1,
                'drift': 0.0001,
                'jump_prob': 0.005,
                'jump_size': 0.001,
                'base_price': 100000
            },
            # Boom/Crash Indices
            'Boom 1000 Index': {
                'volatility': 0.3,
                'drift': 0.0002,
                'jump_prob': 0.05,
                'jump_size': 0.02,
                'jump_direction': 'up',  # Boom indices tend to jump up
                'base_price': 1000
            },
            'Boom 500 Index': {
                'volatility': 0.25,
                'drift': 0.00015,
                'jump_prob': 0.04,
                'jump_size': 0.015,
                'jump_direction': 'up',
                'base_price': 500
            },
            'Crash 1000 Index': {
                'volatility': 0.3,
                'drift': -0.0002,
                'jump_prob': 0.05,
                'jump_size': 0.02,
                'jump_direction': 'down',  # Crash indices tend to jump down
                'base_price': 1000
            },
            'Crash 500 Index': {
                'volatility': 0.25,
                'drift': -0.00015,
                'jump_prob': 0.04,
                'jump_size': 0.015,
                'jump_direction': 'down',
                'base_price': 500
            },
            # Step Index
            'Step Index': {
                'volatility': 0.1,
                'drift': 0.0001,
                'jump_prob': 0.1,
                'jump_size': 0.002,
                'jump_direction': 'step',  # Alternating up/down
                'base_price': 1000
            },
            # Jump Indices
            'Jump 25 Index': {
                'volatility': 0.15,
                'drift': 0.0001,
                'jump_prob': 0.08,
                'jump_size': 0.003,
                'jump_direction': 'random',
                'base_price': 2500
            },
            'Jump 50 Index': {
                'volatility': 0.2,
                'drift': 0.0001,
                'jump_prob': 0.08,
                'jump_size': 0.004,
                'jump_direction': 'random',
                'base_price': 5000
            },
            'Jump 75 Index': {
                'volatility': 0.25,
                'drift': 0.0001,
                'jump_prob': 0.08,
                'jump_size': 0.005,
                'jump_direction': 'random',
                'base_price': 7500
            },
            'Jump 100 Index': {
                'volatility': 0.3,
                'drift': 0.0001,
                'jump_prob': 0.08,
                'jump_size': 0.006,
                'jump_direction': 'random',
                'base_price': 10000
            }
        }
    
    def simulate_prices(self, symbol: str, timeframe: str = 'M5', count: int = 100) -> Optional[pd.DataFrame]:
        """Generate simulated price data using Geometric Brownian Motion with jumps"""
        try:
            params = self.symbol_params.get(symbol)
            if not params:
                logging.warning(f"Unknown symbol {symbol}, using default parameters")
                params = {
                    'volatility': 0.3,
                    'drift': 0.0001,
                    'jump_prob': 0.02,
                    'jump_size': 0.005,
                    'jump_direction': 'random',
                    'base_price': 1000
                }
            
            # Time parameters
            dt = self._get_time_delta(timeframe)
            time_steps = count
            
            # Initialize arrays
            times = np.arange(0, time_steps) * dt
            prices = np.zeros(time_steps)
            prices[0] = params['base_price']
            
            # Generate Brownian motion
            brownian_motion = np.cumsum(np.random.normal(0, 1, time_steps)) * np.sqrt(dt)
            
            # Generate jumps
            jumps = np.zeros(time_steps)
            for i in range(1, time_steps):
                if np.random.random() < params['jump_prob']:
                    jump_direction = self._get_jump_direction(params.get('jump_direction', 'random'))
                    jumps[i] = jump_direction * params['jump_size']
            
            # Calculate prices using GBM with jumps
            drift_term = (params['drift'] - 0.5 * params['volatility']**2) * times
            diffusion_term = params['volatility'] * brownian_motion
            prices = params['base_price'] * np.exp(drift_term + diffusion_term + jumps)
            
            # Generate OHLC data
            data = self._generate_ohlc(prices, times, timeframe)
            
            logging.info(f"Generated simulated data for {symbol}: {len(data)} bars")
            return data
            
        except Exception as e:
            logging.error(f"Error simulating prices for {symbol}: {e}")
            return None
    
    def _get_time_delta(self, timeframe: str) -> float:
        """Get time delta in years for given timeframe"""
        timeframe_minutes = {
            'M1': 1,
            'M5': 5,
            'M15': 15,
            'M30': 30,
            'H1': 60,
            'H4': 240,
            'D1': 1440
        }
        minutes = timeframe_minutes.get(timeframe.upper(), 5)
        return minutes / (365 * 24 * 60)  # Convert to years
    
    def _get_jump_direction(self, direction: str) -> float:
        """Get jump direction based on symbol type"""
        if direction == 'up':
            return 1.0
        elif direction == 'down':
            return -1.0
        elif direction == 'step':
            return 1.0 if np.random.random() > 0.5 else -1.0
        else:  # random
            return 1.0 if np.random.random() > 0.5 else -1.0
    
    def _generate_ohlc(self, prices: np.ndarray, times: np.ndarray, timeframe: str) -> pd.DataFrame:
        """Generate realistic OHLC data from price series"""
        data = []
        base_time = datetime.now() - timedelta(minutes=len(prices) * self._get_timeframe_minutes(timeframe))
        
        for i in range(len(prices)):
            current_time = base_time + timedelta(minutes=i * self._get_timeframe_minutes(timeframe))
            
            # Generate realistic OHLC
            close = prices[i]
            
            # Intraday noise for high/low
            noise_range = close * 0.002  # 0.2% typical range
            high = close + np.random.uniform(0, noise_range)
            low = close - np.random.uniform(0, noise_range)
            
            # Open is previous close or close with small gap
            if i == 0:
                open_price = close + np.random.normal(0, close * 0.0005)
            else:
                gap = np.random.normal(0, close * 0.0005)
                open_price = prices[i-1] + gap
            
            # Ensure OHLC relationships
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Generate volume (random but realistic)
            volume = np.random.randint(100, 1000)
            
            data.append({
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume,
                'spread': round(high - low, 2),
                'real_volume': volume
            })
        
        df = pd.DataFrame(data)
        df.index = pd.date_range(start=base_time, periods=len(df), freq=f'{self._get_timeframe_minutes(timeframe)}min')
        df.index.name = 'time'
        
        return df
    
    def _get_timeframe_minutes(self, timeframe: str) -> int:
        """Get timeframe in minutes"""
        timeframe_map = {
            'M1': 1,
            'M5': 5,
            'M15': 15,
            'M30': 30,
            'H1': 60,
            'H4': 240,
            'D1': 1440
        }
        return timeframe_map.get(timeframe.upper(), 5)
    
    def get_current_price(self, symbol: str) -> Optional[tuple]:
        """Get simulated current price"""
        try:
            params = self.symbol_params.get(symbol)
            if not params:
                return None
            
            # Generate a single price point
            dt = self._get_time_delta('M1')
            drift = params['drift'] * dt
            diffusion = params['volatility'] * np.random.normal(0, np.sqrt(dt))
            
            current_price = params['base_price'] * np.exp(drift + diffusion)
            spread = current_price * 0.0001  # 0.01% spread
            
            bid = current_price - spread / 2
            ask = current_price + spread / 2
            
            return round(bid, 2), round(ask, 2)
            
        except Exception as e:
            logging.error(f"Error getting simulated price for {symbol}: {e}")
            return None

# Global simulator instance
price_simulator = PriceSimulator()
