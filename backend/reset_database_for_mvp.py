#!/usr/bin/env python3
"""
Database Reset Script for MVP
Completely recreates the database with clean, efficient MVP schema.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Reset database to clean MVP schema"""
    logger.info("🚀 Starting MVP Database Reset...")
    
    # Load environment variables from the backend directory
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    logger.info(f"📁 Loading .env from: {env_path}")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        logger.info("Please set DATABASE_URL in your .env file")
        return False
    
    logger.info(f"🔗 Using database: {database_url[:20]}...{database_url[-10:]}")
    
    try:
        # Import and initialize database service after environment is loaded
        from services.database import PostgreSQLService
        
        # Create a fresh database service instance
        db_service = PostgreSQLService()
        
        # Check initial connection
        logger.info("🔗 Testing database connection...")
        if not db_service.pool:
            logger.error("❌ Failed to connect to database")
            return False
        
        logger.info("✅ Database connection successful!")
        
        # Force reinitialize the schema
        logger.info("🗄️ Initializing clean MVP schema...")
        db_service.init_database()
        
        # Verify the new schema
        logger.info("🔍 Verifying new schema...")
        health = db_service.health_check()
        
        if health["status"] == "healthy":
            logger.info("✅ Database reset completed successfully!")
            logger.info(f"📊 Schema: {health.get('schema', 'Unknown')}")
            logger.info(f"👥 Users: {health.get('total_users', 0)}")
            logger.info(f"📄 Documents: {health.get('total_documents', 0)}")
            logger.info(f"📁 Folders: {health.get('total_folders', 0)}")
            logger.info(f"🐘 PostgreSQL Version: {health.get('database_version', 'Unknown')[:50]}...")
            return True
        else:
            logger.error(f"❌ Database health check failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        # Close database connections
        try:
            db_service.close()
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 