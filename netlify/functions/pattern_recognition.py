def detect_candlestick_patterns(opens, highs, lows, closes):
    """Detect candlestick patterns in price data"""
    patterns = []
    
    for i in range(len(closes)-1):
        # Single Candlestick Patterns
        # Doji
        body = abs(closes[i] - opens[i])
        total_range = highs[i] - lows[i]
        if total_range > 0 and body / total_range < 0.1:
            patterns.append({
                'index': i,
                'type': 'Doji',
                'significance': 'neutral',
                'reliability': 0.6
            })
        
        # Hammer/Hanging Man
        if total_range > 0:
            upper_shadow = highs[i] - max(opens[i], closes[i])
            lower_shadow = min(opens[i], closes[i]) - lows[i]
            if lower_shadow > 2 * body and upper_shadow < 0.1 * total_range:
                pattern_type = 'Hammer' if closes[i] > opens[i] else 'Hanging Man'
                patterns.append({
                    'index': i,
                    'type': pattern_type,
                    'significance': 'bullish' if pattern_type == 'Hammer' else 'bearish',
                    'reliability': 0.7
                })
        
        # Two Candlestick Patterns
        if i > 0:
            # Bullish Engulfing
            if (closes[i] > opens[i] and 
                opens[i] < closes[i-1] and 
                closes[i] > opens[i-1] and
                opens[i-1] > closes[i-1]):
                patterns.append({
                    'index': i,
                    'type': 'Bullish Engulfing',
                    'significance': 'bullish',
                    'reliability': 0.8
                })
            
            # Bearish Engulfing
            if (closes[i] < opens[i] and 
                opens[i] > closes[i-1] and 
                closes[i] < opens[i-1] and
                opens[i-1] < closes[i-1]):
                patterns.append({
                    'index': i,
                    'type': 'Bearish Engulfing',
                    'significance': 'bearish',
                    'reliability': 0.8
                })

    return patterns

def detect_price_action_patterns(highs, lows, closes, volume):
    """Detect SMC-specific price action patterns"""
    patterns = []
    
    for i in range(3, len(closes)-1):
        # Double Top
        if (highs[i] > highs[i-1] and 
            abs(highs[i] - highs[i-2]) < highs[i] * 0.01 and
            volume[i] > volume[i-2] * 1.5):
            patterns.append({
                'index': i,
                'type': 'Double Top',
                'significance': 'bearish',
                'reliability': 0.75,
                'target': highs[i] - (highs[i] - lows[i-1])
            })
        
        # Double Bottom
        if (lows[i] < lows[i-1] and 
            abs(lows[i] - lows[i-2]) < abs(lows[i] * 0.01) and
            volume[i] > volume[i-2] * 1.5):
            patterns.append({
                'index': i,
                'type': 'Double Bottom',
                'significance': 'bullish',
                'reliability': 0.75,
                'target': lows[i] + (highs[i-1] - lows[i])
            })
        
        # SMC Break of Structure (BOS)
        if i >= 4:
            # Bullish BOS
            if (lows[i] > lows[i-1] and
                lows[i-1] < lows[i-2] and
                highs[i] > highs[i-1] and
                volume[i] > volume[i-1] * 1.2):
                patterns.append({
                    'index': i,
                    'type': 'Bullish BOS',
                    'significance': 'bullish',
                    'reliability': 0.85,
                    'target': highs[i] + (highs[i] - lows[i-1])
                })
            
            # Bearish BOS
            if (highs[i] < highs[i-1] and
                highs[i-1] > highs[i-2] and
                lows[i] < lows[i-1] and
                volume[i] > volume[i-1] * 1.2):
                patterns.append({
                    'index': i,
                    'type': 'Bearish BOS',
                    'significance': 'bearish',
                    'reliability': 0.85,
                    'target': lows[i] - (highs[i-1] - lows[i])
                })

    return patterns

def detect_chart_patterns(highs, lows, closes, volume):
    """Detect complex chart patterns"""
    patterns = []
    
    # Head and Shoulders
    for i in range(5, len(closes)-5):
        # Left shoulder
        left_shoulder = max(highs[i-5:i-2])
        # Head
        head = max(highs[i-2:i+2])
        # Right shoulder
        right_shoulder = max(highs[i+2:i+5])
        
        # Check pattern formation
        if (abs(left_shoulder - right_shoulder) < head * 0.02 and
            head > left_shoulder * 1.02 and
            head > right_shoulder * 1.02):
            neckline = min(lows[i-3:i+3])
            patterns.append({
                'index': i,
                'type': 'Head and Shoulders',
                'significance': 'bearish',
                'reliability': 0.8,
                'target': neckline - (head - neckline)
            })
    
    # Inverse Head and Shoulders
    for i in range(5, len(closes)-5):
        # Left shoulder
        left_shoulder = min(lows[i-5:i-2])
        # Head
        head = min(lows[i-2:i+2])
        # Right shoulder
        right_shoulder = min(lows[i+2:i+5])
        
        # Check pattern formation
        if (abs(left_shoulder - right_shoulder) < abs(head * 0.02) and
            head < left_shoulder * 0.98 and
            head < right_shoulder * 0.98):
            neckline = max(highs[i-3:i+3])
            patterns.append({
                'index': i,
                'type': 'Inverse Head and Shoulders',
                'significance': 'bullish',
                'reliability': 0.8,
                'target': neckline + (neckline - head)
            })
    
    return patterns

def analyze_patterns(highs, lows, opens, closes, volume):
    """Perform complete pattern analysis"""
    candlestick_patterns = detect_candlestick_patterns(opens, highs, lows, closes)
    price_action_patterns = detect_price_action_patterns(highs, lows, closes, volume)
    chart_patterns = detect_chart_patterns(highs, lows, closes, volume)
    
    return {
        'candlestick_patterns': candlestick_patterns,
        'price_action_patterns': price_action_patterns,
        'chart_patterns': chart_patterns
    }