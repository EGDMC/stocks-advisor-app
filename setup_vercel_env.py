import os
import subprocess
from dotenv import load_dotenv

def setup_vercel_env():
    """Set up Vercel environment variables from .env file"""
    print("\n=== Setting up Vercel Environment Variables ===")
    
    # Load environment variables
    load_dotenv()
    
    # Required variables
    env_vars = {
        'SUPABASE_URL': os.getenv('https://glafyufufuuuieumgvqy.supabase.co'),
        'SUPABASE_KEY': os.getenv('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdsYWZ5dWZ1ZnV1dWlldW1ndnF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI0MzIzMzEsImV4cCI6MjA1ODAwODMzMX0.R5VKyduyQtA3loWj9nIPGlJ2TIzhq6jtW6_dQh9AIgU')
    }
    
    # Check if variables exist
    missing = [key for key, value in env_vars.items() if not value]
    if missing:
        print("\n❌ Error: Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these in your .env file first.")
        return False
    
    print("\n🔑 Setting up environment variables in Vercel...")
    
    try:
        # Add each environment variable to Vercel
        for key, value in env_vars.items():
            print(f"\nAdding {key}...")
            result = subprocess.run(
                ['vercel', 'env', 'add', key],
                input=value.encode(),
                capture_output=True
            )
            if result.returncode == 0:
                print(f"✅ Successfully set {key}")
            else:
                print(f"❌ Failed to set {key}")
                print(f"Error: {result.stderr.decode()}")
        
        print("\n✨ Environment setup complete!")
        print("\nNext steps:")
        print("1. Deploy your app: vercel --prod")
        print("2. Visit your app URL")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged in to Vercel (run 'vercel login')")
        print("2. Check your internet connection")
        print("3. Verify your .env file is properly formatted")
        return False

if __name__ == '__main__':
    setup_vercel_env()