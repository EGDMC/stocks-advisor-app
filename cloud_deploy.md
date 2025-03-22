# Deploying to Google Cloud Run

This guide explains how to deploy the Trading Analysis application to Google Cloud Run.

## Prerequisites

1. Install Google Cloud SDK:
   - Visit: https://cloud.google.com/sdk/docs/install
   - Follow the installation instructions for your operating system

2. Initialize Google Cloud:
   ```bash
   gcloud init
   ```

3. Set up a Google Cloud project:
   ```bash
   # Create new project
   gcloud projects create [PROJECT_ID]
   
   # Set project
   gcloud config set project [PROJECT_ID]
   
   # Enable required APIs
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

## Deployment Steps

1. Install deployment requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the deployment script:
   ```bash
   python deploy_cloud.py
   ```

The script will:
- Build the Docker container
- Upload it to Google Container Registry
- Deploy to Cloud Run
- Configure scaling and resources
- Output the service URL

## Verification

Once deployed, you can:
1. Visit the provided URL
2. Upload a stock data file
3. Verify all analysis features work correctly

## Monitoring

Monitor your deployment:
```bash
# View logs
gcloud logging tail "resource.type=cloud_run_revision"

# Check service status
gcloud run services describe trading-analysis

# View metrics
gcloud run services describe trading-analysis --format='yaml(status.traffic,status.url)'
```

## Troubleshooting

1. If deployment fails:
   ```bash
   # View build logs
   gcloud builds list
   gcloud builds log [BUILD_ID]
   ```

2. If service fails:
   ```bash
   # View service logs
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=trading-analysis"
   ```

3. Memory issues:
   - Increase memory allocation in `deploy_cloud.py`
   - Modify the `--memory` flag value

4. Scaling issues:
   - Adjust `--max-instances` in `deploy_cloud.py`
   - Monitor concurrent requests

## Cost Management

The free tier includes:
- 2 million requests per month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds of compute time

Monitor usage:
```bash
gcloud billing accounts list
gcloud alpha billing accounts get-spend-information
```

## Cleanup

To remove the deployment:
```bash
# Delete Cloud Run service
gcloud run services delete trading-analysis --platform managed --region us-central1

# Delete container images
gcloud container images delete gcr.io/[PROJECT_ID]/trading-analysis