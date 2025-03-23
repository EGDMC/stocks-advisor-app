#!/bin/bash
set -e

echo "Starting build process..."

# Install dependencies
echo "Installing Python packages..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Setup environment
echo "Setting up environment..."
export PYTHONPATH="/opt/build/repo/netlify/functions:$PYTHONPATH"

# Test imports
echo "Testing imports..."
python -c "
import numpy
import pandas
import plotly
import sklearn
print('All imports successful!')
"

echo "Build completed successfully!"