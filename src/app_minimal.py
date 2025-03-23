import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
from database.supabase_handler import SupabaseHandler
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Initialize Supabase client
db = SupabaseHandler(SUPABASE_URL, SUPABASE_KEY)

def create_price_chart(df):
    """Create a basic price chart without heavy analysis"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ),
        row=1, col=1
    )

    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['volume'],
            name='Volume'
        ),
        row=2, col=1
    )

    fig.update_layout(
        title='EGX 30 Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        yaxis2_title='Volume',
        showlegend=False,
        height=800
    )

    return fig

def parse_contents(contents, filename):
    """Parse uploaded file contents"""
    if contents is None:
        return None

    try:
        # Read and process CSV file
        df = pd.read_csv(filename)
        df['date'] = pd.to_datetime(df['date'])
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        if not all(col in df.columns for col in required_columns):
            return None
            
        return df
    except Exception:
        return None

# Layout
app.layout = html.Div([
    html.H1('EGX 30 Stock Analysis', style={'textAlign': 'center'}),
    
    html.Div([
        # Analysis Type Selection
        html.Label('Select Analysis Type:'),
        dcc.RadioItems(
            id='analysis-type',
            options=[
                {'label': 'Bullish Market', 'value': 'bullish'},
                {'label': 'Bearish Market', 'value': 'bearish'},
                {'label': 'Custom Data', 'value': 'custom'}
            ],
            value='bullish',
            style={'marginBottom': '20px'}
        ),
        
        # File Upload (for custom analysis)
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'marginBottom': '20px'
                }
            )
        ], id='upload-container', style={'display': 'none'}),
        
        # Analyze Button
        html.Button('Analyze', id='analyze-button', n_clicks=0,
                   style={'marginBottom': '20px'}),
        
        # Results Display
        html.Div(id='output-container')
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
])

# Callbacks
@app.callback(
    Output('upload-container', 'style'),
    Input('analysis-type', 'value')
)
def toggle_upload(analysis_type):
    """Show/hide file upload based on analysis type"""
    if analysis_type == 'custom':
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    Output('output-container', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('analysis-type', 'value'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(n_clicks, analysis_type, contents, filename):
    if n_clicks == 0:
        return ''
    
    try:
        # Get data from Supabase or files
        if analysis_type == 'bullish':
            try:
                df = db.get_market_data('bullish')
            except Exception as e:
                return html.Div(f'Error accessing database: {str(e)}', style={'color': 'red'})
                
        elif analysis_type == 'bearish':
            try:
                df = db.get_market_data('bearish')
            except Exception as e:
                return html.Div(f'Error accessing database: {str(e)}', style={'color': 'red'})
                
        elif analysis_type == 'custom':
            if contents is None:
                return html.Div('Please upload a file for custom analysis', style={'color': 'red'})
                
            df = parse_contents(contents, filename)
            if df is None:
                return html.Div('Error processing file. Check format.', style={'color': 'red'})

        # Create chart
        fig = create_price_chart(df)
        
        # Get cached analysis or request new one
        try:
            analysis = db.get_latest_analysis(analysis_type)
        except Exception:
            analysis = {
                'trend': 'Loading...',
                'prediction': 'Calculating...',
                'confidence': 0,
                'recommendation': 'Please wait...',
                'summary': 'Analysis in progress...'
            }
        
        return html.Div([
            html.H3('Analysis Results'),
            dcc.Graph(figure=fig),
            html.Div([
                html.P(f"Market Trend: {analysis['trend']}"),
                html.P(f"AI Prediction: {analysis['prediction']}"),
                html.P(f"Confidence: {analysis['confidence']}%"),
                html.P(f"Recommended Action: {analysis['recommendation']}"),
                html.Hr(),
                html.P(f"Summary: {analysis['summary']}")
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '5px'})
        ])
        
    except Exception as e:
        return html.Div(f'Error: {str(e)}', style={'color': 'red'})

if __name__ == '__main__':
    app.run_server(debug=True)