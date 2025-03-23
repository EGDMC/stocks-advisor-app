import subprocess
import sys
import os
from pathlib import Path

def check_node():
    """Check if Node.js is installed"""
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        return True
    except:
        return False

def check_npm():
    """Check if npm is installed"""
    try:
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        return True
    except:
        return False

def install_vercel():
    """Install Vercel CLI"""
    try:
        subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        return True
    except:
        return False

def setup_vercel():
    """Setup Vercel account and project"""
    print("=== Setting up Vercel ===")
    
    # Check Node.js installation
    if not check_node():
        print("Error: Node.js is not installed.")
        print("Please install Node.js from https://nodejs.org/")
        return False
    
    # Check npm installation
    if not check_npm():
        print("Error: npm is not installed.")
        print("Please install npm (comes with Node.js)")
        return False
    
    # Install Vercel CLI
    print("\nInstalling Vercel CLI...")
    if not install_vercel():
        print("Error installing Vercel CLI")
        return False
    
    print("\nVercel CLI installed successfully!")
    print("\nNext steps:")
    print("1. Run 'vercel login' to connect your account")
    print("2. Run 'vercel link' in the project directory")
    print("3. Configure project settings when prompted")
    
    return True

def main():
    if not setup_vercel():
        sys.exit(1)

if __name__ == "__main__":
    main()