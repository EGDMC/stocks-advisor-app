import numpy as np
from typing import List, Dict, Any

def detect_order_blocks(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray) -> List[Dict[str, Any]]:
    """Detect institutional order blocks based on price action and volume."""
    order_blocks = []
    lookback = 10  # Look back period for order block detection
    
    for i in range(len(closes)-lookback, 0, -1):
        # Bullish order block conditions
        if (closes[i] > closes[i-1] and    # Strong close
            volumes[i] > np.mean(volumes[i:i+lookback]) * 1.5 and  # High volume
            any(closes[i:i+lookback] > closes[i] * 1.02)):  # Price moved away
            
            order_blocks.append({
                'type': 'bullish',
                'price_high': highs[i],
                'price_low': lows[i],
                'volume': volumes[i],
                'strength': volumes[i] / np.mean(volumes[i:i+lookback]),
                'index': i
            })
        
        # Bearish order block conditions
        elif (closes[i] < closes[i-1] and  # Strong drop
              volumes[i] > np.mean(volumes[i:i+lookback]) * 1.5 and  # High volume
              any(closes[i:i+lookback] < closes[i] * 0.98)):  # Price moved away
            
            order_blocks.append({
                'type': 'bearish',
                'price_high': highs[i],
                'price_low': lows[i],
                'volume': volumes[i],
                'strength': volumes[i] / np.mean(volumes[i:i+lookback]),
                'index': i
            })
    
    return order_blocks

def analyze_volume_profile(prices: np.ndarray, volumes: np.ndarray, num_bins: int = 50) -> Dict[str, Any]:
    """Analyze volume distribution across price levels."""
    # Create price bins
    price_bins = np.linspace(min(prices), max(prices), num_bins)
    volume_profile = np.zeros(num_bins-1)
    
    # Calculate volume for each price level
    for i in range(len(prices)):
        bin_idx = np.digitize(prices[i], price_bins) - 1
        if 0 <= bin_idx < len(volume_profile):
            volume_profile[bin_idx] += volumes[i]
    
    # Find value areas
    total_volume = np.sum(volume_profile)
    cumulative_volume = np.cumsum(np.sort(volume_profile)[::-1])
    value_area_threshold = total_volume * 0.7  # 70% of volume
    
    value_area_mask = cumulative_volume <= value_area_threshold
    high_volume_nodes = np.where(volume_profile >= np.sort(volume_profile)[::-1][value_area_mask][-1])[0]
    
    return {
        'price_levels': price_bins[:-1],
        'volumes': volume_profile,
        'poc_price': price_bins[np.argmax(volume_profile)],  # Point of Control
        'value_area_high': price_bins[high_volume_nodes[-1]],
        'value_area_low': price_bins[high_volume_nodes[0]],
        'high_volume_nodes': [(price_bins[i], volume_profile[i]) for i in high_volume_nodes]
    }

def detect_liquidity_pools(highs: np.ndarray, lows: np.ndarray, volumes: np.ndarray) -> List[Dict[str, Any]]:
    """Detect institutional liquidity pools."""
    liquidity_pools = []
    window = 5
    
    for i in range(window, len(highs)-window):
        # Look for clustered highs (resistance liquidity)
        high_cluster = np.abs(highs[i-window:i+window] - highs[i]) < (highs[i] * 0.001)
        if sum(high_cluster) >= 3:  # At least 3 clustered highs
            avg_volume = np.mean(volumes[i-window:i+window][high_cluster])
            
            liquidity_pools.append({
                'type': 'resistance',
                'price': highs[i],
                'volume': avg_volume,
                'strength': sum(high_cluster),
                'index': i
            })
        
        # Look for clustered lows (support liquidity)
        low_cluster = np.abs(lows[i-window:i+window] - lows[i]) < (lows[i] * 0.001)
        if sum(low_cluster) >= 3:  # At least 3 clustered lows
            avg_volume = np.mean(volumes[i-window:i+window][low_cluster])
            
            liquidity_pools.append({
                'type': 'support',
                'price': lows[i],
                'volume': avg_volume,
                'strength': sum(low_cluster),
                'index': i
            })
    
    return liquidity_pools

def detect_institutional_patterns(opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray) -> List[Dict[str, Any]]:
    """Detect institutional trading patterns."""
    patterns = []
    window = 3
    
    for i in range(window, len(closes)-1):
        # Institutional Stop Hunt Pattern
        if (highs[i] > max(highs[i-window:i]) and    # New high
            closes[i] < opens[i] and                  # Bearish close
            volumes[i] > np.mean(volumes[i-window:i]) * 1.5):  # High volume
            
            patterns.append({
                'type': 'stop_hunt',
                'direction': 'bearish',
                'price': highs[i],
                'volume': volumes[i],
                'strength': volumes[i] / np.mean(volumes[i-window:i]),
                'index': i
            })
        
        # Institutional Accumulation Pattern
        elif (lows[i] < min(lows[i-window:i]) and    # New low
              closes[i] > opens[i] and               # Bullish close
              volumes[i] > np.mean(volumes[i-window:i]) * 1.5):  # High volume
            
            patterns.append({
                'type': 'accumulation',
                'direction': 'bullish',
                'price': lows[i],
                'volume': volumes[i],
                'strength': volumes[i] / np.mean(volumes[i-window:i]),
                'index': i
            })
    
    return patterns

def analyze_smc(highs: np.ndarray, lows: np.ndarray, opens: np.ndarray, closes: np.ndarray, volumes: np.ndarray) -> Dict[str, Any]:
    """Enhanced Smart Money Concepts analysis."""
    # Convert inputs to numpy arrays if they aren't already
    highs = np.array(highs)
    lows = np.array(lows)
    opens = np.array(opens)
    closes = np.array(closes)
    volumes = np.array(volumes)
    
    # Get order blocks
    order_blocks = detect_order_blocks(highs, lows, closes, volumes)
    
    # Analyze volume profile
    volume_profile = analyze_volume_profile(closes, volumes)
    
    # Detect liquidity pools
    liquidity_pools = detect_liquidity_pools(highs, lows, volumes)
    
    # Detect institutional patterns
    inst_patterns = detect_institutional_patterns(opens, highs, lows, closes, volumes)
    
    # Determine current market context
    latest_close = closes[0]
    context = {
        'above_poc': latest_close > volume_profile['poc_price'],
        'in_value_area': volume_profile['value_area_low'] <= latest_close <= volume_profile['value_area_high'],
        'near_liquidity': any(abs(pool['price'] - latest_close) / latest_close < 0.01 
                             for pool in liquidity_pools),
        'active_patterns': [p for p in inst_patterns if p['index'] > len(closes)-5]
    }
    
    return {
        'order_blocks': order_blocks,
        'volume_profile': volume_profile,
        'liquidity_pools': liquidity_pools,
        'institutional_patterns': inst_patterns,
        'market_context': context
    }