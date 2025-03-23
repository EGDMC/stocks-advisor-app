import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def predict_trend(data):
    """Predict market trend using multiple indicators"""
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

        # Calculate technical indicators
        df = calculate_indicators(df)
        
        # Generate prediction
        prediction = generate_prediction(df)
        
        # Calculate support/resistance levels
        levels = calculate_key_levels(df)
        
        # Generate future dates for projection
        future_dates = [df['Date'].iloc[-1] + timedelta(days=x) for x in range(1, 6)]
        
        return {
            'status': 'success',
            'current_trend': prediction['trend'],
            'future_trend': prediction['future_trend'],
            'confidence': prediction['confidence'],
            'next_target': prediction['target'],
            'key_levels': levels,
            'projection': {
                'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'values': calculate_projection(df, prediction['trend'], len(future_dates))
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def calculate_indicators(df):
    """Calculate technical indicators for trend analysis"""
    # Moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # Momentum indicators
    df['RSI'] = calculate_rsi(df['Close'])
    df['MACD'], df['Signal'] = calculate_macd(df['Close'])
    
    # Volatility
    df['ATR'] = calculate_atr(df)
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = calculate_bollinger_bands(df['Close'])
    
    # Volume analysis
    df['OBV'] = calculate_obv(df)
    
    return df

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

def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    tr1 = df['High'] - df['Low']
    tr2 = abs(df['High'] - df['Close'].shift(1))
    tr3 = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.DataFrame([tr1, tr2, tr3]).max()
    return tr.rolling(window=period).mean()

def calculate_bollinger_bands(prices, period=20, std=2):
    """Calculate Bollinger Bands"""
    middle = prices.rolling(window=period).mean()
    std_dev = prices.rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return upper, middle, lower

def calculate_obv(df):
    """Calculate On Balance Volume"""
    obv = (df['Volume'] * (~df['Close'].diff().le(0) * 2 - 1)).cumsum()
    return obv

def calculate_key_levels(df):
    """Calculate key support and resistance levels"""
    # Recent price action
    recent = df.tail(20)
    
    # Find potential support levels
    support = recent['Low'].min()
    strong_support = recent['Low'].nsmallest(3).mean()
    
    # Find potential resistance levels
    resistance = recent['High'].max()
    strong_resistance = recent['High'].nlargest(3).mean()
    
    return {
        'support': float(support),
        'strong_support': float(strong_support),
        'resistance': float(resistance),
        'strong_resistance': float(strong_resistance)
    }

def generate_prediction(df):
    """Generate trend prediction based on technical analysis"""
    # Get latest values
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Price momentum
    price_trend = 'up' if latest['Close'] > latest['SMA_20'] > latest['SMA_50'] else \
                 'down' if latest['Close'] < latest['SMA_20'] < latest['SMA_50'] else \
                 'neutral'
    
    # MACD analysis
    macd_trend = 'up' if latest['MACD'] > latest['Signal'] else 'down'
    
    # RSI analysis
    rsi_trend = 'up' if latest['RSI'] > 50 and latest['RSI'] < 70 else \
                'down' if latest['RSI'] < 50 and latest['RSI'] > 30 else \
                'neutral'
    
    # Volume confirmation
    volume_trend = 'up' if latest['OBV'] > prev['OBV'] else 'down'
    
    # Combine signals
    signals = [price_trend, macd_trend, rsi_trend, volume_trend]
    up_signals = signals.count('up')
    down_signals = signals.count('down')
    
    # Calculate overall trend and confidence
    if up_signals > down_signals:
        trend = 'Bullish'
        confidence = (up_signals / len(signals)) * 100
    elif down_signals > up_signals:
        trend = 'Bearish'
        confidence = (down_signals / len(signals)) * 100
    else:
        trend = 'Neutral'
        confidence = 50
    
    # Project future trend
    future_trend = trend if confidence > 60 else 'Neutral'
    
    # Calculate price target
    atr = latest['ATR']
    if trend == 'Bullish':
        target = latest['Close'] + (atr * 2)
    elif trend == 'Bearish':
        target = latest['Close'] - (atr * 2)
    else:
        target = latest['Close']
    
    return {
        'trend': trend,
        'future_trend': future_trend,
        'confidence': round(confidence, 2),
        'target': float(target)
    }

def calculate_projection(df, trend, periods):
    """Calculate price projection for future periods"""
    last_price = df['Close'].iloc[-1]
    atr = df['ATR'].iloc[-1]
    
    if trend == 'Bullish':
        multiplier = 1
    elif trend == 'Bearish':
        multiplier = -1
    else:
        multiplier = 0
    
    return [round(last_price + (atr * multiplier * (i + 1)), 2) for i in range(periods)]

def main():
    """Main function to handle command line execution"""
    try:
        # Get input data from environment variable
        input_data = os.environ.get('INPUT_DATA')
        if not input_data:
            raise ValueError("No input data provided")
        
        # Parse input data
        data = json.loads(input_data)
        
        # Generate prediction
        result = predict_trend(data)
        
        # Print result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }))

if __name__ == "__main__":
    main()