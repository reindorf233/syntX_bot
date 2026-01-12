# Enhanced Backtesting Module
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Backtester:
    """Advanced backtesting engine for strategy validation"""
    
    def __init__(self, initial_balance: float = 1000.0, risk_per_trade: float = 0.01):
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.results = {}
        
    def run_backtest(self, historical_data: pd.DataFrame, signals: List[Dict]) -> Dict:
        """Run comprehensive backtest on historical data with signals"""
        try:
            trades = []
            balance = self.initial_balance
            max_balance = balance
            max_drawdown = 0
            wins = 0
            losses = 0
            total_profit = 0
            total_loss = 0
            
            for signal in signals:
                # Get signal entry point
                entry_time = signal.get('timestamp')
                entry_price = signal.get('entry_price')
                stop_loss = signal.get('stop_loss')
                take_profit = signal.get('take_profit')
                direction = signal.get('direction')
                
                if not all([entry_time, entry_price, stop_loss, take_profit, direction]):
                    continue
                
                # Calculate position size
                risk_amount = balance * self.risk_per_trade
                if direction == 'bullish':
                    stop_distance = entry_price - stop_loss
                else:
                    stop_distance = stop_loss - entry_price
                
                if stop_distance <= 0:
                    continue
                
                position_size = risk_amount / stop_distance
                
                # Simulate trade execution
                trade_result = self._simulate_trade(
                    historical_data, entry_time, entry_price, 
                    stop_loss, take_profit, direction
                )
                
                if trade_result:
                    profit_loss = trade_result['profit_loss']
                    balance += profit_loss
                    
                    # Update statistics
                    if profit_loss > 0:
                        wins += 1
                        total_profit += profit_loss
                    else:
                        losses += 1
                        total_loss += abs(profit_loss)
                    
                    # Track max drawdown
                    if balance > max_balance:
                        max_balance = balance
                    drawdown = (max_balance - balance) / max_balance
                    max_drawdown = max(max_drawdown, drawdown)
                    
                    trades.append({
                        'entry_time': entry_time,
                        'entry_price': entry_price,
                        'exit_price': trade_result['exit_price'],
                        'profit_loss': profit_loss,
                        'direction': direction,
                        'duration': trade_result['duration'],
                        'exit_reason': trade_result['exit_reason']
                    })
            
            # Calculate metrics
            total_trades = wins + losses
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            avg_win = total_profit / wins if wins > 0 else 0
            avg_loss = total_loss / losses if losses > 0 else 0
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            expectancy = ((win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)) if total_trades > 0 else 0
            total_return = ((balance - self.initial_balance) / self.initial_balance) * 100
            
            self.results = {
                'total_trades': total_trades,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'expectancy': expectancy,
                'total_return': total_return,
                'max_drawdown': max_drawdown * 100,
                'final_balance': balance,
                'trades': trades
            }
            
            return self.results
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {}
    
    def _simulate_trade(self, data: pd.DataFrame, entry_time: datetime, 
                     entry_price: float, stop_loss: float, take_profit: float, 
                     direction: str) -> Optional[Dict]:
        """Simulate individual trade execution"""
        try:
            # Find entry point in data
            entry_data = data[data.index >= entry_time]
            if entry_data.empty:
                return None
            
            # Simulate trade progression
            for i, (timestamp, row) in enumerate(entry_data.iterrows()):
                current_price = row['close']
                
                # Check exit conditions
                if direction == 'bullish':
                    if current_price >= take_profit:
                        return {
                            'exit_price': take_profit,
                            'profit_loss': (take_profit - entry_price) * (entry_price / stop_loss),
                            'duration': i,
                            'exit_reason': 'take_profit'
                        }
                    elif current_price <= stop_loss:
                        return {
                            'exit_price': stop_loss,
                            'profit_loss': (stop_loss - entry_price) * (entry_price / stop_loss),
                            'duration': i,
                            'exit_reason': 'stop_loss'
                        }
                else:  # bearish
                    if current_price <= take_profit:
                        return {
                            'exit_price': take_profit,
                            'profit_loss': (entry_price - take_profit) * (entry_price / stop_loss),
                            'duration': i,
                            'exit_reason': 'take_profit'
                        }
                    elif current_price >= stop_loss:
                        return {
                            'exit_price': stop_loss,
                            'profit_loss': (entry_price - stop_loss) * (entry_price / stop_loss),
                            'duration': i,
                            'exit_reason': 'stop_loss'
                        }
            
            # If no exit found, use last price
            last_price = entry_data.iloc[-1]['close']
            if direction == 'bullish':
                profit_loss = (last_price - entry_price) * (entry_price / stop_loss)
            else:
                profit_loss = (entry_price - last_price) * (entry_price / stop_loss)
            
            return {
                'exit_price': last_price,
                'profit_loss': profit_loss,
                'duration': len(entry_data),
                'exit_reason': 'end_of_data'
            }
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return None
    
    def generate_report(self) -> str:
        """Generate comprehensive backtest report"""
        if not self.results:
            return "❌ No backtest results available"
        
        report = f"📊 *Backtest Results*\n\n"
        report += f"📈 *Performance Metrics:*\n"
        report += f"• Total Trades: {self.results['total_trades']}\n"
        report += f"• Win Rate: {self.results['win_rate']:.1f}%\n"
        report += f"• Total Return: {self.results['total_return']:.1f}%\n"
        report += f"• Max Drawdown: {self.results['max_drawdown']:.1f}%\n\n"
        
        report += f"💰 *Trade Analysis:*\n"
        report += f"• Wins: {self.results['wins']} | Losses: {self.results['losses']}\n"
        report += f"• Avg Win: ${self.results['avg_win']:.2f}\n"
        report += f"• Avg Loss: ${self.results['avg_loss']:.2f}\n"
        report += f"• Profit Factor: {self.results['profit_factor']:.2f}\n"
        report += f"• Expectancy: ${self.results['expectancy']:.2f}\n\n"
        
        report += f"📊 *Final Balance: ${self.results['final_balance']:.2f}*\n"
        
        # Performance assessment
        if self.results['win_rate'] > 50 and self.results['profit_factor'] > 1.5:
            report += f"✅ *Strategy is PROFITABLE*\n"
        elif self.results['win_rate'] > 45 and self.results['profit_factor'] > 1.2:
            report += f"⚠️ *Strategy is MODERATE*\n"
        else:
            report += f"❌ *Strategy needs IMPROVEMENT*\n"
        
        return report
    
    def get_best_signals(self, signals: List[Dict], top_n: int = 10) -> List[Dict]:
        """Get top performing signals from backtest"""
        if not self.results or not self.results.get('trades'):
            return signals[:top_n]
        
        # Analyze which signal characteristics performed best
        profitable_trades = [t for t in self.results['trades'] if t['profit_loss'] > 0]
        
        if not profitable_trades:
            return signals[:top_n]
        
        # Sort by profit and return top signals
        sorted_signals = sorted(signals, key=lambda x: x.get('strength', 0), reverse=True)
        return sorted_signals[:top_n]

# Global backtester instance
backtester = Backtester()
