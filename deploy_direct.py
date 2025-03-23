import os
import subprocess
from pathlib import Path
import shutil

def setup_vercel_project():
    """Prepare the Vercel project files"""
    print("\n=== Setting up Vercel Project ===")
    
    # Create vercel-deploy if it doesn't exist
    deploy_dir = Path('vercel-deploy')
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy necessary files
    files_to_copy = [
        ('src/app_minimal.py', 'app.py'),
        ('requirements_prod.txt', 'requirements.txt'),
        ('vercel.json', 'vercel.json'),
        ('.env', '.env')
    ]
    
    for src, dest in files_to_copy:
        src_path = Path(src)
        dest_path = deploy_dir / dest
        if src_path.exists():
            shutil.copy2(src_path, dest_path)
            print(f"✓ Copied {src} to {dest}")
        else:
            print(f"✗ Missing {src}")
            return False
            
    print("✓ Project files prepared")
    return True

def deploy_to_vercel():
    """Deploy to Vercel using CLI"""
    print("\n=== Deploying to Vercel ===")
    
    try:
        # Check if Vercel CLI is installed
        subprocess.run(['vercel', '--version'], check=True, capture_output=True)
    except FileNotFoundError:
        print("✗ Vercel CLI not found")
        print("Installing Vercel CLI...")
        try:
            subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        except:
            print("✗ Failed to install Vercel CLI")
            print("Please install Node.js and run: npm install -g vercel")
            return False
    
    try:
        os.chdir('vercel-deploy')
        
        # Login if needed
        try:
            subprocess.run(['vercel', 'whoami'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("\nPlease login to Vercel:")
            subprocess.run(['vercel', 'login'], check=True)
        
        # Deploy
        print("\nDeploying project...")
        subprocess.run(['vercel', '--prod'], check=True)
        
        print("✓ Deployment successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Deployment failed: {e}")
        return False
    finally:
        os.chdir('..')

def main():
    print("=== EGX 30 Stock Advisor Deployment ===")
    
    if not setup_vercel_project():
        print("\n✗ Setup failed. Please check the errors above.")
        exit(1)
        
    if not deploy_to_vercel():
        print("\n✗ Deployment failed. Please check the errors above.")
        exit(1)
        
    print("\n=== Deployment Completed Successfully ===")
    print("\nNext steps:")
    print("1. Check your Vercel dashboard")
    print("2. Configure environment variables if needed")
    print("3. Add custom domain if desired")

if __name__ == "__main__":
    main()