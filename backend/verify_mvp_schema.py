#!/usr/bin/env python3
"""
MVP Schema Verification Script
Verifies that the new database schema is correctly defined for MVP features.
"""

import os
import sys
import logging
import re

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_tables_from_schema():
    """Extract table definitions from the database service"""
    try:
        # Import database service to get schema
        from services.database import PostgreSQLService
        
        # Get the init_database method source
        import inspect
        source = inspect.getsource(PostgreSQLService.init_database)
        
        # Extract CREATE TABLE statements
        table_pattern = r'CREATE TABLE IF NOT EXISTS (\w+) \('
        tables = re.findall(table_pattern, source)
        
        return tables
    except Exception as e:
        logger.error(f"Failed to extract schema: {e}")
        return []

def verify_mvp_features():
    """Verify that all MVP features are supported by the schema"""
    
    logger.info("🔍 Verifying MVP Schema Completeness...")
    
    # Expected tables for MVP
    expected_tables = {
        'users': 'User authentication and profiles',
        'documents': 'Core document storage and management', 
        'folders': 'Document organization',
        'refresh_tokens': 'JWT authentication tokens',
        'login_logs': 'Security and authentication logging',
        'user_preferences': 'User settings and corrections',
        'user_feedback': 'AI learning from user feedback'
    }
    
    # Tables that should NOT exist in MVP
    removed_tables = {
        'document_versions': 'Version control (too complex for MVP)',
        'series': 'Multi-document series (not used)',
        'user_sessions': 'Session management (replaced with JWT)'
    }
    
    # Extract actual tables from schema
    actual_tables = extract_tables_from_schema()
    
    logger.info(f"📋 Found {len(actual_tables)} tables in schema")
    
    # Check expected tables
    missing_tables = []
    for table, purpose in expected_tables.items():
        if table in actual_tables:
            logger.info(f"✅ {table} - {purpose}")
        else:
            logger.error(f"❌ Missing: {table} - {purpose}")
            missing_tables.append(table)
    
    # Check removed tables
    logger.info("\n🗑️ Verifying removed tables:")
    for table, reason in removed_tables.items():
        if table not in actual_tables:
            logger.info(f"✅ Removed: {table} - {reason}")
        else:
            logger.warning(f"⚠️ Still exists: {table} - {reason}")
    
    return len(missing_tables) == 0

def verify_core_endpoints():
    """Verify that main.py endpoints match the new schema"""
    
    logger.info("\n🌐 Verifying API endpoints match schema...")
    
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        # Check for key MVP endpoints and router inclusions
        mvp_checks = [
            ('/api/auth/register', 'User registration endpoint'),
            ('/api/auth/login', 'User login endpoint'), 
            ('/api/documents', 'Document management endpoints'),
            ('/api/folders', 'Folder organization endpoints'),
            ('chat_router', 'AI chat router inclusion'),
            ('grammar_router', 'Grammar checking router inclusion')
        ]
        
        found_endpoints = []
        for endpoint, description in mvp_checks:
            if endpoint in main_content:
                logger.info(f"✅ Found: {description}")
                found_endpoints.append(endpoint)
            else:
                logger.error(f"❌ Missing: {description}")
        
        return len(found_endpoints) == len(mvp_checks)
        
    except Exception as e:
        logger.error(f"Failed to verify endpoints: {e}")
        return False

def main():
    """Main verification function"""
    logger.info("🚀 Starting MVP Schema Verification...")
    
    schema_ok = verify_mvp_features()
    endpoints_ok = verify_core_endpoints()
    
    if schema_ok and endpoints_ok:
        logger.info("\n✅ MVP Schema Verification PASSED!")
        logger.info("🎯 Database schema is optimized for MVP")
        logger.info("🔧 When deployed to Railway, the new schema will be automatically applied")
        return True
    else:
        logger.error("\n❌ MVP Schema Verification FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 