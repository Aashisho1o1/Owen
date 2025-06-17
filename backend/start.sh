#!/bin/bash
set -e

echo "Starting Owen AI Backend on port $PORT"

# Start uvicorn with correct module reference and Railway port variable
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT 