# Deploying to Google Cloud Run

Google Cloud Run is a better alternative to Cloud Functions for our application because:
1. Higher memory limits (up to 32GB)
2. Longer execution time
3. Better for containerized applications
4. Cost-effective scaling

## Prerequisites

1. Google Cloud SDK installed
2. Docker installed
3. Project created on Google Cloud Console

## Setup Steps

### 1. Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com
```

### 2. Configure Docker for Google Cloud

```bash
# Configure Docker to use Google Cloud
gcloud auth configure-docker
```

### 3. Build Container Image

```bash
# Build the image
docker build -t gcr.io/[PROJECT-ID]/egx30-advisor .

# Push to Google Container Registry
docker push gcr.io/[PROJECT-ID]/egx30-advisor
```

### 4. Deploy to Cloud Run

```bash
gcloud run deploy egx30-advisor \
  --image gcr.io/[PROJECT-ID]/egx30-advisor \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars "SUPABASE_URL=[YOUR_URL],SUPABASE_KEY=[YOUR_KEY]"
```

### 5. Update Frontend Configuration

Add these environment variables to your Vercel deployment:
```
CLOUD_RUN_URL=https://[YOUR-SERVICE-URL].run.app
```

## Directory Structure

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

## Dockerfile for Cloud Run

```dockerfile
# Use Python 3.9
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080

# Run the application
CMD exec gunicorn --bind :$PORT main:app
```

## Requirements for Cloud Run

```txt
numpy>=1.24.3
pandas>=2.1.4
scikit-learn>=1.3.0
joblib>=1.3.2
flask>=2.0.0
gunicorn>=21.2.0
```

## Testing Locally

1. Build container:
```bash
docker build -t egx30-advisor .
```

2. Run container:
```bash
docker run -p 8080:8080 egx30-advisor
```

3. Test endpoint:
```bash
curl http://localhost:8080/analyze
```

## Monitoring

1. View logs:
```bash
gcloud run services logs read egx30-advisor
```

2. Monitor performance:
```bash
gcloud run services describe egx30-advisor
```

## Cost Management

1. Set budget alerts in Google Cloud Console
2. Configure auto-scaling limits:
```bash
gcloud run services update egx30-advisor \
  --min-instances 0 \
  --max-instances 10
```

## Troubleshooting

1. Check container logs:
```bash
docker logs [CONTAINER_ID]
```

2. Check Cloud Run logs:
```bash
gcloud runs services logs read egx30-advisor
```

3. Test container locally:
```bash
docker run -it egx30-advisor /bin/bash
```

## Security Best Practices

1. Use secret manager for credentials:
```bash
# Store secret
gcloud secrets create supabase-key --replication-policy="automatic"
echo -n "your-key" | gcloud secrets versions add supabase-key --data-file=-

# Use in deployment
gcloud run deploy egx30-advisor \
  --set-secrets SUPABASE_KEY=supabase-key:latest
```

2. Configure IAM roles appropriately
3. Use VPC connector if needed
4. Enable Cloud Audit Logs

## Next Steps

1. Set up CI/CD pipeline
2. Configure monitoring alerts
3. Implement caching strategy
4. Setup backup procedures