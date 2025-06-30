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
    
    # Generate JWT secret if not set
    if [ -z "$JWT_SECRET_KEY" ]; then
        echo "⚠️ JWT_SECRET_KEY not set, generating one..."
        export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
        echo "✅ Generated JWT_SECRET_KEY (${#JWT_SECRET_KEY} characters)"
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

# Function to test database connectivity
test_database() {
    echo "🔍 Testing database connectivity..."
    
    python -c "
import os
import psycopg2
from urllib.parse import urlparse

try:
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL not set')
        exit(1)
    
    # Parse the DATABASE_URL
    parsed = urlparse(db_url)
    print(f'🔍 Database host: {parsed.hostname}')
    print(f'🔍 Database port: {parsed.port}')
    print(f'🔍 Database name: {parsed.path[1:] if parsed.path else \"unknown\"}')
    
    # Test connection
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f'✅ Database connection successful')
    print(f'🗄️ PostgreSQL version: {version[:50]}...')
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('💡 Common fixes:')
    print('   - Ensure PostgreSQL service is running in Railway')
    print('   - Check if DATABASE_URL uses postgres.railway.internal')
    print('   - Verify database credentials are correct')
    exit(1)
"
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

# Test database (optional - don't fail if this doesn't work)
echo "🔍 Testing database connectivity (optional)..."
if test_database; then
    echo "✅ Database test passed"
else
    echo "⚠️ Database test failed, but continuing startup..."
fi

# Install dependencies (Railway usually handles this, but just in case)
# install_dependencies

# Start the server
echo "🎯 All checks passed, starting server..."
start_server 