#!/usr/bin/env python3
"""
Test signal generator with detailed logging
"""
import asyncio
import logging
import os
from signal_generator import signal_generator

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_signal_detailed():
    """Test signal generator with detailed logging"""
    logger.info("=== DETAILED SIGNAL TEST ===")
    
    # Test getting current price for Volatility 10
    symbol = 'Volatility 10 Index'
    logger.info(f"Testing {symbol}...")
    
    try:
        # Get current price
        logger.info("Calling get_current_price...")
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
        import traceback
        traceback.print_exc()
    
    logger.info("=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_signal_detailed())
