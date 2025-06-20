#!/bin/bash
set -e

# Load environment from .env if exists (for local development)
if [ -f .env ]; then
    echo "🔧 Loading local .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🚨 NUCLEAR RESET: Starting DOG Writer with aggressive process cleanup"

# Get the port from environment
PORT=${PORT:-8080}
echo "📡 Target port: $PORT"

# AGGRESSIVE PROCESS CLEANUP - Kill anything using our port
echo "🔍 Checking for processes using port $PORT..."

# Method 1: Use netstat to find processes
if command -v netstat &> /dev/null; then
    PIDS=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1 | grep -v '-' || true)
    if [ ! -z "$PIDS" ]; then
        echo "🚫 Found processes using port $PORT: $PIDS"
        for PID in $PIDS; do
            echo "💀 Killing process $PID"
            kill -9 $PID 2>/dev/null || true
        done
    fi
fi

# Method 2: Use lsof to find processes
if command -v lsof &> /dev/null; then
    LSOF_PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ ! -z "$LSOF_PIDS" ]; then
        echo "🚫 lsof found processes using port $PORT: $LSOF_PIDS"
        for PID in $LSOF_PIDS; do
            echo "💀 Killing process $PID (via lsof)"
            kill -9 $PID 2>/dev/null || true
        done
    fi
fi

# Method 3: Kill any Python processes (in case they're stuck)
echo "🐍 Cleaning up any stuck Python processes..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "hypercorn.*main:app" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true

# Wait a moment for cleanup
echo "⏳ Waiting for process cleanup..."
sleep 2

# Verify port is free
echo "🔍 Final port check..."
if command -v lsof &> /dev/null; then
    if lsof -ti:$PORT &> /dev/null; then
        echo "❌ Port $PORT still occupied after cleanup!"
        lsof -i:$PORT || true
    else
        echo "✅ Port $PORT is now free"
    fi
fi

# NUCLEAR OPTION: Try different binding strategies
echo "🚀 Starting hypercorn with nuclear binding strategy..."

# Strategy 1: IPv4 only first
echo "🔄 Attempt 1: IPv4 only binding"
python -m hypercorn main:app \
    --bind "0.0.0.0:$PORT" \
    --access-logfile - \
    --error-logfile - \
    --worker-class asyncio \
    --workers 1 \
    --timeout-keep-alive 5 \
    --timeout-graceful-shutdown 10 &

HYPERCORN_PID=$!
sleep 3

# Check if it started successfully
if kill -0 $HYPERCORN_PID 2>/dev/null; then
    echo "✅ Hypercorn started successfully with IPv4 binding (PID: $HYPERCORN_PID)"
    wait $HYPERCORN_PID
else
    echo "❌ IPv4 binding failed, trying dual-stack..."
    
    # Strategy 2: Dual-stack binding
    echo "🔄 Attempt 2: Dual-stack binding"
    exec python -m hypercorn main:app \
        --bind "[::]:$PORT" \
        --bind "0.0.0.0:$PORT" \
        --access-logfile - \
        --error-logfile - \
        --worker-class asyncio \
        --workers 1 \
        --timeout-keep-alive 5 \
        --timeout-graceful-shutdown 10
fi

echo "📊 Environment Check:"
echo "   DATABASE_URL: ${DATABASE_URL:+SET}" # Only show if set
echo "   JWT_SECRET_KEY: ${JWT_SECRET_KEY:+SET}"
echo "   GEMINI_API_KEY: ${GEMINI_API_KEY:+SET}"
echo "   OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}" 