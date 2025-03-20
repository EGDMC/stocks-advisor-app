import os
import sys
import subprocess
import webbrowser
import time

# Add src directory to Python path
sys.path.append('src')
from utils.spinner import Spinner

def get_npm_path():
    """Get npm executable path using PowerShell on Windows or which on Unix"""
    try:
        if os.name == 'nt':
            result = subprocess.run(
                ['powershell', '-Command', '(Get-Command npm).Path'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return os.path.dirname(result.stdout.strip())
        else:
            result = subprocess.run(['which', 'npm'], capture_output=True, text=True)
            if result.returncode == 0:
                return os.path.dirname(result.stdout.strip())
    except:
        pass
    return None

def update_path():
    """Update PATH to include npm paths"""
    if os.name == 'nt':  # Windows
        # Add standard npm paths
        paths_to_add = [
            os.path.join(os.environ.get('APPDATA', ''), 'npm'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs'),
        ]
        
        # Add discovered npm path
        npm_path = get_npm_path()
        if npm_path:
            paths_to_add.append(npm_path)
            
        # Update PATH
        for path in paths_to_add:
            if path and os.path.exists(path) and path not in os.environ['PATH']:
                os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
def run_vercel_command(args, use_popen=False):
    """Run a vercel command using PowerShell"""
    if os.name == 'nt':
        # Simple PowerShell command that just runs vercel
        if use_popen:
            return subprocess.Popen(['powershell', '-NoProfile', 'vercel'] + args,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        return subprocess.run(['powershell', '-NoProfile', 'vercel'] + args,
                           capture_output=True,
                           text=True)
    else:
        cmd = ['vercel'] + args
        if use_popen:
            return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        return subprocess.run(cmd, capture_output=True, text=True)
    
    if use_popen:
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return subprocess.run(cmd, capture_output=True, text=True)

# Global variable to store working vercel path
VERCEL_PATH = 'vercel'

def check_vercel_installation():
    """Verify Vercel CLI installation"""
    try:
        # Update PATH to include npm directories
        update_path()
        
        # Try vercel version check
        result = run_vercel_command(['--version'])
        if result.returncode == 0 and 'Vercel CLI' in result.stdout:
            return True
            
        # If version check failed, print diagnostic info
        print("\nDiagnostic Information:")
        
        print("\n1. Checking npm installation...")
        try:
            npm_version = subprocess.run(
                ['powershell', '-Command', 'npm --version'],
                capture_output=True,
                text=True
            )
            if npm_version.returncode == 0:
                print(f"   npm version: {npm_version.stdout.strip()}")
                # Check npm global directory using PowerShell
                npm_path = subprocess.run(
                    ['powershell', '-Command', 'npm root -g'],
                    capture_output=True,
                    text=True
                )
                if npm_path.returncode == 0:
                    print(f"   npm global directory: {npm_path.stdout.strip()}")
            else:
                print("   ❌ npm not found")
        except Exception as e:
            print(f"   ❌ Error checking npm: {str(e)}")
            
        print("\n2. Checking PATH environment...")
        path_entries = os.environ.get('PATH', '').split(os.pathsep)
        print("   PATH entries:")
        for entry in path_entries:
            print(f"   - {entry}")
            
        return False
        
    except Exception as e:
        print(f"\nDebug: Vercel check error: {str(e)}")
        return False

def login_vercel():
    """Guide user through Vercel login process"""
    print("\n=== Vercel Authentication Setup ===")
    print("This will help you authenticate with Vercel.\n")
    
    # Check Vercel installation
    spinner = Spinner("Checking Vercel CLI installation")
    spinner.start()
    if not check_vercel_installation():
        spinner.stop()
        print("\n❌ Vercel CLI not found or not working properly.")
        print("\nTo fix this:")
        print("1. Run: npm install -g vercel@latest")
        print("2. Verify installation: vercel --version")
        print("3. Try this script again")
        return False
    spinner.stop()
    print("✅ Vercel CLI is properly installed")
    
    # Check if already logged in
    try:
        result = run_vercel_command(['whoami'])
        if 'Error: Not logged in' not in result.stderr:
            print("✅ Already logged in to Vercel")
            return True
    except:
        pass

    print("\n1️⃣ Choose login method:")
    print("1. GitHub (Recommended)")
    print("2. GitLab")
    print("3. Bitbucket")
    print("4. Email")
    print("5. SAML Single Sign-On")
    print("\nℹ️ GitHub is recommended for:")
    print("  • Faster authentication")
    print("  • Better integration with Vercel")
    print("  • Automatic project linking")
    
    choice = input("\nEnter your choice (1-5) [1]: ").strip() or "1"
    
    login_methods = {
        "1": "--github",
        "2": "--gitlab",
        "3": "--bitbucket",
        "4": "--email",
        "5": "--sso"
    }
    
    if choice not in login_methods:
        print("❌ Invalid choice. Defaulting to GitHub login.")
        choice = "1"
    
    print(f"\n2️⃣ Starting {choice} authentication...")
    print("• A browser window will open")
    print("• Complete the authentication process")
    print("• Return here once done\n")
    
    spinner = Spinner("Initiating authentication")
    spinner.start()
    
    try:
        # Start login process
        process = run_vercel_command(['login', login_methods[choice]], use_popen=True)
        
        # Wait for URL to appear in output
        while True:
            line = process.stdout.readline()
            if not line:
                break
            if 'https://' in line:
                url = line.strip().split()[-1]
                spinner.stop()
                print("\n🌐 Opening browser for authentication...")
                try:
                    webbrowser.open(url)
                except:
                    print(f"\nℹ️ Please visit this URL manually:\n{url}")
                spinner = Spinner("Waiting for authentication to complete")
                spinner.start()
                break
        
        # Wait for process to complete with timeout
        try:
            timeout = 300  # 5 minutes timeout
            start_time = time.time()
            while process.poll() is None:
                if time.time() - start_time > timeout:
                    process.terminate()
                    spinner.stop()
                    print("\n❌ Authentication timed out after 5 minutes.")
                    print("Please try again or use an alternative login method.")
                    return False
                time.sleep(1)
            
            spinner.stop()
            
            # Check if process was successful
            if process.returncode != 0:
                print("\n❌ Authentication process failed.")
                print("Try an alternative login method or see vercel_troubleshooting.md")
                return False
                
        except KeyboardInterrupt:
            process.terminate()
            spinner.stop()
            print("\n\n❌ Authentication cancelled by user.")
            print("Run the script again when you're ready to continue.")
            return False
        
        # Verify login was successful
        result = run_vercel_command(['whoami'])
        if 'Error' not in result.stderr:
            print("\n✅ Successfully logged in to Vercel!")
            print("\nNext steps:")
            print("1. Run: python setup_vercel_env.py")
            print("2. Then: python deploy.py")
            return True
        else:
            print("\n❌ Login verification failed.")
            print("Please try again or see vercel_troubleshooting.md")
            return False
            
    except Exception as e:
        spinner.stop()
        print(f"\n❌ Error during login: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print(f"2. Try manual login: {VERCEL_PATH} login")
        print("3. See vercel_troubleshooting.md for more help")
        return False

def cleanup_vercel_processes():
    """Clean up any lingering Vercel processes"""
    try:
        # Windows
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/IM', 'node.exe'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        # Unix-like
        else:
            subprocess.run(['pkill', '-f', 'vercel'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except:
        pass

if __name__ == '__main__':
    try:
        cleanup_vercel_processes()
        success = login_vercel()
        if not success:
            print("\nFor detailed troubleshooting steps, see:")
            print("  vercel_troubleshooting.md")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Process cancelled by user")
        cleanup_vercel_processes()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        cleanup_vercel_processes()
        sys.exit(1)
