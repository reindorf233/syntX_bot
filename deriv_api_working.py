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
        """Get recent ticks for a symbol"""
        try:
            if not self.connected:
                await self.connect()
            
            # Rate limiting
            await asyncio.sleep(0.5)
            
            # Get ticks history
            response = await self.api.ticks(symbol)
            
            if response and 'tick' in response:
                # Extract tick data
                tick_data = response['tick']
                if isinstance(tick_data, dict):
                    # Create DataFrame from single tick
                    df = pd.DataFrame([{
                        'epoch': tick_data.get('epoch'),
                        'close': tick_data.get('quote'),
                        'open': tick_data.get('quote'),
                        'high': tick_data.get('quote'),
                        'low': tick_data.get('quote'),
                        'volume': 100
                    }])
                    
                    df['time'] = pd.to_datetime(df['epoch'], unit='s')
                    df.set_index('time', inplace=True)
                    return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching ticks for {symbol}: {e}")
            return None
    
    async def get_ohlc(self, symbol: str, timeframe: str = 'M5', count: int = 100) -> Optional[pd.DataFrame]:
        """Get OHLC candles for a symbol by aggregating ticks"""
        try:
            if not self.connected:
                await self.connect()
            
            # Rate limiting
            await asyncio.sleep(0.5)
            
            # Get multiple ticks to create OHLC
            all_ticks = []
            for i in range(10):  # Get 10 batches of ticks
                response = await self.api.ticks(symbol)
                if response and 'tick' in response:
                    tick_data = response['tick']
                    if isinstance(tick_data, dict):
                        all_ticks.append({
                            'epoch': tick_data.get('epoch'),
                            'close': tick_data.get('quote'),
                            'volume': 100
                        })
                await asyncio.sleep(0.1)  # Small delay between requests
            
            if all_ticks:
                df = pd.DataFrame(all_ticks)
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                df.set_index('time', inplace=True)
                
                # Create OHLC from ticks
                df_ohlc = df.resample('5T').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
                
                return df_ohlc
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching OHLC for {symbol}: {e}")
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
