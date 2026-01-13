#!/usr/bin/env python3
"""
Simple test to check Deriv API connection and credentials
"""
import asyncio
import logging
import os
from deriv_api_handler import DerivAPIHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_connection():
    """Test basic Deriv API connection"""
    logger.info("=== DERIV CONNECTION TEST ===")
    
    # Check environment variables
    app_id = os.getenv('DERIV_APP_ID', '120931')
    token = os.getenv('DERIV_TOKEN', 'RNaduc1QRp2NxMJ')
    
    logger.info(f"App ID: {app_id}")
    logger.info(f"Token: {token[:10]}...")
    
    # Test connection
    handler = DerivAPIHandler(app_id, token)
    
    try:
        connected = await handler.connect()
        logger.info(f"Connection result: {connected}")
        
        if connected:
            # Test a simple API call
            logger.info("Testing API call...")
            
            # Try to get account info
            try:
                account = await handler.api.account()
                logger.info(f"Account info: {account}")
            except Exception as e:
                logger.error(f"Account info failed: {e}")
            
            # Test getting ticks for a simple symbol
            try:
                logger.info("Testing ticks for R_10...")
                response = await handler.api.ticks('R_10')
                logger.info(f"Ticks response: {response}")
                
                if response and 'tick' in response:
                    tick = response['tick']
                    price = tick.get('quote')
                    logger.info(f"✅ SUCCESS: Got tick price: {price}")
                else:
                    logger.error(f"❌ FAILED: No tick in response")
                    
            except Exception as e:
                logger.error(f"Ticks failed: {e}")
            
        else:
            logger.error("❌ FAILED: Could not connect to Deriv API")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
    
    finally:
        await handler.disconnect()
        logger.info("=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_connection())
