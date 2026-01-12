import MetaTrader5 as mt5
import pandas as pd
import time
import logging
from typing import Optional, Tuple
from config import config

class MT5Handler:
    def __init__(self):
        self.is_connected = False
        self.connection_attempts = 0
        self.max_retries = 5
        self.retry_delay = 2  # seconds
        
    def connect(self) -> bool:
        """Connect to MT5 with retry logic"""
        if self.is_connected:
            return True
            
        for attempt in range(self.max_retries):
            try:
                # Initialize MT5
                if not mt5.initialize():
                    logging.error(f"MT5 initialize() failed, error code = {mt5.last_error()}")
                    continue
                
                # Login to account
                if not mt5.login(login=config.mt5_login, 
                               password=config.mt5_password,
                               server=config.mt5_server):
                    logging.error(f"MT5 login failed, error code = {mt5.last_error()}")
                    mt5.shutdown()
                    continue
                
                # Verify connection
                account_info = mt5.account_info()
                if account_info is None:
                    logging.error("Failed to get account info")
                    mt5.shutdown()
                    continue
                
                self.is_connected = True
                logging.info(f"Successfully connected to MT5 account {account_info.login}")
                return True
                
            except Exception as e:
                logging.error(f"MT5 connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 1.5  # Exponential backoff
        
        logging.error("All MT5 connection attempts failed")
        return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            logging.info("Disconnected from MT5")
    
    def get_symbol_info(self, symbol: str) -> Optional[dict]:
        """Get symbol information"""
        if not self.is_connected:
            return None
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logging.warning(f"Symbol {symbol} not found")
                return None
            return {
                'symbol': symbol_info.name,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'trade_contract_size': symbol_info.trade_contract_size,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
                'spread': symbol_info.spread,
                'swap_long': symbol_info.swap_long,
                'swap_short': symbol_info.swap_short
            }
        except Exception as e:
            logging.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def fetch_ohlc_data(self, symbol: str, timeframe: str, count: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLC data from MT5"""
        if not self.is_connected:
            return None
        
        try:
            # Convert timeframe string to MT5 constant
            mt5_timeframe = self._convert_timeframe(timeframe)
            if mt5_timeframe is None:
                logging.error(f"Invalid timeframe: {timeframe}")
                return None
            
            # Request rates
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None or len(rates) == 0:
                logging.error(f"Failed to get rates for {symbol}, error = {mt5.last_error()}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            logging.info(f"Successfully fetched {len(df)} bars for {symbol}")
            return df
            
        except Exception as e:
            logging.error(f"Error fetching OHLC data for {symbol}: {e}")
            return None
    
    def _convert_timeframe(self, timeframe: str) -> Optional[int]:
        """Convert timeframe string to MT5 constant"""
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        return timeframe_map.get(timeframe.upper())
    
    def get_current_price(self, symbol: str) -> Optional[Tuple[float, float]]:
        """Get current bid/ask price for symbol"""
        if not self.is_connected:
            return None
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logging.error(f"Failed to get tick for {symbol}")
                return None
            
            return tick.bid, tick.ask
        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {e}")
            return None

# Global MT5 handler instance
mt5_handler = MT5Handler()
