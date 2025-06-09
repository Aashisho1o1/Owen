#!/bin/bash
set -e

# Set default port if not provided
PORT=${PORT:-8000}

echo "Starting Owen AI Backend on port $PORT"

# Start uvicorn with the port
exec python -m uvicorn app:app --host 0.0.0.0 --port "$PORT" 