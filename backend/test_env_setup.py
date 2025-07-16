#!/usr/bin/env python3
"""
Test Environment Setup
Sets up minimal environment variables for testing without full deployment
"""

import os
import sys
from pathlib import Path

def setup_test_environment():
    """Set up minimal environment variables for testing"""
    
    # Set up basic environment variables
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-local-testing-only-not-production'
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test_db'  # Mock DB URL
    os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', 'test-key')  # Use real key if available
    os.environ['RAILWAY_ENVIRONMENT'] = 'test'
    
    # Disable telemetry
    os.environ['ANONYMIZED_TELEMETRY'] = 'False'
    os.environ['CHROMA_TELEMETRY'] = 'False'
    os.environ['CHROMA_TELEMETRY_ENABLED'] = 'False'
    os.environ['CHROMA_DISABLE_TELEMETRY'] = 'True'
    os.environ['CHROMA_ANONYMIZED_TELEMETRY'] = 'False'
    os.environ['POSTHOG_DISABLED'] = 'True'
    os.environ['POSTHOG_CAPTURE_DISABLED'] = 'True'
    os.environ['TELEMETRY_DISABLED'] = 'True'
    
    print("🔧 Test environment variables set up:")
    print(f"   JWT_SECRET_KEY: {'✅ SET' if os.getenv('JWT_SECRET_KEY') else '❌ NOT SET'}")
    print(f"   DATABASE_URL: {'✅ SET' if os.getenv('DATABASE_URL') else '❌ NOT SET'}")
    print(f"   GEMINI_API_KEY: {'✅ SET' if os.getenv('GEMINI_API_KEY') else '❌ NOT SET'}")
    print(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")

if __name__ == "__main__":
    setup_test_environment() 