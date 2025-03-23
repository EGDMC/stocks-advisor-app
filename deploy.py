import os
import shutil
import subprocess
import json
from pathlib import Path

def setup_vercel():
    """Setup Vercel deployment files"""
    print("Setting up Vercel deployment...")
    
    # Create vercel-deploy directory if it doesn't exist
    os.makedirs('vercel-deploy', exist_ok=True)
    
    # Copy minimal app
    shutil.copy2('src/app_minimal.py', 'vercel-deploy/app.py')
    
    # Copy necessary files
    files_to_copy = [
        'src/database/supabase_handler.py',
        'src/config.py',
        '.env',
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            dest_path = os.path.join('vercel-deploy', os.path.basename(file))
            shutil.copy2(file, dest_path)
    
    print("Vercel setup complete!")

def setup_cloud_functions():
    """Setup Google Cloud Functions deployment files"""
    print("Setting up Google Cloud Functions...")
    
    # Create cloud-functions directory
    os.makedirs('cloud-functions', exist_ok=True)
    os.makedirs('cloud-functions/models', exist_ok=True)
    os.makedirs('cloud-functions/utils', exist_ok=True)
    
    # Copy ML models and utilities
    files_to_copy = [
        ('src/models/ai_predictor.py', 'cloud-functions/models/'),
        ('src/models/smc_analyzer.py', 'cloud-functions/models/'),
        ('src/models/__init__.py', 'cloud-functions/models/'),
    ]
    
    for src, dest in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dest)
    
    print("Google Cloud Functions setup complete!")

def create_deployment_config():
    """Create deployment configuration files"""
    config = {
        'vercel': {
            'app_path': 'vercel-deploy/app.py',
            'requirements': 'vercel-deploy/requirements.txt',
            'env_vars': [
                'SUPABASE_URL',
                'SUPABASE_KEY'
            ]
        },
        'google_cloud': {
            'function_name': 'analyze_market',
            'runtime': 'python39',
            'memory': '1024MB',
            'timeout': '120s'
        }
    }
    
    with open('deployment_config.json', 'w') as f:
        json.dump(config, f, indent=2)

def check_prerequisites():
    """Check if all necessary tools are installed"""
    requirements = {
        'vercel': 'vercel --version',
        'gcloud': 'gcloud --version',
        'python': 'python --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            subprocess.run(command.split(), capture_output=True)
            print(f"✓ {tool} is installed")
        except FileNotFoundError:
            missing.append(tool)
            print(f"✗ {tool} is not installed")
    
    return len(missing) == 0

def main():
    print("=== EGX 30 Stock Advisor Deployment Setup ===")
    
    if not check_prerequisites():
        print("\nPlease install missing prerequisites and try again.")
        return
    
    print("\nStarting deployment setup...")
    
    # Create deployment directories
    setup_vercel()
    setup_cloud_functions()
    
    # Create config files
    create_deployment_config()
    
    print("\nDeployment setup complete!")
    print("""
Next steps:
1. Review deployment_config.json
2. Set up environment variables
3. Deploy to Vercel:
   vercel vercel-deploy
4. Deploy to Google Cloud:
   cd cloud-functions
   gcloud functions deploy analyze_market --trigger-http
    """)

if __name__ == "__main__":
    main()