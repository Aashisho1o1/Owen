#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting Owen's Enhanced Backend Server..."

# Use hypercorn for better Railway compatibility
# Bind to 0.0.0.0 to be accessible externally
# Use PORT environment variable provided by Railway
hypercorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 3 