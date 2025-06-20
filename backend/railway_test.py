#!/usr/bin/env python3
"""
Railway Startup Test Script
Test basic Python environment and imports to identify startup failures
"""

import sys
import os
import traceback
from datetime import datetime

def test_python_environment():
    """Test basic Python environment"""
    print(f"🐍 Python version: {sys.version}")
    print(f"📍 Current working directory: {os.getcwd()}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    
def test_environment_variables():
    """Test critical environment variables"""
    print("\n🔍 Environment Variables:")
    critical_vars = ['DATABASE_URL', 'JWT_SECRET_KEY', 'PORT', 'RAILWAY_ENVIRONMENT']
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Show first 20 chars for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: NOT SET")

def test_basic_imports():
    """Test critical imports that might cause startup failures"""
    print("\n📦 Testing Critical Imports:")
    
    imports_to_test = [
        ('os', 'os'),
        ('FastAPI', 'fastapi'),
        ('PostgreSQL driver', 'psycopg2'),
        ('JWT', 'jwt'),
        ('bcrypt', 'bcrypt'),
        ('dotenv', 'dotenv'),
    ]
    
    for name, module in imports_to_test:
        try:
            __import__(module)
            print(f"   ✅ {name}: OK")
        except ImportError as e:
            print(f"   ❌ {name}: FAILED - {e}")
            return False
    
    return True

def test_app_imports():
    """Test our application imports"""
    print("\n🎯 Testing Application Imports:")
    
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        print("   🔄 Testing services.database...")
        from services.database import db_service
        print("   ✅ Database service: OK")
        
        print("   🔄 Testing services.auth_service...")  
        from services.auth_service import auth_service
        print("   ✅ Auth service: OK")
        
        print("   🔄 Testing main app...")
        from main import app
        print("   ✅ Main app: OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Application import failed: {e}")
        print(f"   📝 Full traceback:")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️  Testing Database Connection:")
    
    try:
        from services.database import db_service
        
        # Test basic connection
        health = db_service.health_check()
        print(f"   📊 Database health: {health}")
        
        if health.get('status') == 'healthy':
            print("   ✅ Database: CONNECTED")
            return True
        else:
            print(f"   ❌ Database: UNHEALTHY - {health.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Railway Startup Test - " + datetime.now().isoformat())
    print("=" * 60)
    
    try:
        test_python_environment()
        test_environment_variables()
        
        if not test_basic_imports():
            print("\n❌ CRITICAL: Basic imports failed!")
            sys.exit(1)
            
        if not test_app_imports():
            print("\n❌ CRITICAL: Application imports failed!")
            sys.exit(1)
            
        if not test_database_connection():
            print("\n⚠️  WARNING: Database connection failed!")
            print("   💡 App may start but won't function properly")
        
        print("\n✅ ALL TESTS PASSED - App should start successfully!")
        print("🚀 Proceeding to start FastAPI application...")
        
        # Use the same method as start.sh for Railway compatibility
        port = int(os.getenv('PORT', 8000))
        print(f"🌐 Starting FastAPI on port {port} with hypercorn (Railway compatible)")
        
        # Use exec to replace the process - same as start.sh
        os.execvp("python", [
            "python", "-m", "hypercorn", "main:app",
            "--bind", f"[::]:{port}",  # IPv6 binding
            "--bind", f"0.0.0.0:{port}",  # IPv4 binding  
            "--access-logfile", "-",
            "--error-logfile", "-"
        ])
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 