
#!/bin/bash

# Create Python virtual environment
python -m venv .python_env

# Activate virtual environment
source .python_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
