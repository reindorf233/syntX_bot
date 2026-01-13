#!/usr/bin/env python3
"""
Test script to verify live price fetching from Deriv API
"""
import asyncio
import logging
from signal_generator import signal_generator
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_live_prices():
    """Test live price fetching for all symbols"""
    logger.info("=== LIVE PRICE TEST ===")
    
    # Test symbols to verify
    test_symbols = [
        'Volatility 10 Index',
        'Volatility 25 Index',
        'Step Index',
        'Boom 500 Index',
        'Crash 1000 Index',
        'Jump 25 Index'
    ]
    
    for symbol in test_symbols:
        logger.info(f"\n--- Testing {symbol} ---")
        
        try:
            # Get current price
            price_info = await signal_generator.get_current_price(symbol)
            
            if price_info:
                bid, ask, is_simulated = price_info
                current_price = (bid + ask) / 2
                
                logger.info(f"✅ {symbol}: {current_price} (Bid: {bid}, Ask: {ask}, Simulated: {is_simulated})")
                
                # Check if it's live data
                if is_simulated:
                    logger.warning(f"⚠️  {symbol}: Still getting simulated data!")
                else:
                    logger.info(f"✅ {symbol}: Live data confirmed!")
            else:
                logger.error(f"❌ {symbol}: Failed to get price")
                
        except Exception as e:
            logger.error(f"❌ {symbol}: Error - {e}")
    
    logger.info("\n=== TEST COMPLETE ===")

async def test_symbol_mapping():
    """Test symbol mapping"""
    logger.info("=== SYMBOL MAPPING TEST ===")
    
    mappings = signal_generator.deriv_symbols
    
    for display_name, deriv_symbol in mappings.items():
        logger.info(f"{display_name} -> {deriv_symbol}")
    
    logger.info("=== MAPPING TEST COMPLETE ===")

if __name__ == "__main__":
    logger.info(f"App ID: {config.deriv_app_id}")
    logger.info(f"Deriv Token: {config.deriv_token[:10]}..." if config.deriv_token else "None")
    
    asyncio.run(test_symbol_mapping())
    asyncio.run(test_live_prices())
