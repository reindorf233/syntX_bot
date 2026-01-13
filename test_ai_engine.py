#!/usr/bin/env python3
"""
Test AI Analysis Engine
"""
import asyncio
import logging
import os
from ai_analysis_engine import AIAnalysisEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ai():
    """Test AI analysis engine"""
    logger.info("🤖 Testing AI Analysis Engine")
    
    # Initialize AI engine with your API key
    ai_engine = AIAnalysisEngine('46398b22307b44a9958c41c6c566f869')
    
    # Create sample data
    import pandas as pd
    import numpy as np
    
    # Sample price data for Volatility 10
    dates = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='5min')
    base_price = 5698.24
    
    # Generate realistic price movements
    np.random.seed(42)  # For reproducible results
    prices = []
    for i in range(50):
        change = np.random.normal(0, base_price * 0.001)  # 0.1% volatility
        price = base_price + (change * i * 0.1)
        prices.append(price)
    
    price_data = pd.DataFrame({
        'open': prices,
        'high': [p * 1.001 for p in prices],
        'low': [p * 0.999 for p in prices],
        'close': prices,
        'volume': [100] * len(prices)
    }, index=dates)
    
    # Technical indicators
    technical_indicators = {
        'rsi': 55.0,
        'macd': 2.5,
        'bb_position': 0.6,
        'volume_trend': 0.1,
        'atr': 15.0
    }
    
    # Market data
    market_data = {
        'price_changes': price_data['close'].pct_change().dropna().tolist()[-20:],
        'volume_data': price_data['volume'].tolist()[-20:],
        'high_low_data': {
            'recent_high': price_data['high'].tail(20).max(),
            'recent_low': price_data['low'].tail(20).min()
        }
    }
    
    try:
        # Test AI analysis
        logger.info("🧠 Running AI analysis...")
        ai_result = await ai_engine.analyze_with_ai(
            'Volatility 10 Index', price_data, market_data, technical_indicators
        )
        
        if ai_result:
            logger.info("✅ AI Analysis Successful!")
            logger.info(f"📊 Direction: {ai_result.get('direction', 'UNKNOWN')}")
            logger.info(f"🎯 Confidence: {ai_result.get('ai_confidence', 0):.2%}")
            logger.info(f"💰 Entry: {ai_result.get('entry_price', 0):.2f}")
            logger.info(f"🛡️ Stop Loss: {ai_result.get('stop_loss', 0):.2f}")
            logger.info(f"🎯 Take Profit: {ai_result.get('take_profit', 0):.2f}")
            logger.info(f"📈 Risk/Reward: 1:{ai_result.get('risk_reward', 0):.2f}")
            
            # Check if AI enhanced
            if ai_result.get('is_ai_enhanced', False):
                logger.info("🤖 AI Enhancement: ACTIVE")
                logger.info(f"🧠 AI Model: {ai_result.get('ai_model', 'Unknown')}")
                logger.info(f"🔌 AI Provider: {ai_result.get('ai_provider', 'Unknown')}")
            else:
                logger.info("📊 Using Local AI Analysis")
            
            return True
        else:
            logger.error("❌ AI Analysis Failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ AI Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment for testing
    os.environ['AI_API_KEY'] = '46398b22307b44a9958c41c6c566f869'
    os.environ['AI_PROVIDER'] = 'openai'
    os.environ['AI_MODEL'] = 'gpt-4'
    
    # Run test
    result = asyncio.run(test_ai())
    
    if result:
        print("\n🎉 AI Analysis Engine is WORKING! 🤖")
        print("✅ Ready for AI-enhanced trading!")
    else:
        print("\n❌ AI Analysis Engine FAILED!")
        print("🔧 Check API key and connection")
