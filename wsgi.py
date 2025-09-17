#!/usr/bin/env python3
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/public_html/ai-content-agent')

# Activate virtual environment
activate_this = '/home/public_html/ai-content-agent/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Import the Flask application
from app import app as application

if __name__ == "__main__":
    application.run()
