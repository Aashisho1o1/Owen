#!/usr/bin/env python3
"""
Test script to verify character voice router imports correctly
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_router_import():
    """Test importing the character voice router"""
    try:
        print("🔄 Testing character voice router import...")
        
        # Test individual imports
        print("1. Testing dependencies import...")
        from dependencies import get_current_user_id
        print("   ✅ dependencies imported")
        
        print("2. Testing services import...")
        from services.character_voice_service import CharacterVoiceService
        print("   ✅ CharacterVoiceService imported")
        
        print("3. Testing schemas import...")
        from models.schemas import (
            VoiceConsistencyRequest, VoiceConsistencyResponse, VoiceConsistencyResult,
            CharacterVoiceProfilesResponse, CharacterVoiceProfile
        )
        print("   ✅ schemas imported")
        
        print("4. Testing rate limiter import...")
        from services.rate_limiter import SimpleRateLimiter
        print("   ✅ rate limiter imported")
        
        print("5. Testing security logger import...")
        from services.security_logger import SecurityLogger
        print("   ✅ security logger imported")
        
        print("6. Testing router import...")
        from routers.character_voice_router import router
        print("   ✅ router imported")
        
        print("7. Checking router routes...")
        if hasattr(router, 'routes'):
            print(f"   Router has {len(router.routes)} routes:")
            for route in router.routes:
                if hasattr(route, 'methods') and hasattr(route, 'path'):
                    print(f"     {list(route.methods)} {route.path}")
        else:
            print("   ❌ Router has no routes attribute")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_router_import()
    sys.exit(0 if success else 1) 