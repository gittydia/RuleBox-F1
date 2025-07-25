import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the existing FastAPI app
from app import app

# This is the entry point for Vercel
def handler(request):
    return app

# Also export as app for compatibility
application = app
