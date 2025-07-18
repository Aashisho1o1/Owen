#!/bin/bash

# DOG Writer Backend - Railway Startup Script
# Enhanced with debugging and error handling

set -e  # Exit on any error

echo "🚀 Starting DOG Writer Backend on Railway..."
echo "📅 Timestamp: $(date)"
echo "🐍 Python version: $(python --version)"
echo "📦 Current directory: $(pwd)"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment variables
validate_env() {
    echo "🔍 Validating environment variables..."
    
    # Critical variables
    if [ -z "$DATABASE_URL" ]; then
        echo "❌ CRITICAL: DATABASE_URL is not set!"
        echo "💡 This should be automatically set by Railway PostgreSQL service"
        echo "💡 Check Railway dashboard -> Variables tab"
        exit 1
    else
        echo "✅ DATABASE_URL is set (${#DATABASE_URL} characters)"
        # Show masked version for debugging
        echo "🔍 DATABASE_URL format: ${DATABASE_URL:0:20}...${DATABASE_URL: -10}"
    fi
    
    # CRITICAL: JWT_SECRET_KEY must be set in Railway environment variables
    if [ -z "$JWT_SECRET_KEY" ]; then
        echo "❌ CRITICAL: JWT_SECRET_KEY environment variable is not set!"
        echo "💡 This MUST be set in Railway dashboard -> Variables tab"
        echo "💡 Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
        echo "🚨 SECURITY: Auto-generating JWT keys invalidates all user sessions on restart!"
        echo "🚨 DEPLOYMENT BLOCKED: Set JWT_SECRET_KEY in Railway environment variables"
        exit 1
    else
        echo "✅ JWT_SECRET_KEY is set (${#JWT_SECRET_KEY} characters)"
    fi
    
    # Optional variables
    if [ -z "$GEMINI_API_KEY" ]; then
        echo "⚠️ GEMINI_API_KEY not set (AI features may be limited)"
    else
        echo "✅ GEMINI_API_KEY is set"
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️ OPENAI_API_KEY not set (AI features may be limited)"
    else
        echo "✅ OPENAI_API_KEY is set"
    fi
    
    # Railway specific variables
    echo "🚂 Railway Environment: ${RAILWAY_ENVIRONMENT:-unknown}"
    echo "🚂 Railway Service: ${RAILWAY_SERVICE:-unknown}"
    echo "🚂 Railway Project: ${RAILWAY_PROJECT_NAME:-unknown}"
}



# Function to install dependencies if needed
install_dependencies() {
    echo "📦 Checking Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        echo "📋 Found requirements.txt"
        pip install --no-cache-dir -r requirements.txt
        echo "✅ Dependencies installed"
    else
        echo "⚠️ No requirements.txt found"
    fi
}

# Function to start the server
start_server() {
    echo "🌐 Starting FastAPI server..."
    
    # Use Railway's PORT or default to 8000
    PORT=${PORT:-8000}
    HOST=${HOST:-0.0.0.0}
    
    echo "🔧 Server configuration:"
    echo "   Host: $HOST"
    echo "   Port: $PORT"
    echo "   Workers: 1 (Railway optimized)"
    
    # Start with hypercorn for better Railway compatibility
    if command_exists hypercorn; then
        echo "🚀 Starting with Hypercorn (production server)..."
        exec hypercorn main:app \
            --bind $HOST:$PORT \
            --workers 1 \
            --worker-class asyncio \
            --access-logfile - \
            --error-logfile - \
            --log-level info \
            --graceful-timeout 30 \
            --keep-alive 65
    elif command_exists uvicorn; then
        echo "🚀 Starting with Uvicorn (fallback server)..."
        exec uvicorn main:app \
            --host $HOST \
            --port $PORT \
            --workers 1 \
            --access-log \
            --log-level info
    else
        echo "❌ No ASGI server found (hypercorn or uvicorn required)"
        exit 1
    fi
}

# Main execution
echo "🔧 Starting Railway deployment process..."

# Validate environment
validate_env



# Install dependencies (Railway usually handles this, but just in case)
# install_dependencies

# Start the server
echo "🎯 All checks passed, starting server..."
start_server 