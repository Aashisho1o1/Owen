#!/bin/bash
# Quick test script for backend

echo "🧪 Testing Owen Voice Analyzer Backend"
echo ""

# Check if server is running
echo "1. Checking if server is running..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Test registration
echo "2. Testing user registration..."
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test1234"}' | python3 -m json.tool
echo ""

# Test login
echo "3. Testing user login..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test1234"}')

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✅ Got token: ${TOKEN:0:20}..."
echo ""

# Test voice analysis
echo "4. Testing voice analysis..."
curl -s -X POST http://localhost:8000/api/voice/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "text": "Jake: Listen up. We got five minutes.\nJake: No time for questions. Move!\nSarah: But what about the—\nJake: I said move! Now!"
  }' | python3 -m json.tool
echo ""

# Test get profiles
echo "5. Getting character profiles..."
curl -s -X GET http://localhost:8000/api/voice/profiles \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "✅ All tests complete!"
