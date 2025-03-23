import os
import subprocess
import json
import argparse
from pathlib import Path

class CloudRunDeployer:
    def __init__(self, project_id=None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.service_name = 'egx30-advisor'
        self.region = 'us-central1'

    def check_prerequisites(self):
        """Check if required tools are installed"""
        requirements = {
            'gcloud': 'gcloud --version',
            'docker': 'docker --version'
        }
        
        missing = []
        for tool, command in requirements.items():
            try:
                subprocess.run(command.split(), check=True, capture_output=True)
                print(f"✓ Found {tool}")
            except:
                missing.append(tool)
                print(f"✗ Missing {tool}")
        
        return len(missing) == 0

    def enable_apis(self):
        """Enable required Google Cloud APIs"""
        apis = [
            'run.googleapis.com',
            'containerregistry.googleapis.com'
        ]
        
        for api in apis:
            print(f"Enabling {api}...")
            subprocess.run(['gcloud', 'services', 'enable', api], check=True)

    def setup_docker(self):
        """Configure Docker for Google Cloud"""
        print("Configuring Docker authentication...")
        subprocess.run(['gcloud', 'auth', 'configure-docker'], check=True)

    def build_image(self):
        """Build Docker image"""
        image_name = f'gcr.io/{self.project_id}/{self.service_name}'
        print(f"\nBuilding Docker image: {image_name}")
        
        subprocess.run(['docker', 'build', '-t', image_name, '.'], check=True)
        return image_name

    def push_image(self, image_name):
        """Push image to Google Container Registry"""
        print(f"\nPushing image to GCR: {image_name}")
        subprocess.run(['docker', 'push', image_name], check=True)

    def deploy_service(self, image_name):
        """Deploy to Cloud Run"""
        print(f"\nDeploying to Cloud Run: {self.service_name}")
        
        cmd = [
            'gcloud', 'run', 'deploy', self.service_name,
            '--image', image_name,
            '--platform', 'managed',
            '--region', self.region,
            '--memory', '2Gi',
            '--timeout', '3600',
            '--allow-unauthenticated'
        ]
        
        # Add environment variables if they exist
        if os.path.exists('.env'):
            env_vars = []
            with open('.env') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        env_vars.append(line.strip())
            if env_vars:
                cmd.extend(['--set-env-vars', ','.join(env_vars)])
        
        subprocess.run(cmd, check=True)

    def setup_monitoring(self):
        """Setup basic monitoring"""
        print("\nSetting up monitoring...")
        
        # Set up logging
        subprocess.run([
            'gcloud', 'run', 'services', 'update-traffic', self.service_name,
            '--region', self.region,
            '--log-http',
            '--log-http-response-size'
        ], check=True)

    def deploy(self):
        """Run full deployment process"""
        print("=== Starting Cloud Run Deployment ===\n")
        
        if not self.project_id:
            print("Error: No project ID specified")
            print("Please set GOOGLE_CLOUD_PROJECT environment variable or provide --project-id")
            return False
        
        try:
            if not self.check_prerequisites():
                return False
            
            self.enable_apis()
            self.setup_docker()
            
            image_name = self.build_image()
            self.push_image(image_name)
            self.deploy_service(image_name)
            self.setup_monitoring()
            
            print("\n=== Deployment Completed Successfully ===")
            print(f"\nService URL: https://{self.service_name}-{self.project_id}.run.app")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\nError during deployment: {str(e)}")
            return False
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Deploy to Google Cloud Run')
    parser.add_argument('--project-id', help='Google Cloud Project ID')
    args = parser.parse_args()
    
    deployer = CloudRunDeployer(args.project_id)
    if not deployer.deploy():
        exit(1)

if __name__ == '__main__':
    main()