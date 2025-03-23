import os
import sys
import pkg_resources
import json
from pathlib import Path

def get_package_size(package_name):
    """Get the size of an installed package"""
    try:
        package = pkg_resources.working_set.by_key[package_name]
        package_path = package.location
        total_size = 0
        
        if os.path.isdir(package_path):
            for dirpath, dirnames, filenames in os.walk(package_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        else:
            total_size = os.path.getsize(package_path)
            
        return total_size / (1024 * 1024)  # Convert to MB
    except:
        return 0

def analyze_requirements():
    """Analyze requirements.txt for package sizes"""
    print("=== Package Size Analysis ===\n")
    
    total_size = 0
    package_sizes = []
    
    with open('requirements_prod.txt') as f:
        requirements = f.read().splitlines()
        
    for req in requirements:
        if req and not req.startswith('#'):
            package_name = req.split('==')[0]
            size = get_package_size(package_name)
            package_sizes.append((package_name, size))
            total_size += size
            
    # Sort by size
    package_sizes.sort(key=lambda x: x[1], reverse=True)
    
    print("Package Sizes:")
    print("-" * 40)
    for package, size in package_sizes:
        print(f"{package:<30} {size:>6.1f} MB")
    
    print("-" * 40)
    print(f"Total Size: {total_size:.1f} MB")
    
    if total_size > 250:
        print("\n⚠️  Total size exceeds Vercel's 250MB limit!")
        print("\nRecommendations:")
        for package, size in package_sizes:
            if size > 50:  # Suggest alternatives for large packages
                if package == 'scikit-learn':
                    print(f"- Replace {package} ({size:.1f}MB) with API calls to Cloud Run")
                elif package == 'numpy':
                    print(f"- Use minimal numpy installation or replace calculations")
                elif package == 'pandas':
                    print(f"- Consider using lighter alternatives or process data server-side")
    else:
        print("\n✓ Total size is within Vercel's limit")

def analyze_model_sizes():
    """Analyze ML model file sizes"""
    print("\n=== Model Size Analysis ===\n")
    
    model_dir = Path('models')
    if not model_dir.exists():
        print("No models directory found")
        return
        
    total_size = 0
    model_sizes = []
    
    for file in model_dir.glob('*'):
        size = os.path.getsize(file) / (1024 * 1024)  # Convert to MB
        model_sizes.append((file.name, size))
        total_size += size
        
    if model_sizes:
        print("Model File Sizes:")
        print("-" * 40)
        for model, size in sorted(model_sizes, key=lambda x: x[1], reverse=True):
            print(f"{model:<30} {size:>6.1f} MB")
            
        print("-" * 40)
        print(f"Total Model Size: {total_size:.1f} MB")

def main():
    analyze_requirements()
    analyze_model_sizes()
    
    print("\nNext Steps:")
    print("1. Move ML models to Cloud Run")
    print("2. Create lightweight Vercel frontend")
    print("3. Use API calls for predictions")

if __name__ == "__main__":
    main()