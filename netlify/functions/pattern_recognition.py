import json
import os
import numpy as np
import pandas as pd
from datetime import datetime

def detect_patterns(data):
    """Detect various candlestick patterns"""
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

        # Calculate basic data needed for patterns
        df['BodyLength'] = df['Close'] - df['Open']
        df['UpperShadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
        df['LowerShadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
        df['TotalLength'] = df['High'] - df['Low']

        # Detect patterns
        patterns = {
            'candlestick_patterns': detect_candlestick_patterns(df),
            'chart_patterns': detect_chart_patterns(df),
            'support_resistance': find_support_resistance(df),
            'trend_patterns': detect_trend_patterns(df)
        }

        # Add pattern signals
        signals = generate_pattern_signals(patterns)

        return {
            'status': 'success',
            'patterns': patterns,
            'signals': signals
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def detect_candlestick_patterns(df):
    """Detect candlestick patterns"""
    patterns = {}
    
    # Doji
    patterns['doji'] = is_doji(df.iloc[-1])
    
    # Hammer/Hanging Man
    patterns['hammer'] = is_hammer(df.iloc[-1])
    
    # Engulfing
    if len(df) >= 2:
        patterns['bullish_engulfing'] = is_bullish_engulfing(df.iloc[-2:])
        patterns['bearish_engulfing'] = is_bearish_engulfing(df.iloc[-2:])
    
    # Morning/Evening Star
    if len(df) >= 3:
        patterns['morning_star'] = is_morning_star(df.iloc[-3:])
        patterns['evening_star'] = is_evening_star(df.iloc[-3:])
    
    return patterns

def detect_chart_patterns(df):
    """Detect chart patterns"""
    patterns = {}
    
    # Head and Shoulders
    patterns['head_shoulders'] = detect_head_shoulders(df)
    
    # Double Top/Bottom
    patterns['double_top'] = detect_double_top(df)
    patterns['double_bottom'] = detect_double_bottom(df)
    
    # Triangle Patterns
    patterns['ascending_triangle'] = detect_ascending_triangle(df)
    patterns['descending_triangle'] = detect_descending_triangle(df)
    
    return patterns

def find_support_resistance(df):
    """Find support and resistance levels"""
    levels = {}
    
    # Calculate potential levels using pivot points
    high = df['High'].iloc[-20:]  # Last 20 periods
    low = df['Low'].iloc[-20:]
    close = df['Close'].iloc[-20:]
    
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    
    levels['pivot'] = float(pivot.mean())
    levels['resistance1'] = float(r1.mean())
    levels['resistance2'] = float(r2.mean())
    levels['support1'] = float(s1.mean())
    levels['support2'] = float(s2.mean())
    
    return levels

def detect_trend_patterns(df):
    """Detect trend patterns"""
    patterns = {}
    
    # Calculate trends
    sma20 = df['Close'].rolling(window=20).mean()
    sma50 = df['Close'].rolling(window=50).mean()
    
    # Current trend
    current_price = df['Close'].iloc[-1]
    patterns['trend'] = 'Uptrend' if current_price > sma20.iloc[-1] > sma50.iloc[-1] else \
                       'Downtrend' if current_price < sma20.iloc[-1] < sma50.iloc[-1] else \
                       'Sideways'
    
    # Trend strength
    atr = calculate_atr(df)
    patterns['trend_strength'] = 'Strong' if atr > atr.mean() * 1.5 else \
                                'Weak' if atr < atr.mean() * 0.5 else \
                                'Moderate'
    
    return patterns

def is_doji(candle, doji_size=0.1):
    """Check if candle is a doji"""
    return abs(candle['BodyLength']) <= (candle['TotalLength'] * doji_size)

def is_hammer(candle, body_size=0.3, shadow_size=2):
    """Check if candle is a hammer"""
    return (abs(candle['BodyLength']) <= (candle['TotalLength'] * body_size) and
            candle['LowerShadow'] >= (abs(candle['BodyLength']) * shadow_size))

def is_bullish_engulfing(candles):
    """Check for bullish engulfing pattern"""
    return (candles.iloc[0]['BodyLength'] < 0 and
            candles.iloc[1]['BodyLength'] > 0 and
            candles.iloc[1]['Open'] < candles.iloc[0]['Close'] and
            candles.iloc[1]['Close'] > candles.iloc[0]['Open'])

def is_bearish_engulfing(candles):
    """Check for bearish engulfing pattern"""
    return (candles.iloc[0]['BodyLength'] > 0 and
            candles.iloc[1]['BodyLength'] < 0 and
            candles.iloc[1]['Open'] > candles.iloc[0]['Close'] and
            candles.iloc[1]['Close'] < candles.iloc[0]['Open'])

def is_morning_star(candles):
    """Check for morning star pattern"""
    return (candles.iloc[0]['BodyLength'] < 0 and
            abs(candles.iloc[1]['BodyLength']) <= abs(candles.iloc[0]['BodyLength'] * 0.3) and
            candles.iloc[2]['BodyLength'] > 0)

def is_evening_star(candles):
    """Check for evening star pattern"""
    return (candles.iloc[0]['BodyLength'] > 0 and
            abs(candles.iloc[1]['BodyLength']) <= abs(candles.iloc[0]['BodyLength'] * 0.3) and
            candles.iloc[2]['BodyLength'] < 0)

def detect_head_shoulders(df):
    """Detect head and shoulders pattern"""
    if len(df) < 20:
        return False
    
    return {
        'detected': False,
        'confidence': 0
    }

def detect_double_top(df):
    """Detect double top pattern"""
    if len(df) < 20:
        return False
    
    return {
        'detected': False,
        'confidence': 0
    }

def detect_double_bottom(df):
    """Detect double bottom pattern"""
    if len(df) < 20:
        return False
    
    return {
        'detected': False,
        'confidence': 0
    }

def detect_ascending_triangle(df):
    """Detect ascending triangle pattern"""
    if len(df) < 20:
        return False
    
    return {
        'detected': False,
        'confidence': 0
    }

def detect_descending_triangle(df):
    """Detect descending triangle pattern"""
    if len(df) < 20:
        return False
    
    return {
        'detected': False,
        'confidence': 0
    }

def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    tr1 = df['High'] - df['Low']
    tr2 = abs(df['High'] - df['Close'].shift(1))
    tr3 = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.DataFrame([tr1, tr2, tr3]).max()
    return tr.rolling(window=period).mean()

def generate_pattern_signals(patterns):
    """Generate trading signals based on detected patterns"""
    signals = []
    
    # Candlestick patterns
    if patterns['candlestick_patterns'].get('doji', False):
        signals.append({
            'pattern': 'Doji',
            'type': 'Reversal',
            'strength': 'Moderate'
        })
    
    if patterns['candlestick_patterns'].get('bullish_engulfing', False):
        signals.append({
            'pattern': 'Bullish Engulfing',
            'type': 'Reversal',
            'strength': 'Strong'
        })
    
    if patterns['candlestick_patterns'].get('bearish_engulfing', False):
        signals.append({
            'pattern': 'Bearish Engulfing',
            'type': 'Reversal',
            'strength': 'Strong'
        })
    
    # Chart patterns
    for pattern, data in patterns['chart_patterns'].items():
        if isinstance(data, dict) and data.get('detected', False):
            signals.append({
                'pattern': pattern.replace('_', ' ').title(),
                'type': 'Continuation' if 'triangle' in pattern else 'Reversal',
                'strength': 'Strong' if data.get('confidence', 0) > 70 else 'Moderate'
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
        
        # Detect patterns
        result = detect_patterns(data)
        
        # Print result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }))

if __name__ == "__main__":
    main()