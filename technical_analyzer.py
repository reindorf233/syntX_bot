import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from config import config

class TechnicalAnalyzer:
    def __init__(self):
        self.rsi_period = config.rsi_period
        self.bb_period = config.bb_period
        self.bb_std = config.bb_std
        self.ema_fast = config.ema_fast
        self.ema_slow = config.ema_slow
        self.macd_fast = config.macd_fast
        self.macd_slow = config.macd_slow
        self.macd_signal = config.macd_signal
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = df.copy()
        
        # RSI (manual implementation)
        df['rsi'] = self.calculate_rsi(df['close'], self.rsi_period)
        
        # Bollinger Bands (manual implementation)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df['close'], self.bb_period, self.bb_std)
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        df['bb_width'] = (bb_upper - bb_lower) / bb_middle
        df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
        
        # EMAs (manual implementation)
        df['ema_fast'] = df['close'].ewm(span=self.ema_fast).mean()
        df['ema_slow'] = df['close'].ewm(span=self.ema_slow).mean()
        
        # MACD (manual implementation)
        macd_line, macd_signal, macd_histogram = self.calculate_macd(df['close'], self.macd_fast, self.macd_slow, self.macd_signal)
        df['macd'] = macd_line
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd_histogram
        
        # ATR (manual implementation)
        df['atr'] = self.calculate_atr(df['high'], df['low'], df['close'], 14)
        
        # Volume indicators
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            # Add default volume if not present
            df['volume'] = 1000
            df['volume_sma'] = 1000
            df['volume_ratio'] = 1.0
        
        # Price changes
        df['price_change'] = df['close'].pct_change()
        df['price_change_abs'] = df['price_change'].abs()
        
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI manually"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std: float = 2.0):
        """Calculate Bollinger Bands manually"""
        middle = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return upper, middle, lower
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD manually"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        return macd_line, macd_signal, macd_histogram
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate ATR manually"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def identify_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """Identify Fair Value Gaps (FVGs)"""
        try:
            fvgs = []
            
            for i in range(2, len(df)):
                # Bullish FVG (gap up)
                if df.iloc[i-2]['high'] < df.iloc[i]['low']:
                    fvgs.append({
                        'type': 'bullish',
                        'start_index': i-2,
                        'end_index': i,
                        'top': df.iloc[i]['low'],
                        'bottom': df.iloc[i-2]['high'],
                        'size': df.iloc[i]['low'] - df.iloc[i-2]['high'],
                        'time': df.index[i]
                    })
                
                # Bearish FVG (gap down)
                elif df.iloc[i-2]['low'] > df.iloc[i]['high']:
                    fvgs.append({
                        'type': 'bearish',
                        'start_index': i-2,
                        'end_index': i,
                        'top': df.iloc[i-2]['low'],
                        'bottom': df.iloc[i]['high'],
                        'size': df.iloc[i-2]['low'] - df.iloc[i]['high'],
                        'time': df.index[i]
                    })
            
            return fvgs
            
        except Exception as e:
            logging.error(f"Error identifying FVGs: {e}")
            return []
    
    def identify_order_blocks(self, df: pd.DataFrame, lookback: int = 10) -> List[Dict]:
        """Identify Order Blocks"""
        try:
            order_blocks = []
            
            for i in range(lookback, len(df)):
                # Check for strong bullish candle
                if (df.iloc[i]['close'] > df.iloc[i]['open'] and  # Bullish
                    df.iloc[i]['close'] > df.iloc[i-1]['close'] and  # Higher close
                    df.iloc[i]['volume'] > df.iloc[i]['volume_sma'] * 1.5):  # High volume
                    
                    # The previous candle could be an order block
                    ob_candle = df.iloc[i-1]
                    order_blocks.append({
                        'type': 'bullish',
                        'index': i-1,
                        'high': ob_candle['high'],
                        'low': ob_candle['low'],
                        'time': df.index[i-1],
                        'strength': df.iloc[i]['volume'] / df.iloc[i]['volume_sma']
                    })
                
                # Check for strong bearish candle
                elif (df.iloc[i]['close'] < df.iloc[i]['open'] and  # Bearish
                      df.iloc[i]['close'] < df.iloc[i-1]['close'] and  # Lower close
                      df.iloc[i]['volume'] > df.iloc[i]['volume_sma'] * 1.5):  # High volume
                    
                    # The previous candle could be an order block
                    ob_candle = df.iloc[i-1]
                    order_blocks.append({
                        'type': 'bearish',
                        'index': i-1,
                        'high': ob_candle['high'],
                        'low': ob_candle['low'],
                        'time': df.index[i-1],
                        'strength': df.iloc[i]['volume'] / df.iloc[i]['volume_sma']
                    })
            
            return order_blocks
            
        except Exception as e:
            logging.error(f"Error identifying order blocks: {e}")
            return []
    
    def identify_liquidity_sweeps(self, df: pd.DataFrame, lookback: int = 20) -> List[Dict]:
        """Identify liquidity sweeps"""
        try:
            sweeps = []
            
            if len(df) < lookback:
                return sweeps
            
            # Find recent highs and lows
            recent_high = df['high'].iloc[-lookback:].max()
            recent_low = df['low'].iloc[-lookback:].min()
            
            # Check for sweep of recent high
            if df.iloc[-1]['high'] > recent_high:
                # Check if price quickly reversed down
                if (df.iloc[-1]['close'] < df.iloc[-1]['open'] and  # Bearish reversal
                    df.iloc[-1]['close'] < recent_high * 0.995):  # Significant pullback
                    sweeps.append({
                        'type': 'high_sweep',
                        'level': recent_high,
                        'time': df.index[-1],
                        'sweep_high': df.iloc[-1]['high']
                    })
            
            # Check for sweep of recent low
            elif df.iloc[-1]['low'] < recent_low:
                # Check if price quickly reversed up
                if (df.iloc[-1]['close'] > df.iloc[-1]['open'] and  # Bullish reversal
                    df.iloc[-1]['close'] > recent_low * 1.005):  # Significant bounce
                    sweeps.append({
                        'type': 'low_sweep',
                        'level': recent_low,
                        'time': df.index[-1],
                        'sweep_low': df.iloc[-1]['low']
                    })
            
            return sweeps
            
        except Exception as e:
            logging.error(f"Error identifying liquidity sweeps: {e}")
            return []
    
    def analyze_price_action(self, df: pd.DataFrame) -> Dict:
        """Analyze price action patterns"""
        try:
            if len(df) < 5:
                return {}
            
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Candlestick patterns
            patterns = {}
            
            # Engulfing patterns
            if (current['close'] > current['open'] and  # Current bullish
                prev['close'] < prev['open'] and  # Previous bearish
                current['open'] < prev['close'] and  # Engulfs previous
                current['close'] > prev['open']):
                patterns['bullish_engulfing'] = True
            
            elif (current['close'] < current['open'] and  # Current bearish
                  prev['close'] > prev['open'] and  # Previous bullish
                  current['open'] > prev['close'] and  # Engulfs previous
                  current['close'] < prev['open']):
                patterns['bearish_engulfing'] = True
            
            # Hammer/Doji patterns
            body_size = abs(current['close'] - current['open'])
            wick_size = current['high'] - current['low']
            
            if body_size < wick_size * 0.3:  # Small body
                if current['close'] > current['open']:  # Bullish
                    patterns['hammer'] = True
                else:
                    patterns['doji'] = True
            
            # Trend analysis
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['close'].rolling(50).mean().iloc[-1]
            
            trend = {}
            if current['close'] > sma_20 > sma_50:
                trend['direction'] = 'bullish'
                trend['strength'] = 'strong'
            elif current['close'] < sma_20 < sma_50:
                trend['direction'] = 'bearish'
                trend['strength'] = 'strong'
            elif current['close'] > sma_20:
                trend['direction'] = 'bullish'
                trend['strength'] = 'weak'
            elif current['close'] < sma_20:
                trend['direction'] = 'bearish'
                trend['strength'] = 'weak'
            else:
                trend['direction'] = 'sideways'
                trend['strength'] = 'neutral'
            
            return {
                'patterns': patterns,
                'trend': trend,
                'current_price': current['close'],
                'price_change_1': current['close'] - prev['close'],
                'price_change_pct_1': (current['close'] - prev['close']) / prev['close'] * 100
            }
            
        except Exception as e:
            logging.error(f"Error analyzing price action: {e}")
            return {}
    
    def get_signal_strength(self, df: pd.DataFrame) -> Dict:
        """Calculate overall signal strength based on multiple factors"""
        try:
            if len(df) < 50:
                return {'strength': 0, 'direction': 'neutral', 'factors': {}}
            
            current = df.iloc[-1]
            factors = {}
            total_score = 0
            max_score = 0
            
            # RSI factor
            if not pd.isna(current['rsi']):
                if current['rsi'] < 30:
                    rsi_score = 2  # Oversold
                    factors['rsi'] = {'score': 2, 'reason': 'Oversold'}
                elif current['rsi'] > 70:
                    rsi_score = -2  # Overbought
                    factors['rsi'] = {'score': -2, 'reason': 'Overbought'}
                elif 40 <= current['rsi'] <= 60:
                    rsi_score = 0  # Neutral
                    factors['rsi'] = {'score': 0, 'reason': 'Neutral'}
                else:
                    rsi_score = 1 if current['rsi'] > 50 else -1  # Slight bias
                    factors['rsi'] = {'score': rsi_score, 'reason': 'Slight bias'}
                
                total_score += rsi_score
                max_score += 2
            
            # Bollinger Bands factor
            if 'bb_position' in df and not pd.isna(current['bb_position']):
                if current['bb_position'] < 0.1:
                    bb_score = 2  # Near lower band
                    factors['bollinger'] = {'score': 2, 'reason': 'Near lower band'}
                elif current['bb_position'] > 0.9:
                    bb_score = -2  # Near upper band
                    factors['bollinger'] = {'score': -2, 'reason': 'Near upper band'}
                else:
                    bb_score = 0  # Middle
                    factors['bollinger'] = {'score': 0, 'reason': 'Middle bands'}
                
                total_score += bb_score
                max_score += 2
            
            # EMA factor
            if not pd.isna(current['ema_fast']) and not pd.isna(current['ema_slow']):
                if current['close'] > current['ema_fast'] > current['ema_slow']:
                    ema_score = 2  # Bullish alignment
                    factors['ema'] = {'score': 2, 'reason': 'Above both EMAs'}
                elif current['close'] < current['ema_fast'] < current['ema_slow']:
                    ema_score = -2  # Bearish alignment
                    factors['ema'] = {'score': -2, 'reason': 'Below both EMAs'}
                else:
                    ema_score = 0  # Mixed
                    factors['ema'] = {'score': 0, 'reason': 'Mixed EMA signals'}
                
                total_score += ema_score
                max_score += 2
            
            # MACD factor
            if 'macd' in df and 'macd_signal' in df and not pd.isna(current['macd']) and not pd.isna(current['macd_signal']):
                if current['macd'] > current['macd_signal'] and current.get('macd_histogram', 0) > 0:
                    macd_score = 1  # Bullish
                    factors['macd'] = {'score': 1, 'reason': 'MACD bullish'}
                elif current['macd'] < current['macd_signal'] and current.get('macd_histogram', 0) < 0:
                    macd_score = -1  # Bearish
                    factors['macd'] = {'score': -1, 'reason': 'MACD bearish'}
                else:
                    macd_score = 0  # Neutral
                    factors['macd'] = {'score': 0, 'reason': 'MACD neutral'}
                
                total_score += macd_score
                max_score += 1
            
            # SMC factors
            fvgs = self.identify_fvg(df.tail(20))
            order_blocks = self.identify_order_blocks(df.tail(20))
            sweeps = self.identify_liquidity_sweeps(df.tail(20))
            
            smc_score = 0
            if fvgs:
                smc_score += 1
                factors['fvg'] = {'score': 1, 'reason': f'FVGs detected: {len(fvgs)}'}
            
            if order_blocks:
                smc_score += 1
                factors['order_blocks'] = {'score': 1, 'reason': f'Order blocks: {len(order_blocks)}'}
            
            if sweeps:
                smc_score += 2  # Liquidity sweeps are significant
                factors['sweeps'] = {'score': 2, 'reason': f'Liquidity sweeps: {len(sweeps)}'}
            
            total_score += smc_score
            max_score += 4
            
            # Calculate normalized strength (0-10)
            if max_score > 0:
                normalized_score = (total_score + max_score) / (2 * max_score) * 10
                strength = max(0, min(10, normalized_score))
            else:
                strength = 0
            
            # Determine direction
            if strength > 6:
                direction = 'bullish' if total_score > 0 else 'bearish'
            elif strength < 4:
                direction = 'neutral'
            else:
                direction = 'bullish' if total_score > 0 else 'bearish'
            
            return {
                'strength': round(strength, 1),
                'direction': direction,
                'raw_score': total_score,
                'max_score': max_score,
                'factors': factors
            }
            
        except Exception as e:
            logging.error(f"Error calculating signal strength: {e}")
            return {'strength': 0, 'direction': 'neutral', 'factors': {}}

# Global analyzer instance
technical_analyzer = TechnicalAnalyzer()
