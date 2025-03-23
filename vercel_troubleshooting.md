# Vercel Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Size Limit Exceeded (250MB)

**Problem:**
```
Error: A Serverless Function has exceeded the unzipped maximum size of 250 MB
```

**Solutions:**
1. Split into smaller components:
   - Move ML models to Google Cloud Run
   - Keep only UI components on Vercel
   - Use API calls for heavy processing

2. Optimize dependencies:
   ```txt
   # Remove unnecessary packages
   dash>=2.14.2
   dash-bootstrap-components>=1.5.0
   pandas>=2.1.4
   plotly>=5.18.0
   requests>=2.31.0
   ```

### 2. Build Errors

**Problem:**
```
Error: Cannot find module 'X'
```

**Solutions:**
1. Check requirements.txt:
   ```bash
   # Verify all dependencies are listed
   pip freeze > requirements.txt
   ```

2. Update build settings in vercel.json:
   ```json
   {
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python",
         "config": { "maxLambdaSize": "15mb" }
       }
     ]
   }
   ```

### 3. Environment Variables

**Problem:**
```
Error: Missing environment variable 'X'
```

**Solutions:**
1. Check Vercel Dashboard:
   - Go to Project Settings
   - Environment Variables
   - Add missing variables

2. Use .env file locally:
   ```bash
   cp .env.example .env
   # Update values in .env
   ```

### 4. Runtime Errors

**Problem:**
```
Error: Function timed out
```

**Solutions:**
1. Optimize code:
   - Cache heavy computations
   - Use async functions
   - Minimize database queries

2. Update timeout settings:
   ```json
   {
     "functions": {
       "api/*.py": {
         "memory": 1024,
         "maxDuration": 10
       }
     }
   }
   ```

### 5. Path Resolution Issues

**Problem:**
```
Error: Module not found in path
```

**Solutions:**
1. Update PYTHONPATH:
   ```json
   {
     "env": {
       "PYTHONPATH": "."
     }
   }
   ```

2. Use absolute imports:
   ```python
   from src.models import AIPredictor
   ```

## Preventive Measures

1. Test locally first:
   ```bash
   vercel dev
   ```

2. Check deployment size:
   ```bash
   du -sh .vercel/
   ```

3. Monitor resources:
   ```bash
   vercel inspect
   ```

## Deployment Steps

1. Initialize project:
   ```bash
   vercel init
   ```

2. Configure project:
   ```bash
   vercel link
   ```

3. Set environment variables:
   ```bash
   vercel env add
   ```

4. Deploy:
   ```bash
   vercel --prod
   ```

## Rollback Process

1. List deployments:
   ```bash
   vercel ls
   ```

2. Rollback to previous:
   ```bash
   vercel rollback
   ```

## Performance Optimization

1. Enable caching:
   ```python
   @app.cache.memoize(timeout=300)
   def heavy_computation():
       pass
   ```

2. Use CDN:
   ```json
   {
     "headers": [
       {
         "source": "/static/(.*)",
         "headers": [
           {
             "key": "Cache-Control",
             "value": "public, max-age=31536000, immutable"
           }
         ]
       }
     ]
   }
   ```

3. Compress responses:
   ```python
   from flask_compress import Compress
   Compress(app)
   ```

## Monitoring

1. View logs:
   ```bash
   vercel logs
   ```

2. Check metrics:
   ```bash
   vercel insights
   ```

3. Set up alerts:
   - Go to Project Settings
   - Alerts
   - Configure thresholds

## Support Resources

1. Vercel Documentation:
   - https://vercel.com/docs
   - https://vercel.com/guides

2. Community Support:
   - Discord: https://vercel.com/discord
   - GitHub Issues: https://github.com/vercel/vercel/issues

3. Status Page:
   - https://www.vercel-status.com