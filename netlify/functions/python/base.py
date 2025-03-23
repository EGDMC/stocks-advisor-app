import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

class BaseAnalyzer:
    def __init__(self):
        self.data = None
        self.df = None

    def load_data(self, input_data=None):
        """Load and validate input data"""
        if input_data is None:
            # Get input from environment variable
            input_str = os.environ.get('INPUT_DATA')
            if not input_str:
                raise ValueError("No input data provided")
            input_data = json.loads(input_str)

        # Convert to DataFrame
        self.df = pd.DataFrame({
            'Date': pd.to_datetime(input_data['dates']),
            'Open': input_data['open'],
            'High': input_data['high'],
            'Low': input_data['low'],
            'Close': input_data['close'],
            'Volume': input_data['volume']
        }).set_index('Date')

        # Calculate basic indicators
        self._calculate_basic_indicators()
        return self.df

    def _calculate_basic_indicators(self):
        """Calculate common technical indicators"""
        # Moving averages
        self.df['SMA_20'] = self.df['Close'].rolling(window=20).mean()
        self.df['SMA_50'] = self.df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = self.df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['Close'].ewm(span=26, adjust=False).mean()
        self.df['MACD'] = exp1 - exp2
        self.df['Signal'] = self.df['MACD'].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        self.df['BB_Middle'] = self.df['Close'].rolling(window=20).mean()
        std = self.df['Close'].rolling(window=20).std()
        self.df['BB_Upper'] = self.df['BB_Middle'] + (std * 2)
        self.df['BB_Lower'] = self.df['BB_Middle'] - (std * 2)

        # True Range and ATR
        tr1 = self.df['High'] - self.df['Low']
        tr2 = abs(self.df['High'] - self.df['Close'].shift())
        tr3 = abs(self.df['Low'] - self.df['Close'].shift())
        tr = pd.DataFrame([tr1, tr2, tr3]).max()
        self.df['ATR'] = tr.rolling(window=14).mean()

    def get_latest_values(self):
        """Get the latest indicator values"""
        latest = self.df.iloc[-1]
        return {
            'close': float(latest['Close']),
            'sma_20': float(latest['SMA_20']),
            'sma_50': float(latest['SMA_50']),
            'rsi': float(latest['RSI']),
            'macd': float(latest['MACD']),
            'signal': float(latest['Signal']),
            'bb_upper': float(latest['BB_Upper']),
            'bb_middle': float(latest['BB_Middle']),
            'bb_lower': float(latest['BB_Lower']),
            'atr': float(latest['ATR'])
        }

    def determine_trend(self):
        """Determine the current market trend"""
        latest = self.df.iloc[-1]
        
        if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
            trend = 'Bullish'
            confidence = min(90, 60 + (latest['RSI'] - 50))
        elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
            trend = 'Bearish'
            confidence = min(90, 60 + (50 - latest['RSI']))
        else:
            trend = 'Neutral'
            confidence = 50

        return {
            'trend': trend,
            'confidence': round(float(confidence), 2)
        }

    def generate_chart_data(self):
        """Generate basic chart data"""
        return [
            {
                'x': self.df.index.strftime('%Y-%m-%d').tolist(),
                'y': self.df['Close'].tolist(),
                'type': 'scatter',
                'name': 'Price',
                'line': {'color': '#17BECF'}
            },
            {
                'x': self.df.index.strftime('%Y-%m-%d').tolist(),
                'y': self.df['SMA_20'].tolist(),
                'type': 'scatter',
                'name': 'SMA 20',
                'line': {'color': '#7F7F7F'}
            },
            {
                'x': self.df.index.strftime('%Y-%m-%d').tolist(),
                'y': self.df['SMA_50'].tolist(),
                'type': 'scatter',
                'name': 'SMA 50',
                'line': {'color': '#FFA500'}
            }
        ]

    @staticmethod
    def format_response(data):
        """Format the response as JSON string"""
        return json.dumps(data)

def run_analysis(analyzer_class):
    """Helper function to run analysis and handle errors"""
    try:
        analyzer = analyzer_class()
        analyzer.load_data()
        result = analyzer.analyze()
        print(BaseAnalyzer.format_response(result))
    except Exception as e:
        print(BaseAnalyzer.format_response({
            'status': 'error',
            'error': str(e),
            'details': {
                'type': type(e).__name__,
                'traceback': str(e)
            }
        }))