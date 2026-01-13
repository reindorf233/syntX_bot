#!/usr/bin/env python3
"""
Test config and environment variables
"""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """Test configuration loading"""
    logger.info("=== CONFIG TEST ===")
    
    # Check all environment variables
    vars_to_check = [
        'DERIV_APP_ID',
        'DERIV_TOKEN',
        'TELEGRAM_BOT_TOKEN',
        'PUBLIC_CHANNEL_ID',
        'BOT_OWNER_ID'
    ]
    
    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            if 'TOKEN' in var:
                logger.info(f"{var}: {value[:10]}...")
            else:
                logger.info(f"{var}: {value}")
        else:
            logger.error(f"{var}: NOT SET")
    
    logger.info("=== CONFIG TEST COMPLETE ===")

if __name__ == "__main__":
    test_config()
