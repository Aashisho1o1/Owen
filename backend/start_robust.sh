#!/bin/bash

echo "🚀 Starting DOG Writer Backend with Robust Error Handling"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port_processes() {
    local port=$1
    log "🔍 Checking for processes on port $port..."
    
    # Find and kill processes using the port
    lsof -ti:$port | xargs -r kill -9 2>/dev/null || true
    sleep 2
    
    if check_port $port; then
        log "⚠️ Some processes still running on port $port, forcing cleanup..."
        fuser -k $port/tcp 2>/dev/null || true
        sleep 2
    fi
}

# Function to test Python imports
test_imports() {
    log "🐍 Testing Python imports..."
    
    # Test basic imports
    python3 -c "
import sys
import os
import logging
from datetime import datetime
print('✅ Basic imports successful')
" || {
        log "❌ Basic Python imports failed"
        return 1
    }
    
    # Test FastAPI imports
    python3 -c "
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
print('✅ FastAPI imports successful')
" || {
        log "❌ FastAPI imports failed"
        return 1
    }
    
    # Test application imports
    python3 -c "
import sys
sys.path.insert(0, '/app')
from services.database import db_service
from routers.auth_router import router as auth_router
print('✅ Application imports successful')
" || {
        log "❌ Application imports failed"
        return 1
    }
    
    return 0
}



# Function to start the application
start_application() {
    local port=${PORT:-8080}
    local bind_host="0.0.0.0:$port"
    local workers=${WEB_CONCURRENCY:-1}
    
    log "🚀 Starting application on $bind_host with $workers workers..."
    
    # Try hypercorn first (preferred for Railway)
    if command -v hypercorn >/dev/null 2>&1; then
        log "📡 Using hypercorn server..."
        exec hypercorn main:app \
            --bind "$bind_host" \
            --workers "$workers" \
            --worker-class asyncio \
            --access-logfile - \
            --error-logfile - \
            --log-level info \
            --graceful-timeout 30 \
            --keep-alive 30 \
            --max-requests 1000 \
            --max-requests-jitter 100
    # Fallback to uvicorn
    elif command -v uvicorn >/dev/null 2>&1; then
        log "📡 Fallback to uvicorn server..."
        exec uvicorn main:app \
            --host 0.0.0.0 \
            --port "$port" \
            --workers "$workers" \
            --log-level info \
            --access-log \
            --loop asyncio
    else
        log "❌ No ASGI server found (hypercorn or uvicorn required)"
        exit 1
    fi
}

# Main execution
main() {
    log "🏁 Starting robust backend deployment process..."
    
    # Environment checks
    PORT=${PORT:-8080}
    log "📡 Target port: $PORT"
    log "🌍 Environment: ${RAILWAY_ENVIRONMENT:-local}"
    
    # Change to app directory
    cd /app || {
        log "❌ Failed to change to /app directory"
        exit 1
    }
    
    # Clean up any existing processes
    kill_port_processes $PORT
    
    # Wait for port to be free
    for i in {1..10}; do
        if ! check_port $PORT; then
            log "✅ Port $PORT is available"
            break
        else
            log "⏳ Waiting for port $PORT to be free (attempt $i/10)..."
            sleep 2
        fi
        
        if [ $i -eq 10 ]; then
            log "❌ Port $PORT still occupied after 20 seconds"
            exit 1
        fi
    done
    
    # Test imports
    if ! test_imports; then
        log "❌ Import tests failed - cannot start application"
        exit 1
    fi
    

    
    # Start application
    log "🚀 All checks passed - starting application..."
    start_application
}

# Set error handling
set -e
set -o pipefail

# Trap errors
trap 'log "❌ Script failed at line $LINENO"' ERR

# Run main function
main "$@" 