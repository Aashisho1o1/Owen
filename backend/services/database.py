"""
PostgreSQL Database Service for DOG Writer
Modern, production-ready database service with connection pooling,
security, and Railway optimizations.
Simple but flexible schema for prototype development.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class PostgreSQLService:
    """
    Production-ready PostgreSQL service for Railway deployment.
    Features connection pooling, automatic reconnection, and security.
    Simple but flexible schema for prototype development.
    """
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
        
        if not self.database_url:
            logger.error("DATABASE_URL environment variable is not set")
            logger.info("Database service created but not connected - set DATABASE_URL to connect")
            return
        
        try:
            # Initialize connection pool
            self._init_connection_pool()
            
            # Initialize database schema
            self.init_database()
            
            logger.info("PostgreSQL service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            self.pool = None
    
    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool for better performance"""
        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                dsn=self.database_url,
                cursor_factory=RealDictCursor
            )
            logger.info("Connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise DatabaseError(f"Connection pool initialization failed: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool with automatic cleanup"""
        conn = None
        try:
            conn = self.pool.getconn()
            if conn.closed:
                # Connection is closed, get a new one
                self.pool.putconn(conn, close=True)
                conn = self.pool.getconn()
            
            yield conn
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None) -> Union[List[Dict], Dict, int, None]:
        """Execute database query with proper error handling"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch == 'one':
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == 'all':
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return cursor.rowcount
    
    def init_database(self):
        """Initialize essential database schema - simple but flexible for future expansion"""
        
        schema_queries = [
            # Users table - Core authentication
            '''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMPTZ,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMPTZ,
                preferences JSONB DEFAULT '{}'
            )
            ''',
            
            # Documents table - Core document management (flexible for future features)
            '''
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(500) NOT NULL,
                content TEXT,
                document_type VARCHAR(50) DEFAULT 'novel',
                folder_id UUID REFERENCES folders(id) ON DELETE SET NULL,
                series_id UUID REFERENCES series(id) ON DELETE SET NULL,
                status VARCHAR(20) DEFAULT 'draft',
                tags JSONB DEFAULT '[]',
                is_favorite BOOLEAN DEFAULT FALSE,
                word_count INTEGER DEFAULT 0,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # Document versions for change tracking
            '''
            CREATE TABLE IF NOT EXISTS document_versions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                version_number INTEGER NOT NULL,
                title VARCHAR(500) NOT NULL,
                content TEXT,
                word_count INTEGER DEFAULT 0,
                change_summary TEXT,
                is_auto_save BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # Folders for organization
            '''
            CREATE TABLE IF NOT EXISTS folders (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                parent_id UUID REFERENCES folders(id) ON DELETE CASCADE,
                color VARCHAR(7),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # Series for multi-document projects
            '''
            CREATE TABLE IF NOT EXISTS series (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                total_chapters INTEGER DEFAULT 0,
                total_words INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # Refresh tokens for JWT management
            '''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash VARCHAR(255) NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                revoked BOOLEAN DEFAULT FALSE,
                device_info TEXT,
                ip_address INET
            )
            ''',
            
            # Login logs for security
            '''
            CREATE TABLE IF NOT EXISTS login_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                email VARCHAR(255) NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address INET,
                attempted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                failure_reason TEXT
            )
            ''',
            
            # User sessions
            '''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMPTZ NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                ip_address INET,
                last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            '''
        ]
        
        # Essential performance indexes
        index_queries = [
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
            'CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_folder_id ON documents(folder_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_series_id ON documents(series_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents(updated_at)',
            'CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id)',
            'CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_series_user_id ON series(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at)',
            'CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)'
        ]
        
        # Execute all schema creation
        for query in schema_queries:
            try:
                self.execute_query(query)
            except Exception as e:
                logger.error(f"Failed to execute schema query: {e}")
                # Continue with other queries
        
        # Execute all indexes
        for query in index_queries:
            try:
                self.execute_query(query)
            except Exception as e:
                logger.error(f"Failed to create index: {e}")
                # Continue with other indexes
        
        logger.info("Essential PostgreSQL schema initialized successfully")
    
    def health_check(self) -> Dict[str, Any]:
        """Check database connectivity and status"""
        if not self.database_url:
            return {
                "status": "unhealthy",
                "error": "DATABASE_URL not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        if not self.pool:
            return {
                "status": "unhealthy",
                "error": "Database connection pool not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            result = self.execute_query("SELECT version()", fetch='one')
            user_count = self.execute_query("SELECT COUNT(*) as count FROM users", fetch='one')
            doc_count = self.execute_query("SELECT COUNT(*) as count FROM documents", fetch='one')
            
            return {
                "status": "healthy",
                "database_version": result['version'] if result else "unknown",
                "total_users": user_count['count'] if user_count else 0,
                "total_documents": doc_count['count'] if doc_count else 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def close(self):
        """Close all database connections"""
        if hasattr(self, 'pool') and self.pool:
            try:
                self.pool.closeall()
                logger.info("Database connections closed")
            except Exception as e:
                logger.error(f"Error closing database connections: {e}")

# Global database service instance
db_service = PostgreSQLService() 