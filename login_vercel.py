import subprocess
import os
import json
import sys
from pathlib import Path
import time

class VercelLogin:
    def __init__(self):
        self.config_file = Path.home() / '.vercel' / 'config.json'
        self.project_path = Path.cwd() / 'vercel-deploy'

    def check_vercel_cli(self):
        """Check if Vercel CLI is installed"""
        try:
            subprocess.run(['vercel', '--version'], check=True, capture_output=True)
            print("✓ Vercel CLI is installed")
            return True
        except FileNotFoundError:
            print("✗ Vercel CLI is not installed")
            print("Please install it using: npm install -g vercel")
            return False
        except subprocess.CalledProcessError:
            print("✗ Error checking Vercel CLI")
            return False

    def check_login_status(self):
        """Check if already logged in to Vercel"""
        if not self.config_file.exists():
            return False

        try:
            with open(self.config_file) as f:
                config = json.load(f)
                return 'token' in config and config['token']
        except:
            return False

    def login(self):
        """Perform Vercel login"""
        print("\nLogging in to Vercel...")
        try:
            subprocess.run(['vercel', 'login'], check=True)
            print("✓ Successfully logged in to Vercel")
            return True
        except subprocess.CalledProcessError:
            print("✗ Error logging in to Vercel")
            return False

    def check_project_setup(self):
        """Check if project is set up in Vercel"""
        if not self.project_path.exists():
            print("✗ vercel-deploy directory not found")
            return False

        try:
            result = subprocess.run(
                ['vercel', 'project', 'ls'],
                check=True,
                capture_output=True,
                text=True
            )
            project_name = self.project_path.parent.name.lower()
            return project_name in result.stdout.lower()
        except:
            return False

    def setup_project(self):
        """Set up Vercel project"""
        print("\nSetting up Vercel project...")
        try:
            os.chdir(self.project_path)
            subprocess.run(['vercel', 'link'], check=True)
            print("✓ Project linked successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Error linking project")
            return False
        finally:
            os.chdir(self.project_path.parent)

    def test_connection(self):
        """Test Vercel connection"""
        print("\nTesting Vercel connection...")
        try:
            result = subprocess.run(
                ['vercel', 'whoami'],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✓ Connected as: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            print("✗ Error testing connection")
            return False

    def run(self):
        """Run the complete login and setup process"""
        print("=== Vercel Login and Setup ===\n")

        if not self.check_vercel_cli():
            return False

        if self.check_login_status():
            print("✓ Already logged in to Vercel")
        else:
            if not self.login():
                return False

        if not self.test_connection():
            return False

        if self.check_project_setup():
            print("✓ Project already set up")
        else:
            if not self.setup_project():
                return False

        print("\nVercel setup completed successfully!")
        print("\nNext steps:")
        print("1. Update project settings in Vercel dashboard")
        print("2. Configure environment variables")
        print("3. Run 'vercel --prod' to deploy")

        return True

def main():
    login = VercelLogin()
    if not login.run():
        sys.exit(1)

if __name__ == "__main__":
    main()
