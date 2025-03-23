import numpy as np
import pandas as pd

class SMCAnalyzer:
    def __init__(self):
        self.trend = None
        self.order_blocks = []
        self.liquidity_zones = []
        self.fvg_zones = []

    def detect_trend(self, data):
        """Detect overall market trend using SMC principles"""
        if len(data) < 20:
            return "Insufficient Data"
        
        # Calculate 20-period moving average
        ma20 = data['close'].rolling(window=20).mean()
        current_price = data['close'].iloc[-1]
        
        # Basic trend detection
        if current_price > ma20.iloc[-1]:
            recent_highs = data['high'][-10:].values
            if np.all(recent_highs[1:] >= recent_highs[:-1]):
                return "Bullish"
            return "Bullish with Resistance"
        else:
            recent_lows = data['low'][-10:].values
            if np.all(recent_lows[1:] <= recent_lows[:-1]):
                return "Bearish"
            return "Bearish with Support"

    def find_order_blocks(self, data):
        """Identify potential order blocks using price action"""
        blocks = []
        window = 5
        
        for i in range(window, len(data)):
            window_data = data.iloc[i-window:i]
            
            # Look for bearish order blocks
            if data['high'].iloc[i] < window_data['low'].min():
                blocks.append({
                    'type': 'bearish',
                    'top': window_data['high'].max(),
                    'bottom': window_data['low'].min(),
                    'index': i
                })
            
            # Look for bullish order blocks
            if data['low'].iloc[i] > window_data['high'].max():
                blocks.append({
                    'type': 'bullish',
                    'top': window_data['high'].max(),
                    'bottom': window_data['low'].min(),
                    'index': i
                })
        
        self.order_blocks = blocks
        return blocks

    def identify_liquidity_zones(self, data):
        """Find liquidity zones based on price clusters"""
        zones = []
        window = 10
        
        for i in range(window, len(data)):
            window_data = data.iloc[i-window:i]
            volume_weighted_price = (window_data['close'] * window_data['volume']).sum() / window_data['volume'].sum()
            
            if abs(data['close'].iloc[i] - volume_weighted_price) < 0.02 * volume_weighted_price:
                zones.append({
                    'price': volume_weighted_price,
                    'volume': window_data['volume'].sum(),
                    'index': i
                })
        
        self.liquidity_zones = zones
        return zones

    def detect_fair_value_gaps(self, data):
        """Identify Fair Value Gaps in price action"""
        gaps = []
        
        for i in range(1, len(data)-1):
            current_candle = data.iloc[i]
            prev_candle = data.iloc[i-1]
            next_candle = data.iloc[i+1]
            
            # Bullish FVG
            if prev_candle['low'] > next_candle['high']:
                gaps.append({
                    'type': 'bullish',
                    'top': prev_candle['low'],
                    'bottom': next_candle['high'],
                    'index': i
                })
            
            # Bearish FVG
            if prev_candle['high'] < next_candle['low']:
                gaps.append({
                    'type': 'bearish',
                    'top': next_candle['low'],
                    'bottom': prev_candle['high'],
                    'index': i
                })
        
        self.fvg_zones = gaps
        return gaps

    def analyze_market_structure(self, data):
        """Complete market structure analysis"""
        return {
            'trend': self.detect_trend(data),
            'order_blocks': self.find_order_blocks(data),
            'liquidity_zones': self.identify_liquidity_zones(data),
            'fvg_zones': self.detect_fair_value_gaps(data)
        }