#!/bin/bash

# Test Deployment Script for AI Content Agent
# Run this locally to verify everything works before deploying to Render

set -e

echo "🧪 AI Content Agent - Deployment Test"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required files exist
echo "📁 Checking required files..."
FILES=("app.py" "requirements.txt" "Dockerfile" "render.yaml" "ai-content-agent-ui/package.json")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file missing!"
        exit 1
    fi
done
echo ""

# Check if .env file exists
echo "🔐 Checking environment variables..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    if grep -q "OPENAI_API_KEY" .env; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY found in .env"
    else
        echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY not found in .env"
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found (optional for local testing)"
fi
echo ""

# Test Docker build
echo "🐳 Testing Docker build..."
if command -v docker &> /dev/null; then
    echo "Building Docker image..."
    docker build -t ai-content-agent-test . --quiet || {
        echo -e "${RED}✗${NC} Docker build failed!"
        exit 1
    }
    echo -e "${GREEN}✓${NC} Docker image built successfully"
    
    # Test if image can be run
    echo "Testing Docker container..."
    docker run -d --name ai-content-agent-test -p 5050:5050 ai-content-agent-test || {
        echo -e "${RED}✗${NC} Docker container failed to start!"
        docker rm -f ai-content-agent-test 2>/dev/null
        exit 1
    }
    
    echo "Waiting for container to start..."
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:5050/api/health &> /dev/null; then
        echo -e "${GREEN}✓${NC} Health endpoint responding"
    else
        echo -e "${RED}✗${NC} Health endpoint not responding"
        docker logs ai-content-agent-test
        docker stop ai-content-agent-test
        docker rm ai-content-agent-test
        exit 1
    fi
    
    # Cleanup
    docker stop ai-content-agent-test &> /dev/null
    docker rm ai-content-agent-test &> /dev/null
    docker rmi ai-content-agent-test &> /dev/null
    echo -e "${GREEN}✓${NC} Docker test passed"
else
    echo -e "${YELLOW}⚠${NC} Docker not installed, skipping Docker test"
fi
echo ""

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    echo "Python version: $(python3 --version)"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        echo -e "${GREEN}✓${NC} Virtual environment exists"
    else
        echo -e "${YELLOW}⚠${NC} No virtual environment found (run: python3 -m venv venv)"
    fi
    
    # Try to check required packages
    if pip3 show flask &> /dev/null; then
        echo -e "${GREEN}✓${NC} Flask installed"
    else
        echo -e "${YELLOW}⚠${NC} Flask not installed (run: pip install -r requirements.txt)"
    fi
else
    echo -e "${RED}✗${NC} Python3 not found!"
    exit 1
fi
echo ""

# Check Node.js and frontend
echo "📦 Checking Node.js and frontend..."
if command -v node &> /dev/null; then
    echo "Node version: $(node --version)"
    
    if [ -d "ai-content-agent-ui/node_modules" ]; then
        echo -e "${GREEN}✓${NC} Frontend dependencies installed"
    else
        echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed (run: cd ai-content-agent-ui && npm install)"
    fi
    
    if [ -d "ai-content-agent-ui/build" ]; then
        echo -e "${GREEN}✓${NC} Frontend build exists"
    else
        echo -e "${YELLOW}⚠${NC} Frontend not built (run: cd ai-content-agent-ui && npm run build)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Node.js not found (required for frontend)"
fi
echo ""

# Check Git status
echo "📊 Checking Git status..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Git repository initialized"
    
    # Check if there are uncommitted changes
    if git diff-index --quiet HEAD --; then
        echo -e "${GREEN}✓${NC} No uncommitted changes"
    else
        echo -e "${YELLOW}⚠${NC} You have uncommitted changes"
        echo "  Run: git add . && git commit -m 'Prepare for Render deployment'"
    fi
    
    # Check if remote is set
    if git remote -v | grep -q "origin"; then
        echo -e "${GREEN}✓${NC} Git remote configured"
        git remote -v | head -1
    else
        echo -e "${YELLOW}⚠${NC} No Git remote configured"
        echo "  Run: git remote add origin <your-github-repo-url>"
    fi
else
    echo -e "${RED}✗${NC} Not a Git repository!"
    echo "  Run: git init"
fi
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}✅ Pre-deployment checks complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Commit and push your code to GitHub"
echo "2. Go to https://render.com and create a new Web Service"
echo "3. Connect your GitHub repository"
echo "4. Set OPENAI_API_KEY in Render environment variables"
echo "5. Deploy!"
echo ""
echo "For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md"
echo "For quick start, see: RENDER_QUICK_START.md"

