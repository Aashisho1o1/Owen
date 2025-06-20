#!/usr/bin/env python3
"""
Railway Gemini Test

Quick test to verify that google-generativeai==0.7.2 works correctly
on Railway's Python environment.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_import():
    """Test Google Generative AI import."""
    try:
        import google.generativeai as genai
        logger.info("✅ google-generativeai imported successfully")
        logger.info(f"Version: {genai.__version__ if hasattr(genai, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import google-generativeai: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error importing google-generativeai: {e}")
        return False

def test_gemini_service():
    """Test Gemini service initialization."""
    try:
        # Set a dummy API key for testing
        os.environ['GEMINI_API_KEY'] = 'test-key-for-import-testing'
        
        from services.llm.gemini_service import gemini_service
        
        logger.info(f"✅ Gemini service imported successfully")
        logger.info(f"Service available: {gemini_service.is_available()}")
        
        model_info = gemini_service.get_model_info()
        logger.info(f"Model info: {model_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini service: {e}")
        return False

def test_fastapi_creation():
    """Test FastAPI app creation with Gemini service."""
    try:
        # Set required environment variables (proper lengths)
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing-with-proper-length-requirements'
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        from main import app
        
        logger.info("✅ FastAPI app created successfully")
        logger.info(f"App routes: {len(app.routes)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create FastAPI app: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Railway Gemini Compatibility Test")
    logger.info("=" * 50)
    
    tests = [
        ("Google Generative AI Import", test_gemini_import),
        ("Gemini Service Initialization", test_gemini_service),
        ("FastAPI App Creation", test_fastapi_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"🔍 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} passed")
            else:
                logger.error(f"❌ {test_name} failed")
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
        
        logger.info("-" * 30)
    
    logger.info("=" * 50)
    logger.info(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Railway deployment should work correctly.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Railway deployment may have issues.")
        sys.exit(1)

if __name__ == "__main__":
    main() 