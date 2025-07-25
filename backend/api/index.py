import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the existing FastAPI app
from app import app

# Export for Vercel
handler = app
