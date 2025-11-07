# Multi-stage build for AI Content Agent
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy frontend package files
COPY ai-content-agent-ui/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY ai-content-agent-ui/ ./

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/build ./ai-content-agent-ui/build

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5050

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5050/api/health').read()" || exit 1

# Run the application
CMD ["python", "app.py"]
