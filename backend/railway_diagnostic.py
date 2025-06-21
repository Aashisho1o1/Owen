#!/usr/bin/env python3
"""
Railway Database Connection Diagnostic Tool
Helps identify the exact issue with DATABASE_URL and connection setup
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import traceback

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def diagnose_environment():
    """Check environment variables"""
    print_section("ENVIRONMENT VARIABLES CHECK")
    
    # Check critical env vars
    env_vars = ['DATABASE_URL', 'JWT_SECRET_KEY', 'GEMINI_API_KEY', 'OPENAI_API_KEY']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'DATABASE_URL':
                # Parse and display URL structure without revealing credentials
                try:
                    parsed = urlparse(value)
                    print(f"✅ {var}: SET")
                    print(f"   Scheme: {parsed.scheme}")
                    print(f"   Host: {parsed.hostname}")
                    print(f"   Port: {parsed.port}")
                    print(f"   Database: {parsed.path[1:] if parsed.path else 'None'}")
                    print(f"   Username: {parsed.username}")
                    print(f"   Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
                    
                    # Check if using internal Railway URL
                    if parsed.hostname and parsed.hostname.endswith('postgres.railway.internal'):
                        print(f"   ✅ Using Railway internal URL (CORRECT)")
                    elif parsed.hostname and (parsed.hostname == 'viaduct.proxy.rlwy.net' or parsed.hostname.endswith('.viaduct.proxy.rlwy.net')):
                        print(f"   ⚠️  Using external proxy URL (MIGHT CAUSE ISSUES)")
                        print(f"   💡 TIP: Try using postgres.railway.internal:5432 instead")
                    else:
                        print(f"   ❓ Unknown host format")
                        
                except Exception as e:
                    print(f"❌ {var}: INVALID FORMAT - {e}")
            else:
                print(f"✅ {var}: SET ({len(value)} chars)")
        else:
            print(f"❌ {var}: NOT SET")

def test_database_connection():
    """Test direct database connection"""
    print_section("DATABASE CONNECTION TEST")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set - cannot test connection")
        return False
    
    try:
        print("🔄 Testing direct psycopg2 connection...")
        
        # Try to connect
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            connect_timeout=10  # 10 second timeout
        )
        
        print("✅ Database connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user;")
        result = cursor.fetchone()
        
        print(f"✅ Database info:")
        print(f"   Version: {result['version']}")
        print(f"   Database: {result['current_database']}")
        print(f"   User: {result['current_user']}")
        
        # Test table creation (to check permissions)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection_check (
                    id SERIAL PRIMARY KEY,
                    test_message TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Table creation permissions: OK")
            
            # Test insert
            cursor.execute("""
                INSERT INTO test_connection_check (test_message) 
                VALUES ('Railway diagnostic test')
                RETURNING id
            """)
            test_id = cursor.fetchone()['id']
            print(f"✅ Insert permissions: OK (test record id: {test_id})")
            
            # Clean up
            cursor.execute("DROP TABLE test_connection_check")
            print("✅ Drop permissions: OK")
            
        except Exception as e:
            print(f"⚠️  Database permissions issue: {e}")
        
        conn.commit()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed (OperationalError): {e}")
        
        # Specific Railway diagnostics
        if "could not connect to server" in str(e):
            print("💡 LIKELY CAUSES:")
            print("   1. Database service not running")
            print("   2. Wrong host (should be postgres.railway.internal)")
            print("   3. Wrong port (should be 5432)")
            print("   4. Network connectivity issues")
        elif "authentication failed" in str(e):
            print("💡 LIKELY CAUSES:")
            print("   1. Wrong username/password")
            print("   2. Database user doesn't exist")
        elif "does not exist" in str(e):
            print("💡 LIKELY CAUSES:")
            print("   1. Database name is wrong")
            print("   2. Database hasn't been created yet")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_connection_pool():
    """Test connection pooling like the app does"""
    print_section("CONNECTION POOL TEST")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set - cannot test pool")
        return False
    
    try:
        from psycopg2.pool import ThreadedConnectionPool
        
        print("🔄 Testing ThreadedConnectionPool initialization...")
        
        pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=5,  # Smaller pool for testing
            dsn=database_url,
            cursor_factory=RealDictCursor
        )
        
        print("✅ Connection pool created successfully!")
        
        # Test getting connection from pool
        conn = pool.getconn()
        print("✅ Got connection from pool")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✅ Pool query successful: {result['test']}")
        
        # Return connection to pool
        pool.putconn(conn)
        print("✅ Returned connection to pool")
        
        # Close pool
        pool.closeall()
        print("✅ Connection pool closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection pool test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run complete diagnostic"""
    print("🔍 Railway Database Connection Diagnostics")
    print("=" * 60)
    
    # Run all diagnostics
    env_ok = True
    diagnose_environment()
    
    db_ok = test_database_connection()
    pool_ok = test_connection_pool()
    
    # Summary
    print_section("DIAGNOSTIC SUMMARY")
    
    if db_ok and pool_ok:
        print("✅ ALL TESTS PASSED!")
        print("✅ Database connection is working correctly")
        print("💡 The issue might be in FastAPI app startup or other code")
    else:
        print("❌ TESTS FAILED!")
        print("💡 Fix the database connection issues above")
        
        if not db_ok:
            print("\n🔧 NEXT STEPS:")
            print("1. Check Railway PostgreSQL service is running")
            print("2. Verify DATABASE_URL uses 'postgres.railway.internal:5432'")
            print("3. Ensure DATABASE_URL has correct credentials")
            print("4. Check if PostgreSQL service has been provisioned")

if __name__ == "__main__":
    main() 