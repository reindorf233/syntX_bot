#!/usr/bin/env python3
"""
Test with hardcoded credentials to verify API works
"""
import asyncio
import logging
from deriv_api_handler import DerivAPIHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_with_hardcoded_creds():
    """Test Deriv API with hardcoded credentials"""
    logger.info("=== HARDCODED CREDS TEST ===")
    
    # Hardcoded credentials
    app_id = "120931"
    token = "RNaduc1QRp2NxMJ"
    
    logger.info(f"App ID: {app_id}")
    logger.info(f"Token: {token[:10]}...")
    
    # Test connection
    handler = DerivAPIHandler(app_id, token)
    
    try:
        logger.info("Attempting to connect...")
        connected = await handler.connect()
        logger.info(f"Connection result: {connected}")
        
        if connected:
            logger.info("✅ Connected successfully!")
            
            # Test getting ticks
            try:
                logger.info("Testing ticks for R_10...")
                response = await handler.api.ticks('R_10')
                logger.info(f"Ticks response type: {type(response)}")
                logger.info(f"Ticks response: {response}")
                
                if response and isinstance(response, dict):
                    if 'tick' in response:
                        tick = response['tick']
                        price = tick.get('quote')
                        epoch = tick.get('epoch')
                        logger.info(f"✅ SUCCESS: Got tick - Price: {price}, Epoch: {epoch}")
                    elif 'history' in response:
                        history = response['history']
                        prices = history.get('prices', [])
                        logger.info(f"✅ SUCCESS: Got history - Prices: {prices[:5]}...")  # Show first 5
                    else:
                        logger.error(f"❌ Unknown response format: {list(response.keys())}")
                else:
                    logger.error(f"❌ Invalid response format: {response}")
                    
            except Exception as e:
                logger.error(f"❌ Ticks failed: {e}")
                import traceback
                traceback.print_exc()
            
        else:
            logger.error("❌ FAILED: Could not connect to Deriv API")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            await handler.disconnect()
            logger.info("Disconnected")
        except:
            pass
        logger.info("=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_with_hardcoded_creds())
