#!/usr/bin/env python3
"""
Test script to verify environment variables and basic functionality
"""
import os
import logging
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables and basic setup"""
    logger.info("=== Environment Test ===")
    
    # Test Telegram Bot Token
    if config.telegram_bot_token:
        if config.telegram_bot_token == "YOUR_BOT_TOKEN_HERE":
            logger.warning("❌ TELEGRAM_BOT_TOKEN is placeholder - needs real token")
        else:
            logger.info("✅ TELEGRAM_BOT_TOKEN is set")
    else:
        logger.warning("❌ TELEGRAM_BOT_TOKEN not set")
    
    # Test Deriv API credentials
    if config.deriv_app_id:
        logger.info(f"✅ DERIV_APP_ID: {config.deriv_app_id}")
    else:
        logger.warning("❌ DERIV_APP_ID not set")
    
    if config.deriv_token:
        if config.deriv_token == "YOUR_DERIV_TOKEN_HERE":
            logger.warning("❌ DERIV_TOKEN is placeholder - needs real token")
        else:
            logger.info("✅ DERIV_TOKEN is set")
    else:
        logger.warning("❌ DERIV_TOKEN not set")
    
    # Test other important configs
    logger.info(f"✅ SIGNAL_STRENGTH_THRESHOLD: {config.signal_strength_threshold}")
    logger.info(f"✅ AUTO_SCAN_ENABLED: {config.auto_scan_enabled}")
    logger.info(f"✅ SCAN_INTERVAL: {config.scan_interval} seconds")
    
    logger.info("=== Test Complete ===")

def test_price_normalization():
    """Test price normalization function"""
    logger.info("=== Price Normalization Test ===")
    
    try:
        from signal_generator import signal_generator
        
        # Test with inflated price
        test_prices = [
            (999995, "R_10"),
            (5738, "R_10"),
            (1000000, "R_25"),
            (5800, "R_25"),
            (999999, "BOOM500"),
            (500, "BOOM500")
        ]
        
        for price, symbol in test_prices:
            normalized = signal_generator.normalize_deriv_price(price, symbol)
            logger.info(f"{symbol}: {price} -> {normalized}")
        
        logger.info("✅ Price normalization test passed")
        
    except Exception as e:
        logger.error(f"❌ Price normalization test failed: {e}")
    
    logger.info("=== Test Complete ===")

if __name__ == "__main__":
    test_environment()
    test_price_normalization()
