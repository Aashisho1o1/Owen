#!/usr/bin/env python3
"""
Railway Backend Debug Script
Comprehensive diagnostic tool to identify backend deployment issues
"""

import os
import sys
import asyncio
import logging
import traceback
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_section(title):
    """Log a section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def log_result(test_name, success, details=None):
    """Log test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

async def main():
    """Main diagnostic function"""
    print("🚀 Railway Backend Diagnostic Tool")
    print(f"🕐 Started at: {datetime.now()}")
    
    # 1. Environment Check
    log_section("ENVIRONMENT VARIABLES")
    
    required_vars = [
        'DATABASE_URL', 'JWT_SECRET_KEY', 'PORT', 'RAILWAY_ENVIRONMENT'
    ]
    
    optional_vars = [
        'GEMINI_API_KEY', 'OPENAI_API_KEY', 'RAILWAY_SERVICE', 'RAILWAY_DEPLOYMENT_ID'
    ]
    
    env_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var or 'URL' in var:
                masked = f"{value[:8]}...{value[-8:]}" if len(value) > 16 else "***"
                log_result(f"{var}", True, f"SET ({masked})")
            else:
                log_result(f"{var}", True, f"SET ({value})")
        else:
            log_result(f"{var}", False, "NOT SET")
            env_ok = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                masked = f"{value[:8]}...{value[-8:]}" if len(value) > 16 else "***"
                log_result(f"{var} (optional)", True, f"SET ({masked})")
            else:
                log_result(f"{var} (optional)", True, f"SET ({value})")
        else:
            log_result(f"{var} (optional)", False, "NOT SET")
    
    # 2. Python Environment Check
    log_section("PYTHON ENVIRONMENT")
    
    log_result("Python Version", True, f"{sys.version}")
    log_result("Current Directory", True, os.getcwd())
    log_result("Python Path", True, sys.path[0])
    
    # 3. Module Import Tests
    log_section("MODULE IMPORTS")
    
    import_tests = [
        ("os", "import os"),
        ("sys", "import sys"),
        ("asyncio", "import asyncio"),
        ("logging", "import logging"),
        ("datetime", "from datetime import datetime"),
        ("dotenv", "from dotenv import load_dotenv"),
        ("fastapi", "from fastapi import FastAPI"),
        ("cors", "from fastapi.middleware.cors import CORSMiddleware"),
        ("psycopg2", "import psycopg2"),
        ("jwt", "import jwt"),
        ("bcrypt", "import bcrypt"),
    ]
    
    for name, import_statement in import_tests:
        try:
            exec(import_statement)
            log_result(f"Import {name}", True)
        except Exception as e:
            log_result(f"Import {name}", False, str(e))
    
    # 4. Database Connection Test
    log_section("DATABASE CONNECTION")
    
    try:
        # Test database import
        from services.database import db_service
        log_result("Database service import", True)
        
        # Test database health
        health = db_service.health_check()
        if health['status'] == 'healthy':
            log_result("Database connection", True, f"Users: {health.get('total_users', 0)}, Docs: {health.get('total_documents', 0)}")
        else:
            log_result("Database connection", False, health.get('error', 'Unknown error'))
            
    except Exception as e:
        log_result("Database connection", False, str(e))
        traceback.print_exc()
    
    # 5. FastAPI App Creation Test
    log_section("FASTAPI APP CREATION")
    
    try:
        # Test basic FastAPI app creation
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="Test App")
        log_result("FastAPI app creation", True)
        
        # Test CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        log_result("CORS middleware", True)
        
        # Test route creation
        @app.get("/test")
        async def test_route():
            return {"status": "ok"}
        
        log_result("Route creation", True)
        
    except Exception as e:
        log_result("FastAPI app creation", False, str(e))
        traceback.print_exc()
    
    # 6. Router Import Tests
    log_section("ROUTER IMPORTS")
    
    routers = [
        ("auth_router", "routers.auth_router"),
        ("document_router", "routers.document_router"),
        ("folder_router", "routers.folder_router"),
        ("chat_router", "routers.chat_router"),
        ("character_voice_router", "routers.character_voice_router"),
    ]
    
    for name, module_path in routers:
        try:
            module = __import__(module_path, fromlist=["router"])
            router = getattr(module, "router")
            log_result(f"Router {name}", True)
        except Exception as e:
            log_result(f"Router {name}", False, str(e))
    
    # 7. Main App Import Test
    log_section("MAIN APP IMPORT")
    
    try:
        # Test main app import
        import main
        log_result("Main module import", True)
        
        # Test app object access
        app = main.app
        log_result("App object access", True)
        
        # Count routes
        route_count = len(app.routes)
        log_result("Route count", True, f"{route_count} routes")
        
    except Exception as e:
        log_result("Main app import", False, str(e))
        traceback.print_exc()
    
    # 8. Port and Network Test
    log_section("NETWORK CONFIGURATION")
    
    port = os.getenv('PORT', '8080')
    log_result("Port configuration", True, f"Port {port}")
    
    # Test if port is available
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', int(port)))
        sock.close()
        
        if result == 0:
            log_result("Port availability", False, f"Port {port} is already in use")
        else:
            log_result("Port availability", True, f"Port {port} is available")
    except Exception as e:
        log_result("Port availability", False, str(e))
    
    # 9. Start Server Test (if not already running)
    log_section("SERVER STARTUP TEST")
    
    try:
        # Only test if we're not in a running server context
        if not os.getenv('RAILWAY_STATIC_URL'):
            print("⚠️ Not in Railway deployment context - skipping server startup test")
        else:
            print("🚀 Starting server test...")
            
            # Import the configured app
            from main import app
            
            # Test server startup with hypercorn
            import hypercorn.config
            import hypercorn.asyncio
            
            config = hypercorn.config.Config()
            config.bind = [f"0.0.0.0:{port}"]
            config.workers = 1
            config.worker_class = "asyncio"
            
            # Test config creation
            log_result("Server config creation", True)
            
            # Test server creation (don't actually start)
            server = hypercorn.asyncio.serve(app, config, shutdown_trigger=lambda: True)
            log_result("Server creation", True)
            
    except Exception as e:
        log_result("Server startup test", False, str(e))
        traceback.print_exc()
    
    # 10. Summary
    log_section("DIAGNOSTIC SUMMARY")
    
    print(f"✅ Diagnostic completed at {datetime.now()}")
    print("📋 Key findings:")
    print(f"   • Environment: {'✅ OK' if env_ok else '❌ MISSING VARS'}")
    print(f"   • Python: ✅ {sys.version_info.major}.{sys.version_info.minor}")
    print(f"   • Port: {port}")
    print(f"   • Railway: {'✅ DETECTED' if os.getenv('RAILWAY_ENVIRONMENT') else '❌ NOT DETECTED'}")
    
    # If we get here, try to start the actual server
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        print("\n🚀 STARTING PRODUCTION SERVER...")
        
        # Start the actual server
        import hypercorn.asyncio
        import hypercorn.config
        from main import app
        
        config = hypercorn.config.Config()
        config.bind = [f"0.0.0.0:{port}"]
        config.workers = 1
        config.worker_class = "asyncio"
        config.access_log_format = "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\""
        config.accesslog = "-"
        config.errorlog = "-"
        
        await hypercorn.asyncio.serve(app, config)
    else:
        print("\n⚠️ Not in production environment - diagnostic only")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        traceback.print_exc()
        sys.exit(1) 