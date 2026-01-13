# AI/ML Signal Validation with PyTorch
# Install: pip install torch

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
import pickle
import os

logger = logging.getLogger(__name__)

class SignalValidatorNN(nn.Module):
    """Neural Network for signal validation"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 1):
        super(SignalValidatorNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, output_size)
        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))
        return x

class AISignalValidator:
    """AI-powered signal validation and enhancement"""
    
    def __init__(self, model_path: str = "ai_model.pth"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.is_trained = False
        
    def _create_model(self, input_size: int = 10):
        """Create and initialize the neural network"""
        self.model = SignalValidatorNN(input_size=input_size).to(self.device)
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
    def _extract_features(self, signal_data: Dict) -> np.ndarray:
        """Extract features from signal data for AI prediction"""
        features = []
        
        # Technical indicators
        features.append(signal_data.get('rsi', 50) / 100.0)  # RSI normalized
        features.append(signal_data.get('macd_diff', 0) / 100.0)  # MACD diff normalized
        features.append(signal_data.get('bb_position', 0.5))  # BB position
        features.append(signal_data.get('ema_slope', 0))  # EMA slope
        features.append(signal_data.get('atr_ratio', 0))  # ATR ratio
        
        # SMC features
        features.append(signal_data.get('fvg_count', 0) / 10.0)  # FVG count normalized
        features.append(signal_data.get('order_block_count', 0) / 5.0)  # Order blocks normalized
        features.append(signal_data.get('sweep_count', 0) / 5.0)  # Sweeps normalized
        
        # Price action features
        features.append(signal_data.get('price_change_pct', 0))  # Recent price change
        features.append(signal_data.get('volume_ratio', 1.0))  # Volume ratio
        
        return np.array(features, dtype=np.float32)
    
    def train_model(self, training_data: List[Dict], labels: List[int], epochs: int = 20):
        """Train the AI model on historical data"""
        try:
            if not training_data or not labels:
                logger.error("No training data provided")
                return False
            
            # Extract features
            features = [self._extract_features(data) for data in training_data]
            X = torch.FloatTensor(features).to(self.device)
            y = torch.FloatTensor(labels).to(self.device).view(-1, 1)
            
            # Create model if not exists
            if self.model is None:
                self._create_model(input_size=len(features[0]))
            
            # Training loop
            self.model.train()
            for epoch in range(epochs):
                # Forward pass
                outputs = self.model(X)
                loss = self.criterion(outputs, y)
                
                # Backward pass and optimize
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                if (epoch + 1) % 5 == 0:
                    logger.info(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
            
            self.is_trained = True
            self._save_model()
            logger.info(f"AI model trained successfully - Final loss: {loss.item():.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Error training AI model: {e}")
            return False
    
    def validate_signal(self, signal_data: Dict) -> Tuple[float, str]:
        """Validate signal using AI model"""
        try:
            if not self.is_trained or self.model is None:
                return 0.5, "AI model not trained"
            
            self.model.eval()
            with torch.no_grad():
                features = self._extract_features(signal_data)
                features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
                
                prediction = self.model(features_tensor)
                confidence = prediction.item()
                
                # Generate insight based on confidence
                if confidence > 0.8:
                    insight = f"AI model predicts {confidence*100:.0f}% chance of success - Strong signal"
                elif confidence > 0.7:
                    insight = f"AI model predicts {confidence*100:.0f}% chance of success - Good signal"
                elif confidence > 0.6:
                    insight = f"AI model predicts {confidence*100:.0f}% chance of success - Moderate signal"
                else:
                    insight = f"AI model predicts {confidence*100:.0f}% chance of success - Weak signal"
                
                return confidence, insight
                
        except Exception as e:
            logger.error(f"Error validating signal with AI: {e}")
            return 0.5, "AI validation failed"
    
    def enhance_signal_strength(self, base_strength: float, ai_confidence: float) -> float:
        """Enhance signal strength based on AI confidence"""
        # Boost strength if AI confidence is high
        if ai_confidence > 0.8:
            return min(base_strength + 1.5, 10.0)
        elif ai_confidence > 0.7:
            return min(base_strength + 1.0, 10.0)
        elif ai_confidence > 0.6:
            return min(base_strength + 0.5, 10.0)
        else:
            return base_strength  # No enhancement for low confidence
    
    def _save_model(self):
        """Save the trained model"""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'is_trained': self.is_trained
            }, self.model_path)
            logger.info("AI model saved successfully")
        except Exception as e:
            logger.error(f"Error saving AI model: {e}")
    
    def load_model(self) -> bool:
        """Load a previously trained model"""
        try:
            if os.path.exists(self.model_path):
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                # Create model
                self._create_model()
                
                # Load states
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                self.is_trained = checkpoint.get('is_trained', False)
                
                logger.info("AI model loaded successfully")
                return True
            else:
                logger.info("No pre-trained AI model found")
                return False
                
        except Exception as e:
            logger.error(f"Error loading AI model: {e}")
            return False
    
    def should_approve_signal(self, base_strength: float, ai_confidence: float) -> bool:
        """Determine if signal should be approved based on AI validation"""
        # Only approve if base strength is good AND AI confidence is high
        if base_strength >= 7.0 and ai_confidence > 0.7:
            return True
        elif base_strength >= 8.0 and ai_confidence > 0.6:
            return True
        else:
            return False

# Global AI validator instance
ai_validator = AISignalValidator()
