# Manual Setup Guide

This guide provides step-by-step instructions for setting up and deploying the EGX 30 Stock Advisor without using automated scripts.

## Local Development Setup

1. Create Virtual Environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

2. Install Dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements_prod.txt
```

3. Set Up Environment Variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Vercel Setup

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Create Vercel Project Structure:
```
vercel-deploy/
├── app.py                 # Copy from src/app_minimal.py
├── requirements.txt       # Minimal requirements
├── vercel.json           # Vercel configuration
└── .env                  # Environment variables
```

3. Create Minimal Requirements:
```txt
# vercel-deploy/requirements.txt
dash>=2.14.2
dash-bootstrap-components>=1.5.0
pandas>=2.1.4
plotly>=5.18.0
requests>=2.31.0
```

4. Configure Vercel:
```json
// vercel-deploy/vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

5. Deploy to Vercel:
```bash
cd vercel-deploy
vercel login
vercel
```

## Google Cloud Run Setup

1. Install Google Cloud SDK from:
   https://cloud.google.com/sdk/docs/install

2. Initialize Google Cloud:
```bash
gcloud init
gcloud auth login
```

3. Create Project Structure:
```
cloud-run/
├── Dockerfile
├── requirements.txt
├── main.py
└── models/
    ├── __init__.py
    ├── ai_predictor.py
    └── smc_analyzer.py
```

4. Create Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8080
CMD exec gunicorn --bind :$PORT main:app
```

5. Build and Deploy:
```bash
# Build image
docker build -t gcr.io/[PROJECT-ID]/egx30-advisor .

# Push to Google Container Registry
docker push gcr.io/[PROJECT-ID]/egx30-advisor

# Deploy to Cloud Run
gcloud run deploy egx30-advisor \
  --image gcr.io/[PROJECT-ID]/egx30-advisor \
  --platform managed \
  --region us-central1 \
  --memory 2Gi
```

## Database Setup

1. Create Supabase Account:
   - Go to https://supabase.com
   - Create new project

2. Get Credentials:
   - Project Settings → API
   - Copy URL and anon key

3. Update Environment Variables:
```env
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

## Testing

1. Test Local Development:
```bash
python src/main.py
```

2. Test Vercel Deployment:
```bash
cd vercel-deploy
vercel dev
```

3. Test Cloud Run:
```bash
docker build -t egx30-advisor .
docker run -p 8080:8080 egx30-advisor
```

## Common Issues

1. Size Limit on Vercel:
   - Move ML models to Cloud Run
   - Keep only UI on Vercel

2. Docker Issues:
   - Check Docker daemon is running
   - Verify permissions

3. Environment Variables:
   - Check all variables are set
   - Verify file paths

## Monitoring

1. Vercel Dashboard:
   - Deployment status
   - Error logs
   - Analytics

2. Google Cloud Console:
   - Cloud Run metrics
   - Logs viewer
   - Error reporting

## Maintenance

1. Update Dependencies:
```bash
pip install --upgrade -r requirements.txt
```

2. Backup Data:
```bash
# Export Supabase data
supabase db dump -f backup.sql
```

3. Update Models:
```bash
# Train new models
python src/main.py --train --save-model models/new_model
```

## Security Best Practices

1. Keep Credentials Secret:
   - Use environment variables
   - Never commit .env files

2. Regular Updates:
   - Update dependencies
   - Check security advisories

3. Access Control:
   - Set up proper IAM roles
   - Use authentication