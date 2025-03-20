import os
import sys
import webbrowser
import time

# Add src directory to Python path
sys.path.append('src')
from utils.spinner import Spinner

def setup_vercel():
    """Guide user through Vercel account setup and authentication"""
    print("\n=== Vercel Account Setup Guide ===")
    print("This guide will help you set up your Vercel account and deploy your app.\n")
    
    print("1️⃣ Create Vercel Account:")
    print("• Opening Vercel signup page in your browser...")
    print("• Select 'Continue with GitHub' for easier setup")
    print("• Allow access to your GitHub account")
    print("• Complete your profile information")
    
    try:
        webbrowser.open('https://vercel.com/signup')
    except:
        print("\n❌ Could not open browser automatically.")
        print("Please visit: https://vercel.com/signup")
    
    response = input("\nHave you created your account? (yes/no): ").lower()
    if response != 'yes':
        print("\n❌ Please create your Vercel account first.")
        print("Then run this script again.")
        return False
    
    print("\n2️⃣ Connect with GitHub:")
    print("• Vercel needs access to your GitHub repositories")
    print("• This allows automatic deployments and updates")
    print("• You can limit access to specific repositories")
    
    print("\nVerifying GitHub connection...")
    spinner = Spinner("Checking GitHub status")
    spinner.start()
    
    try:
        # Check if git is configured
        result = os.system('git config --get user.name')
        if result != 0:
            spinner.stop()
            print("\n❌ Git is not configured.")
            print("\nPlease set up Git first:")
            print("1. Run: git config --global user.name 'Your Name'")
            print("2. Run: git config --global user.email 'your@email.com'")
            print("3. Then run this script again")
            return False
            
        spinner.stop()
        print("✅ Git is configured correctly")
        
        response = input("\nHave you authorized Vercel to access your GitHub? (yes/no): ").lower()
        if response != 'yes':
            print("\nPlease complete GitHub authorization:")
            print("1. Visit: https://vercel.com/dashboard")
            print("2. Click on your avatar → Settings → Git")
            print("3. Connect your GitHub account")
            print("\nThen run this script again.")
            return False
            
    except Exception as e:
        spinner.stop()
        print(f"\n❌ Error checking Git configuration: {str(e)}")
        return False
    
    print("\n3️⃣ Authenticating with Vercel:")
    from login_vercel import login_vercel
    
    if not login_vercel():
        print("\nPlease retry the Vercel authentication before continuing.")
        return False
        
    print("\n✅ CLI authentication successful!")
    
    print("\n4️⃣ Verifying Setup:")
    print("Checking authentication status...")
    
    # Test authentication
    result = os.system('vercel whoami')
    
    if result == 0:
        print("\n✅ Vercel setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python setup_vercel_env.py")
        print("2. Then: python deploy.py")
        return True
    else:
        print("\n❌ Setup verification failed.")
        print("\nTroubleshooting steps:")
        print("1. Try manual login: vercel login --github")
        print("2. Check account status at vercel.com/dashboard")
        print("3. See vercel_troubleshooting.md for more help")
        return False

if __name__ == '__main__':
    setup_vercel()