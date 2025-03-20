import os
import sys
import subprocess
from dotenv import load_dotenv
from supabase import create_client
import shutil

# Add src directory to Python path
sys.path.append('src')
from utils.spinner import with_spinner, Spinner

# Create utils directory if it doesn't exist
os.makedirs('src/utils', exist_ok=True)

# Create __init__.py in utils directory
with open('src/utils/__init__.py', 'a'):
    pass

@with_spinner("Setting up environment...")
def install_requirements():
    """Install required packages"""
    try:
        import pip
    except ImportError:
        print("❌ Error: pip is not available.")
        sys.exit(1)

    requirements = [
        'python-dotenv>=0.19.0',
        'supabase>=1.0.3',
        'pandas>=1.3.0'
    ]

    print("\n=== Package Installation ===")
    print("📦 Installing required packages:")
    for req in requirements:
        spinner = Spinner(f"Installing {req}")
        spinner.start()
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', req],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            spinner.stop()
            print(f"  ✅ {req} installed successfully")
        except subprocess.CalledProcessError as e:
            spinner.stop()
            print(f"\n❌ Error installing {req}:")
            print(f"  → {e.stderr.decode()}")
            print("\nTroubleshooting steps:")
            print("  1. Check your internet connection")
            print("  2. Try running: pip install --upgrade pip")
            print("  3. If behind a proxy, configure pip to use it")
            sys.exit(1)
    
    print("\n✨ All packages installed successfully!")
    print("🔄 Restarting script with new packages...")
    print("=" * 50 + "\n")
    os.execv(sys.executable, ['python'] + sys.argv)

@with_spinner("Checking network connectivity...")
def check_network():
    """Test network connectivity"""
    import urllib.request
    try:
        urllib.request.urlopen('https://supabase.com', timeout=5)
        return True
    except urllib.error.URLError as e:
        print("\n❌ Network connectivity issue detected!")
        print("\nError details:")
        if isinstance(e.reason, str):
            print(f"  → {e.reason}")
        else:
            print(f"  → {e.reason.strerror}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify you can access https://supabase.com in a browser")
        print("3. Check if you're behind a proxy or firewall")
        print("4. Try disabling VPN if you're using one")
        return False
    except Exception as e:
        print("\n❌ Unexpected error during network check!")
        print(f"\nError: {str(e)}")
        print("\nPlease report this issue if it persists.")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("\nNo .env file found. Let's create one.")
            print("\nPlease enter your Supabase credentials:")
            print("(Find these in your Supabase project settings → API)")
            print("\nProject URL example: https://xyz.supabase.co")
            
            while True:
                supabase_url = input("Project URL: ").strip()
                if not supabase_url.startswith('http'):
                    print("❌ Invalid URL format. URL should start with http:// or https://")
                    continue
                break
            
            print("\nAnon Key example: eyJ0eXAiOiJKV1QiLCJhbGciOi...")
            while True:
                supabase_key = input("Anon/Public Key: ").strip()
                if len(supabase_key) < 30:
                    print("❌ Invalid key format. Key should be a long JWT token")
                    continue
                break
            
            # Create .env from example
            shutil.copy('.env.example', '.env')
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('your_supabase_project_url', supabase_url)
            content = content.replace('your_supabase_anon_key', supabase_key)
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("\n✅ Created .env file with your credentials")
            return True
        else:
            print("\n❌ Error: .env.example file not found")
            return False
    return True

