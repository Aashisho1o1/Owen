#!/bin/bash
set -e

# Load environment from .env if exists (for local development)
if [ -f .env ]; then
    echo "🔧 Loading local .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default port if not provided
PORT=${PORT:-8000}

echo "🚀 Starting DOG Writer Backend on port $PORT"
echo "📊 Environment Check:"
echo "   DATABASE_URL: ${DATABASE_URL:+SET}" # Only show if set
echo "   JWT_SECRET_KEY: ${JWT_SECRET_KEY:+SET}"
echo "   GEMINI_API_KEY: ${GEMINI_API_KEY:+SET}"
echo "   OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}"

# Railway-specific debugging: Check if port is available
echo "🔍 Checking port $PORT availability..."
if command -v netstat >/dev/null 2>&1; then
    echo "🔍 Port check results:"
    netstat -tuln | grep ":$PORT " || echo "✅ Port $PORT appears available"
fi

# Kill any existing processes on the port (Railway cleanup)
if command -v lsof >/dev/null 2>&1; then
    echo "🧹 Cleaning up any existing processes on port $PORT..."
    lsof -ti:$PORT | xargs -r kill -9 || true
fi

# Railway-specific: Use hypercorn for proper IPv4/IPv6 dual stack binding
# This enables both public access and private network access
echo "🚂 Starting hypercorn with dual-stack binding..."
exec python -m hypercorn main:app --bind [::]:$PORT --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - 