from flask import Flask, request, jsonify
import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get backend URL from environment
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8080')

def handler(event, context):
    """Netlify function handler"""
    # Parse request details
    path = event['path']
    http_method = event['httpMethod']
    headers = event['headers']
    body = event.get('body', '')
    
    try:
        if path == '/':
            # Serve static landing page
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>EGX 30 Stock Advisor</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 40px; }
                            .container { max-width: 800px; margin: 0 auto; }
                            .button { 
                                padding: 10px 20px;
                                background: #007bff;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                            }
                            .button:hover { background: #0056b3; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>EGX 30 Stock Advisor</h1>
                            <p>Welcome to the EGX 30 Stock Advisor. This is a lightweight frontend that connects to our ML backend.</p>
                            <h2>Available Analysis Types:</h2>
                            <ul>
                                <li>Bullish Market Analysis</li>
                                <li>Bearish Market Analysis</li>
                                <li>Custom Data Analysis</li>
                            </ul>
                            <p>
                                <a href="/docs" class="button">View API Documentation</a>
                            </p>
                        </div>
                    </body>
                </html>
                """
            }
            
        elif path == '/analyze':
            if http_method == 'POST':
                # Forward analysis request to backend
                try:
                    data = json.loads(body) if body else {}
                    response = requests.post(
                        f"{BACKEND_URL}/analyze",
                        json=data,
                        headers={
                            'Content-Type': 'application/json',
                            'X-API-Key': os.getenv('API_KEY', '')
                        }
                    )
                    
                    return {
                        'statusCode': response.status_code,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(response.json())
                    }
                    
                except requests.RequestException as e:
                    return {
                        'statusCode': 503,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'error': 'Backend service unavailable',
                            'message': str(e)
                        })
                    }
                    
        elif path == '/docs':
            # Serve API documentation
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>API Documentation - EGX 30 Stock Advisor</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 40px; }
                            .container { max-width: 800px; margin: 0 auto; }
                            pre { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>API Documentation</h1>
                            
                            <h2>Analyze Endpoint</h2>
                            <p>POST /analyze</p>
                            
                            <h3>Request Format:</h3>
                            <pre>
{
    "type": "bullish|bearish|custom",
    "data": {
        "dates": [...],
        "prices": [...],
        "volumes": [...]
    }
}
                            </pre>
                            
                            <h3>Response Format:</h3>
                            <pre>
{
    "trend": "Bullish|Bearish",
    "prediction": "Up|Down",
    "confidence": 95.5,
    "recommendation": "BUY|SELL|WAIT"
}
                            </pre>
                            
                            <p><a href="/">Back to Home</a></p>
                        </div>
                    </body>
                </html>
                """
            }
            
        elif path == '/health':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'healthy',
                    'version': '1.0.0'
                })
            }
            
        # Handle 404
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not Found'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }