import os
import sys
import subprocess
import requests
import pandas as pd
from pathlib import Path

class SetupTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def check_directories(self):
        """Check if all required directories exist"""
        print("\nChecking directories...")
        required_dirs = [
            'vercel-deploy',
            'cloud-functions',
            'src',
            'models',
            'data'
        ]
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                self.errors.append(f"Missing directory: {dir_name}")
            else:
                print(f"✓ Found {dir_name}/")

    def check_files(self):
        """Check if all required files exist"""
        print("\nChecking files...")
        required_files = [
            'src/app_minimal.py',
            'src/config.py',
            'vercel-deploy/requirements.txt',
            'vercel-deploy/vercel.json',
            'cloud-functions/main.py',
            'deployment_config.json'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                self.errors.append(f"Missing file: {file_path}")
            else:
                print(f"✓ Found {file_path}")

    def check_env_vars(self):
        """Check if environment variables are set"""
        print("\nChecking environment variables...")
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Missing environment variable: {var}")
            else:
                print(f"✓ Found {var}")

    def check_dependencies(self):
        """Check if all required Python packages are installed"""
        print("\nChecking Python dependencies...")
        try:
            with open('vercel-deploy/requirements.txt') as f:
                requirements = f.read().splitlines()
            
            for req in requirements:
                try:
                    __import__(req.split('==')[0])
                    print(f"✓ Found {req}")
                except ImportError:
                    self.errors.append(f"Missing package: {req}")
        except FileNotFoundError:
            self.errors.append("requirements.txt not found")

    def check_sample_data(self):
        """Verify sample data files"""
        print("\nChecking sample data...")
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        for file in ['data/egx30_sample.csv', 'data/test_bearish.csv']:
            if not os.path.exists(file):
                self.warnings.append(f"Missing sample data file: {file}")
                continue
                
            try:
                df = pd.read_csv(file)
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    self.warnings.append(f"Missing columns in {file}: {missing_cols}")
                else:
                    print(f"✓ Verified {file}")
            except Exception as e:
                self.warnings.append(f"Error reading {file}: {str(e)}")

    def check_deployment_tools(self):
        """Check if deployment tools are installed"""
        print("\nChecking deployment tools...")
        tools = {
            'vercel': 'vercel --version',
            'gcloud': 'gcloud --version',
            'git': 'git --version'
        }
        
        for tool, command in tools.items():
            try:
                subprocess.run(command.split(), capture_output=True)
                print(f"✓ Found {tool}")
            except FileNotFoundError:
                self.warnings.append(f"Missing tool: {tool}")

    def run_tests(self):
        """Run all setup tests"""
        print("=== Running Setup Tests ===")
        
        self.check_directories()
        self.check_files()
        self.check_env_vars()
        self.check_dependencies()
        self.check_sample_data()
        self.check_deployment_tools()
        
        print("\n=== Test Results ===")
        if self.errors:
            print("\nErrors (must be fixed):")
            for error in self.errors:
                print(f"✗ {error}")
        
        if self.warnings:
            print("\nWarnings (should be addressed):")
            for warning in self.warnings:
                print(f"! {warning}")
                
        if not self.errors and not self.warnings:
            print("\n✓ All tests passed! Ready for deployment.")
        elif not self.errors:
            print("\n⚠ Setup complete with warnings.")
        else:
            print("\n✗ Setup incomplete. Please fix errors.")
        
        return len(self.errors) == 0

def main():
    tester = SetupTester()
    if tester.run_tests():
        print("\nYou can now run deploy.py to start the deployment process.")
    else:
        print("\nPlease fix the errors before attempting deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()