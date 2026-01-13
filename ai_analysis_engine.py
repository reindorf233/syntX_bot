#!/usr/bin/env python3
"""
AI Analysis Module for syntX Bot
Uses AI API for enhanced trading analysis and predictions
"""
import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class AIAnalysisEngine:
    """AI-powered trading analysis engine"""
    
    def __init__(self, ai_api_key: str = None):
        self.ai_api_key = ai_api_key or os.getenv('AI_API_KEY', '46398b22307b44a9958c41c6c566f869')
        self.ai_provider = os.getenv('AI_PROVIDER', 'openai')  # openai, anthropic, gemini
        self.model_name = os.getenv('AI_MODEL', 'gpt-4')
        
        # AI Analysis weights
        self.ai_weights = {
            'pattern_recognition': 0.30,
            'sentiment_analysis': 0.20,
            'market_prediction': 0.25,
            'risk_assessment': 0.15,
            'optimization': 0.10
        }
        
        # AI confidence thresholds
        self.confidence_threshold = 0.75
        self.max_risk_per_trade = 0.02  # 2% max risk
        
    async def analyze_with_ai(self, symbol: str, price_data: pd.DataFrame, 
                           market_data: Dict, technical_indicators: Dict) -> Dict:
        """Comprehensive AI analysis of trading opportunity"""
        try:
            logger.info(f"🤖 Starting AI analysis for {symbol}")
            
            # Prepare data for AI
            ai_input = self.prepare_ai_data(symbol, price_data, market_data, technical_indicators)
            
            # Get AI predictions from multiple models
            ai_predictions = await self.get_ai_predictions(ai_input)
            
            # Analyze patterns with AI
            pattern_analysis = await self.analyze_patterns_with_ai(price_data, ai_predictions)
            
            # Market sentiment analysis
            sentiment_analysis = await self.analyze_market_sentiment(symbol, market_data)
            
            # Predictive analysis
            prediction_analysis = await self.predict_market_movement(price_data, ai_predictions)
            
            # Risk assessment with AI
            risk_analysis = await self.assess_risk_with_ai(symbol, price_data, technical_indicators)
            
            # Optimize entry/exit with AI
            optimization = await self.optimize_trade_parameters(price_data, ai_predictions)
            
            # Combine all AI analyses
            ai_signal = self.combine_ai_analyses(
                pattern_analysis, sentiment_analysis, 
                prediction_analysis, risk_analysis, optimization
            )
            
            # Add AI metadata
            ai_signal.update({
                'ai_confidence': ai_predictions.get('confidence', 0.0),
                'ai_model': self.model_name,
                'ai_provider': self.ai_provider,
                'ai_timestamp': datetime.now().isoformat(),
                'ai_predictions': ai_predictions,
                'is_ai_enhanced': True
            })
            
            logger.info(f"✅ AI analysis complete for {symbol} - Confidence: {ai_signal['ai_confidence']:.2f}")
            return ai_signal
            
        except Exception as e:
            logger.error(f"❌ AI analysis error for {symbol}: {e}")
            return self.get_fallback_signal(symbol, price_data)
    
    def prepare_ai_data(self, symbol: str, price_data: pd.DataFrame, 
                      market_data: Dict, technical_indicators: Dict) -> Dict:
        """Prepare data for AI analysis"""
        try:
            # Recent price action
            recent_prices = price_data['close'].tail(50).tolist()
            price_changes = np.diff(recent_prices).tolist()
            
            # Technical indicators summary
            technical_summary = {
                'rsi': technical_indicators.get('rsi', 50),
                'macd': technical_indicators.get('macd', 0),
                'bb_position': technical_indicators.get('bb_position', 0.5),
                'volume_trend': technical_indicators.get('volume_trend', 0),
                'atr': technical_indicators.get('atr', 50)
            }
            
            # Market context
            market_context = {
                'symbol': symbol,
                'timeframe': '5min',
                'market_session': self.get_market_session(),
                'volatility_regime': self.detect_volatility_regime(price_data),
                'trend_strength': self.calculate_trend_strength(price_data)
            }
            
            return {
                'symbol': symbol,
                'recent_prices': recent_prices[-20:],  # Last 20 prices
                'price_changes': price_changes[-19:],
                'technical_indicators': technical_summary,
                'market_context': market_context,
                'analysis_type': 'trading_signal'
            }
            
        except Exception as e:
            logger.error(f"❌ AI data preparation error: {e}")
            return {}
    
    async def get_ai_predictions(self, ai_input: Dict) -> Dict:
        """Get predictions from AI API"""
        try:
            if not self.ai_api_key:
                logger.warning("⚠️ No AI API key - using local analysis")
                return self.get_local_ai_predictions(ai_input)
            
            # Prepare prompt for AI
            prompt = self.create_ai_prompt(ai_input)
            
            # Call AI API based on provider
            if self.ai_provider == 'openai':
                return await self.call_openai_api(prompt)
            elif self.ai_provider == 'anthropic':
                return await self.call_anthropic_api(prompt)
            elif self.ai_provider == 'gemini':
                return await self.call_gemini_api(prompt)
            else:
                return self.get_local_ai_predictions(ai_input)
                
        except Exception as e:
            logger.error(f"❌ AI API error: {e}")
            return self.get_local_ai_predictions(ai_input)
    
    def create_ai_prompt(self, ai_input: Dict) -> str:
        """Create comprehensive prompt for AI analysis"""
        prompt = f"""
You are an expert trading analyst AI. Analyze the following market data and provide trading recommendations.

SYMBOL: {ai_input.get('symbol', 'Unknown')}
TIMEFRAME: {ai_input.get('market_context', {}).get('timeframe', '5min')}

RECENT PRICE ACTION:
{json.dumps(ai_input.get('recent_prices', []), indent=2)}

TECHNICAL INDICATORS:
{json.dumps(ai_input.get('technical_indicators', {}), indent=2)}

MARKET CONTEXT:
{json.dumps(ai_input.get('market_context', {}), indent=2)}

ANALYSIS REQUIRED:
1. Pattern Recognition: Identify chart patterns, support/resistance levels, trend lines
2. Market Sentiment: Assess bullish/bearish bias based on price action
3. Prediction: Forecast likely price movement in next 1-5 candles
4. Risk Assessment: Evaluate risk/reward ratio and probability
5. Optimization: Suggest optimal entry, stop loss, take profit levels

RESPONSE FORMAT (JSON):
{{
    "direction": "BULLISH/BEARISH/NEUTRAL",
    "confidence": 0.0-1.0,
    "entry_price": 0.0,
    "stop_loss": 0.0,
    "take_profit": 0.0,
    "risk_reward": 0.0,
    "patterns_found": ["pattern1", "pattern2"],
    "key_levels": {{
        "support": [level1, level2],
        "resistance": [level1, level2]
    }},
    "reasoning": "Detailed analysis explanation",
    "risk_factors": ["factor1", "factor2"],
    "probability_of_success": 0.0-1.0
}}

Provide only the JSON response, no additional text.
"""
        return prompt
    
    async def call_openai_api(self, prompt: str) -> Dict:
        """Call OpenAI API for analysis"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.ai_api_key)
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse AI response")
                return self.get_local_ai_predictions({})
                
        except ImportError:
            logger.warning("⚠️ OpenAI library not installed")
            return self.get_local_ai_predictions({})
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return self.get_local_ai_predictions({})
    
    async def call_anthropic_api(self, prompt: str) -> Dict:
        """Call Anthropic API for analysis"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.ai_api_key)
            
            response = client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text.strip()
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse Anthropic response")
                return self.get_local_ai_predictions({})
                
        except ImportError:
            logger.warning("⚠️ Anthropic library not installed")
            return self.get_local_ai_predictions({})
        except Exception as e:
            logger.error(f"❌ Anthropic API error: {e}")
            return self.get_local_ai_predictions({})
    
    async def call_gemini_api(self, prompt: str) -> Dict:
        """Call Google Gemini API for analysis"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.ai_api_key)
            model = genai.GenerativeModel(self.model_name)
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse Gemini response")
                return self.get_local_ai_predictions({})
                
        except ImportError:
            logger.warning("⚠️ Gemini library not installed")
            return self.get_local_ai_predictions({})
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            return self.get_local_ai_predictions({})
    
    def get_local_ai_predictions(self, ai_input: Dict) -> Dict:
        """Fallback local AI analysis when API is unavailable"""
        try:
            # Simple pattern recognition
            recent_prices = ai_input.get('recent_prices', [])
            if len(recent_prices) < 10:
                return self.get_default_ai_response()
            
            # Calculate basic indicators
            prices = np.array(recent_prices)
            returns = np.diff(prices) / prices[:-1]
            
            # Trend analysis
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-20:])
            
            # Volatility analysis
            volatility = np.std(returns) * 100
            
            # Simple prediction logic
            if short_ma > long_ma and volatility > 0.5:
                direction = "BULLISH"
                confidence = min(0.8, 0.5 + volatility * 0.3)
            elif short_ma < long_ma and volatility > 0.5:
                direction = "BEARISH"
                confidence = min(0.8, 0.5 + volatility * 0.3)
            else:
                direction = "NEUTRAL"
                confidence = 0.3
            
            current_price = prices[-1]
            atr = volatility * current_price / 100
            
            return {
                'direction': direction,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': current_price - (atr * 1.5) if direction == 'BULLISH' else current_price + (atr * 1.5),
                'take_profit': current_price + (atr * 2.0) if direction == 'BULLISH' else current_price - (atr * 2.0),
                'risk_reward': 2.0,
                'patterns_found': ['trend_following', 'momentum'],
                'key_levels': {
                    'support': [current_price - (atr * 2), current_price - (atr * 4)],
                    'resistance': [current_price + (atr * 2), current_price + (atr * 4)]
                },
                'reasoning': f"Local AI analysis based on {direction} trend with {volatility:.2f}% volatility",
                'risk_factors': ['market_volatility', 'trend_reversal_risk'],
                'probability_of_success': confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Local AI analysis error: {e}")
            return self.get_default_ai_response()
    
    def get_default_ai_response(self) -> Dict:
        """Default AI response when analysis fails"""
        return {
            'direction': 'NEUTRAL',
            'confidence': 0.3,
            'entry_price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'risk_reward': 1.0,
            'patterns_found': [],
            'key_levels': {'support': [], 'resistance': []},
            'reasoning': 'AI analysis unavailable - using default values',
            'risk_factors': ['no_ai_analysis'],
            'probability_of_success': 0.3
        }
    
    async def analyze_patterns_with_ai(self, price_data: pd.DataFrame, 
                                    ai_predictions: Dict) -> Dict:
        """AI-enhanced pattern recognition"""
        try:
            patterns = []
            confidence = 0.0
            
            # Candlestick patterns
            patterns.extend(self.detect_candlestick_patterns(price_data))
            
            # Chart patterns
            patterns.extend(self.detect_chart_patterns(price_data))
            
            # AI-identified patterns
            ai_patterns = ai_predictions.get('patterns_found', [])
            patterns.extend(ai_patterns)
            
            # Calculate pattern confidence
            if patterns:
                confidence = min(0.9, len(patterns) * 0.15 + ai_predictions.get('confidence', 0.0))
            
            return {
                'patterns': patterns,
                'confidence': confidence,
                'primary_pattern': patterns[0] if patterns else 'none'
            }
            
        except Exception as e:
            logger.error(f"❌ Pattern analysis error: {e}")
            return {'patterns': [], 'confidence': 0.0, 'primary_pattern': 'none'}
    
    async def analyze_market_sentiment(self, symbol: str, market_data: Dict) -> Dict:
        """AI-powered market sentiment analysis"""
        try:
            # Price-based sentiment
            price_changes = market_data.get('price_changes', [])
            if not price_changes:
                return {'sentiment': 'NEUTRAL', 'confidence': 0.5}
            
            # Calculate sentiment indicators
            positive_changes = sum(1 for change in price_changes if change > 0)
            negative_changes = sum(1 for change in price_changes if change < 0)
            total_changes = len(price_changes)
            
            bullish_ratio = positive_changes / total_changes if total_changes > 0 else 0.5
            
            # Determine sentiment
            if bullish_ratio > 0.6:
                sentiment = 'BULLISH'
                confidence = min(0.9, bullish_ratio)
            elif bullish_ratio < 0.4:
                sentiment = 'BEARISH'
                confidence = min(0.9, 1.0 - bullish_ratio)
            else:
                sentiment = 'NEUTRAL'
                confidence = 0.5
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'bullish_ratio': bullish_ratio,
                'momentum': np.mean(price_changes) if price_changes else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis error: {e}")
            return {'sentiment': 'NEUTRAL', 'confidence': 0.5}
    
    async def predict_market_movement(self, price_data: pd.DataFrame, 
                                  ai_predictions: Dict) -> Dict:
        """AI-powered market movement prediction"""
        try:
            # Time series prediction
            prices = price_data['close'].values
            
            # Simple ML prediction (fallback)
            prediction = self.simple_time_series_prediction(prices)
            
            # AI prediction enhancement
            ai_direction = ai_predictions.get('direction', 'NEUTRAL')
            ai_confidence = ai_predictions.get('confidence', 0.5)
            
            # Combine predictions
            if ai_direction != 'NEUTRAL' and ai_confidence > 0.7:
                final_direction = ai_direction
                final_confidence = ai_confidence
            else:
                final_direction = prediction['direction']
                final_confidence = prediction['confidence']
            
            return {
                'predicted_direction': final_direction,
                'confidence': final_confidence,
                'time_horizon': '1-5 candles',
                'predicted_move': prediction.get('predicted_move', 0),
                'ai_enhanced': ai_confidence > 0.7
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {'predicted_direction': 'NEUTRAL', 'confidence': 0.3}
    
    async def assess_risk_with_ai(self, symbol: str, price_data: pd.DataFrame, 
                               technical_indicators: Dict) -> Dict:
        """AI-enhanced risk assessment"""
        try:
            # Calculate risk factors
            volatility = technical_indicators.get('atr', 50) / price_data['close'].iloc[-1] * 100
            rsi = technical_indicators.get('rsi', 50)
            
            # Risk scoring
            risk_factors = []
            risk_score = 0.0
            
            # Volatility risk
            if volatility > 2.0:
                risk_factors.append('high_volatility')
                risk_score += 0.3
            
            # RSI risk
            if rsi > 80 or rsi < 20:
                risk_factors.append('extreme_rsi')
                risk_score += 0.2
            
            # Trend risk
            trend_strength = self.calculate_trend_strength(price_data)
            if trend_strength < 0.3:
                risk_factors.append('weak_trend')
                risk_score += 0.2
            
            # Market regime risk
            regime = self.detect_volatility_regime(price_data)
            if regime == 'high_volatility':
                risk_factors.append('volatile_regime')
                risk_score += 0.3
            
            # Risk level classification
            if risk_score < 0.3:
                risk_level = 'LOW'
            elif risk_score < 0.6:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'HIGH'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'max_position_size': self.calculate_position_size(risk_score),
                'recommended_stop_distance': volatility * 1.5
            }
            
        except Exception as e:
            logger.error(f"❌ Risk assessment error: {e}")
            return {'risk_level': 'MEDIUM', 'risk_score': 0.5, 'risk_factors': ['analysis_error']}
    
    async def optimize_trade_parameters(self, price_data: pd.DataFrame, 
                                   ai_predictions: Dict) -> Dict:
        """AI-powered trade parameter optimization"""
        try:
            current_price = price_data['close'].iloc[-1]
            volatility = price_data['close'].pct_change().std() * 100
            
            # AI confidence-based optimization
            confidence = ai_predictions.get('confidence', 0.5)
            
            # Dynamic position sizing
            if confidence > 0.8:
                position_size = 0.02  # 2%
            elif confidence > 0.6:
                position_size = 0.015  # 1.5%
            else:
                position_size = 0.01  # 1%
            
            # Optimized stop loss and take profit
            atr = volatility * current_price / 100
            
            if confidence > 0.7:
                stop_distance = atr * 1.2  # Tighter stop for high confidence
                profit_distance = atr * 2.5  # Larger target for high confidence
            else:
                stop_distance = atr * 1.8  # Wider stop for low confidence
                profit_distance = atr * 2.0  # Standard target
            
            return {
                'optimized_position_size': position_size,
                'optimized_stop_loss': stop_distance,
                'optimized_take_profit': profit_distance,
                'risk_reward_ratio': profit_distance / stop_distance,
                'confidence_based_sizing': True
            }
            
        except Exception as e:
            logger.error(f"❌ Parameter optimization error: {e}")
            return {
                'optimized_position_size': 0.01,
                'optimized_stop_loss': 50,
                'optimized_take_profit': 100,
                'risk_reward_ratio': 2.0,
                'confidence_based_sizing': False
            }
    
    def combine_ai_analyses(self, pattern_analysis: Dict, sentiment_analysis: Dict,
                           prediction_analysis: Dict, risk_analysis: Dict, 
                           optimization: Dict) -> Dict:
        """Combine all AI analyses into final signal"""
        try:
            # Calculate weighted score
            pattern_score = pattern_analysis.get('confidence', 0.0) * self.ai_weights['pattern_recognition']
            sentiment_score = sentiment_analysis.get('confidence', 0.0) * self.ai_weights['sentiment_analysis']
            prediction_score = prediction_analysis.get('confidence', 0.0) * self.ai_weights['market_prediction']
            risk_score = (1.0 - risk_analysis.get('risk_score', 0.5)) * self.ai_weights['risk_assessment']
            optimization_score = optimization.get('risk_reward_ratio', 2.0) / 10.0 * self.ai_weights['optimization']
            
            total_score = pattern_score + sentiment_score + prediction_score + risk_score + optimization_score
            
            # Determine final direction
            direction_votes = [
                prediction_analysis.get('predicted_direction', 'NEUTRAL'),
                sentiment_analysis.get('sentiment', 'NEUTRAL'),
                pattern_analysis.get('primary_pattern', 'NEUTRAL')
            ]
            
            bullish_votes = sum(1 for d in direction_votes if d == 'BULLISH')
            bearish_votes = sum(1 for d in direction_votes if d == 'BEARISH')
            
            if bullish_votes > bearish_votes:
                final_direction = 'BULLISH'
            elif bearish_votes > bullish_votes:
                final_direction = 'BEARISH'
            else:
                final_direction = 'NEUTRAL'
            
            return {
                'direction': final_direction,
                'strength': min(10.0, total_score * 10),
                'confidence': total_score,
                'pattern_analysis': pattern_analysis,
                'sentiment_analysis': sentiment_analysis,
                'prediction_analysis': prediction_analysis,
                'risk_analysis': risk_analysis,
                'optimization': optimization,
                'ai_weighted_score': total_score
            }
            
        except Exception as e:
            logger.error(f"❌ AI combination error: {e}")
            return {'direction': 'NEUTRAL', 'strength': 0.0, 'confidence': 0.0}
    
    def get_fallback_signal(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """Fallback signal when AI analysis fails"""
        try:
            current_price = price_data['close'].iloc[-1]
            
            return {
                'direction': 'NEUTRAL',
                'strength': 0.0,
                'confidence': 0.0,
                'entry_price': current_price,
                'stop_loss': current_price * 0.98,
                'take_profit': current_price * 1.02,
                'risk_reward': 1.0,
                'ai_confidence': 0.0,
                'is_ai_enhanced': False,
                'fallback_reason': 'AI_analysis_failed'
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback signal error: {e}")
            return {'direction': 'NEUTRAL', 'strength': 0.0}
    
    # Helper methods
    def get_market_session(self) -> str:
        """Determine current market session"""
        hour = datetime.now().hour
        
        if 0 <= hour < 8:
            return 'asian'
        elif 8 <= hour < 16:
            return 'london'
        elif 16 <= hour < 22:
            return 'new_york'
        else:
            return 'asian'
    
    def detect_volatility_regime(self, price_data: pd.DataFrame) -> str:
        """Detect current volatility regime"""
        try:
            returns = price_data['close'].pct_change().dropna()
            volatility = returns.std() * 100
            
            if volatility < 0.5:
                return 'low_volatility'
            elif volatility < 1.5:
                return 'normal_volatility'
            else:
                return 'high_volatility'
        except:
            return 'normal_volatility'
    
    def calculate_trend_strength(self, price_data: pd.DataFrame) -> float:
        """Calculate trend strength"""
        try:
            prices = price_data['close'].values
            if len(prices) < 20:
                return 0.5
            
            # Linear regression for trend
            x = np.arange(len(prices))
            slope, _ = np.polyfit(x, prices, 1)
            
            # Normalize slope
            price_range = np.max(prices) - np.min(prices)
            normalized_slope = abs(slope) / price_range if price_range > 0 else 0
            
            return min(1.0, normalized_slope * 100)
        except:
            return 0.5
    
    def detect_candlestick_patterns(self, price_data: pd.DataFrame) -> List[str]:
        """Detect basic candlestick patterns"""
        patterns = []
        
        try:
            if len(price_data) < 3:
                return patterns
            
            # Last 3 candles
            recent = price_data.tail(3)
            
            # Doji pattern
            for i in range(1, len(recent)):
                body_size = abs(recent.iloc[i]['close'] - recent.iloc[i]['open'])
                range_size = recent.iloc[i]['high'] - recent.iloc[i]['low']
                
                if body_size < range_size * 0.1:
                    patterns.append('doji')
            
            # Engulfing patterns
            for i in range(1, len(recent)):
                prev_candle = recent.iloc[i-1]
                curr_candle = recent.iloc[i]
                
                # Bullish engulfing
                if (prev_candle['close'] < prev_candle['open'] and
                    curr_candle['close'] > curr_candle['open'] and
                    curr_candle['open'] < prev_candle['close']):
                    patterns.append('bullish_engulfing')
                
                # Bearish engulfing
                elif (prev_candle['close'] > prev_candle['open'] and
                      curr_candle['close'] < curr_candle['open'] and
                      curr_candle['open'] > prev_candle['close']):
                    patterns.append('bearish_engulfing')
        
        except Exception as e:
            logger.error(f"❌ Candlestick pattern error: {e}")
        
        return patterns
    
    def detect_chart_patterns(self, price_data: pd.DataFrame) -> List[str]:
        """Detect basic chart patterns"""
        patterns = []
        
        try:
            if len(price_data) < 20:
                return patterns
            
            # Support and resistance
            highs = price_data['high'].rolling(10).max()
            lows = price_data['low'].rolling(10).min()
            
            current_price = price_data['close'].iloc[-1]
            current_high = highs.iloc[-1]
            current_low = lows.iloc[-1]
            
            # Near resistance
            if current_price > current_high * 0.98:
                patterns.append('near_resistance')
            
            # Near support
            if current_price < current_low * 1.02:
                patterns.append('near_support')
            
            # Breakout patterns
            if current_price > current_high:
                patterns.append('resistance_breakout')
            elif current_price < current_low:
                patterns.append('support_breakout')
        
        except Exception as e:
            logger.error(f"❌ Chart pattern error: {e}")
        
        return patterns
    
    def simple_time_series_prediction(self, prices: np.ndarray) -> Dict:
        """Simple time series prediction"""
        try:
            if len(prices) < 10:
                return {'direction': 'NEUTRAL', 'confidence': 0.3, 'predicted_move': 0}
            
            # Simple momentum prediction
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-20:])
            
            if short_ma > long_ma * 1.01:
                return {'direction': 'BULLISH', 'confidence': 0.6, 'predicted_move': 0.5}
            elif short_ma < long_ma * 0.99:
                return {'direction': 'BEARISH', 'confidence': 0.6, 'predicted_move': -0.5}
            else:
                return {'direction': 'NEUTRAL', 'confidence': 0.3, 'predicted_move': 0}
        
        except Exception as e:
            logger.error(f"❌ Time series prediction error: {e}")
            return {'direction': 'NEUTRAL', 'confidence': 0.3, 'predicted_move': 0}
    
    def calculate_position_size(self, risk_score: float) -> float:
        """Calculate position size based on risk"""
        if risk_score < 0.3:
            return 0.02  # 2% for low risk
        elif risk_score < 0.6:
            return 0.015  # 1.5% for medium risk
        else:
            return 0.01  # 1% for high risk
