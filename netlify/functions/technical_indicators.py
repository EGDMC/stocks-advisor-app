def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        return [100] * len(prices)
    
    rs = avg_gain / avg_loss
    rsi = [100 - (100 / (1 + rs))]
    
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
    
    # Pad the beginning with None values
    return [None] * period + rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    # Calculate EMAs
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = [data[0]]
        
        for price in data[1:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        
        return ema_values
    
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    
    # Calculate MACD line
    macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(prices))]
    
    # Calculate Signal line
    signal_line = ema(macd_line, signal)
    
    # Calculate Histogram
    histogram = [macd_line[i] - signal_line[i] for i in range(len(prices))]
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    def sma(data, window):
        return [sum(data[i:i+window]) / window for i in range(len(data) - window + 1)]
    
    def standard_deviation(data, window):
        means = sma(data, window)
        squared_diff = []
        
        for i in range(len(data) - window + 1):
            variance = sum((x - means[i]) ** 2 for x in data[i:i+window]) / window
            squared_diff.append(variance ** 0.5)
        
        return squared_diff
    
    middle_band = sma(prices, period)
    std_values = standard_deviation(prices, period)
    
    upper_band = [middle_band[i] + (std_dev * std_values[i]) for i in range(len(middle_band))]
    lower_band = [middle_band[i] - (std_dev * std_values[i]) for i in range(len(middle_band))]
    
    # Pad the beginning with None values
    padding = [None] * (len(prices) - len(middle_band))
    return {
        'upper': padding + upper_band,
        'middle': padding + middle_band,
        'lower': padding + lower_band
    }

def analyze_technicals(prices):
    """Perform technical analysis and return indicators"""
    analysis = {
        'rsi': calculate_rsi(prices),
        'macd': calculate_macd(prices),
        'bollinger': calculate_bollinger_bands(prices)
    }
    
    # Add technical signals
    current_rsi = analysis['rsi'][-1]
    if current_rsi is not None:
        analysis['signals'] = {
            'rsi': {
                'value': round(current_rsi, 2),
                'condition': 'oversold' if current_rsi < 30 else 'overbought' if current_rsi > 70 else 'neutral'
            },
            'macd': {
                'trend': 'bullish' if analysis['macd']['histogram'][-1] > 0 else 'bearish',
                'strength': abs(round(analysis['macd']['histogram'][-1], 2))
            },
            'bollinger': {
                'width': round(analysis['bollinger']['upper'][-1] - analysis['bollinger']['lower'][-1], 2),
                'position': 'upper' if prices[-1] > analysis['bollinger']['middle'][-1] else 'lower'
            }
        }
    
    return analysis