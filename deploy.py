import os
import sys
import subprocess
from utils.spinner import Spinner

def check_vercel():
    """Check if Vercel CLI is installed"""
    try:
        subprocess.run(['vercel', '--version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_vercel_url():
    """Get the production URL from Vercel"""
    try:
        result = subprocess.run(['vercel', 'ls', '--production'], 
                              capture_output=True, 
                              text=True,
                              check=True)
        # Parse URL from output
        for line in result.stdout.split('\n'):
            if 'egx30-analysis' in line and '.vercel.app' in line:
                return line.split()[1]
    except:
        return None

def deploy():
    """Deploy the application to Vercel"""
    print("\n=== EGX 30 Stock Analysis Dashboard Deployment ===")
    
    # Check for Vercel CLI
    # Check for Vercel CLI and authentication
    if not check_vercel():
        print("❌ Error: Vercel CLI not found or not authenticated.")
        print("\nTo set up Vercel:")
        print("1. Install Vercel CLI:")
        print("   npm install -g vercel")
        print("\n2. Log in to Vercel:")
        print("   vercel login")
        print("\n3. Verify installation:")
        print("   vercel whoami")
        print("\n4. Try deploying again")
        return False

    # Check authentication status
    try:
        subprocess.run(['vercel', 'whoami'],
                      check=True,
                      capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Error: Not logged in to Vercel.")
        print("\nPlease authenticate first:")
        print("1. Run: vercel login")
        print("2. Follow the browser prompts")
        print("3. Return here and try deploying again")
        return False
    
    # Check for required files
    required_files = ['vercel.json', '.env', 'requirements_prod.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("\n❌ Error: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("\n🚀 Starting deployment process...")
    spinner = Spinner("Deploying to Vercel")
    spinner.start()
    
    try:
        # Deploy to Vercel
        result = subprocess.run(['vercel', '--prod'], 
                              capture_output=True, 
                              text=True,
                              check=True)
        spinner.stop()
        
        # Get the URL
        url = get_vercel_url()
        if url:
            print("\n✅ Deployment successful!")
            print("\n📱 Your app is now live at:")
            print(f"   {url}")
            
            # Try to open URL in browser
            try:
                import webbrowser
                webbrowser.open(url)
                print("\n🌐 Opening your app in the browser...")
            except:
                print("\n🌐 Visit your app URL in your browser")
            
            print("\n📊 Next steps:")
            print("1. Log in to the admin dashboard")
            print("2. Upload your market data")
            print("3. Monitor your app in Vercel dashboard")
            print("\n💡 Tip: Run 'vercel logs' to monitor your app")
            return True
        else:
            print("\n⚠️ Deployment successful but couldn't fetch URL.")
            print("Visit https://vercel.com/dashboard to find your app URL")
            return True
            
    except subprocess.CalledProcessError as e:
        spinner.stop()
        print("\n❌ Deployment failed!")
        print("\nError details:")
        print(e.stderr)
        print("\nTroubleshooting steps:")
        print("1. Verify your Vercel account is properly set up")
        print("2. Check your internet connection")
        print("3. Try running 'vercel' manually for more details")
        return False

if __name__ == '__main__':
    sys.exit(0 if deploy() else 1)