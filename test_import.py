#!/usr/bin/env python3
"""
Debug test to check Deriv API import and basic functionality
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if Deriv API can be imported"""
    logger.info("=== IMPORT TEST ===")
    
    try:
        from deriv_api import DerivAPI
        logger.info("✅ DerivAPI imported successfully")
        
        # Try to create an instance
        try:
            app_id = "120931"
            api = DerivAPI(app_id=app_id)
            logger.info("✅ DerivAPI instance created successfully")
            logger.info(f"API object: {api}")
            logger.info(f"API type: {type(api)}")
            
            # Check available methods
            methods = [method for method in dir(api) if not method.startswith('_')]
            logger.info(f"Available methods: {methods}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create DerivAPI instance: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        logger.error(f"❌ Failed to import DerivAPI: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("=== IMPORT TEST COMPLETE ===")

if __name__ == "__main__":
    test_imports()
