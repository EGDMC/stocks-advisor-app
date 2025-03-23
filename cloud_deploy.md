# Google Cloud Functions Deployment Guide

## Overview
This guide explains how to deploy the heavy processing components of the EGX 30 Stock Advisor to Google Cloud Functions.

## Prerequisites
1. Google Cloud account
2. Google Cloud SDK installed
3. Project created on Google Cloud Console

## Setup Steps

### 1. Install Google Cloud SDK
```bash
# Install from https://cloud.google.com/sdk/docs/install
gcloud init
gcloud auth login
```

### 2. Structure Cloud Functions

Create a directory structure:
```
cloud-functions/
├── main.py              # Main function handler
├── requirements.txt     # Dependencies
├── models/             # ML models
│   ├── __init__.py
│   ├── ai_predictor.py
│   └── smc_analyzer.py
└── utils/              # Helper functions
```

### 3. Create Cloud Function Requirements
```txt
# cloud-functions/requirements.txt
numpy==1.24.3
pandas==2.1.4
scikit-learn==1.3.0
joblib==1.3.2
plotly==5.18.0
```

### 4. Create Main Function Handler
```python
# cloud-functions/main.py
from models.ai_predictor import AIPredictor
from models.smc_analyzer import SMCAnalyzer
import functions_framework
import json

@functions_framework.http
def analyze_market(request):
    """Cloud Function entry point"""
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    try:
        # Get data from request
        request_json = request.get_json()
        data = request_json['data']
        
        # Initialize models
        advisor = AIPredictor()
        analyzer = SMCAnalyzer()
        
        # Perform analysis
        results = {
            'ai_prediction': advisor.predict(data),
            'market_structure': analyzer.analyze(data)
        }
        
        return (json.dumps(results), 200, headers)
        
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, headers)
```

### 5. Deploy Function
```bash
cd cloud-functions
gcloud functions deploy analyze_market \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 1024MB \
    --timeout 120s
```

### 6. Update Frontend Configuration
Add the Cloud Function URL to your environment variables:
```
GOOGLE_CLOUD_FUNCTION_URL=https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/analyze_market
```

### 7. Test Deployment
```python
import requests

# Test cloud function
url = "YOUR_FUNCTION_URL"
data = {
    "data": {
        "dates": [...],
        "prices": [...]
    }
}

response = requests.post(url, json=data)
print(response.json())
```

## Memory Management Tips
1. Load models lazily
2. Use smaller data chunks
3. Clean up resources after use
4. Monitor memory usage

## Error Handling
1. Implement proper error handling
2. Return meaningful error messages
3. Log errors for debugging

## Monitoring
1. Set up Cloud Monitoring
2. Configure alerts
3. Monitor function performance

## Cost Management
1. Set budget alerts
2. Monitor function invocations
3. Optimize cold starts
4. Use appropriate memory settings

## Security
1. Set up IAM roles
2. Implement authentication
3. Secure sensitive data
4. Use environment variables

## Next Steps
1. Monitor function performance
2. Optimize based on usage patterns
3. Implement caching if needed
4. Set up CI/CD pipeline