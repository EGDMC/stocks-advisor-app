import json
import os
import numpy as np
import pandas as pd
from datetime import datetime

def analyze_market_data(data):
    """Analyze market data using SMC principles"""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame({
            'Date': data['dates'],
            'Open': data['open'],
            'High': data['high'],
            'Low': data['low'],
            'Close': data['close'],
            'Volume': data['volume']
        })
        
        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # Calculate technical indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = calculate_rsi(df['Close'])
        df['ADX'] = calculate_adx(df)
        
        # Determine trend
        trend = determine_trend(df)
        
        # Generate chart data
        chart_data = generate_chart_data(df)
        
        # Generate prediction
        prediction = generate_prediction(df)
        
        return {
            'status': 'success',
            'trend': trend,
            'chart_data': chart_data,
            'indicators': {
                'sma_20': float(df['SMA_20'].iloc[-1]) if not pd.isna(df['SMA_20'].iloc[-1]) else None,
                'sma_50': float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else None,
                'rsi': float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else None,
                'adx': float(df['ADX'].iloc[-1]) if not pd.isna(df['ADX'].iloc[-1]) else None,
                'volume': int(df['Volume'].iloc[-1])
            },
            'prediction': prediction
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'details': {
                'type': type(e).__name__,
                'traceback': str(e)
            }
        }

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1. + rs)
    
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
            
        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down if down != 0 else 0
        rsi[i] = 100. - 100./(1. + rs)
        
    return rsi

def calculate_adx(df, period=14):
    """Calculate Average Directional Index"""
    df = df.copy()
    df['TR'] = np.maximum(df['High'] - df['Low'], 
                         np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                  abs(df['Low'] - df['Close'].shift(1))))
    df['DMplus'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
                           np.maximum(df['High'] - df['High'].shift(1), 0), 0)
    df['DMminus'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
                            np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)
    
    TR_smoothed = df['TR'].rolling(window=period).mean()
    DMplus_smoothed = df['DMplus'].rolling(window=period).mean()
    DMminus_smoothed = df['DMminus'].rolling(window=period).mean()
    
    DIplus = 100 * DMplus_smoothed / TR_smoothed
    DIminus = 100 * DMminus_smoothed / TR_smoothed
    
    DX = 100 * abs(DIplus - DIminus) / (DIplus + DIminus)
    ADX = DX.rolling(window=period).mean()
    
    return ADX

def determine_trend(df):
    """Determine market trend using multiple indicators"""
    last_close = df['Close'].iloc[-1]
    last_sma20 = df['SMA_20'].iloc[-1]
    last_sma50 = df['SMA_50'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_adx = df['ADX'].iloc[-1]
    
    # Strong trend criteria
    strong_trend = last_adx > 25
    
    if strong_trend:
        if last_close > last_sma20 and last_sma20 > last_sma50 and last_rsi > 50:
            return 'Bullish'
        elif last_close < last_sma20 and last_sma20 < last_sma50 and last_rsi < 50:
            return 'Bearish'
    
    return 'Neutral'

def generate_chart_data(df):
    """Generate chart data for Plotly"""
    return [
        {
            'x': df.index.strftime('%Y-%m-%d').tolist(),
            'y': df['Close'].tolist(),
            'type': 'scatter',
            'name': 'Price',
            'line': {'color': '#17BECF'}
        },
        {
            'x': df.index.strftime('%Y-%m-%d').tolist(),
            'y': df['SMA_20'].tolist(),
            'type': 'scatter',
            'name': 'SMA 20',
            'line': {'color': '#7F7F7F'}
        },
        {
            'x': df.index.strftime('%Y-%m-%d').tolist(),
            'y': df['SMA_50'].tolist(),
            'type': 'scatter',
            'name': 'SMA 50',
            'line': {'color': '#FFA500'}
        }
    ]

def generate_prediction(df):
    """Generate market prediction"""
    last_close = df['Close'].iloc[-1]
    last_sma20 = df['SMA_20'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_adx = df['ADX'].iloc[-1]
    
    # Initialize confidence and direction
    confidence = 50.0
    direction = "Sideways"
    
    # Strong trend detection
    if last_adx > 25:
        if last_close > last_sma20:
            direction = "Up"
            confidence = min(90, 60 + last_adx * 0.5)
            if last_rsi > 70:
                confidence *= 0.8  # Reduce confidence if overbought
        else:
            direction = "Down"
            confidence = min(90, 60 + last_adx * 0.5)
            if last_rsi < 30:
                confidence *= 0.8  # Reduce confidence if oversold
    
    # Generate recommendation
    if direction == "Up" and confidence > 65:
        recommendation = "BUY"
    elif direction == "Down" and confidence > 65:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
    
    return {
        'direction': direction,
        'confidence': round(confidence, 2),
        'recommendation': recommendation,
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Main function to handle command line execution"""
    try:
        # Get input data from environment variable
        input_data = os.environ.get('INPUT_DATA')
        if not input_data:
            raise ValueError("No input data provided")
        
        # Parse input data
        data = json.loads(input_data)
        
        # Analyze data
        result = analyze_market_data(data['data'])
        
        # Print result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()