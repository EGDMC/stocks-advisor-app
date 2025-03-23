import os
import json
import shutil
from pathlib import Path
import webbrowser

class ProjectSetup:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.vercel_dir = self.root_dir / 'vercel-deploy'
        self.env_file = self.root_dir / '.env'

    def get_user_input(self, prompt, default=None):
        """Get input from user with optional default value"""
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
            return value if value else default
        return input(f"{prompt}: ").strip()

    def setup_vercel_project(self):
        """Interactive Vercel project setup"""
        print("\n=== Vercel Project Setup ===")
        
        print("\n1. First, let's create a new project on Vercel:")
        print("   a. Go to https://vercel.com/new")
        print("   b. Choose 'Import Git Repository'")
        print("   c. Select your repository")
        
        webbrowser.open('https://vercel.com/new')
        
        input("\nPress Enter once you've created the project...")
        
        # Get project details
        project_name = self.get_user_input("Enter your Vercel project name", "egx30-stock-advisor")
        project_id = self.get_user_input("Enter your Vercel project ID (from project settings)")
        
        # Update vercel.json
        vercel_config = {
            "version": 2,
            "name": project_name,
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
        
        with open(self.vercel_dir / 'vercel.json', 'w') as f:
            json.dump(vercel_config, f, indent=2)
        
        print("✓ Updated vercel.json")
        return project_id

    def setup_environment(self):
        """Interactive environment setup"""
        print("\n=== Environment Setup ===")
        
        # Get environment variables
        supabase_url = self.get_user_input("Enter your Supabase URL")
        supabase_key = self.get_user_input("Enter your Supabase Key")
        vercel_token = self.get_user_input("Enter your Vercel token")
        
        # Update .env file
        env_vars = {
            'SUPABASE_URL': supabase_url,
            'SUPABASE_KEY': supabase_key,
            'VERCEL_TOKEN': vercel_token,
            'DEBUG': 'True',
            'PORT': '8080'
        }
        
        with open(self.env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print("✓ Updated .env file")
        
        # Copy to vercel-deploy
        shutil.copy2(self.env_file, self.vercel_dir / '.env')
        print("✓ Copied .env to vercel-deploy")

    def prepare_deployment_files(self):
        """Prepare files for deployment"""
        print("\n=== Preparing Deployment Files ===")
        
        self.vercel_dir.mkdir(exist_ok=True)
        
        files_to_copy = [
            ('src/app_minimal.py', 'app.py'),
            ('requirements_prod.txt', 'requirements.txt')
        ]
        
        for src, dest in files_to_copy:
            src_path = Path(src)
            if src_path.exists():
                shutil.copy2(src_path, self.vercel_dir / dest)
                print(f"✓ Copied {src} to {dest}")
            else:
                print(f"✗ Missing {src}")

    def print_next_steps(self):
        """Print next steps for deployment"""
        print("\n=== Next Steps ===")
        print("1. Go to Vercel dashboard")
        print("2. Deploy your project:")
        print("   vercel deploy --prod")
        print("\nOr run deploy_api.py to deploy programmatically")

    def setup(self):
        """Run complete setup process"""
        print("=== EGX 30 Stock Advisor Setup ===")
        
        try:
            self.prepare_deployment_files()
            project_id = self.setup_vercel_project()
            self.setup_environment()
            
            print("\n✓ Setup completed successfully!")
            self.print_next_steps()
            
        except KeyboardInterrupt:
            print("\n\nSetup interrupted. You can run the script again to continue.")
        except Exception as e:
            print(f"\nError during setup: {str(e)}")
            return False
            
        return True

def main():
    setup = ProjectSetup()
    if not setup.setup():
        exit(1)

if __name__ == "__main__":
    main()