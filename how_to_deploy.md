# EGX 30 Stock Advisor Deployment Guide

## Current Architecture Issues
- Vercel 250MB size limit exceeded
- Heavy ML dependencies
- Large model files

## Solution Architecture

### 1. Local Development
- Keep full functionality locally
- Train and test models
- Full technical analysis

### 2. Cloud Components

#### A. Vercel Frontend (Lightweight)
- Basic UI components
- Simple charts
- API calls to other services
- Requirements:
  ```
  dash-core-components
  dash-html-components
  plotly (minimal)
  ```

#### B. Google Cloud Functions (Heavy Processing)
- ML predictions
- Technical analysis
- Model serving
- Requirements stay in cloud:
  ```
  scikit-learn
  numpy
  pandas
  ```

#### C. Supabase (Data Layer)
- Store market data
- Cache analysis results
- Store user configurations

## Deployment Steps

1. Split the app:
   - Move ML models to Google Cloud
   - Keep UI on Vercel
   - Use Supabase as data bridge

2. Create lightweight Vercel app:
   ```python
   # vercel-deploy/app.py
   import dash
   from dash import html, dcc
   import plotly.graph_objects as go
   import requests
   
   # Call Google Cloud for analysis
   # Display results with minimal processing
   ```

3. Setup Google Cloud Function:
   ```python
   # cloud-function/main.py
   from models.ai_predictor import AIPredictor
   from models.smc_analyzer import SMCAnalyzer
   
   def analyze_market(request):
       # Handle heavy processing
       # Return JSON results
   ```

4. Use Supabase to:
   - Store analysis results
   - Cache predictions
   - Manage data flow

## Benefits
1. Stay within Vercel limits
2. Better scalability
3. Separate concerns
4. Faster frontend

## Next Steps
1. Create lightweight Vercel frontend
2. Setup Google Cloud Functions
3. Configure Supabase data flow
4. Test distributed system
