# Deriv API Integration
# Install: pip install python-deriv-api

"""
Deriv API Setup Instructions:
1. Create Deriv account at https://deriv.com
2. Register app at https://developers.deriv.com/apps
3. Get app_id and API token with scopes: 'read', 'trade'
4. Add to .env:
   - DERIV_APP_ID=your_app_id
   - DERIV_TOKEN=your_api_token
"""

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
            account_info = await self.api.account_info()
            if account_info:
                self.connected = True
                logger.info(f"Deriv API connected - Account: {account_info.get('login', 'Unknown')}")
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
            
            # Get active symbols
            symbols = await self.api.active_symbols()
            
            # Filter for synthetic indices
            synthetic_symbols = []
            for symbol in symbols:
                symbol_name = symbol.get('symbol', '')
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
            
            # Rate limiting - add small delay
            await asyncio.sleep(0.5)
            
            # Get ticks history
            ticks = await self.api.ticks_history(
                symbol=symbol,
                count=count,
                end='latest'
            )
            
            if ticks and 'history' in ticks:
                df = pd.DataFrame(ticks['history'])
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                df.set_index('time', inplace=True)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching ticks for {symbol}: {e}")
            return None
    
    async def get_ohlc(self, symbol: str, timeframe: str = 'M5', count: int = 100) -> Optional[pd.DataFrame]:
        """Get OHLC candles for a symbol"""
        try:
            if not self.connected:
                await self.connect()
            
            # Rate limiting
            await asyncio.sleep(0.5)
            
            # Get OHLC data
            ohlc = await self.api.candles(
                symbol=symbol,
                granularity=self._get_granularity(timeframe),
                count=count,
                end='latest'
            )
            
            if ohlc and 'candles' in ohlc:
                df = pd.DataFrame(ohlc['candles'])
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                df.set_index('time', inplace=True)
                df.rename(columns={
                    'open': 'open',
                    'high': 'high', 
                    'low': 'low',
                    'close': 'close'
                }, inplace=True)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching OHLC for {symbol}: {e}")
            return None
    
    def _get_granularity(self, timeframe: str) -> int:
        """Convert timeframe to granularity in seconds"""
        timeframe_map = {
            'M1': 60,
            'M5': 300,
            'M15': 900,
            'M30': 1800,
            'H1': 3600,
            'H4': 14400,
            'D1': 86400
        }
        return timeframe_map.get(timeframe, 300)  # Default to M5
    
    async def get_historical_data(self, symbol: str, count: int = 10000) -> Optional[pd.DataFrame]:
        """Get extensive historical data for training"""
        try:
            if not self.connected:
                await self.connect()
            
            # Get historical data in chunks to respect rate limits
            all_data = []
            chunk_size = 1000
            chunks_needed = count // chunk_size
            
            for i in range(chunks_needed):
                await asyncio.sleep(1)  # Rate limiting
                
                chunk = await self.api.candles(
                    symbol=symbol,
                    granularity=60,  # 1-minute data
                    count=chunk_size,
                    end='latest' if i == 0 else all_data[0]['epoch']
                )
                
                if chunk and 'candles' in chunk:
                    all_data.extend(chunk['candles'])
            
            if all_data:
                df = pd.DataFrame(all_data)
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                df.set_index('time', inplace=True)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
