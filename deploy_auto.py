import os
import sys
import subprocess
import json
import requests
from pathlib import Path

class AutoDeployer:
    def __init__(self):
        self.vercel_token = os.getenv('VERCEL_TOKEN')
        self.project_id = os.getenv('VERCEL_PROJECT_ID')
        self.api_base = 'https://api.vercel.com'

    def deploy_to_vercel(self):
        """Deploy frontend to Vercel"""
        print("\nDeploying to Vercel...")
        
        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }
        
        # Create deployment
        deploy_url = f"{self.api_base}/v13/deployments"
        data = {
            "name": "egx30-stock-advisor",
            "project": self.project_id,
            "target": "production",
            "files": self.prepare_files()
        }
        
        response = requests.post(deploy_url, headers=headers, json=data)
        if response.status_code == 200:
            deployment = response.json()
            print(f"✓ Frontend deployed: {deployment['url']}")
            return deployment['url']
        else:
            print(f"✗ Vercel deployment failed: {response.text}")
            return None

    def prepare_files(self):
        """Prepare files for Vercel deployment"""
        files = {}
        vercel_dir = Path('vercel-deploy')
        
        # Only include necessary files
        include_files = [
            'app.py',
            'requirements.txt',
            'vercel.json'
        ]
        
        for file in include_files:
            file_path = vercel_dir / file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    files[file] = {
                        'content': f.read()
                    }
                    
        return files

    def deploy_to_cloud_run(self):
        """Deploy backend to Cloud Run"""
        print("\nDeploying to Cloud Run...")
        
        try:
            # Build container
            image_name = f'gcr.io/{os.getenv("GOOGLE_CLOUD_PROJECT")}/egx30-advisor'
            subprocess.run([
                'docker', 'build', 
                '-t', image_name,
                '-f', 'Dockerfile',
                '.'
            ], check=True)
            
            # Push to Container Registry
            subprocess.run([
                'docker', 'push', image_name
            ], check=True)
            
            # Deploy to Cloud Run
            result = subprocess.run([
                'gcloud', 'run', 'deploy', 'egx30-advisor',
                '--image', image_name,
                '--platform', 'managed',
                '--region', 'us-central1',
                '--memory', '2Gi',
                '--allow-unauthenticated'
            ], check=True, capture_output=True, text=True)
            
            service_url = self.extract_service_url(result.stdout)
            print(f"✓ Backend deployed: {service_url}")
            return service_url
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Cloud Run deployment failed: {e.stderr}")
            return None

    def extract_service_url(self, output):
        """Extract service URL from gcloud output"""
        for line in output.split('\n'):
            if 'Service URL:' in line:
                return line.split('Service URL: ')[-1].strip()
        return None

    def update_frontend_config(self, backend_url):
        """Update frontend configuration with backend URL"""
        if not backend_url:
            return
            
        config_path = Path('vercel-deploy/config.py')
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
            
            content = content.replace(
                'BACKEND_URL = ""',
                f'BACKEND_URL = "{backend_url}"'
            )
            
            with open(config_path, 'w') as f:
                f.write(content)

    def deploy(self):
        """Run complete deployment process"""
        print("=== Starting Automated Deployment ===")
        
        # Verify credentials
        if not all([self.vercel_token, os.getenv('GOOGLE_APPLICATION_CREDENTIALS')]):
            print("Error: Missing required credentials")
            print("Please set VERCEL_TOKEN and GOOGLE_APPLICATION_CREDENTIALS")
            return False
            
        try:
            # Deploy backend first
            backend_url = self.deploy_to_cloud_run()
            if not backend_url:
                return False
                
            # Update frontend configuration
            self.update_frontend_config(backend_url)
            
            # Deploy frontend
            frontend_url = self.deploy_to_vercel()
            if not frontend_url:
                return False
            
            print("\n=== Deployment Completed Successfully ===")
            print(f"Frontend: {frontend_url}")
            print(f"Backend: {backend_url}")
            
            return True
            
        except Exception as e:
            print(f"\nError during deployment: {str(e)}")
            return False

def main():
    deployer = AutoDeployer()
    if not deployer.deploy():
        sys.exit(1)

if __name__ == "__main__":
    main()