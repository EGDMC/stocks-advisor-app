import json
import os
import numpy as np
import pandas as pd
from datetime import datetime

def generate_charts(data):
    """Generate various chart data for market analysis"""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame({
            'Date': pd.to_datetime(data['dates']),
            'Open': data['open'],
            'High': data['high'],
            'Low': data['low'],
            'Close': data['close'],
            'Volume': data['volume']
        })

        # Calculate indicators
        df = calculate_indicators(df)
        
        # Generate chart data
        charts = {
            'price_chart': generate_price_chart(df),
            'volume_chart': generate_volume_chart(df),
            'technical_chart': generate_technical_chart(df),
            'indicators_chart': generate_indicators_chart(df)
        }
        
        return {
            'status': 'success',
            'charts': charts
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def calculate_indicators(df):
    """Calculate technical indicators for charts"""
    # Moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + (df['Close'].rolling(window=20).std() * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['Close'].rolling(window=20).std() * 2)
    
    # RSI
    df['RSI'] = calculate_rsi(df['Close'])
    
    # MACD
    df['MACD'], df['Signal'] = calculate_macd(df['Close'])
    
    return df

def generate_price_chart(df):
    """Generate candlestick chart data"""
    return {
        'type': 'candlestick',
        'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'data': [
            {
                'x': date,
                'open': o,
                'high': h,
                'low': l,
                'close': c
            }
            for date, o, h, l, c in zip(
                df['Date'].dt.strftime('%Y-%m-%d'),
                df['Open'],
                df['High'],
                df['Low'],
                df['Close']
            )
        ],
        'overlays': [
            {
                'name': 'SMA 20',
                'type': 'line',
                'data': df['SMA_20'].tolist()
            },
            {
                'name': 'SMA 50',
                'type': 'line',
                'data': df['SMA_50'].tolist()
            },
            {
                'name': 'BB Upper',
                'type': 'line',
                'data': df['BB_Upper'].tolist()
            },
            {
                'name': 'BB Lower',
                'type': 'line',
                'data': df['BB_Lower'].tolist()
            }
        ]
    }

def generate_volume_chart(df):
    """Generate volume chart data"""
    return {
        'type': 'bar',
        'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'data': df['Volume'].tolist(),
        'colors': [
            'green' if c >= o else 'red'
            for c, o in zip(df['Close'], df['Open'])
        ]
    }

def generate_technical_chart(df):
    """Generate technical analysis chart data"""
    return {
        'type': 'multi',
        'charts': [
            {
                'name': 'RSI',
                'type': 'line',
                'data': df['RSI'].tolist(),
                'levels': [30, 70]
            },
            {
                'name': 'MACD',
                'type': 'line',
                'data': {
                    'macd': df['MACD'].tolist(),
                    'signal': df['Signal'].tolist(),
                    'histogram': (df['MACD'] - df['Signal']).tolist()
                }
            }
        ]
    }

def generate_indicators_chart(df):
    """Generate indicators summary chart"""
    return {
        'type': 'summary',
        'current': {
            'close': float(df['Close'].iloc[-1]),
            'sma_20': float(df['SMA_20'].iloc[-1]),
            'sma_50': float(df['SMA_50'].iloc[-1]),
            'rsi': float(df['RSI'].iloc[-1]),
            'macd': float(df['MACD'].iloc[-1]),
            'signal': float(df['Signal'].iloc[-1])
        },
        'signals': generate_signals(df)
    }

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD and Signal line"""
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def generate_signals(df):
    """Generate trading signals based on indicators"""
    signals = []
    latest = df.iloc[-1]
    
    # Moving Average signals
    if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
        signals.append({
            'type': 'MA',
            'signal': 'Bullish',
            'message': 'Price above both moving averages'
        })
    elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
        signals.append({
            'type': 'MA',
            'signal': 'Bearish',
            'message': 'Price below both moving averages'
        })
    
    # RSI signals
    if latest['RSI'] > 70:
        signals.append({
            'type': 'RSI',
            'signal': 'Overbought',
            'message': f'RSI at {round(latest["RSI"], 2)}'
        })
    elif latest['RSI'] < 30:
        signals.append({
            'type': 'RSI',
            'signal': 'Oversold',
            'message': f'RSI at {round(latest["RSI"], 2)}'
        })
    
    # MACD signals
    if latest['MACD'] > latest['Signal']:
        signals.append({
            'type': 'MACD',
            'signal': 'Bullish',
            'message': 'MACD above signal line'
        })
    else:
        signals.append({
            'type': 'MACD',
            'signal': 'Bearish',
            'message': 'MACD below signal line'
        })
    
    return signals

def main():
    """Main function to handle command line execution"""
    try:
        # Get input data from environment variable
        input_data = os.environ.get('INPUT_DATA')
        if not input_data:
            raise ValueError("No input data provided")
        
        # Parse input data
        data = json.loads(input_data)
        
        # Generate charts
        result = generate_charts(data)
        
        # Print result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }))

if __name__ == "__main__":
    main()