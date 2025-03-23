import os
import subprocess
import shutil
from pathlib import Path

class NetlifySetup:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.netlify_dir = self.root_dir / 'netlify'
        self.functions_dir = self.netlify_dir / 'functions'

    def create_directories(self):
        """Create necessary directories"""
        print("\n=== Creating Directories ===")
        self.functions_dir.mkdir(parents=True, exist_ok=True)
        print("✓ Created netlify/functions directory")

    def copy_files(self):
        """Copy necessary files"""
        print("\n=== Copying Files ===")
        
        # Ensure source files exist
        if not (self.functions_dir / 'app.py').exists():
            print("✗ Missing netlify/functions/app.py")
            return False
            
        if not (self.functions_dir / 'requirements.txt').exists():
            print("✗ Missing netlify/functions/requirements.txt")
            return False
            
        if not Path('netlify.toml').exists():
            print("✗ Missing netlify.toml")
            return False
            
        print("✓ All required files present")
        return True

    def setup_environment(self):
        """Setup environment variables"""
        print("\n=== Setting Up Environment Variables ===")
        
        env_vars = {
            'BACKEND_URL': input("Enter backend URL (e.g., https://your-api.herokuapp.com): "),
            'API_KEY': input("Enter API key: "),
            'SUPABASE_URL': input("Enter Supabase URL: "),
            'SUPABASE_KEY': input("Enter Supabase key: ")
        }
        
        # Save to .env file
        with open('.env', 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print("✓ Created .env file")
        
        # Copy to netlify/functions
        shutil.copy2('.env', self.functions_dir / '.env')
        print("✓ Copied .env to functions directory")

    def install_netlify_cli(self):
        """Install Netlify CLI if not present"""
        print("\n=== Checking Netlify CLI ===")
        
        try:
            subprocess.run(['netlify', '--version'], check=True, capture_output=True)
            print("✓ Netlify CLI is already installed")
            return True
        except:
            print("Installing Netlify CLI...")
            try:
                subprocess.run(['npm', 'install', '-g', 'netlify-cli'], check=True)
                print("✓ Netlify CLI installed successfully")
                return True
            except:
                print("✗ Failed to install Netlify CLI")
                print("Please install Node.js and run: npm install -g netlify-cli")
                return False

    def deploy(self):
        """Run deployment steps"""
        print("=== Starting Netlify Deployment Setup ===")
        
        if not self.install_netlify_cli():
            return False
            
        self.create_directories()
        
        if not self.copy_files():
            return False
            
        self.setup_environment()
        
        print("\n=== Setup Complete! ===")
        print("\nNext steps:")
        print("1. Run 'netlify login' to connect your account")
        print("2. Run 'netlify init' to initialize the project")
        print("3. Run 'netlify deploy --prod' to deploy")
        print("\nNote: Make sure to set up environment variables in Netlify dashboard")
        
        return True

def main():
    setup = NetlifySetup()
    if not setup.deploy():
        print("\n✗ Setup failed. Please fix the errors above.")
        exit(1)

if __name__ == "__main__":
    main()