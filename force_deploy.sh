#!/bin/bash

echo "🚀 Forcing Railway deployment during high traffic period..."

# Method 1: Create a deployment trigger file
echo "Creating deployment trigger..."
echo "$(date)" > .force-deploy-$(date +%s)

# Method 2: Update a tracked file to trigger deployment
echo "# Force deploy: $(date)" >> dog-writer/backend/.railway-clean

# Method 3: Use Railway CLI with force flags
echo "Attempting Railway CLI deployment..."

# Change to backend directory
cd dog-writer/backend

# Try multiple Railway deployment methods
echo "Method 1: Standard deployment..."
railway up --detach 2>/dev/null || echo "Standard deployment failed"

echo "Method 2: Force redeploy..."
echo "y" | railway redeploy 2>/dev/null || echo "Redeploy failed"

# Method 4: Create a new deployment by modifying a file
echo "Method 3: File modification trigger..."
echo "# Deployment trigger: $(date)" >> .force-deploy

# Method 5: Environment variable trigger
echo "Method 4: Environment trigger..."
railway run echo "Deployment triggered at $(date)"

# Clean up
echo "Cleaning up trigger files..."
rm -f .force-deploy
rm -f ../../.force-deploy-*

echo "✅ Force deployment attempts completed!"
echo "Check your Railway dashboard for deployment status." 