#!/usr/bin/env python3
"""
Simplified Deriv API Handler - No Simulation Mode
"""
import asyncio
import logging
from deriv_api import DerivAPI

logger = logging.getLogger(__name__)

class DerivAPIHandler:
    """Simplified Deriv API handler"""
    
    def __init__(self, app_id: str, token: str):
        self.app_id = app_id
        self.token = token
        self.api = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to Deriv API"""
        try:
            self.api = DerivAPI(app_id=self.app_id)
            
            # Authorize
            auth_result = await self.api.authorize(self.token)
            
            if auth_result and 'authorize' in auth_result:
                self.connected = True
                logger.info(f"✅ Connected to Deriv API - Account: {auth_result['authorize'].get('loginid', 'Unknown')}")
                return True
            else:
                logger.error("❌ Deriv API authorization failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Deriv API connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Deriv API"""
        try:
            if self.api:
                await self.api.disconnect()
                self.connected = False
                logger.info("✅ Disconnected from Deriv API")
        except Exception as e:
            logger.error(f"❌ Disconnect error: {e}")
    
    async def get_tick(self, symbol: str) -> dict:
        """Get current tick for symbol"""
        try:
            if not self.connected:
                await self.connect()
            
            response = await self.api.ticks(symbol)
            
            if response and 'tick' in response:
                return response['tick']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Tick error for {symbol}: {e}")
            return None
    
    async def get_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            tick = await self.get_tick(symbol)
            
            if tick and 'quote' in tick:
                price = tick['quote']
                logger.info(f"✅ Live price for {symbol}: {price}")
                return float(price)
            
            logger.error(f"❌ No price data for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Price error for {symbol}: {e}")
            return None
