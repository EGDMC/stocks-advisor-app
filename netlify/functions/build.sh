#!/bin/bash

# Create Python virtual environment
python -m venv .python_env

# Activate virtual environment
source .python_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .netlify directory if it doesn't exist
mkdir -p .netlify

# Create runtime.txt for Python version
echo "3.9" > runtime.txt

# Deactivate virtual environment
deactivate