import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import io
import sys

def analyze_data(file_content):
    """Analyze market data from CSV content"""
    try:
        # Read CSV content
        df = pd.read_csv(io.StringIO(file_content))
        
        # Ensure required columns exist
        required_columns = ['Date', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert Date column
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Sort by date
        df = df.sort_values('Date')
        
        # Calculate basic indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = calculate_rsi(df['Close'])
        
        # Determine trend
        trend = determine_trend(df)
        
        # Prepare chart data
        chart_data = prepare_chart_data(df)
        
        # Generate prediction
        prediction = generate_prediction(df)
        
        return {
            'status': 'success',
            'trend': trend,
            'chart_data': chart_data,
            'indicators': {
                'sma_20': float(df['SMA_20'].iloc[-1]),
                'sma_50': float(df['SMA_50'].iloc[-1]),
                'rsi': float(df['RSI'].iloc[-1]),
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
                'message': str(e)
            }
        }

def calculate_rsi(prices, periods=14):
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:periods+1]
    up = seed[seed >= 0].sum()/periods
    down = -seed[seed < 0].sum()/periods
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:periods] = 100. - 100./(1. + rs)
    
    for i in range(periods, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
            
        up = (up*(periods - 1) + upval)/periods
        down = (down*(periods - 1) + downval)/periods
        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)
        
    return rsi

def determine_trend(df):
    """Determine market trend"""
    last_sma_20 = df['SMA_20'].iloc[-1]
    last_sma_50 = df['SMA_50'].iloc[-1]
    last_close = df['Close'].iloc[-1]
    
    if last_close > last_sma_20 and last_sma_20 > last_sma_50:
        return 'Bullish'
    elif last_close < last_sma_20 and last_sma_20 < last_sma_50:
        return 'Bearish'
    else:
        return 'Neutral'

def prepare_chart_data(df):
    """Prepare data for Plotly charts"""
    return [{
        'x': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'y': df['Close'].tolist(),
        'type': 'scatter',
        'name': 'Price'
    }, {
        'x': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'y': df['SMA_20'].tolist(),
        'type': 'scatter',
        'name': 'SMA 20'
    }, {
        'x': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'y': df['SMA_50'].tolist(),
        'type': 'scatter',
        'name': 'SMA 50'
    }]

def generate_prediction(df):
    """Generate simple prediction based on technical indicators"""
    last_close = df['Close'].iloc[-1]
    last_sma_20 = df['SMA_20'].iloc[-1]
    last_sma_50 = df['SMA_50'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # Simple prediction logic
    if last_close > last_sma_20 and last_rsi < 70:
        direction = "Up"
        confidence = min(90, 60 + ((last_close - last_sma_20) / last_sma_20 * 100))
        recommendation = "BUY"
    elif last_close < last_sma_20 and last_rsi > 30:
        direction = "Down"
        confidence = min(90, 60 + ((last_sma_20 - last_close) / last_sma_20 * 100))
        recommendation = "SELL"
    else:
        direction = "Sideways"
        confidence = 50
        recommendation = "HOLD"
    
    return {
        'direction': direction,
        'confidence': round(confidence, 2),
        'recommendation': recommendation,
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Main function to handle requests"""
    try:
        # Get file content from environment variable
        file_content = os.environ.get('FILE_CONTENT')
        if not file_content:
            raise ValueError("No file content provided")
            
        # Analyze data
        result = analyze_data(file_content)
        
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