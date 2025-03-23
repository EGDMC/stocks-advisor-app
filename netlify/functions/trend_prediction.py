import math
from statistics import mean, stdev

def calculate_trend_strength(prices, window=20):
    """Calculate trend strength using price momentum and volatility"""
    if len(prices) < window:
        return {'strength': 0, 'direction': 'neutral'}
    
    # Calculate price changes
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    recent_changes = changes[:window]
    
    # Calculate momentum
    momentum = sum(recent_changes)
    avg_momentum = momentum / window
    
    # Calculate volatility
    volatility = stdev(recent_changes) if len(recent_changes) > 1 else 0
    
    # Calculate trend strength (-1 to 1)
    strength = 0
    if volatility > 0:
        strength = avg_momentum / volatility
        strength = max(min(strength, 1), -1)  # Clamp between -1 and 1
    
    # Determine direction
    direction = 'bullish' if strength > 0.2 else 'bearish' if strength < -0.2 else 'neutral'
    
    return {
        'strength': abs(strength),
        'direction': direction
    }

def predict_breakout(prices, levels, volume, window=20):
    """Predict potential breakout levels"""
    breakouts = []
    
    if len(prices) < window:
        return breakouts
    
    recent_prices = prices[:window]
    recent_volume = volume[:window]
    avg_volume = mean(recent_volume)
    price_volatility = stdev(recent_prices)
    
    for level in levels:
        level_price = level['price']
        distance = abs(prices[0] - level_price)
        
        # Check if price is near the level
        if distance <= price_volatility:
            # Check for volume increase
            volume_increase = volume[0] > avg_volume * 1.2
            
            # Determine breakout probability
            prob_factors = []
            
            # Volume factor
            prob_factors.append(0.7 if volume_increase else 0.3)
            
            # Price momentum factor
            recent_momentum = (prices[0] - prices[window-1]) / prices[window-1]
            momentum_factor = 0.6 if abs(recent_momentum) > price_volatility / prices[0] else 0.4
            prob_factors.append(momentum_factor)
            
            # Distance factor (closer = higher probability)
            distance_factor = 1 - (distance / price_volatility)
            prob_factors.append(distance_factor)
            
            # Calculate overall probability
            probability = sum(prob_factors) / len(prob_factors)
            
            # Determine direction based on current price position
            direction = 'up' if prices[0] < level_price else 'down'
            
            breakouts.append({
                'level': level_price,
                'type': level['type'],
                'direction': direction,
                'probability': round(probability, 2),
                'volume_confirmed': volume_increase
            })
    
    return breakouts

def project_price_targets(prices, patterns, trend):
    """Project price targets based on patterns and trend"""
    targets = []
    current_price = prices[0]
    
    # Get volatility-based targets
    volatility = stdev(prices) if len(prices) > 1 else 0
    
    # Short-term targets based on volatility
    targets.append({
        'timeframe': 'short',
        'target': round(current_price * (1 + volatility / current_price), 2) if trend['direction'] == 'bullish'
                 else round(current_price * (1 - volatility / current_price), 2),
        'confidence': 0.7,
        'method': 'volatility'
    })
    
    # Add pattern-based targets
    for pattern in patterns:
        if 'target' in pattern:
            target_distance = abs(pattern['target'] - current_price)
            # Calculate confidence based on pattern reliability and target distance
            confidence = pattern['reliability'] * (1 - min(target_distance / (current_price * 2), 0.9))
            
            targets.append({
                'timeframe': 'pattern',
                'target': round(pattern['target'], 2),
                'confidence': round(confidence, 2),
                'method': pattern['type']
            })
    
    # Project trend-based targets
    if trend['strength'] > 0.3:
        trend_target = current_price * (1 + trend['strength']) if trend['direction'] == 'bullish' else current_price * (1 - trend['strength'])
        targets.append({
            'timeframe': 'trend',
            'target': round(trend_target, 2),
            'confidence': round(trend['strength'], 2),
            'method': f"{trend['direction']} trend"
        })
    
    return targets

def analyze_trend(prices, volumes, patterns, support_resistance_levels):
    """Perform complete trend analysis"""
    # Calculate basic trend metrics
    trend = calculate_trend_strength(prices)
    
    # Predict potential breakouts
    breakouts = predict_breakout(prices, support_resistance_levels, volumes)
    
    # Project price targets
    targets = project_price_targets(prices, patterns, trend)
    
    # Calculate trend metrics
    trend_metrics = {
        'momentum': round((prices[0] - prices[-1]) / prices[-1] * 100, 2),
        'volatility': round(stdev(prices) / mean(prices) * 100, 2) if len(prices) > 1 else 0,
        'volume_trend': 'increasing' if volumes[0] > mean(volumes) else 'decreasing'
    }
    
    # Sort targets by confidence
    sorted_targets = sorted(targets, key=lambda x: x['confidence'], reverse=True)
    
    return {
        'trend': trend,
        'breakouts': breakouts,
        'targets': sorted_targets,
        'metrics': trend_metrics
    }