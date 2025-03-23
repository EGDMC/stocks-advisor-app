from base import BaseAnalyzer, run_analysis
import numpy as np

class ChartAnalyzer(BaseAnalyzer):
    def analyze(self):
        """Generate various chart data"""
        return {
            'status': 'success',
            'charts': {
                'price_chart': self._generate_price_chart(),
                'volume_chart': self._generate_volume_chart(),
                'technical_chart': self._generate_technical_chart(),
                'indicators_chart': self._generate_indicators_chart()
            }
        }

    def _generate_price_chart(self):
        """Generate candlestick chart data"""
        dates = self.df.index.strftime('%Y-%m-%d').tolist()
        
        # Main candlestick data
        candlesticks = {
            'type': 'candlestick',
            'x': dates,
            'open': self.df['Open'].tolist(),
            'high': self.df['High'].tolist(),
            'low': self.df['Low'].tolist(),
            'close': self.df['Close'].tolist(),
            'name': 'Price'
        }

        # Moving averages
        sma20 = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['SMA_20'].tolist(),
            'name': 'SMA 20',
            'line': {'color': '#7F7F7F'}
        }
        
        sma50 = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['SMA_50'].tolist(),
            'name': 'SMA 50',
            'line': {'color': '#FFA500'}
        }

        # Bollinger Bands
        bb_upper = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['BB_Upper'].tolist(),
            'name': 'BB Upper',
            'line': {'color': '#17BECF', 'dash': 'dash'}
        }
        
        bb_lower = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['BB_Lower'].tolist(),
            'name': 'BB Lower',
            'line': {'color': '#17BECF', 'dash': 'dash'}
        }

        return {
            'data': [candlesticks, sma20, sma50, bb_upper, bb_lower],
            'layout': {
                'title': 'Price Analysis',
                'yaxis': {'title': 'Price'},
                'xaxis': {'title': 'Date'}
            }
        }

    def _generate_volume_chart(self):
        """Generate volume chart data"""
        dates = self.df.index.strftime('%Y-%m-%d').tolist()
        colors = ['green' if c >= o else 'red' 
                 for c, o in zip(self.df['Close'], self.df['Open'])]

        return {
            'data': [{
                'type': 'bar',
                'x': dates,
                'y': self.df['Volume'].tolist(),
                'marker': {'color': colors},
                'name': 'Volume'
            }],
            'layout': {
                'title': 'Volume',
                'yaxis': {'title': 'Volume'},
                'xaxis': {'title': 'Date'}
            }
        }

    def _generate_technical_chart(self):
        """Generate technical indicators chart"""
        dates = self.df.index.strftime('%Y-%m-%d').tolist()
        
        # RSI subplot
        rsi = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['RSI'].tolist(),
            'name': 'RSI',
            'yaxis': 'y2'
        }
        
        # MACD subplot
        macd = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['MACD'].tolist(),
            'name': 'MACD',
            'yaxis': 'y3'
        }
        
        signal = {
            'type': 'scatter',
            'x': dates,
            'y': self.df['Signal'].tolist(),
            'name': 'Signal',
            'yaxis': 'y3'
        }

        return {
            'data': [rsi, macd, signal],
            'layout': {
                'title': 'Technical Indicators',
                'yaxis2': {
                    'title': 'RSI',
                    'domain': [0.7, 1],
                    'showgrid': True
                },
                'yaxis3': {
                    'title': 'MACD',
                    'domain': [0.35, 0.65],
                    'showgrid': True
                }
            }
        }

    def _generate_indicators_chart(self):
        """Generate indicator summary"""
        latest = self.get_latest_values()
        trend = self.determine_trend()
        
        return {
            'current_values': latest,
            'trend': trend,
            'signals': self._generate_signals()
        }

if __name__ == "__main__":
    run_analysis(ChartAnalyzer)