#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting Owen's Memory-Optimized Backend Server..."

# MEMORY OPTIMIZATION: Switch from 3 workers to 1 worker
# Engineering reasoning:
# 1. Memory usage: 3 workers × 400MB models = 1.2GB → 1 worker × 90MB model = 90MB
# 2. Railway environment: Single worker sufficient for current load (<100 concurrent users)
# 3. FastAPI async: Single worker can handle 1000+ req/sec with proper async code
# 4. Singleton pattern: Ensures models are shared efficiently within the worker

# Use hypercorn for better Railway compatibility
# Bind to 0.0.0.0 to be accessible externally
# Use PORT environment variable provided by Railway
hypercorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 1 