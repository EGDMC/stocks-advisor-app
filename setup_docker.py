import os
import sys
import subprocess
import webbrowser
import time

def check_admin():
    """Check if script is running with admin privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def install_docker():
    """Guide through Docker installation process"""
    print("\nDocker Installation Guide")
    print("=======================\n")
    
    # Check if Docker is already installed
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        print("✓ Docker is already installed")
        return True
    except FileNotFoundError:
        print("Docker needs to be installed.\n")
    except subprocess.CalledProcessError:
        print("Docker installation seems incomplete.\n")
    
    # Open Docker Desktop download page
    print("1. Opening Docker Desktop download page...")
    webbrowser.open('https://www.docker.com/products/docker-desktop')
    
    print("\nPlease:")
    print("1. Download Docker Desktop for Windows")
    print("2. Run the installer")
    print("3. Follow the installation wizard")
    print("4. Restart your computer when prompted")
    
    input("\nPress Enter once you've completed these steps...")
    
    return check_docker_installation()

def check_docker_installation():
    """Verify Docker installation"""
    try:
        # Check Docker version
        result = subprocess.run(['docker', '--version'], 
                             check=True, capture_output=True, text=True)
        print(f"\n✓ Docker installed: {result.stdout.strip()}")
        
        # Check Docker service
        subprocess.run(['docker', 'info'], check=True, capture_output=True)
        print("✓ Docker service running")
        
        return True
        
    except FileNotFoundError:
        print("\n✗ Docker is not installed or not in PATH")
        return False
    except subprocess.CalledProcessError:
        print("\n✗ Docker service is not running")
        print("\nPlease:")
        print("1. Start Docker Desktop")
        print("2. Wait for Docker to finish starting")
        print("3. Try running this script again")
        return False

def check_wsl():
    """Check and install WSL if needed"""
    try:
        result = subprocess.run(['wsl', '--status'], 
                              check=True, capture_output=True, text=True)
        print("✓ WSL is installed")
        return True
    except FileNotFoundError:
        print("\nInstalling WSL...")
        try:
            subprocess.run(['wsl', '--install'], check=True)
            print("✓ WSL installed successfully")
            print("\nPlease restart your computer to complete WSL installation")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Error installing WSL: {e}")
            return False

def setup_docker_environment():
    """Set up Docker environment variables and configuration"""
    print("\nConfiguring Docker environment...")
    
    # Create .docker directory if it doesn't exist
    docker_config_dir = os.path.expanduser('~/.docker')
    os.makedirs(docker_config_dir, exist_ok=True)
    
    # Create or update Docker config
    config_file = os.path.join(docker_config_dir, 'config.json')
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write('{\n  "experimental": true,\n  "features": {\n    "buildkit": true\n  }\n}')
        print("✓ Created Docker configuration file")
    
    # Set environment variables
    docker_env = {
        'DOCKER_BUILDKIT': '1',
        'COMPOSE_DOCKER_CLI_BUILD': '1'
    }
    
    for key, value in docker_env.items():
        try:
            subprocess.run(['setx', key, value], check=True, capture_output=True)
            print(f"✓ Set {key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error setting {key}: {e}")

def test_docker():
    """Test Docker installation with a simple container"""
    print("\nTesting Docker installation...")
    
    try:
        # Pull and run hello-world container
        subprocess.run(['docker', 'pull', 'hello-world'], check=True)
        result = subprocess.run(['docker', 'run', '--rm', 'hello-world'], 
                              check=True, capture_output=True, text=True)
        
        if "Hello from Docker!" in result.stdout:
            print("✓ Docker test successful")
            return True
        else:
            print("✗ Docker test failed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error testing Docker: {e}")
        return False

def main():
    """Main setup function"""
    print("Docker Setup Script")
    print("==================\n")
    
    if not check_admin():
        print("Please run this script as administrator")
        print("Right-click the script and select 'Run as administrator'")
        sys.exit(1)
    
    # Check/Install WSL
    if not check_wsl():
        print("\nWSL setup required. Please restart your computer and run this script again.")
        sys.exit(1)
    
    # Install Docker if needed
    if not install_docker():
        sys.exit(1)
    
    # Set up Docker environment
    setup_docker_environment()
    
    # Test Docker installation
    if test_docker():
        print("\nDocker setup completed successfully!")
        print("\nYou can now run 'python test_docker.py' to test your application build.")
    else:
        print("\nDocker setup incomplete. Please check the errors above.")

if __name__ == '__main__':
    main()