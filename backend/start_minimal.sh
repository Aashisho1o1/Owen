#!/bin/bash
set -e

echo "🧪 TESTING: Starting minimal FastAPI app to test CORS"

# Get the port from environment
PORT=${PORT:-8080}
echo "📡 Target port: $PORT"

# Run the minimal test app
echo "🚀 Starting minimal FastAPI app..."
exec python -m hypercorn minimal_test:app \
    --bind "0.0.0.0:$PORT" \
    --access-logfile - \
    --error-logfile - \
    --worker-class asyncio \
    --workers 1 \
    --keep-alive 5 \
    --graceful-timeout 10 