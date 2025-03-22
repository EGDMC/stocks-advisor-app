import subprocess
import sys
import os
import psutil
import time
from datetime import datetime

def get_size_str(bytes_size):
    """Convert bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

def check_docker():
    """Check if Docker is installed and running"""
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        print("✓ Docker is installed")
    except FileNotFoundError:
        print("✗ Docker is not installed")
        print("Please install Docker from: https://docs.docker.com/get-docker/")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("✗ Error checking Docker version")
        sys.exit(1)

def check_resources():
    """Check available system resources"""
    print("\nSystem Resources:")
    print("-----------------")
    
    # Memory
    memory = psutil.virtual_memory()
    print(f"Memory Total: {get_size_str(memory.total)}")
    print(f"Memory Available: {get_size_str(memory.available)}")
    print(f"Memory Used: {memory.percent}%")
    
    # CPU
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"\nCPU Cores: {cpu_count}")
    print(f"CPU Usage: {cpu_percent}%")
    
    # Disk
    disk = psutil.disk_usage('/')
    print(f"\nDisk Total: {get_size_str(disk.total)}")
    print(f"Disk Free: {get_size_str(disk.free)}")
    print(f"Disk Used: {disk.percent}%")

def build_docker():
    """Build Docker image and report size"""
    print("\nBuilding Docker Image:")
    print("---------------------")
    
    start_time = time.time()
    
    try:
        # Build the image
        subprocess.run(['docker', 'build', '-t', 'trading-analysis:test', '.'], check=True)
        
        # Get image size
        result = subprocess.run(
            ['docker', 'images', 'trading-analysis:test', '--format', '{{.Size}}'],
            capture_output=True,
            text=True,
            check=True
        )
        image_size = result.stdout.strip()
        
        build_time = time.time() - start_time
        
        print(f"\n✓ Build successful")
        print(f"Build time: {build_time:.2f} seconds")
        print(f"Image size: {image_size}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def test_container():
    """Test running the container locally"""
    print("\nTesting Container:")
    print("-----------------")
    
    try:
        # Stop any existing container
        subprocess.run(
            ['docker', 'stop', 'trading-analysis-test'],
            capture_output=True
        )
        
        # Remove any existing container
        subprocess.run(
            ['docker', 'rm', 'trading-analysis-test'],
            capture_output=True
        )
        
        # Run the container
        print("Starting container...")
        subprocess.run([
            'docker', 'run',
            '--name', 'trading-analysis-test',
            '-p', '8080:8080',
            '-d',
            'trading-analysis:test'
        ], check=True)
        
        # Wait for startup
        print("Waiting for application startup...")
        time.sleep(5)
        
        # Check container status
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=trading-analysis-test', '--format', '{{.Status}}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if 'Up' in result.stdout:
            print("✓ Container running successfully")
            print("\nTest the application at: http://localhost:8080")
            print("\nPress Ctrl+C to stop the container...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping container...")
                subprocess.run(['docker', 'stop', 'trading-analysis-test'], check=True)
                print("Container stopped")
        else:
            print("✗ Container not running properly")
            print("Checking container logs:")
            subprocess.run(['docker', 'logs', 'trading-analysis-test'])
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Error output: {e.stderr}")
    finally:
        # Cleanup
        try:
            subprocess.run(['docker', 'stop', 'trading-analysis-test'], capture_output=True)
            subprocess.run(['docker', 'rm', 'trading-analysis-test'], capture_output=True)
        except:
            pass

def main():
    """Main test function"""
    print("Docker Build Test")
    print("================\n")
    
    # Record start time
    start_time = datetime.now()
    print(f"Test started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run tests
    check_docker()
    check_resources()
    build_docker()
    test_container()
    
    # Report completion
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nTest completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration.total_seconds():.2f} seconds")

if __name__ == '__main__':
    main()