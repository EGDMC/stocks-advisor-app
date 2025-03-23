import os
import shutil
import zipfile
from pathlib import Path

def prepare_minimal_deploy():
    """Prepare minimal Netlify deployment package"""
    print("=== Preparing Minimal Netlify Deployment ===")
    
    # Create a temporary directory for the package
    temp_dir = Path('netlify-minimal')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Create public directory
    public_dir = temp_dir / 'public'
    public_dir.mkdir()
    
    # Create necessary files
    files = {
        # Root config file
        'netlify.toml': """
[build]
  publish = "public"
  command = "echo 'No build required'"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
""",
        # Simple index page
        'public/index.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EGX 30 Stock Advisor</title>
    <style>
        body { 
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>EGX 30 Stock Advisor</h1>
        <p>Site is up and running!</p>
        <p>Status: Online</p>
        <hr>
        <p><small>Deployed with Netlify</small></p>
    </div>
</body>
</html>
"""
    }
    
    # Write files
    for file_path, content in files.items():
        full_path = temp_dir / file_path
        full_path.parent.mkdir(exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✓ Created {file_path}")
    
    # Create zip file
    zip_path = 'netlify-minimal.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arc_name)
                print(f"✓ Added to zip: {arc_name}")
    
    # Cleanup temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"\n✓ Created {zip_path}")
    print("\nNext steps:")
    print("1. Go to Netlify Dashboard")
    print("2. Drag and drop the netlify-minimal.zip file")
    print("3. Wait for deployment")
    print("4. Once successful, we can add functions and other features")

if __name__ == "__main__":
    prepare_minimal_deploy()