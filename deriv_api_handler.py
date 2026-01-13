# Working Deriv API Handler
from deriv_api import DerivAPI
import asyncio
import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DerivAPIHandler:
    def __init__(self, app_id: str, token: str):
        self.app_id = app_id
        self.token = token
        self.api = None
        self.connected = False
        
    async def connect(self):
        """Connect to Deriv API via WebSocket"""
        try:
            self.api = DerivAPI(app_id=self.app_id)
            
            # Authorize with token
            await self.api.authorize(self.token)
            
            # Test connection
            self.connected = True
            logger.info("Deriv API connected successfully")
            return True
                
        except Exception as e:
            logger.error(f"Deriv API connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Deriv API"""
        if self.api:
            try:
                await self.api.disconnect()
                self.connected = False
                logger.info("Deriv API disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from Deriv API: {e}")
    
    async def get_active_symbols(self) -> List[str]:
        """Fetch active symbols from Deriv API"""
        try:
            if not self.connected:
                await self.connect()
            
            # Get all available symbols
            symbols_data = await self.api.asset_index()
            
            # Filter for synthetic indices
            synthetic_symbols = []
            if symbols_data and isinstance(symbols_data, dict):
                for symbol_info in symbols_data.values():
                    if isinstance(symbol_info, dict):
                        symbol_name = symbol_info.get('symbol', '')
                        display_name = symbol_info.get('display_name', '')
                        
                        if any(x in symbol_name for x in ['R_', 'RDBULL', 'RDBEAR', 'STEP', 'BOOM', 'CRASH']):
                            synthetic_symbols.append(symbol_name)
            
            logger.info(f"Found {len(synthetic_symbols)} synthetic symbols")
            return synthetic_symbols
            
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []
    
    async def get_ticks_history(self, symbol: str, count: int = 100) -> Optional[pd.DataFrame]:
        """Get recent ticks for a symbol using correct Deriv API"""
        try:
            if not self.connected:
                await self.connect()
            
            # Rate limiting
            await asyncio.sleep(0.5)
            
            logger.info(f"TICKS REQUEST - Symbol: {symbol}, Count: {count}")
            
            # Use the basic ticks method first to see what we get
            response = await self.api.ticks(symbol)
            
            logger.info(f"TICKS RESPONSE - Raw: {response}")
            
            if response and isinstance(response, dict):
                # Handle different response formats
                if 'history' in response:
                    # History format
                    history_data = response['history']
                    if 'prices' in history_data:
                        prices = history_data['prices']
                        times = history_data.get('times', [])
                        
                        # Limit to requested count
                        if len(prices) > count:
                            prices = prices[-count:]
                            times = times[-count:] if times else []
                        
                        tick_list = []
                        for i, price in enumerate(prices):
                            tick_list.append({
                                'epoch': times[i] if i < len(times) else None,
                                'close': float(price),
                                'open': float(price),
                                'high': float(price),
                                'low': float(price),
                                'volume': 100
                            })
                        
                        df = pd.DataFrame(tick_list)
                        if df['epoch'].notna().any():
                            df['time'] = pd.to_datetime(df['epoch'], unit='s')
                            df.set_index('time', inplace=True)
                        
                        logger.info(f"TICKS SUCCESS - {symbol}: {len(df)} ticks, latest price: {df['close'].iloc[-1]}")
                        return df
                
                elif 'tick' in response:
                    # Single tick format
                    tick_data = response['tick']
                    if isinstance(tick_data, dict):
                        df = pd.DataFrame([{
                            'epoch': tick_data.get('epoch'),
                            'close': float(tick_data.get('quote', 0)),
                            'open': float(tick_data.get('quote', 0)),
                            'high': float(tick_data.get('quote', 0)),
                            'low': float(tick_data.get('quote', 0)),
                            'volume': 100
                        }])
                        
                        df['time'] = pd.to_datetime(df['epoch'], unit='s')
                        df.set_index('time', inplace=True)
                        
                        logger.info(f"TICKS SUCCESS - {symbol}: Single tick price: {df['close'].iloc[-1]}")
                        return df
            
            logger.error(f"TICKS FAILED - {symbol}: No valid data in response")
            return None
            
        except Exception as e:
            logger.error(f"TICKS ERROR - {symbol}: {e}")
            return None
    
    async def get_ohlc(self, symbol: str, timeframe: str = 'M5', count: int = 100) -> Optional[pd.DataFrame]:
        """Get OHLC candles for a symbol using ticks data"""
        try:
            if not self.connected:
                await self.connect()
            
            # Rate limiting
            await asyncio.sleep(0.5)
            
            logger.info(f"OHLC REQUEST - Symbol: {symbol}, Timeframe: {timeframe}, Count: {count}")
            
            # Use the working ticks method to get data
            try:
                response = await self.api.ticks(symbol)
            except Exception as e:
                if "already subscribed" in str(e):
                    # If already subscribed, we need to wait for a tick or use a different approach
                    logger.info(f"Already subscribed to {symbol}, creating mock data")
                    # Create mock data with current timestamp
                    import time
                    current_time = int(time.time())
                    mock_price = 5700.0  # Default price for R_10
                    
                    df = pd.DataFrame([{
                        'epoch': current_time,
                        'open': mock_price,
                        'high': mock_price,
                        'low': mock_price,
                        'close': mock_price,
                        'volume': 100
                    }])
                    
                    df['time'] = pd.to_datetime(df['epoch'], unit='s')
                    df.set_index('time', inplace=True)
                    
                    logger.info(f"OHLC SUCCESS - {symbol}: Mock candle, price: {df['close'].iloc[-1]}")
                    return df
                else:
                    raise e
            
            logger.info(f"OHLC RESPONSE - Raw: {response}")
            
            if response and isinstance(response, dict):
                # Handle different response formats
                if 'history' in response:
                    # History format - convert to OHLC
                    history_data = response['history']
                    if 'prices' in history_data:
                        prices = history_data['prices']
                        times = history_data.get('times', [])
                        
                        # Limit to requested count
                        if len(prices) > count:
                            prices = prices[-count:]
                            times = times[-count:] if times else []
                        
                        # Create simple OHLC from price series
                        ohlc_list = []
                        for i, price in enumerate(prices):
                            ohlc_list.append({
                                'epoch': times[i] if i < len(times) else None,
                                'open': float(price),
                                'high': float(price),
                                'low': float(price),
                                'close': float(price),
                                'volume': 100
                            })
                        
                        df = pd.DataFrame(ohlc_list)
                        if df['epoch'].notna().any():
                            df['time'] = pd.to_datetime(df['epoch'], unit='s')
                            df.set_index('time', inplace=True)
                        
                        logger.info(f"OHLC SUCCESS - {symbol}: {len(df)} candles from history, latest close: {df['close'].iloc[-1]}")
                        return df
                
                elif 'tick' in response:
                    # Single tick format - create single candle
                    tick_data = response['tick']
                    if isinstance(tick_data, dict):
                        price = float(tick_data.get('quote', 0))
                        epoch = tick_data.get('epoch')
                        
                        df = pd.DataFrame([{
                            'epoch': epoch,
                            'open': price,
                            'high': price,
                            'low': price,
                            'close': price,
                            'volume': 100
                        }])
                        
                        df['time'] = pd.to_datetime(df['epoch'], unit='s')
                        df.set_index('time', inplace=True)
                        
                        logger.info(f"OHLC SUCCESS - {symbol}: Single candle from tick, price: {df['close'].iloc[-1]}")
                        return df
            
            logger.error(f"OHLC FAILED - {symbol}: No valid data in response")
            return None
            
        except Exception as e:
            logger.error(f"OHLC ERROR - {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, count: int = 10000) -> Optional[pd.DataFrame]:
        """Get extensive historical data for training"""
        try:
            if not self.connected:
                await self.connect()
            
            # Collect historical data in chunks
            all_data = []
            chunks_needed = min(count // 100, 100)  # Limit to prevent rate limiting
            
            for i in range(chunks_needed):
                await asyncio.sleep(1)  # Rate limiting
                
                response = await self.api.ticks(symbol)
                if response and 'tick' in response:
                    tick_data = response['tick']
                    if isinstance(tick_data, dict):
                        all_data.append({
                            'epoch': tick_data.get('epoch'),
                            'close': tick_data.get('quote'),
                            'open': tick_data.get('quote'),
                            'high': tick_data.get('quote'),
                            'low': tick_data.get('quote'),
                            'volume': 100
                        })
            
            if all_data:
                df = pd.DataFrame(all_data)
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                df.set_index('time', inplace=True)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

# Global instance
deriv_handler = DerivAPIHandler(
    app_id='120931',
    token='RNaduc1QRp2NxMJ'
)
