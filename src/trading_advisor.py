from models.smc_analyzer import SMCAnalyzer
from models.ai_predictor import AIPredictor
import pandas as pd
import numpy as np

class TradingAdvisor:
    def __init__(self, ai_model_type='mlp'):
        """Initialize the trading advisor with specified AI model type"""
        self.smc_analyzer = SMCAnalyzer()
        self.ai_predictor = AIPredictor(model_type=ai_model_type)
        
    def calculate_risk_reward_ratio(self, entry, target, stop):
        """Calculate risk-reward ratio for a trade"""
        if stop >= entry:  # For short positions
            risk = stop - entry
            reward = entry - target
        else:  # For long positions
            risk = entry - stop
            reward = target - entry
            
        return (reward / risk) if risk != 0 else 0
    
    def analyze_trade_setup(self, data):
        """Perform complete trade analysis using SMC and AI"""
        # Ensure we have enough data
        if len(data) < 25:  # Minimum required for analysis
            raise ValueError("Not enough data points. Need at least 25 data points.")
            
        # Get SMC analysis
        smc_analysis = self.smc_analyzer.analyze_market_structure(data)
        
        try:
            # Get AI predictions
            ai_metrics = self.ai_predictor.get_prediction_metrics(data)
            
            # Current price
            current_price = data['close'].iloc[-1]
            
            # Determine trade direction
            trend = smc_analysis['trend']
            ai_movement = ai_metrics['predicted_movement']
            
            # Find closest support and resistance from liquidity zones
            support = min([zone['price'] for zone in smc_analysis['liquidity_zones']] or [current_price * 0.95])
            resistance = max([zone['price'] for zone in smc_analysis['liquidity_zones']] or [current_price * 1.05])
            
            # Calculate entry, target, and stop levels
            if trend.startswith('Bullish') and ai_movement == 'Up':
                entry = current_price
                target = resistance
                stop = support
                action = 'BUY'
            elif trend.startswith('Bearish') and ai_movement == 'Down':
                entry = current_price
                target = support
                stop = resistance
                action = 'SELL'
            else:
                action = 'WAIT'
                entry = target = stop = current_price
            
            # Calculate risk-reward ratio
            rrr = self.calculate_risk_reward_ratio(entry, target, stop)
            
            return {
                'market_structure': {
                    'trend': trend,
                    'bos_choch': 'Detected' if smc_analysis['order_blocks'] else 'Not Detected',
                    'order_blocks': [f"{block['type'].capitalize()} OB at {block['top']:.2f}-{block['bottom']:.2f}"
                                   for block in smc_analysis['order_blocks']],
                    'liquidity_zones': [f"Zone at {zone['price']:.2f}" for zone in smc_analysis['liquidity_zones']],
                    'fair_value_gaps': [f"{gap['type'].capitalize()} FVG at {gap['top']:.2f}-{gap['bottom']:.2f}"
                                      for gap in smc_analysis['fvg_zones']]
                },
                'ai_prediction': {
                    'next_price': ai_metrics['predicted_price'],
                    'movement': ai_movement,
                    'change_percent': ai_metrics['predicted_change_percent'],
                    'confidence': ai_metrics['confidence']
                },
                'trade_recommendation': {
                    'action': action,
                    'entry': entry,
                    'target': target,
                    'stop_loss': stop,
                    'risk_reward_ratio': rrr
                },
                'summary': self._generate_summary(action, trend, ai_movement, rrr)
            }
        except Exception as e:
            raise Exception(f"Error during analysis: {str(e)}")
    
    def _generate_summary(self, action, trend, ai_movement, rrr):
        """Generate a summary explanation for the trade recommendation"""
        if action == 'WAIT':
            return ("Market conditions are unclear. SMC analysis shows conflicting signals "
                   "with AI predictions. Recommend waiting for clearer setup.")
        
        return (
            f"Recommended {action} based on {trend} trend alignment with {ai_movement} "
            f"AI prediction. Risk-Reward ratio: {rrr:.2f}. "
            f"Trade shows {'favorable' if rrr >= 2 else 'moderate'} probability of success "
            f"based on SMC structure and AI analysis."
        )
    
    def train_ai_model(self, training_data):
        """Train the AI prediction model with historical data"""
        return self.ai_predictor.train(training_data)
    
    def save_models(self, path):
        """Save trained AI models"""
        self.ai_predictor.save_model(path)
    
    def load_models(self, path):
        """Load trained AI models"""
        self.ai_predictor.load_model(path)