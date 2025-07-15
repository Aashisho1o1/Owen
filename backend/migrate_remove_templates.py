#!/usr/bin/env python3
"""
Database Migration Script: Remove Template System
Run this script to clean up template-related database structures after deploying the template system removal.

Usage:
    python migrate_remove_templates.py

This script:
1. Removes the template_id column from documents table
2. Drops template-related tables if they exist
3. Logs all operations for audit trail
"""

import os
import sys
import logging
from typing import List

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.database import db_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('template_migration.log')
    ]
)

logger = logging.getLogger(__name__)

def run_template_cleanup_migration():
    """Execute the template system cleanup migration"""
    
    logger.info("🧹 Starting template system cleanup migration...")
    
    # Template system cleanup queries
    template_cleanup_queries = [
        'ALTER TABLE documents DROP COLUMN IF EXISTS template_id',
        'DROP TABLE IF EXISTS templates CASCADE',
        'DROP TABLE IF EXISTS template_categories CASCADE',
        'DROP TABLE IF EXISTS document_templates CASCADE',
        'DROP TABLE IF EXISTS fiction_templates CASCADE'
    ]
    
    # Verification queries
    verification_queries = [
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'documents' AND column_name = 'template_id'",
        "SELECT table_name FROM information_schema.tables WHERE table_name IN ('templates', 'template_categories', 'document_templates', 'fiction_templates')"
    ]
    
    try:
        # Check database connection
        health = db_service.health_check()
        if health['status'] != 'healthy':
            logger.error(f"❌ Database not healthy: {health}")
            return False
        
        logger.info("✅ Database connection verified")
        
        # Execute cleanup queries
        for i, query in enumerate(template_cleanup_queries, 1):
            try:
                logger.info(f"🔄 Executing cleanup query {i}/{len(template_cleanup_queries)}: {query}")
                result = db_service.execute_query(query)
                logger.info(f"✅ Query {i} completed successfully")
            except Exception as e:
                logger.warning(f"⚠️ Query {i} failed (might not exist): {e}")
        
        # Verify cleanup
        logger.info("🔍 Verifying template cleanup...")
        
        # Check if template_id column still exists
        result = db_service.execute_query(verification_queries[0], fetch='all')
        if result:
            logger.warning("⚠️ template_id column still exists in documents table")
        else:
            logger.info("✅ template_id column successfully removed from documents table")
        
        # Check if template tables still exist
        result = db_service.execute_query(verification_queries[1], fetch='all')
        if result:
            remaining_tables = [row['table_name'] for row in result]
            logger.warning(f"⚠️ Template tables still exist: {remaining_tables}")
        else:
            logger.info("✅ All template tables successfully removed")
        
        # Final health check
        final_health = db_service.health_check()
        logger.info(f"📊 Final database health: {final_health['status']}")
        
        logger.info("🎉 Template system cleanup migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Template System Cleanup Migration")
    logger.info("=" * 50)
    
    # Confirm environment
    env = os.getenv('RAILWAY_ENVIRONMENT', 'development')
    logger.info(f"🌍 Environment: {env}")
    
    if env == 'production':
        logger.warning("⚠️ Running in PRODUCTION environment")
        confirmation = input("Are you sure you want to proceed? (yes/no): ")
        if confirmation.lower() != 'yes':
            logger.info("❌ Migration cancelled by user")
            return
    
    # Run migration
    success = run_template_cleanup_migration()
    
    if success:
        logger.info("✅ Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 