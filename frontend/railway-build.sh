#!/bin/bash

# Railway Build Script for Frontend
# Ensures all Rollup native binaries are available before building

echo "🚀 Starting Railway frontend build process..."

# Check Node.js version
echo "📋 Node.js version: $(node --version)"
echo "📋 NPM version: $(npm --version)"

# Ensure we're in the right directory
cd /app || cd frontend || pwd

# Clean any existing build artifacts
echo "🧹 Cleaning previous build artifacts..."
rm -rf dist/

# Install dependencies with explicit platform binaries
echo "📦 Installing dependencies with platform-specific binaries..."
npm ci --include=optional --force

# Verify Rollup binaries are available
echo "🔍 Checking for Rollup binaries..."
if [ -d "node_modules/@rollup/rollup-linux-x64-gnu" ]; then
    echo "✅ rollup-linux-x64-gnu found"
else
    echo "⚠️ Installing rollup-linux-x64-gnu..."
    npm install @rollup/rollup-linux-x64-gnu --force --no-save
fi

if [ -d "node_modules/@rollup/rollup-linux-x64-musl" ]; then
    echo "✅ rollup-linux-x64-musl found"
else
    echo "⚠️ Installing rollup-linux-x64-musl..."
    npm install @rollup/rollup-linux-x64-musl --force --no-save
fi

# List available Rollup binaries for debugging
echo "📂 Available Rollup binaries:"
ls -la node_modules/@rollup/ || echo "No @rollup directory found"

# Build the application
echo "🏗️ Building the application..."
npm run build

# Verify build output
if [ -d "dist" ]; then
    echo "✅ Build completed successfully!"
    echo "📊 Build output:"
    ls -la dist/
else
    echo "❌ Build failed - no dist directory created"
    exit 1
fi

echo "🎉 Railway frontend build completed!" 