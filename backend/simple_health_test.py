#!/usr/bin/env python3
"""
Simple diagnostic script to test what's failing in Railway deployment
"""

import os
import sys
import traceback

def test_basic_imports():
    """Test if all imports work"""
    print("🔍 Testing basic imports...")
    try:
        import logging
        import uuid
        import json
        from datetime import datetime, timedelta
        from typing import Dict, List, Optional
        from contextlib import asynccontextmanager
        from enum import Enum
        import asyncio
        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_external_imports():
    """Test external library imports"""
    print("🔍 Testing external library imports...")
    try:
        from dotenv import load_dotenv
        from fastapi import FastAPI, HTTPException, Depends, Query, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.security import HTTPBearer
        from pydantic import BaseModel, Field
        print("✅ External library imports successful")
        return True
    except Exception as e:
        print(f"❌ External library imports failed: {e}")
        traceback.print_exc()
        return False

def test_local_imports():
    """Test local service imports"""
    print("🔍 Testing local service imports...")
    try:
        from services.database import db_service, DatabaseError
        print("✅ Database service import successful")
        
        from services.auth_service import auth_service, AuthenticationError
        print("✅ Auth service import successful")
        
        from dependencies import get_current_user_id
        print("✅ Dependencies import successful")
        
        from routers.chat_router import router as chat_router
        print("✅ Chat router import successful")
        
        from routers.grammar_router import router as grammar_router
        print("✅ Grammar router import successful")
        
        from middleware.security_middleware import SecurityMiddleware
        print("✅ Security middleware import successful")
        
        return True
    except Exception as e:
        print(f"❌ Local service imports failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("🔍 Testing environment variables...")
    try:
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        db_url = os.getenv("DATABASE_URL")
        
        print(f"JWT_SECRET_KEY: {'✅ SET' if jwt_secret else '❌ NOT SET'}")
        print(f"DATABASE_URL: {'✅ SET' if db_url else '❌ NOT SET'}")
        
        if not jwt_secret:
            print("❌ JWT_SECRET_KEY is required")
            return False
        
        if len(jwt_secret) < 32:
            print("❌ JWT_SECRET_KEY too short")
            return False
            
        if not db_url:
            print("❌ DATABASE_URL is required")
            return False
        
        print("✅ Environment variables validated")
        return True
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing database connection...")
    try:
        from services.database import db_service
        health = db_service.health_check()
        print(f"Database health: {health}")
        
        if health.get('status') == 'healthy':
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: {health.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        traceback.print_exc()
        return False

def test_fastapi_creation():
    """Test FastAPI app creation"""
    print("🔍 Testing FastAPI app creation...")
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="Test App")
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}
        
        print("✅ FastAPI app creation successful")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 Starting DOG Writer Backend Diagnostics")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_external_imports,
        test_environment,
        test_local_imports,
        test_database_connection,
        test_fastapi_creation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            results.append(False)
            print()
    
    print("=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed - the issue might be in the startup sequence")
    else:
        print("❌ Some tests failed - these are likely causing the 500 error")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 