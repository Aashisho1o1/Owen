#!/usr/bin/env python3
"""
Quick health check test for Owen AI Writer backend
Run this to verify the app works before deploying
"""

import asyncio
import httpx
import time

async def test_health_endpoints():
    """Test all health endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/health", 
        "/api/health",
        "/api/status",
        "/api/chat/basic"
    ]
    
    print("🔍 Testing Owen AI Writer Backend Health Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                print(f"Testing {endpoint}...", end=" ")
                response = await client.get(f"{base_url}{endpoint}")
                
                if response.status_code == 200:
                    print(f"✅ OK ({response.status_code})")
                    if endpoint == "/api/health":
                        data = response.json()
                        print(f"    Status: {data.get('status', 'unknown')}")
                        print(f"    Healthy: {data.get('healthy', 'unknown')}")
                else:
                    print(f"❌ FAILED ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
    
    print("=" * 50)
    print("✅ Health check test completed!")

if __name__ == "__main__":
    print("Starting backend health check test...")
    print("Make sure your backend is running with: uvicorn app:app --reload")
    print()
    asyncio.run(test_health_endpoints()) 