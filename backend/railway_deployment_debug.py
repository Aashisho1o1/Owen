#!/usr/bin/env python3
"""
Railway Deployment Debug Script
Helps identify common deployment issues when deploying to Railway.
"""

import os
import sys
import json
import psutil
import traceback
from datetime import datetime

def print_header(title):
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_environment():
    """Check critical environment variables"""
    print_header("ENVIRONMENT VARIABLES CHECK")
    
    critical_vars = [
        'DATABASE_URL',
        'JWT_SECRET_KEY', 
        'PORT',
        'RAILWAY_ENVIRONMENT_NAME'
    ]
    
    optional_vars = [
        'GEMINI_API_KEY',
        'OPENAI_API_KEY',
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID'
    ]
    
    print("✅ Critical Variables:")
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            if var == 'DATABASE_URL':
                # Mask sensitive parts of DATABASE_URL
                if 'postgresql://' in value:
                    parts = value.split('@')
                    if len(parts) > 1:
                        masked = f"postgresql://***:***@{parts[1]}"
                    else:
                        masked = "postgresql://***"
                else:
                    masked = "***"
                print(f"  {var}: {masked}")
            elif 'KEY' in var or 'SECRET' in var:
                print(f"  {var}: {'*' * min(len(value), 8)}...")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  ❌ {var}: NOT SET")
    
    print("\n🔧 Optional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                print(f"  {var}: {'*' * min(len(value), 8)}...")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: NOT SET")

def test_imports():
    """Test critical imports"""
    print_header("IMPORT TEST")
    
    imports_to_test = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'uvicorn'),
        ('hypercorn', 'hypercorn'),
        ('psycopg2', 'psycopg2'),
        ('jwt', 'PyJWT'),
        ('bcrypt', 'bcrypt'),
        ('google.generativeai', 'google-generativeai'),
        ('openai', 'openai'),
        ('dotenv', 'python-dotenv')
    ]
    
    for module_name, package_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {package_name}: OK")
        except ImportError as e:
            print(f"❌ {package_name}: FAILED - {e}")

def test_database_connection():
    """Test database connectivity"""
    print_header("DATABASE CONNECTION TEST")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
        
        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connection successful")
        print(f"   PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")

def check_port_availability():
    """Check if the target port is available"""
    print_header("PORT AVAILABILITY CHECK")
    
    port = int(os.getenv('PORT', 8080))
    print(f"Target port: {port}")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"❌ Port {port} is already in use")
        else:
            print(f"✅ Port {port} is available")
            
    except Exception as e:
        print(f"⚠️ Port check failed: {e}")

def test_fastapi_creation():
    """Test basic FastAPI app creation"""
    print_header("FASTAPI APP CREATION TEST")
    
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Test App")
        
        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
        
        print("✅ FastAPI app created successfully")
        print("✅ Test endpoint added successfully")
        
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        traceback.print_exc()

def system_info():
    """Display system information"""
    print_header("SYSTEM INFORMATION")
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    
    try:
        print(f"CPU count: {psutil.cpu_count()}")
        memory = psutil.virtual_memory()
        print(f"Total memory: {memory.total / (1024**3):.1f} GB")
        print(f"Available memory: {memory.available / (1024**3):.1f} GB")
    except:
        print("⚠️ Could not get system resource info")

def main():
    """Run all diagnostic checks"""
    print("🚀 Railway Deployment Diagnostic Tool")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()
    
    system_info()
    print()
    
    check_environment()
    print()
    
    test_imports()
    print()
    
    test_database_connection()
    print()
    
    check_port_availability()
    print()
    
    test_fastapi_creation()
    print()
    
    print_header("DIAGNOSTIC COMPLETE")
    print("If you see any ❌ errors above, those need to be fixed for deployment to work.")
    print("Share this output with your team to help troubleshoot deployment issues.")

if __name__ == "__main__":
    main() 