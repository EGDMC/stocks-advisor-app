import os
import json
import base64
import requests
from pathlib import Path

class VercelDeployer:
    def __init__(self):
        self.api_base = "https://api.vercel.com"
        self.token = os.getenv('VERCEL_TOKEN')
        self.deploy_dir = Path('vercel-deploy')
        self.team_id = os.getenv('VERCEL_TEAM_ID')

    def encode_file(self, file_path):
        """Encode file content for Vercel API"""
        with open(file_path, 'rb') as f:
            content = f.read()
            return {
                'file': file_path.name,
                'data': base64.b64encode(content).decode('utf-8'),
                'encoding': 'base64'
            }

    def prepare_files(self):
        """Prepare files for deployment"""
        print("\n=== Preparing Files ===")
        files = []
        
        essential_files = [
            ('src/app_minimal.py', 'app.py'),
            ('requirements_prod.txt', 'requirements.txt'),
            ('vercel.json', 'vercel.json')
        ]
        
        for src, dest in essential_files:
            src_path = Path(src)
            if src_path.exists():
                file_data = self.encode_file(src_path)
                file_data['file'] = dest  # Use destination name
                files.append(file_data)
                print(f"✓ Added {src}")
            else:
                print(f"✗ Missing {src}")
                return None
        
        return files

    def get_headers(self):
        """Get API headers"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        if self.team_id:
            headers['X-Vercel-Team-Id'] = self.team_id
        return headers

    def create_deployment(self, files):
        """Create deployment on Vercel"""
        print("\n=== Creating Deployment ===")
        
        url = f"{self.api_base}/v13/deployments"
        
        # Environment variables as an object
        env = {
            "PYTHONPATH": ".",
            "SUPABASE_URL": os.getenv('SUPABASE_URL', ''),
            "SUPABASE_KEY": os.getenv('SUPABASE_KEY', '')
        }
        
        data = {
            "name": "egx30-stock-advisor",
            "files": files,
            "framework": "python",
            "version": 2,
            "public": True,
            "target": "production",
            "env": env,
            "projectSettings": {
                "framework": "python",
                "buildCommand": None,
                "outputDirectory": None,
                "devCommand": None,
                "installCommand": None
            }
        }
        
        headers = self.get_headers()
        
        try:
            print("Sending deployment request...")
            print(f"Project: egx30-stock-advisor")
            print(f"Files: {len(files)} files")
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                deployment = response.json()
                print(f"\n✓ Deployment created successfully!")
                return deployment
            else:
                print(f"\n✗ Deployment failed with status {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {str(e)}")
            return None

    def check_deployment(self, deployment_id):
        """Check deployment status"""
        print("\nChecking deployment status...")
        
        url = f"{self.api_base}/v13/deployments/{deployment_id}"
        headers = self.get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                status = response.json()
                state = status.get('readyState', 'UNKNOWN')
                print(f"Deployment Status: {state}")
                if state == 'READY':
                    url = status.get('url')
                    if url:
                        print(f"Deployment URL: https://{url}")
                return status
            return None
        except:
            return None

    def deploy(self):
        """Run complete deployment process"""
        if not self.token:
            print("✗ VERCEL_TOKEN not set")
            print("Please set VERCEL_TOKEN environment variable")
            return False
            
        # Prepare files
        files = self.prepare_files()
        if not files:
            return False
            
        # Create deployment
        deployment = self.create_deployment(files)
        if not deployment:
            return False
            
        # Monitor deployment status
        deployment_id = deployment.get('id')
        if deployment_id:
            print("\nWaiting for deployment to complete...")
            status = self.check_deployment(deployment_id)
            if status and status.get('readyState') == 'ERROR':
                print("✗ Deployment failed")
                return False
                
        return True

def setup_env():
    """Set up environment variables from .env file"""
    if not os.path.exists('.env'):
        return
        
    print("\nLoading environment variables...")
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                if not key.startswith('VERCEL_'):
                    print(f"✓ Loaded {key}")

def main():
    print("=== EGX 30 Stock Advisor Deployment ===")
    
    setup_env()
    deployer = VercelDeployer()
    
    if deployer.deploy():
        print("\n=== Deployment Completed Successfully ===")
        print("\nNext steps:")
        print("1. Check deployment status in Vercel dashboard")
        print("2. Verify environment variables")
        print("3. Test the deployed application")
    else:
        print("\n✗ Deployment failed")
        exit(1)

if __name__ == "__main__":
    main()