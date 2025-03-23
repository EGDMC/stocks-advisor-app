import os
import shutil
import zipfile
from pathlib import Path

def prepare_netlify_files():
    """Prepare files for Netlify deployment"""
    print("=== Preparing Netlify Deployment Package ===")
    
    # Create dist directory
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Create necessary subdirectories
    netlify_dir = dist_dir / 'netlify'
    functions_dir = netlify_dir / 'functions'
    public_dir = dist_dir / 'public'
    
    functions_dir.mkdir(parents=True)
    public_dir.mkdir(parents=True)
    
    # Copy files
    files_to_copy = {
        # Functions
        'netlify/functions/app.py': functions_dir / 'app.py',
        'netlify/functions/index.js': functions_dir / 'index.js',
        'netlify/functions/requirements.txt': functions_dir / 'requirements.txt',
        'netlify/functions/package.json': functions_dir / 'package.json',
        'netlify/functions/build.sh': functions_dir / 'build.sh',
        
        # Public
        'public/index.html': public_dir / 'index.html',
        
        # Root files
        'netlify.yml': dist_dir / 'netlify.yml',
        'netlify.toml': dist_dir / 'netlify.toml'
    }
    
    for src, dest in files_to_copy.items():
        if Path(src).exists():
            shutil.copy2(src, dest)
            print(f"✓ Copied {src}")
        else:
            print(f"✗ Missing {src}")
    
    # Create zip file
    zip_path = 'netlify-deploy.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arc_name)
                print(f"✓ Added to zip: {arc_name}")
    
    print(f"\n✓ Created {zip_path}")
    print("\nNext steps:")
    print("1. Go to Netlify Dashboard")
    print("2. Create New Site > Import from ZIP")
    print("3. Upload netlify-deploy.zip")
    print("4. Configure the following environment variables:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_KEY")
    print("   - BACKEND_URL")
    print("   - API_KEY")
    print("5. Deploy!")

if __name__ == "__main__":
    prepare_netlify_files()