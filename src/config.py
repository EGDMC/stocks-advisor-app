import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Model configuration
MODEL_PATH = 'models/default_mlp_model'

# Analysis configuration
ANALYSIS_WINDOW = 20
SUPPORT_RESISTANCE_THRESHOLD = 0.01

# Default data paths
DEFAULT_BULLISH_DATA = 'data/egx30_sample.csv'
DEFAULT_BEARISH_DATA = 'data/test_bearish.csv'