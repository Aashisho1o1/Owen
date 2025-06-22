#!/bin/bash
set -e

echo "🚀 Starting DOG Writer Backend (Simple Mode)"

# Get port from environment (Railway sets this automatically)
PORT=${PORT:-8080}
echo "📡 Port: $PORT"

# Environment check
echo "🔧 Environment Check:"
echo "   DATABASE_URL: ${DATABASE_URL:+✅ SET}"
echo "   JWT_SECRET_KEY: ${JWT_SECRET_KEY:+✅ SET}"
echo "   GEMINI_API_KEY: ${GEMINI_API_KEY:+✅ SET}"
echo "   OPENAI_API_KEY: ${OPENAI_API_KEY:+✅ SET}"

# Run the diagnostic script first
echo "🔍 Running diagnostic checks..."
python railway_deployment_debug.py

echo "🚀 Starting application with hypercorn..."

# Simple hypercorn start - let Railway handle the port binding
exec python -m hypercorn main:app \
    --bind "0.0.0.0:$PORT" \
    --access-logfile - \
    --error-logfile - \
    --workers 1 