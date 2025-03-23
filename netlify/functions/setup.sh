#!/bin/bash
set -e

echo "Starting setup process..."

# Setup Python environment
echo "Setting up Python environment..."
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Setup Node environment
echo "Setting up Node.js environment..."
if [ -f "package.json" ]; then
    npm install
fi

# Add Python directory to path
export PYTHONPATH="/opt/build/repo/netlify/functions/python:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

# Test Python imports
echo "Testing Python imports..."
python -c "
try:
    import numpy
    import pandas
    import plotly
    import scipy
    print('Core packages imported successfully!')
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
"

# Create necessary directories
mkdir -p /opt/build/repo/netlify/functions/python/__pycache__

echo "Setup completed successfully!"