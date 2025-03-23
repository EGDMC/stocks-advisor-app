import functions_framework
from models.ai_predictor import AIPredictor
from models.smc_analyzer import SMCAnalyzer
import pandas as pd
import json

@functions_framework.http
def analyze_market(request):
    """Cloud Function entry point for market analysis"""
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    try:
        # Get data from request
        request_json = request.get_json()
        if not request_json:
            return ('No JSON data received', 400, headers)
            
        # Parse market data
        data = pd.DataFrame(request_json['data'])
        if data.empty:
            return ('No market data provided', 400, headers)
            
        # Initialize models
        advisor = AIPredictor()
        analyzer = SMCAnalyzer()
        
        # Perform analysis
        analysis = {
            'market_structure': analyzer.analyze_market_structure(data),
            'ai_prediction': advisor.predict(data),
            'technical_indicators': analyzer.calculate_indicators(data)
        }
        
        # Add trade recommendations
        if analysis['market_structure']['trend'] == 'Bullish' and analysis['ai_prediction']['movement'] == 'Up':
            recommendation = 'BUY'
        elif analysis['market_structure']['trend'] == 'Bearish' and analysis['ai_prediction']['movement'] == 'Down':
            recommendation = 'SELL'
        else:
            recommendation = 'WAIT'
            
        analysis['recommendation'] = {
            'action': recommendation,
            'confidence': analysis['ai_prediction']['confidence'],
            'justification': f"Based on {analysis['market_structure']['trend']} trend and {analysis['ai_prediction']['movement']} prediction"
        }
        
        return (json.dumps(analysis), 200, headers)
        
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, headers)

if __name__ == "__main__":
    # Local testing
    import os
    os.environ['FUNCTION_TARGET'] = 'analyze_market'
    print("Starting local development server...")