import os
import requests
import json
from pathlib import Path
import webbrowser
import time

class VercelDeployer:
    def __init__(self):
        self.vercel_token = None
        self.project_id = None
        self.api_base = 'https://api.vercel.com'
        self.env_file = Path('.env')
        self.vercel_dir = Path('vercel-deploy')

    def check_token(self):
        """Check if token is valid"""
        if not self.vercel_token:
            return False
            
        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{self.api_base}/v9/user", headers=headers)
        return response.status_code == 200

    def get_token(self):
        """Get Vercel token from user"""
        print("\n1. Go to https://vercel.com/account/tokens")
        print("2. Create a new token")
        print("3. Copy the token")
        
        webbrowser.open('https://vercel.com/account/tokens')
        self.vercel_token = input("\nEnter your Vercel token: ").strip()
        
        if self.check_token():
            print("✓ Token verified successfully")
            return True
        else:
            print("✗ Invalid token")
            return False

    def create_project(self):
        """Create a new project on Vercel"""
        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "name": "egx30-stock-advisor",
            "framework": "other"
        }
        
        response = requests.post(f"{self.api_base}/v9/projects", headers=headers, json=data)
        
        if response.status_code == 201:
            project_data = response.json()
            self.project_id = project_data['id']
            print(f"✓ Project created: {project_data['name']}")
            return True
        else:
            print(f"✗ Failed to create project: {response.text}")
            return False

    def prepare_files(self):
        """Prepare files for deployment"""
        files = {}
        
        # Essential files
        required_files = [
            'app.py',
            'requirements.txt',
            'vercel.json'
        ]
        
        for file in required_files:
            file_path = self.vercel_dir / file
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    files[file] = {
                        'data': f.read(),
                        'encoding': 'base64'
                    }
                print(f"✓ Added {file}")
            else:
                print(f"✗ Missing {file}")
                return None
                
        return files

    def deploy(self):
        """Deploy to Vercel"""
        print("=== Starting Vercel Deployment ===")
        
        # Get token if not set
        if not self.vercel_token and not self.get_token():
            return False
            
        # Create project if needed
        if not self.project_id and not self.create_project():
            return False
            
        # Prepare files
        files = self.prepare_files()
        if not files:
            return False
            
        # Create deployment
        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "name": "egx30-stock-advisor",
            "files": files,
            "projectId": self.project_id,
            "target": "production"
        }
        
        print("\nInitiating deployment...")
        response = requests.post(f"{self.api_base}/v13/deployments", headers=headers, json=data)
        
        if response.status_code == 200:
            deployment = response.json()
            url = f"https://{deployment['url']}"
            print(f"\n✓ Deployment successful!")
            print(f"URL: {url}")
            
            # Open in browser
            webbrowser.open(url)
            return True
        else:
            print(f"\n✗ Deployment failed: {response.text}")
            return False

    def save_config(self):
        """Save configuration to .env file"""
        if self.vercel_token:
            with open(self.env_file, 'a') as f:
                f.write(f"\nVERCEL_TOKEN={self.vercel_token}\n")
                if self.project_id:
                    f.write(f"VERCEL_PROJECT_ID={self.project_id}\n")
            print("✓ Configuration saved to .env")

def main():
    deployer = VercelDeployer()
    if deployer.deploy():
        deployer.save_config()
        print("\nDeployment completed successfully!")
    else:
        print("\nDeployment failed. Please check the errors above.")
        exit(1)

if __name__ == "__main__":
    main()