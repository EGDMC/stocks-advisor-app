from base import BaseAnalyzer, run_analysis
import numpy as np
from datetime import datetime, timedelta

class TrendAnalyzer(BaseAnalyzer):
    def analyze(self):
        """Predict market trend using multiple indicators"""
        # Get trend and confidence
        trend_data = self.determine_trend()
        
        # Calculate key levels
        levels = self._calculate_key_levels()
        
        # Generate future dates
        future_dates = [self.df.index[-1] + timedelta(days=x) for x in range(1, 6)]
        future_dates = [d.strftime('%Y-%m-%d') for d in future_dates]
        
        # Calculate next target
        target = self._calculate_target(trend_data['trend'])
        
        return {
            'status': 'success',
            'current_trend': trend_data['trend'],
            'confidence': trend_data['confidence'],
            'next_target': float(target),
            'key_levels': levels,
            'projection': {
                'dates': future_dates,
                'values': self._calculate_projection(trend_data['trend'], len(future_dates))
            }
        }

    def _calculate_key_levels(self):
        """Calculate key price levels"""
        recent = self.df.tail(20)
        
        # Find support levels
        support = recent['Low'].min()
        strong_support = recent['Low'].nsmallest(3).mean()
        
        # Find resistance levels
        resistance = recent['High'].max()
        strong_resistance = recent['High'].nlargest(3).mean()
        
        # Find pivot points
        typical = (recent['High'] + recent['Low'] + recent['Close']) / 3
        pivot = typical.mean()
        
        return {
            'support': float(support),
            'strong_support': float(strong_support),
            'resistance': float(resistance),
            'strong_resistance': float(strong_resistance),
            'pivot': float(pivot)
        }

    def _calculate_target(self, trend):
        """Calculate next price target"""
        latest = self.df.iloc[-1]
        atr = latest['ATR']
        
        if trend == 'Bullish':
            # Target based on ATR and recent resistance
            resistance = self._calculate_key_levels()['resistance']
            return min(latest['Close'] + (atr * 3), resistance * 1.02)
        elif trend == 'Bearish':
            # Target based on ATR and recent support
            support = self._calculate_key_levels()['support']
            return max(latest['Close'] - (atr * 3), support * 0.98)
        else:
            # Neutral trend - target near current price
            return latest['Close']

    def _calculate_projection(self, trend, periods):
        """Project future prices based on trend"""
        latest = self.df.iloc[-1]
        atr = latest['ATR']
        close = latest['Close']
        
        # Calculate trend multiplier
        if trend == 'Bullish':
            multiplier = 1
        elif trend == 'Bearish':
            multiplier = -1
        else:
            multiplier = 0
        
        # Add random noise to make projection more realistic
        noise = np.random.normal(0, atr * 0.1, periods)
        
        # Generate projections
        projections = [
            round(close + (atr * multiplier * (i + 1)) + noise[i], 2)
            for i in range(periods)
        ]
        
        return projections

    def _analyze_momentum(self):
        """Analyze price momentum"""
        latest = self.df.iloc[-1]
        
        # RSI momentum
        rsi_momentum = 1 if latest['RSI'] > 50 else -1 if latest['RSI'] < 50 else 0
        
        # MACD momentum
        macd_momentum = 1 if latest['MACD'] > latest['Signal'] else -1
        
        # Price momentum (based on moving averages)
        price_momentum = (1 if latest['Close'] > latest['SMA_20'] > latest['SMA_50'] else
                         -1 if latest['Close'] < latest['SMA_20'] < latest['SMA_50'] else 0)
        
        # Combined momentum score
        momentum_score = (rsi_momentum + macd_momentum + price_momentum) / 3
        
        return {
            'score': momentum_score,
            'strength': 'Strong' if abs(momentum_score) > 0.7 else
                       'Moderate' if abs(momentum_score) > 0.3 else 'Weak'
        }

    def _analyze_volume_trend(self):
        """Analyze volume trend"""
        recent = self.df.tail(5)
        avg_volume = recent['Volume'].mean()
        latest_volume = recent['Volume'].iloc[-1]
        
        # Volume trend
        volume_trend = 'Increasing' if latest_volume > avg_volume * 1.1 else \
                      'Decreasing' if latest_volume < avg_volume * 0.9 else \
                      'Stable'
        
        # Volume strength
        strength = 'Strong' if latest_volume > avg_volume * 1.5 else \
                  'Weak' if latest_volume < avg_volume * 0.5 else \
                  'Moderate'
        
        return {
            'trend': volume_trend,
            'strength': strength,
            'ratio': latest_volume / avg_volume
        }

if __name__ == "__main__":
    run_analysis(TrendAnalyzer)