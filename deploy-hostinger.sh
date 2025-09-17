#!/bin/bash

# Hostinger Deployment Script for AI Content Agent
# Usage: ./deploy-hostinger.sh

set -e

echo "🚀 Starting Hostinger deployment for AI Content Agent"

# Configuration
HOSTINGER_HOST="191.101.233.56"
HOSTINGER_USER="root"
PROJECT_DIR="/home/public_html/ai-content-agent"
LOCAL_PROJECT_DIR="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo "Host: $HOSTINGER_HOST"
echo "User: $HOSTINGER_USER"
echo "Remote Directory: $PROJECT_DIR"
echo ""

# Create deployment package
echo -e "${YELLOW}📦 Creating deployment package...${NC}"
tar -czf ai-content-agent-hostinger.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='node_modules' \
    --exclude='ai-content-agent-ui/node_modules' \
    --exclude='ai-content-agent-ui/build' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='token.pickle' \
    --exclude='client_secret.json' \
    .

echo -e "${GREEN}✅ Package created: ai-content-agent-hostinger.tar.gz${NC}"

# Upload to Hostinger
echo -e "${YELLOW}📤 Uploading to Hostinger...${NC}"
scp ai-content-agent-hostinger.tar.gz $HOSTINGER_USER@$HOSTINGER_HOST:~/

# Deploy on Hostinger
echo -e "${YELLOW}🔧 Deploying on Hostinger...${NC}"
ssh $HOSTINGER_USER@$HOSTINGER_HOST << 'EOF'
    set -e
    
    echo "📁 Setting up project directory..."
    mkdir -p /home/public_html/ai-content-agent
    cd /home/public_html/ai-content-agent
    
    echo "📦 Extracting project files..."
    tar -xzf ~/ai-content-agent-hostinger.tar.gz
    
    echo "🐍 Setting up Python environment..."
    # Use Python 3.11 (already confirmed available)
    PYTHON_CMD="python3.11"
    
    echo "Using Python: $PYTHON_CMD"
    $PYTHON_CMD --version
    
    # Create virtual environment
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "🌐 Setting up web server configuration..."
    # Create .htaccess for Apache
    cat > .htaccess << 'HTACCESS'
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^api/(.*)$ wsgi.py/$1 [QSA,L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"

# CORS for API
Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization"
HTACCESS
    
    # Create WSGI configuration
    cat > wsgi.py << 'WSGI'
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
WSGI
    
    chmod +x wsgi.py
    
    echo "🔧 Setting up environment variables..."
    cat > .env << 'ENV'
FLASK_ENV=production
PORT=5050
USE_JSON_LIBRARY=true
FALLBACK_TO_SHEETS=true
# Add your actual values here:
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_SHEETS_TOPICS_ID=your_sheets_id_here
# GOOGLE_SHEETS_PROMPTS_ID=your_sheets_id_here
ENV
    
    echo "🧹 Cleaning up..."
    rm ~/ai-content-agent-hostinger.tar.gz
    
    echo "✅ Deployment completed!"
    echo "📝 Next steps:"
    echo "1. Edit .env file with your actual API keys"
    echo "2. Test the deployment: curl http://191.101.233.56/ai-content-agent/api/health"
    echo "3. Configure your domain to point to this directory"
EOF

# Clean up local package
rm ai-content-agent-hostinger.tar.gz

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. SSH into your server: ssh root@191.101.233.56"
echo "2. Edit environment variables: nano /home/public_html/ai-content-agent/.env"
echo "3. Test the API: curl http://191.101.233.56/ai-content-agent/api/health"
echo "4. Configure your domain to point to /home/public_html/ai-content-agent/"
