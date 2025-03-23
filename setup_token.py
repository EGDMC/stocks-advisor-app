import os
import webbrowser
import json
from pathlib import Path

def setup_vercel_token():
    """Set up Vercel authentication token"""
    print("\n=== Vercel Token Setup ===")
    
    # Check if token exists in environment
    token = os.getenv('VERCEL_TOKEN')
    if token:
        print("✓ VERCEL_TOKEN is already set")
        return True
        
    # Check if token exists in .env file
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if line.startswith('VERCEL_TOKEN='):
                    token = line.strip().split('=', 1)[1]
                    os.environ['VERCEL_TOKEN'] = token
                    print("✓ Found VERCEL_TOKEN in .env file")
                    return True
    
    print("\nTo get your Vercel token:")
    print("1. Go to https://vercel.com/account/tokens")
    print("2. Click 'Create Token'")
    print("3. Give it a name (e.g., 'EGX30 Advisor')")
    print("4. Copy the token")
    
    # Open Vercel tokens page
    webbrowser.open('https://vercel.com/account/tokens')
    
    # Get token from user
    token = input("\nEnter your Vercel token: ").strip()
    
    if not token:
        print("✗ No token provided")
        return False
        
    # Save token to .env file
    env_content = []
    if os.path.exists('.env'):
        with open('.env') as f:
            env_content = f.readlines()
    
    # Remove existing VERCEL_TOKEN line if it exists
    env_content = [line for line in env_content if not line.startswith('VERCEL_TOKEN=')]
    
    # Add new token
    env_content.append(f'\nVERCEL_TOKEN={token}\n')
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.writelines(env_content)
    
    # Set in environment
    os.environ['VERCEL_TOKEN'] = token
    
    print("✓ Token saved to .env file")
    return True

if __name__ == "__main__":
    if setup_vercel_token():
        print("\nToken setup complete! You can now run deploy_api.py")
    else:
        print("\n✗ Token setup failed")
        exit(1)