def test_supabase_connection():
    """Test connection to Supabase and table setup"""
    print("\n=== Supabase Connection Test ===")
    print("🔍 Testing connection to your Supabase project...")
    print("This will verify:")
    print("  • Database connectivity")
    print("  • Table existence and permissions")
    print("  • Data operations (insert/delete)")
    print("  • Environment configuration\n")
    
    # Load environment variables
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("\n❌ Error: Missing Supabase credentials in .env file")
        print("\nTo fix this:")
        print("1. Copy your credentials from Supabase dashboard:")
        print("   - Go to Project Settings > API")
        print("   - Copy 'Project URL' and 'anon' public key")
        print("\n2. Create/update your .env file:")
        print("   SUPABASE_URL=your_project_url")
        print("   SUPABASE_KEY=your_anon_key")
        print("\nThen run this script again.")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Successfully connected to Supabase")
        
        # Test table existence and permissions
        tables = ['market_data', 'analysis_results', 'model_predictions']
        print("\nChecking database tables:")
        for table in tables:
            spinner = Spinner(f"Testing access to '{table}' table")
            spinner.start()
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                spinner.stop()
                print(f"  ✅ Successfully verified '{table}' table")
            except Exception as table_error:
                spinner.stop()
                print(f"\n❌ Table '{table}' not found or inaccessible!")
                print("\nTo set up the required tables:")
                print("1. Go to your Supabase Dashboard")
                print("2. Click on 'SQL Editor' in the left menu")
                print("3. Create a New Query")
                
                # Try to read and display the SQL content
                try:
                    with open('src/database/tables.sql', 'r') as f:
                        sql_content = f.read()
                    print("\n4. Copy this SQL code:")
                    print("\n" + "=" * 60)
                    print("📋 SQL SETUP COMMANDS:")
                    print("-" * 60)
                    print(sql_content.strip())
                    print("=" * 60)
                    print("\n5. Paste the complete SQL code above into the SQL Editor")
                    print("6. Click 'Run' to create the tables")
                except FileNotFoundError:
                    print("\n❌ Could not find src/database/tables.sql")
                    print("Please make sure the file exists in your project.")
                
                print("\nAfter creating the tables, run this script again to verify.")
                return False
        
        print("\nTesting data operations:")
        # Test data insertion
        test_data = {
            'date': '2024-03-20',
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.5,
            'volume': 1000
        }
        
        spinner = Spinner("Testing data insertion")
        spinner.start()
        try:
            result = supabase.table('market_data').insert(test_data).execute()
            spinner.stop()
            print("  ✅ Successfully inserted test data")
        except Exception as e:
            spinner.stop()
            print("  ❌ Failed to insert test data")
            print(f"  Error: {str(e)}")
            return False
            
        spinner = Spinner("Testing data deletion")
        spinner.start()
        try:
            # Clean up test data
            supabase.table('market_data').delete().eq('date', '2024-03-20').execute()
            spinner.stop()
            print("  ✅ Successfully verified data operations")
        except Exception as e:
            spinner.stop()
            print("  ❌ Failed to clean up test data")
            print(f"  Error: {str(e)}")
            print("  You may need to manually delete the test record")
            return False
        
        print("\n🎉 All tests passed! Your Supabase setup is complete.")
        print("\n✓ Database Configuration:")
        print("  • Working connection")
        print("  • Required tables created")
        print("  • Correct permissions set")
        print("  • Data operations verified")
        
        print("\n📊 Next Steps for Data:")
        print("  1. Use the web interface to upload data:")
        print("     - Go to your dashboard at app.supabase.io")
        print("     - Navigate to Table Editor")
        print("     - Upload CSV files directly")
        print("\n  2. Or use the app to load data:")
        print("     - Start the app: python src/app.py")
        print("     - Use 'Custom Analysis' to upload files")
        print("     - Data will be automatically stored")
        
        print("\n🚀 Ready for deployment!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print("\n❌ Setup verification failed!")
        print("\nError details:")
        print(f"  → {error_msg}")
        print("\nPossible solutions:")
        print("  1. Check your Supabase credentials")
        print("  2. Verify table setup using src/database/tables.sql")
        print("  3. Ensure your Supabase project is active")
        print("  4. Check your network connection")
        print("\nFor more help, visit: https://supabase.com/docs/guides/database")
        return False

def main():
    print("\n=== EGX 30 Stock Analysis - Setup Verification ===")
    print("This script will help you verify your Supabase setup.\n")
    
    # Install required packages if not present
    try:
        import pandas
    except ImportError as e:
        print(f"Missing required package: {e}")
        install_requirements()
    
    # Check network connectivity
    if not check_network():
        print("\n❌ Setup failed: Network connectivity issue")
        sys.exit(1)
    
    # Create/verify .env file
    if not create_env_file():
        print("\n❌ Setup failed: Could not create .env file")
        sys.exit(1)
    
    # Test Supabase connection
    print("\n🔄 Testing Supabase connection and tables...")
    success = test_supabase_connection()
    
    if not success:
        print("\n❌ Setup verification failed.")
        print("Please fix the issues mentioned above before deploying.")
        sys.exit(1)
    
    print("\n🎉 Setup verification completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Initialize your database:")
    print("   - Upload sample data: sample_data/egx30_sample.csv")
    print("   - Or import your own market data")
    print("\n2. Deploy your application:")
    print("   - Run: python deploy.py")
    print("   - Follow the deployment prompts")
    print("\n3. Share your app:")
    print("   - Copy your app's URL")
    print("   - Share with team members")
    print("   - Monitor usage in Supabase dashboard")
    return 0

if __name__ == '__main__':
    sys.exit(main())