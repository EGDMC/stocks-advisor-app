import os
import subprocess
import json
from pathlib import Path
import shutil

class VercelSetup:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.vercel_dir = self.root_dir / 'vercel-deploy'
        self.env_file = self.root_dir / '.env'
        self.env_example = self.root_dir / '.env.example'

    def check_env_vars(self):
        """Check if all required environment variables are set"""
        if not self.env_file.exists():
            if self.env_example.exists():
                shutil.copy(self.env_example, self.env_file)
                print("Created .env file from .env.example")
                print("Please update the values in .env")
                return False
            else:
                print("Error: No .env or .env.example file found")
                return False
        
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        missing = []
        with open(self.env_file) as f:
            env_content = f.read()
            for var in required_vars:
                if f"{var}=" not in env_content:
                    missing.append(var)
        
        if missing:
            print("Missing environment variables:")
            for var in missing:
                print(f"- {var}")
            return False
            
        return True

    def prepare_vercel_directory(self):
        """Prepare the Vercel deployment directory"""
        print("\nPreparing Vercel deployment files...")
        
        # Create vercel-deploy directory if it doesn't exist
        self.vercel_dir.mkdir(exist_ok=True)
        
        # Copy necessary files
        files_to_copy = [
            ('src/app_minimal.py', 'app.py'),
            ('src/config.py', 'config.py'),
            ('requirements_prod.txt', 'requirements.txt'),
            ('.env', '.env')
        ]
        
        for src, dest in files_to_copy:
            src_path = self.root_dir / src
            dest_path = self.vercel_dir / dest
            if src_path.exists():
                shutil.copy2(src_path, dest_path)
                print(f"✓ Copied {src} to vercel-deploy/{dest}")
            else:
                print(f"✗ Missing {src}")
                return False
        
        return True

    def create_vercel_config(self):
        """Create or update vercel.json"""
        config = {
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
                "PYTHONPATH": ".",
                "PORT": "8080"
            }
        }
        
        config_path = self.vercel_dir / 'vercel.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print("✓ Created vercel.json")
        return True

    def check_vercel_cli(self):
        """Check if Vercel CLI is installed"""
        try:
            subprocess.run(['vercel', '--version'], check=True, capture_output=True)
            return True
        except:
            print("\nVercel CLI is not installed.")
            print("Please install it using: npm i -g vercel")
            return False

    def setup(self):
        """Run the complete setup process"""
        print("=== Setting up Vercel Deployment ===\n")
        
        if not self.check_env_vars():
            return False
            
        if not self.prepare_vercel_directory():
            return False
            
        if not self.create_vercel_config():
            return False
            
        if not self.check_vercel_cli():
            return False
        
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Update environment variables in .env")
        print("2. Run 'vercel' in the vercel-deploy directory")
        print("3. Follow the Vercel CLI prompts")
        
        return True

def main():
    setup = VercelSetup()
    if not setup.setup():
        exit(1)

if __name__ == "__main__":
    main()