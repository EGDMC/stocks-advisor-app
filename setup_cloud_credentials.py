import os
import subprocess
import json
import webbrowser
from pathlib import Path

class CloudCredentialsSetup:
    def __init__(self):
        self.env_file = Path('.env')
        self.vercel_config = Path.home() / '.vercel' / 'config.json'

    def setup_vercel_token(self):
        """Setup Vercel authentication token"""
        print("\n=== Setting up Vercel Token ===")
        
        # Check for existing token
        if self.vercel_config.exists():
            try:
                with open(self.vercel_config) as f:
                    config = json.load(f)
                    if 'token' in config:
                        print("✓ Vercel token found in config")
                        return config['token']
            except:
                pass

        print("\n1. Go to https://vercel.com/account/tokens")
        print("2. Create a new token")
        print("3. Copy the token")
        
        webbrowser.open('https://vercel.com/account/tokens')
        token = input("\nEnter your Vercel token: ").strip()
        
        if token:
            print("✓ Vercel token received")
            return token
        else:
            print("✗ No token provided")
            return None

    def setup_google_credentials(self):
        """Setup Google Cloud credentials"""
        print("\n=== Setting up Google Cloud Credentials ===")
        
        try:
            # Check if already authenticated
            subprocess.run(['gcloud', 'auth', 'list'], check=True, capture_output=True)
            print("✓ Already authenticated with Google Cloud")
            
            # Get project ID
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                check=True,
                capture_output=True,
                text=True
            )
            project_id = result.stdout.strip()
            
            if project_id:
                print(f"✓ Using Google Cloud project: {project_id}")
                return project_id
                
        except:
            pass

        print("\n1. Go to https://console.cloud.google.com")
        print("2. Create or select a project")
        print("3. Enable required APIs:")
        print("   - Cloud Run API")
        print("   - Container Registry API")
        
        webbrowser.open('https://console.cloud.google.com')
        
        # Login to Google Cloud
        try:
            subprocess.run(['gcloud', 'auth', 'login'], check=True)
        except subprocess.CalledProcessError:
            print("✗ Failed to authenticate with Google Cloud")
            return None
            
        # Get project ID
        project_id = input("\nEnter your Google Cloud project ID: ").strip()
        if project_id:
            try:
                subprocess.run(['gcloud', 'config', 'set', 'project', project_id], check=True)
                print(f"✓ Set Google Cloud project to: {project_id}")
                return project_id
            except subprocess.CalledProcessError:
                print("✗ Failed to set project ID")
                return None
        else:
            print("✗ No project ID provided")
            return None

    def update_env_file(self, vercel_token=None, project_id=None):
        """Update .env file with credentials"""
        env_vars = {}
        
        # Read existing variables
        if self.env_file.exists():
            with open(self.env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value

        # Update with new values
        if vercel_token:
            env_vars['VERCEL_TOKEN'] = vercel_token
        if project_id:
            env_vars['GOOGLE_CLOUD_PROJECT'] = project_id

        # Write back to file
        with open(self.env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

    def setup(self):
        """Run complete setup process"""
        print("=== Cloud Credentials Setup ===")
        
        vercel_token = self.setup_vercel_token()
        project_id = self.setup_google_credentials()
        
        if vercel_token or project_id:
            self.update_env_file(vercel_token, project_id)
            print("\n✓ Credentials saved to .env file")
            return True
        else:
            print("\n✗ Setup incomplete - missing credentials")
            return False

def main():
    setup = CloudCredentialsSetup()
    if not setup.setup():
        exit(1)

if __name__ == "__main__":
    main()