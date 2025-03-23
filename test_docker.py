import subprocess
import requests
import time
import sys
import os
from pathlib import Path

class DockerTester:
    def __init__(self):
        self.container_name = "egx30_stock_advisor"
        self.api_url = "http://localhost:8080"
        self.errors = []
        self.warnings = []

    def run_command(self, command, check=True):
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                shell=True
            )
            return result
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Command failed: {command}\nError: {e.stderr}")
            return None

    def check_docker_installation(self):
        """Verify Docker is installed and running"""
        print("\nChecking Docker installation...")
        
        result = self.run_command("docker --version", check=False)
        if not result or result.returncode != 0:
            self.errors.append("Docker is not installed")
            return False
            
        result = self.run_command("docker info", check=False)
        if not result or result.returncode != 0:
            self.errors.append("Docker daemon is not running")
            return False
            
        print("✓ Docker is installed and running")
        return True

    def check_docker_compose(self):
        """Verify docker-compose is installed"""
        print("\nChecking Docker Compose...")
        
        result = self.run_command("docker-compose --version", check=False)
        if not result or result.returncode != 0:
            self.errors.append("Docker Compose is not installed")
            return False
            
        print("✓ Docker Compose is installed")
        return True

    def check_required_files(self):
        """Check if all required files exist"""
        print("\nChecking required files...")
        
        required_files = [
            "Dockerfile",
            "docker-compose.yml",
            ".env",
            "requirements.txt",
            "src/app.py",
            "src/config.py"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                self.errors.append(f"Missing required file: {file_path}")
            else:
                print(f"✓ Found {file_path}")

    def build_image(self):
        """Attempt to build the Docker image"""
        print("\nBuilding Docker image...")
        
        result = self.run_command("docker-compose build")
        if result and result.returncode == 0:
            print("✓ Docker image built successfully")
            return True
        return False

    def start_container(self):
        """Start the Docker container"""
        print("\nStarting Docker container...")
        
        result = self.run_command("docker-compose up -d")
        if result and result.returncode == 0:
            print("✓ Container started successfully")
            return True
        return False

    def test_api(self):
        """Test if the API is responding"""
        print("\nTesting API endpoints...")
        
        max_retries = 5
        retry_delay = 2
        
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.api_url}/")
                if response.status_code == 200:
                    print("✓ API is responding")
                    return True
                else:
                    print(f"Attempt {i+1}/{max_retries}: API returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                if i < max_retries - 1:
                    print(f"Attempt {i+1}/{max_retries}: API not ready, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.errors.append("API is not responding")
                    return False
        return False

    def check_logs(self):
        """Check container logs for errors"""
        print("\nChecking container logs...")
        
        result = self.run_command(f"docker-compose logs")
        if result:
            logs = result.stdout.lower()
            if 'error' in logs or 'exception' in logs:
                self.warnings.append("Found potential errors in container logs")
            print("✓ Container logs checked")

    def cleanup(self):
        """Stop and remove the container"""
        print("\nCleaning up...")
        
        self.run_command("docker-compose down")
        print("✓ Cleanup completed")

    def run_tests(self):
        """Run all tests"""
        print("=== Running Docker Setup Tests ===")
        
        try:
            if not self.check_docker_installation():
                return False
                
            if not self.check_docker_compose():
                return False
                
            self.check_required_files()
            
            if self.errors:
                print("\nFound errors that must be fixed before continuing.")
                return False
            
            if self.build_image():
                if self.start_container():
                    self.test_api()
                    self.check_logs()
            
        finally:
            self.cleanup()
        
        print("\n=== Test Results ===")
        
        if self.errors:
            print("\nErrors (must be fixed):")
            for error in self.errors:
                print(f"✗ {error}")
        
        if self.warnings:
            print("\nWarnings (should be investigated):")
            for warning in self.warnings:
                print(f"! {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✓ All tests passed! Docker setup is working correctly.")
        elif not self.errors:
            print("\n⚠ Tests completed with warnings.")
        else:
            print("\n✗ Tests failed. Please fix the errors and try again.")
        
        return len(self.errors) == 0

def main():
    tester = DockerTester()
    if not tester.run_tests():
        sys.exit(1)

if __name__ == "__main__":
    main()