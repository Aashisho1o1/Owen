#!/usr/bin/env python3
"""
Simple health check script to test Railway deployment
Run this locally to verify the deployed service is working
"""

import requests
import sys

def check_railway_health(backend_url):
    """Check if the Railway backend is responding"""
    try:
        print(f"🔍 Checking Railway backend: {backend_url}")
        
        # Test root endpoint
        response = requests.get(f"{backend_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
        # Test health endpoint
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code in [200, 503]:  # 503 is OK for unhealthy DB
            data = response.json()
            print(f"✅ Health endpoint working: {data}")
            if data.get('database', {}).get('status') == 'unhealthy':
                print("⚠️  Database unhealthy (expected - need to add DATABASE_URL)")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python health_check_simple.py <backend_url>")
        print("Example: python health_check_simple.py https://your-backend.railway.app")
        sys.exit(1)
    
    backend_url = sys.argv[1].rstrip('/')
    success = check_railway_health(backend_url)
    
    if success:
        print("\n🎉 Railway backend is working!")
        print("🔧 Next step: Add DATABASE_URL environment variable")
    else:
        print("\n💥 Railway backend is not responding properly")
    
    sys.exit(0 if success else 1) 