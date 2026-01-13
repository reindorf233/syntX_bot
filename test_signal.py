#!/usr/bin/env python3
"""
Test signal generator with live API data
"""
import asyncio
import logging
import os
from signal_generator import signal_generator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_signal_generator():
    """Test signal generator with live data"""
    logger.info("=== SIGNAL GENERATOR TEST ===")
    
    # Test getting current price for Volatility 10
    symbol = 'Volatility 10 Index'
    logger.info(f"Testing {symbol}...")
    
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
                
            # Test analysis
            logger.info(f"Testing analysis for {symbol}...")
            signal = await signal_generator.analyze_symbol(symbol)
            
            if signal:
                logger.info(f"✅ Signal generated:")
                logger.info(f"  - Direction: {signal['direction']}")
                logger.info(f"  - Strength: {signal['strength']}")
                logger.info(f"  - Entry: {signal['entry_price']}")
                logger.info(f"  - Current: {signal['current_price']}")
                logger.info(f"  - Simulated: {signal['is_simulated']}")
                
                if not signal['is_simulated']:
                    logger.info(f"✅ {symbol}: Live signal confirmed!")
                else:
                    logger.warning(f"⚠️  {symbol}: Still simulated signal!")
            else:
                logger.error(f"❌ {symbol}: No signal generated")
                
        else:
            logger.error(f"❌ {symbol}: Failed to get price")
            
    except Exception as e:
        logger.error(f"❌ {symbol}: Error - {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("=== TEST COMPLETE ===")

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['DERIV_APP_ID'] = '120931'
    os.environ['DERIV_TOKEN'] = 'RNaduc1QRp2NxMJ'
    
    asyncio.run(test_signal_generator())
