import subprocess
import sys
import os
import platform
from pathlib import Path

def check_gcloud():
    """Check if Google Cloud SDK is installed"""
    try:
        subprocess.run(['gcloud', '--version'], check=True, capture_output=True)
        return True
    except:
        return False

def get_download_url():
    """Get appropriate download URL based on OS"""
    system = platform.system().lower()
    if system == 'windows':
        return 'https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe'
    elif system == 'darwin':  # macOS
        return 'https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-latest-darwin-arm.tar.gz'
    else:  # Linux
        return 'https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-latest-linux-x86_64.tar.gz'

def setup_gcloud():
    """Setup Google Cloud SDK"""
    print("=== Setting up Google Cloud SDK ===")
    
    if check_gcloud():
        print("Google Cloud SDK is already installed!")
        return True
    
    print("\nGoogle Cloud SDK not found. Please install it manually:")
    print(f"\n1. Download from: {get_download_url()}")
    print("\n2. Follow installation instructions for your OS:")
    print("   Windows: Run the downloaded installer")
    print("   macOS/Linux: Extract and run ./install.sh")
    
    print("\nAfter installation:")
    print("1. Run 'gcloud init' to initialize SDK")
    print("2. Run 'gcloud auth login' to authenticate")
    print("3. Run 'gcloud projects create [PROJECT-ID]' to create a project")
    print("4. Run 'gcloud config set project [PROJECT-ID]' to set the project")
    
    return False

def setup_cloud_functions():
    """Setup Cloud Functions configuration"""
    if not check_gcloud():
        return False
        
    print("\nSetting up Cloud Functions...")
    
    # Create cloud-functions directory if it doesn't exist
    Path('cloud-functions').mkdir(exist_ok=True)
    
    # Create requirements.txt for Cloud Functions
    requirements = """
numpy>=1.24.3
pandas>=2.1.4
scikit-learn>=1.3.0
joblib>=1.3.2
functions-framework>=3.4.0
google-cloud-storage>=2.12.0
    """.strip()
    
    with open('cloud-functions/requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("\nCloud Functions setup complete!")
    print("\nNext steps:")
    print("1. Enable Cloud Functions API:")
    print("   gcloud services enable cloudfunctions.googleapis.com")
    print("\n2. Enable Cloud Build API:")
    print("   gcloud services enable cloudbuild.googleapis.com")
    print("\n3. Deploy function:")
    print("   cd cloud-functions")
    print("   gcloud functions deploy analyze_market --runtime python39 --trigger-http")
    
    return True

def main():
    if not setup_gcloud():
        sys.exit(1)
    if not setup_cloud_functions():
        sys.exit(1)

if __name__ == "__main__":
    main()