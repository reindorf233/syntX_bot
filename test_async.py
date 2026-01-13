#!/usr/bin/env python3
"""
Async test to check Deriv API functionality
"""
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_deriv_api():
    """Test Deriv API in async context"""
    logger.info("=== ASYNC DERIV API TEST ===")
    
    try:
        from deriv_api import DerivAPI
        logger.info("✅ DerivAPI imported successfully")
        
        # Create instance in async context
        app_id = "120931"
        api = DerivAPI(app_id=app_id)
        logger.info("✅ DerivAPI instance created successfully")
        
        # Check available methods
        methods = [method for method in dir(api) if not method.startswith('_') and callable(getattr(api, method))]
        logger.info(f"Available methods: {methods}")
        
        # Test authorization
        token = "RNaduc1QRp2NxMJ"
        try:
            logger.info("Attempting authorization...")
            auth_result = await api.authorize(token)
            logger.info(f"✅ Authorization result: {auth_result}")
            
            # Test ticks
            try:
                logger.info("Testing ticks for R_10...")
                ticks_result = await api.ticks('R_10')
                logger.info(f"✅ Ticks result: {ticks_result}")
                
                if ticks_result and isinstance(ticks_result, dict):
                    if 'tick' in ticks_result:
                        tick = ticks_result['tick']
                        price = tick.get('quote')
                        logger.info(f"✅ SUCCESS: Got tick price: {price}")
                    else:
                        logger.info(f"Response keys: {list(ticks_result.keys())}")
                
            except Exception as e:
                logger.error(f"❌ Ticks failed: {e}")
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            logger.error(f"❌ Authorization failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Disconnect
        try:
            await api.disconnect()
            logger.info("✅ Disconnected successfully")
        except Exception as e:
            logger.error(f"❌ Disconnect failed: {e}")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("=== ASYNC TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_deriv_api())
