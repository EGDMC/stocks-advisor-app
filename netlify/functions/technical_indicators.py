import json
import os
import numpy as np
import pandas as pd
from datetime import datetime

def calculate_technical_indicators(data):
    """Calculate various technical indicators"""
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
        df['SMA_20'] = calculate_sma(df['Close'], 20)
        df['SMA_50'] = calculate_sma(df['Close'], 50)
        df['RSI'] = calculate_rsi(df['Close'])
        df['MACD'], df['Signal'] = calculate_macd(df['Close'])
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = calculate_bollinger_bands(df['Close'])
        df['ADX'] = calculate_adx(df)
        df['ATR'] = calculate_atr(df)
        df['OBV'] = calculate_obv(df)

        # Get latest values
        latest = {
            'sma_20': float(df['SMA_20'].iloc[-1]),
            'sma_50': float(df['SMA_50'].iloc[-1]),
            'rsi': float(df['RSI'].iloc[-1]),
            'macd': float(df['MACD'].iloc[-1]),
            'macd_signal': float(df['Signal'].iloc[-1]),
            'bb_upper': float(df['BB_Upper'].iloc[-1]),
            'bb_middle': float(df['BB_Middle'].iloc[-1]),
            'bb_lower': float(df['BB_Lower'].iloc[-1]),
            'adx': float(df['ADX'].iloc[-1]),
            'atr': float(df['ATR'].iloc[-1]),
            'obv': float(df['OBV'].iloc[-1])
        }

        # Generate signals
        signals = generate_signals(df)

        return {
            'status': 'success',
            'indicators': latest,
            'signals': signals
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    return prices.rolling(window=period).mean()

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

def calculate_bollinger_bands(prices, period=20, std=2):
    """Calculate Bollinger Bands"""
    middle = prices.rolling(window=period).mean()
    std_dev = prices.rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return upper, middle, lower

def calculate_adx(df, period=14):
    """Calculate Average Directional Index"""
    tr1 = df['High'] - df['Low']
    tr2 = abs(df['High'] - df['Close'].shift(1))
    tr3 = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.DataFrame([tr1, tr2, tr3]).max()
    dx = pd.DataFrame([tr1, tr2, tr3]).mean()
    adx = dx.rolling(window=period).mean()
    return adx

def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    tr1 = df['High'] - df['Low']
    tr2 = abs(df['High'] - df['Close'].shift(1))
    tr3 = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.DataFrame([tr1, tr2, tr3]).max()
    return tr.rolling(window=period).mean()

def calculate_obv(df):
    """Calculate On Balance Volume"""
    obv = (df['Volume'] * (~df['Close'].diff().le(0) * 2 - 1)).cumsum()
    return obv

def generate_signals(df):
    """Generate trading signals based on indicators"""
    signals = []
    
    # RSI signals
    rsi = df['RSI'].iloc[-1]
    if rsi > 70:
        signals.append({"indicator": "RSI", "signal": "Overbought", "value": rsi})
    elif rsi < 30:
        signals.append({"indicator": "RSI", "signal": "Oversold", "value": rsi})
    
    # MACD signals
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1] and df['MACD'].iloc[-2] <= df['Signal'].iloc[-2]:
        signals.append({"indicator": "MACD", "signal": "Bullish Crossover", "value": df['MACD'].iloc[-1]})
    elif df['MACD'].iloc[-1] < df['Signal'].iloc[-1] and df['MACD'].iloc[-2] >= df['Signal'].iloc[-2]:
        signals.append({"indicator": "MACD", "signal": "Bearish Crossover", "value": df['MACD'].iloc[-1]})
    
    # Bollinger Bands signals
    last_close = df['Close'].iloc[-1]
    if last_close > df['BB_Upper'].iloc[-1]:
        signals.append({"indicator": "Bollinger Bands", "signal": "Price Above Upper Band", "value": last_close})
    elif last_close < df['BB_Lower'].iloc[-1]:
        signals.append({"indicator": "Bollinger Bands", "signal": "Price Below Lower Band", "value": last_close})
    
    # ADX signals
    adx = df['ADX'].iloc[-1]
    if adx > 25:
        signals.append({"indicator": "ADX", "signal": "Strong Trend", "value": adx})
    
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
        
        # Calculate indicators
        result = calculate_technical_indicators(data)
        
        # Print result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }))

if __name__ == "__main__":
    main()