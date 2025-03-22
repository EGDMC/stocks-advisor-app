import os
import subprocess
import sys
import time

def run_command(command, check=True):
    """Run a shell command and print output"""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}", file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}", file=sys.stderr)
        if not check:
            return e
        sys.exit(1)

def deploy_to_cloud_run():
    """Deploy the application to Google Cloud Run"""
    
    # Check if gcloud is installed
    try:
        run_command(['gcloud', '--version'])
    except FileNotFoundError:
        print("Error: Google Cloud SDK (gcloud) not found. Please install it first.")
        print("Visit: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)

    # Get project ID
    result = run_command(['gcloud', 'config', 'get-value', 'project'])
    project_id = result.stdout.strip()
    
    if not project_id:
        print("Error: No Google Cloud project set. Please run:")
        print("gcloud config set project YOUR_PROJECT_ID")
        sys.exit(1)

    # Build the container
    print("\n=== Building Container ===")
    run_command([
        'gcloud', 'builds', 'submit',
        '--tag', f'gcr.io/{project_id}/trading-analysis'
    ])

    # Deploy to Cloud Run
    print("\n=== Deploying to Cloud Run ===")
    run_command([
        'gcloud', 'run', 'deploy', 'trading-analysis',
        '--image', f'gcr.io/{project_id}/trading-analysis',
        '--platform', 'managed',
        '--region', 'us-central1',
        '--allow-unauthenticated',
        '--memory', '2Gi',
        '--cpu', '1',
        '--max-instances', '10',
        '--port', '8080'
    ])

    # Get the deployed URL
    result = run_command([
        'gcloud', 'run', 'services', 'describe', 'trading-analysis',
        '--platform', 'managed',
        '--region', 'us-central1',
        '--format', 'get(status.url)'
    ])
    
    service_url = result.stdout.strip()
    print(f"\n=== Deployment Complete ===")
    print(f"Your application is available at: {service_url}")

def main():
    """Main deployment function"""
    print("=== Starting Cloud Run Deployment ===")
    
    # Verify requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("Error: requirements.txt not found")
        sys.exit(1)
    
    # Verify Dockerfile exists
    if not os.path.exists('Dockerfile'):
        print("Error: Dockerfile not found")
        sys.exit(1)
    
    # Deploy to Cloud Run
    deploy_to_cloud_run()

if __name__ == '__main__':
    main()