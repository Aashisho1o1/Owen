#!/bin/bash
set -e

echo "🚀 Starting DOG Writer Backend (Railway Deployment)"
echo "📅 Timestamp: $(date)"
echo "🐍 Python version: $(python --version)"

# Get port from environment (Railway sets this automatically)
PORT=${PORT:-8080}
echo "📡 Port: $PORT"

# Environment validation with graceful handling
echo "🔧 Environment Check:"

# Critical: DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ CRITICAL: DATABASE_URL not set!"
    echo "💡 Check Railway PostgreSQL service and environment variables"
    exit 1
else
    echo "✅ DATABASE_URL: SET (${#DATABASE_URL} chars)"
fi

# Generate JWT secret if missing
if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️ JWT_SECRET_KEY not set, generating temporary one..."
    export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
    echo "✅ JWT_SECRET_KEY: GENERATED (${#JWT_SECRET_KEY} chars)"
else
    echo "✅ JWT_SECRET_KEY: SET (${#JWT_SECRET_KEY} chars)"
fi

# Optional: AI API keys
echo "🤖 AI API Keys:"
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ GEMINI_API_KEY: NOT SET (AI features limited)"
else
    echo "✅ GEMINI_API_KEY: SET"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ OPENAI_API_KEY: NOT SET (AI features limited)"
else
    echo "✅ OPENAI_API_KEY: SET"
fi

# Railway environment info
echo "🚂 Railway Info:"
echo "   Environment: ${RAILWAY_ENVIRONMENT:-unknown}"
echo "   Service: ${RAILWAY_SERVICE:-unknown}"

# Quick database connectivity test (optional)
echo "🔍 Testing database connectivity..."
python -c "
import os
try:
    import psycopg2
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️ Database test failed: {e}')
    print('💡 App will start anyway - database issues will be logged')
" || echo "⚠️ Database test skipped (continuing startup)"

echo "🚀 Starting FastAPI application with hypercorn..."

# Debug: Show current directory and contents
echo "📁 Current directory: $(pwd)"
echo "📂 Directory contents:"
ls -la

# Check if main.py exists
if [ -f "main.py" ]; then
    echo "✅ main.py found in current directory"
else
    echo "❌ main.py NOT found in current directory"
    echo "🔍 Looking for main.py in parent directories..."
    find .. -name "main.py" -type f 2>/dev/null || echo "main.py not found"
fi

# Start the application with Railway-optimized settings
# Use the current directory's main module
echo "🚀 Starting server from $(pwd)/main.py..."
exec python -m hypercorn main:app \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    --worker-class asyncio \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --graceful-timeout 30 \
    --keep-alive 65 