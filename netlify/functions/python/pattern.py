from base import BaseAnalyzer, run_analysis
import numpy as np

class PatternAnalyzer(BaseAnalyzer):
    def analyze(self):
        """Detect various chart patterns"""
        self.df['BodyLength'] = self.df['Close'] - self.df['Open']
        self.df['UpperShadow'] = self.df['High'] - self.df[['Open', 'Close']].max(axis=1)
        self.df['LowerShadow'] = self.df[['Open', 'Close']].min(axis=1) - self.df['Low']
        self.df['TotalLength'] = self.df['High'] - self.df['Low']

        patterns = {
            'candlestick_patterns': self._detect_candlestick_patterns(),
            'chart_patterns': self._detect_chart_patterns(),
            'support_resistance': self._find_support_resistance(),
            'trend_patterns': self._detect_trend_patterns()
        }

        signals = self._generate_pattern_signals(patterns)

        return {
            'status': 'success',
            'patterns': patterns,
            'signals': signals
        }

    def _detect_candlestick_patterns(self):
        """Detect candlestick patterns in recent data"""
        patterns = {}
        latest = self.df.iloc[-1]
        
        # Doji
        patterns['doji'] = self._is_doji(latest)
        
        # Hammer/Hanging Man
        patterns['hammer'] = self._is_hammer(latest)
        
        if len(self.df) >= 2:
            last_two = self.df.iloc[-2:]
            patterns['bullish_engulfing'] = self._is_bullish_engulfing(last_two)
            patterns['bearish_engulfing'] = self._is_bearish_engulfing(last_two)
        
        if len(self.df) >= 3:
            last_three = self.df.iloc[-3:]
            patterns['morning_star'] = self._is_morning_star(last_three)
            patterns['evening_star'] = self._is_evening_star(last_three)
        
        return patterns

    def _detect_chart_patterns(self):
        """Detect larger chart patterns"""
        window = min(20, len(self.df))
        recent = self.df.iloc[-window:]
        
        patterns = {}
        highs = recent['High']
        lows = recent['Low']
        
        # Double Top/Bottom
        patterns['double_top'] = self._detect_double_top(highs)
        patterns['double_bottom'] = self._detect_double_bottom(lows)
        
        # Head and Shoulders (basic detection)
        patterns['head_shoulders'] = self._detect_head_shoulders(highs, lows)
        
        # Triangle Patterns
        patterns['ascending_triangle'] = self._detect_ascending_triangle(highs, lows)
        patterns['descending_triangle'] = self._detect_descending_triangle(highs, lows)
        
        return patterns

    def _find_support_resistance(self):
        """Find key support and resistance levels"""
        window = min(20, len(self.df))
        recent = self.df.iloc[-window:]
        
        pivot = (recent['High'] + recent['Low'] + recent['Close']) / 3
        r1 = 2 * pivot - recent['Low']
        r2 = pivot + (recent['High'] - recent['Low'])
        s1 = 2 * pivot - recent['High']
        s2 = pivot - (recent['High'] - recent['Low'])
        
        return {
            'pivot': float(pivot.mean()),
            'resistance1': float(r1.mean()),
            'resistance2': float(r2.mean()),
            'support1': float(s1.mean()),
            'support2': float(s2.mean())
        }

    def _detect_trend_patterns(self):
        """Detect trend patterns and strength"""
        trend = self.determine_trend()
        
        # Calculate trend strength using ADX-like measure
        dm_plus = self.df['High'].diff()
        dm_minus = -self.df['Low'].diff()
        tr = self.df['ATR']
        
        dx = abs(dm_plus - dm_minus) / (dm_plus + dm_minus) * 100
        adx = dx.rolling(window=14).mean().iloc[-1]
        
        return {
            'trend': trend['trend'],
            'strength': 'Strong' if adx > 25 else 'Moderate' if adx > 15 else 'Weak',
            'adx': float(adx)
        }

    def _is_doji(self, candle, doji_size=0.1):
        """Check if candle is a doji"""
        return abs(candle['BodyLength']) <= (candle['TotalLength'] * doji_size)

    def _is_hammer(self, candle, body_size=0.3, shadow_size=2):
        """Check if candle is a hammer"""
        return (abs(candle['BodyLength']) <= (candle['TotalLength'] * body_size) and
                candle['LowerShadow'] >= (abs(candle['BodyLength']) * shadow_size))

    def _is_bullish_engulfing(self, candles):
        """Check for bullish engulfing pattern"""
        return (candles.iloc[0]['BodyLength'] < 0 and
                candles.iloc[1]['BodyLength'] > 0 and
                candles.iloc[1]['Open'] < candles.iloc[0]['Close'] and
                candles.iloc[1]['Close'] > candles.iloc[0]['Open'])

    def _is_bearish_engulfing(self, candles):
        """Check for bearish engulfing pattern"""
        return (candles.iloc[0]['BodyLength'] > 0 and
                candles.iloc[1]['BodyLength'] < 0 and
                candles.iloc[1]['Open'] > candles.iloc[0]['Close'] and
                candles.iloc[1]['Close'] < candles.iloc[0]['Open'])

    def _is_morning_star(self, candles):
        """Check for morning star pattern"""
        return (candles.iloc[0]['BodyLength'] < 0 and
                abs(candles.iloc[1]['BodyLength']) <= abs(candles.iloc[0]['BodyLength'] * 0.3) and
                candles.iloc[2]['BodyLength'] > 0)

    def _is_evening_star(self, candles):
        """Check for evening star pattern"""
        return (candles.iloc[0]['BodyLength'] > 0 and
                abs(candles.iloc[1]['BodyLength']) <= abs(candles.iloc[0]['BodyLength'] * 0.3) and
                candles.iloc[2]['BodyLength'] < 0)

    def _detect_double_top(self, prices):
        """Basic double top detection"""
        peaks = self._find_peaks(prices)
        if len(peaks) >= 2:
            return {'detected': True, 'confidence': 70}
        return {'detected': False, 'confidence': 0}

    def _detect_double_bottom(self, prices):
        """Basic double bottom detection"""
        troughs = self._find_peaks(-prices)
        if len(troughs) >= 2:
            return {'detected': True, 'confidence': 70}
        return {'detected': False, 'confidence': 0}

    def _detect_head_shoulders(self, highs, lows):
        """Basic head and shoulders detection"""
        peaks = self._find_peaks(highs)
        if len(peaks) >= 3:
            return {'detected': True, 'confidence': 60}
        return {'detected': False, 'confidence': 0}

    def _detect_ascending_triangle(self, highs, lows):
        """Basic ascending triangle detection"""
        if len(highs) < 5:
            return {'detected': False, 'confidence': 0}
            
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        if abs(high_slope) < 0.1 and low_slope > 0.1:
            return {'detected': True, 'confidence': 65}
        return {'detected': False, 'confidence': 0}

    def _detect_descending_triangle(self, highs, lows):
        """Basic descending triangle detection"""
        if len(highs) < 5:
            return {'detected': False, 'confidence': 0}
            
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        if high_slope < -0.1 and abs(low_slope) < 0.1:
            return {'detected': True, 'confidence': 65}
        return {'detected': False, 'confidence': 0}

    def _find_peaks(self, prices, distance=2):
        """Find peaks in price series"""
        peaks = []
        for i in range(distance, len(prices) - distance):
            if all(prices.iloc[i] > prices.iloc[i-j] for j in range(1, distance+1)) and \
               all(prices.iloc[i] > prices.iloc[i+j] for j in range(1, distance+1)):
                peaks.append(i)
        return peaks

    def _generate_pattern_signals(self, patterns):
        """Generate trading signals from detected patterns"""
        signals = []
        
        # Candlestick patterns
        for pattern, detected in patterns['candlestick_patterns'].items():
            if detected:
                signals.append({
                    'pattern': pattern.replace('_', ' ').title(),
                    'type': 'Candlestick',
                    'strength': 'Strong' if pattern in ['bullish_engulfing', 'bearish_engulfing'] else 'Moderate'
                })
        
        # Chart patterns
        for pattern, data in patterns['chart_patterns'].items():
            if isinstance(data, dict) and data.get('detected', False):
                signals.append({
                    'pattern': pattern.replace('_', ' ').title(),
                    'type': 'Chart Pattern',
                    'strength': 'Strong' if data.get('confidence', 0) > 70 else 'Moderate'
                })
        
        # Trend patterns
        trend_data = patterns['trend_patterns']
        signals.append({
            'pattern': f"{trend_data['strength']} {trend_data['trend']} Trend",
            'type': 'Trend',
            'strength': trend_data['strength']
        })
        
        return signals

if __name__ == "__main__":
    run_analysis(PatternAnalyzer)