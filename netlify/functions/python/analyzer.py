from base import BaseAnalyzer, run_analysis
import numpy as np

class SMCAnalyzer(BaseAnalyzer):
    def analyze(self):
        """Analyze market structure for high probability setups"""
        # Market structure analysis
        structure = self._analyze_market_structure()
        
        # Support/Resistance levels
        levels = self._find_key_levels()
        
        # Current setup
        setup = self._identify_setup()
        
        # Get recent indicators
        indicators = self.get_latest_values()
        
        return {
            'status': 'success',
            'market_structure': structure['type'],
            'trend': structure['trend'],
            'current_setup': setup['type'],
            'setup_confidence': setup['confidence'],
            'levels': levels,
            'indicators': indicators
        }

    def _analyze_market_structure(self):
        """Analyze current market structure"""
        # Get recent swings
        swings = self._find_swing_points(20)
        
        # Determine structure type
        if len(swings['highs']) >= 2 and len(swings['lows']) >= 2:
            # Higher highs and higher lows = Uptrend
            if (swings['highs'][-1] > swings['highs'][-2] and 
                swings['lows'][-1] > swings['lows'][-2]):
                return {'type': 'Uptrend', 'trend': 'Bullish'}
            
            # Lower highs and lower lows = Downtrend
            elif (swings['highs'][-1] < swings['highs'][-2] and 
                  swings['lows'][-1] < swings['lows'][-2]):
                return {'type': 'Downtrend', 'trend': 'Bearish'}
            
            # Sideways movement
            else:
                return {'type': 'Range', 'trend': 'Neutral'}
        
        # Default to recent trend
        trend = self.determine_trend()
        return {
            'type': 'Undefined',
            'trend': trend['trend']
        }

    def _find_key_levels(self):
        """Find key support and resistance levels"""
        recent = self.df.tail(20)
        
        # Find swing highs and lows
        swings = self._find_swing_points(20)
        
        # Calculate support levels
        supports = []
        if len(swings['lows']) > 0:
            supports = sorted(list(set([round(p, 2) for p in swings['lows']])))
        
        # Calculate resistance levels
        resistances = []
        if len(swings['highs']) > 0:
            resistances = sorted(list(set([round(p, 2) for p in swings['highs']])))
        
        # Get current price
        current_price = self.df['Close'].iloc[-1]
        
        # Find nearest levels
        support = max([s for s in supports if s < current_price], default=current_price * 0.95)
        resistance = min([r for r in resistances if r > current_price], default=current_price * 1.05)
        
        return {
            'support': float(support),
            'resistance': float(resistance)
        }

    def _identify_setup(self):
        """Identify potential trading setup"""
        structure = self._analyze_market_structure()
        trend = structure['trend']
        
        # Get latest values
        latest = self.get_latest_values()
        
        # Define basic setups
        if trend == 'Bullish':
            if latest['close'] > latest['bb_upper']:
                return {
                    'type': 'Bullish Breakout',
                    'confidence': 80 if latest['rsi'] < 70 else 60
                }
            elif latest['close'] < latest['bb_lower']:
                return {
                    'type': 'Bullish Reversal',
                    'confidence': 75 if latest['rsi'] < 30 else 55
                }
            else:
                return {
                    'type': 'Bullish Continuation',
                    'confidence': 65
                }
                
        elif trend == 'Bearish':
            if latest['close'] < latest['bb_lower']:
                return {
                    'type': 'Bearish Breakout',
                    'confidence': 80 if latest['rsi'] > 30 else 60
                }
            elif latest['close'] > latest['bb_upper']:
                return {
                    'type': 'Bearish Reversal',
                    'confidence': 75 if latest['rsi'] > 70 else 55
                }
            else:
                return {
                    'type': 'Bearish Continuation',
                    'confidence': 65
                }
        
        return {
            'type': 'No Clear Setup',
            'confidence': 0
        }

    def _find_swing_points(self, lookback=20):
        """Find swing high and low points"""
        highs = []
        lows = []
        
        window = min(lookback, len(self.df))
        prices = self.df.tail(window)
        
        for i in range(2, len(prices) - 2):
            # Swing high
            if (prices['High'].iloc[i] > prices['High'].iloc[i-1] and 
                prices['High'].iloc[i] > prices['High'].iloc[i-2] and
                prices['High'].iloc[i] > prices['High'].iloc[i+1] and
                prices['High'].iloc[i] > prices['High'].iloc[i+2]):
                highs.append(prices['High'].iloc[i])
            
            # Swing low
            if (prices['Low'].iloc[i] < prices['Low'].iloc[i-1] and
                prices['Low'].iloc[i] < prices['Low'].iloc[i-2] and
                prices['Low'].iloc[i] < prices['Low'].iloc[i+1] and
                prices['Low'].iloc[i] < prices['Low'].iloc[i+2]):
                lows.append(prices['Low'].iloc[i])
        
        return {
            'highs': highs,
            'lows': lows
        }

if __name__ == "__main__":
    run_analysis(SMCAnalyzer)