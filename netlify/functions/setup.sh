#!/bin/bash
set -e

echo "Starting environment setup..."

# Verify Python and pip are available
echo "Python version:"
python --version
echo "Pip version:"
pip --version

# Set environment variables
export PYTHONPATH="/opt/build/repo/netlify/functions/python:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

# Install dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Test imports
echo "Testing imports..."
python -c "
import numpy
import pandas
import plotly
import scipy
print('All core packages imported successfully!')
"

# Verify analyzers are accessible
echo "Testing analyzers..."
python -c "
from base import BaseAnalyzer
from technical import TechnicalAnalyzer
from chart import ChartAnalyzer
from pattern import PatternAnalyzer
from trend import TrendAnalyzer
from analyzer import SMCAnalyzer
print('All analyzers imported successfully!')
"

echo "Setup completed successfully!"