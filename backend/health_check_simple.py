#!/usr/bin/env python3
"""
Simple health check script to verify all services are working
Updated with Gemini service verification
"""

import asyncio
import os
from services.llm.gemini_service import gemini_service
from services.llm.openai_service import openai_service

async def check_gemini():
    """Check Gemini service health"""
    print("🔍 Checking Gemini service...")
    
    try:
        # Check if service is available
        if not gemini_service.is_available():
            print("❌ Gemini service not available")
            info = gemini_service.get_model_info()
            print(f"   Service info: {info}")
            return False
        
        print(f"✅ Gemini service available with model: {gemini_service.model_name}")
        
        # Test simple generation
        test_response = await gemini_service.generate_text("Say 'Hello, this is a test!'")
        if test_response and len(test_response) > 0:
            print(f"✅ Gemini test successful: {test_response[:50]}...")
            return True
        else:
            print("❌ Gemini test failed - empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

async def check_openai():
    """Check OpenAI service health"""
    print("🔍 Checking OpenAI service...")
    
    try:
        if not openai_service.available:
            print("❌ OpenAI service not available")
            return False
        
        print("✅ OpenAI service available")
        
        # Test simple generation
        test_response = await openai_service.generate_text("Say 'Hello, this is a test!'")
        if test_response and len(test_response) > 0:
            print(f"✅ OpenAI test successful: {test_response[:50]}...")
            return True
        else:
            print("❌ OpenAI test failed - empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

async def main():
    """Run all health checks"""
    print("🏥 Starting comprehensive health checks...")
    print("=" * 50)
    
    # Check environment variables
    print("🔑 Environment Variables:")
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    
    print(f"   GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Missing'}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
    print(f"   JWT_SECRET_KEY: {'✅ Set' if jwt_secret else '❌ Missing'}")
    print()
    
    # Check services
    results = []
    
    gemini_ok = await check_gemini()
    results.append(("Gemini", gemini_ok))
    print()
    
    openai_ok = await check_openai()
    results.append(("OpenAI", openai_ok))
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Health Check Summary:")
    all_good = True
    for service, status in results:
        status_icon = "✅" if status else "❌"
        print(f"   {service}: {status_icon}")
        if not status:
            all_good = False
    
    if all_good:
        print("\n🎉 All services are healthy!")
    else:
        print("\n⚠️ Some services have issues. Check the logs above.")
    
    return all_good

if __name__ == "__main__":
    asyncio.run(main()) 