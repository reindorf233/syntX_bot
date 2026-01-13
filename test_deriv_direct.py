#!/usr/bin/env python3
"""
Quick test with hardcoded credentials to verify Deriv API works
"""
import asyncio
import logging
from deriv_api_handler import DerivAPIHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_deriv_api():
    """Test Deriv API with hardcoded credentials"""
    logger.info("=== DERIV API TEST ===")
    
    # Hardcoded credentials for testing
    app_id = "120931"
    token = "RNaduc1QRp2NxMJ"
    
    logger.info(f"App ID: {app_id}")
    logger.info(f"Token: {token[:10]}...")
    
    # Create handler
    handler = DerivAPIHandler(app_id, token)
    
    # Test connection
    connected = await handler.connect()
    logger.info(f"Connected: {connected}")
    
    if connected:
        # Test getting ticks for Volatility 10
        symbol = "R_10"
        logger.info(f"Testing ticks for {symbol}...")
        
        ticks = await handler.get_ticks_history(symbol, 1)
        if ticks is not None:
            logger.info(f"✅ Ticks received: {len(ticks)} rows")
            logger.info(f"Latest price: {ticks['close'].iloc[-1]}")
        else:
            logger.error(f"❌ No ticks received")
        
        # Test getting OHLC for Volatility 10
        logger.info(f"Testing OHLC for {symbol}...")
        
        ohlc = await handler.get_ohlc(symbol, 'M5', 5)
        if ohlc is not None:
            logger.info(f"✅ OHLC received: {len(ohlc)} candles")
            logger.info(f"Latest close: {ohlc['close'].iloc[-1]}")
        else:
            logger.error(f"❌ No OHLC received")
    
    # Disconnect
    await handler.disconnect()
    logger.info("=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_deriv_api())
