#!/bin/bash
set -e

# Use hardcoded port 8000 for Railway
PORT=8000

echo "Starting Owen AI Backend on port $PORT"

# Start uvicorn with hardcoded port
exec python -m uvicorn app:app --host 0.0.0.0 --port 8000 