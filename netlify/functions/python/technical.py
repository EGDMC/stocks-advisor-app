from base import BaseAnalyzer, run_analysis

class TechnicalAnalyzer(BaseAnalyzer):
    def analyze(self):
        """Analyze technical indicators"""
        # Get latest indicator values
        indicators = self.get_latest_values()
        
        # Generate signals
        signals = self._generate_signals()
        
        return {
            'status': 'success',
            'indicators': indicators,
            'signals': signals
        }

    def _generate_signals(self):
        """Generate trading signals based on technical indicators"""
        signals = []
        latest = self.df.iloc[-1]
        
        # RSI signals
        if latest['RSI'] > 70:
            signals.append({
                'indicator': 'RSI',
                'signal': 'Overbought',
                'strength': 'Strong',
                'value': float(latest['RSI'])
            })
        elif latest['RSI'] < 30:
            signals.append({
                'indicator': 'RSI',
                'signal': 'Oversold',
                'strength': 'Strong',
                'value': float(latest['RSI'])
            })
        
        # MACD signals
        if latest['MACD'] > latest['Signal'] and self.df['MACD'].iloc[-2] <= self.df['Signal'].iloc[-2]:
            signals.append({
                'indicator': 'MACD',
                'signal': 'Bullish Crossover',
                'strength': 'Moderate',
                'value': float(latest['MACD'])
            })
        elif latest['MACD'] < latest['Signal'] and self.df['MACD'].iloc[-2] >= self.df['Signal'].iloc[-2]:
            signals.append({
                'indicator': 'MACD',
                'signal': 'Bearish Crossover',
                'strength': 'Moderate',
                'value': float(latest['MACD'])
            })
        
        # Moving Average signals
        if latest['Close'] > latest['SMA_20'] and latest['SMA_20'] > latest['SMA_50']:
            signals.append({
                'indicator': 'Moving Averages',
                'signal': 'Strong Uptrend',
                'strength': 'Strong',
                'value': float(latest['Close'])
            })
        elif latest['Close'] < latest['SMA_20'] and latest['SMA_20'] < latest['SMA_50']:
            signals.append({
                'indicator': 'Moving Averages',
                'signal': 'Strong Downtrend',
                'strength': 'Strong',
                'value': float(latest['Close'])
            })
        
        # Bollinger Bands signals
        if latest['Close'] > latest['BB_Upper']:
            signals.append({
                'indicator': 'Bollinger Bands',
                'signal': 'Price Above Upper Band',
                'strength': 'Strong',
                'value': float(latest['Close'])
            })
        elif latest['Close'] < latest['BB_Lower']:
            signals.append({
                'indicator': 'Bollinger Bands',
                'signal': 'Price Below Lower Band',
                'strength': 'Strong',
                'value': float(latest['Close'])
            })
        
        return signals

if __name__ == "__main__":
    run_analysis(TechnicalAnalyzer)