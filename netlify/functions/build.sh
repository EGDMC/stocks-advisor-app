#!/bin/bash
set -e

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Node.js dependencies..."
npm install

echo "Setting up Python environment..."
# Create Python virtual environment
python -m venv .python_env

# Activate virtual environment
source .python_env/bin/activate

# Install dependencies in virtual environment
pip install -r requirements.txt

# Check installations
echo "Checking installations..."
python --version
node --version
npm --version

echo "Build completed successfully!"
