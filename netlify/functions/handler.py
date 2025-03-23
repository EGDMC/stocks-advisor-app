import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from trading_advisor import TradingAdvisor
from database.supabase_handler import SupabaseHandler
from config import SUPABASE_URL, SUPABASE_KEY, DEFAULT_BULLISH_DATA, DEFAULT_BEARISH_DATA, MODEL_PATH

# Initialize Supabase client
db = SupabaseHandler(SUPABASE_URL, SUPABASE_KEY)

def update_output(n_clicks, analysis_type, contents, filename):
    if n_clicks == 0:
        return ''
    
    try:
        # Get the data based on analysis type
        if analysis_type == 'bullish':
            try:
                # Try to get from Supabase first
                df = db.get_market_data()
                if df.empty:
                    # If no data in Supabase, load from file and save to Supabase
                    df = pd.read_csv(DEFAULT_BULLISH_DATA)
                    db.save_market_data(df)
            except Exception as e:
                print(f"Error accessing Supabase: {e}")
                # Fallback to file
                df = pd.read_csv(DEFAULT_BULLISH_DATA)
                
        elif analysis_type == 'bearish':
            df = pd.read_csv(DEFAULT_BEARISH_DATA)
            
        elif analysis_type == 'custom':
            if contents is None:
                return html.Div('Please upload a file for custom analysis', style={'color': 'red'})
            df = parse_contents(contents, filename)
            if df is None:
                return html.Div([
                    html.P('Error: Unable to process the uploaded file.', style={'fontWeight': 'bold'}),
                    html.P('Please ensure your file:'),
                    html.Ul([
                        html.Li('Is a valid CSV file'),
                        html.Li(['Has all required columns: ', html.Code('date,open,high,low,close,volume')]),
                        html.Li(['Date values are in ', html.Code('YYYY-MM-DD'), ' format']),
                        html.Li('Contains numeric values for price and volume data')
                    ])
                ], style={'color': 'red', 'backgroundColor': '#ffe6e6', 'padding': '15px', 'borderRadius': '5px'})
            
            try:
                # Save custom data to Supabase
                db.save_market_data(df)
            except Exception as e:
                print(f"Error saving to Supabase: {e}")
                
        else:
            return html.Div('Invalid analysis type selected', style={'color': 'red'})
        
        # Initialize advisor and ensure model is trained
        advisor = TradingAdvisor()
        
        # Check if model exists, if not train it
        # Use MODEL_PATH from config.py instead of hardcoding
        model_path = MODEL_PATH
        if not os.path.exists(f'{model_path}_mlp.joblib'):
            print("Training new model...")
            advisor.train_ai_model(df)
            advisor.save_models(model_path)
        else:
            print("Loading existing model...")
            advisor.load_models(model_path)
            
        # Run analysis
        analysis = advisor.analyze_trade_setup(df)

        # Save analysis results to Supabase
        try:
            db.save_analysis_result({
                'type': analysis_type,
                'trend': analysis['market_structure']['trend'],
                'prediction': analysis['ai_prediction']['movement'],
                'confidence': analysis['ai_prediction']['confidence'],
                'recommendation': analysis['trade_recommendation']['action'],
                'summary': analysis['summary']
            })
        except Exception as e:
            print(f"Error saving analysis to Supabase: {e}")
        
        # Create chart
        fig = create_price_chart(df, analysis)
        
        # Display results with chart
        return html.Div([
            html.H3('Analysis Results'),
            # Interactive Chart
            html.Div([
                dcc.Graph(figure=fig)
            ], style={'marginBottom': '20px'}),
            # Analysis Details
            html.Div([
                html.P(f"Market Trend: {analysis['market_structure']['trend']}"),
                html.P(f"AI Prediction: {analysis['ai_prediction']['movement']} "
                      f"({analysis['ai_prediction']['change_percent']:+.2f}%)"),
                html.P(f"Confidence: {analysis['ai_prediction']['confidence']:.1f}%"),
                html.P(f"Recommended Action: {analysis['trade_recommendation']['action']}"),
                html.Hr(),
                html.P(f"Summary: {analysis['summary']}")
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '5px'})
        ])
        
    except Exception as e:
        return html.Div(f'Error: {str(e)}', style={'color': 'red'})