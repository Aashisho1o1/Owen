"""
PostgreSQL Database Service for DOG Writer
Modern, production-ready database service with connection pooling,
security, and Railway optimizations.
Simple but flexible schema for prototype development.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from psycopg2 import OperationalError

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
        self._retry_count = 3
        self._retry_delay = 1  # seconds
        self._connection_timeout = 10  # seconds
        
        if not self.database_url:
            logger.error("DATABASE_URL environment variable is not set")
            logger.info("Database service created but not connected - set DATABASE_URL to connect")
            return
        
        try:
            # Initialize connection pool with retry
            self._init_connection_pool_with_retry()
            
            # Initialize database schema
            self.init_database()
            
            logger.info("PostgreSQL service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            self.pool = None
    
    def _init_connection_pool_with_retry(self):
        """Initialize connection pool with retry logic"""
        for attempt in range(self._retry_count):
            try:
                self._init_connection_pool()
                return  # Success
            except Exception as e:
                if attempt < self._retry_count - 1:
                    logger.warning(f"Connection pool init attempt {attempt + 1} failed: {e}")
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise
    
    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool with enhanced settings"""
        try:
            # Close existing pool if any
            if self.pool:
                try:
                    self.pool.closeall()
                except:
                    pass
            
            self.pool = ThreadedConnectionPool(
                minconn=2,  # Increased minimum connections
                maxconn=30,  # Increased maximum connections
                dsn=self.database_url,
                cursor_factory=RealDictCursor,
                connect_timeout=self._connection_timeout,
                # Additional connection parameters for reliability
                options='-c statement_timeout=30000',  # 30 second statement timeout
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            
            # Test the pool
            conn = self.pool.getconn()
            conn.close()
            self.pool.putconn(conn)
            
            logger.info("Connection pool initialized with enhanced settings")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise DatabaseError(f"Connection pool initialization failed: {e}")
    
    def _ensure_pool_health(self):
        """Ensure connection pool is healthy, recreate if needed"""
        if not self.pool:
            logger.warning("Connection pool not initialized, attempting to create...")
            self._init_connection_pool_with_retry()
            return
        
        try:
            # Test pool health
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"Connection pool health check failed: {e}")
            logger.info("Recreating connection pool...")
            self._init_connection_pool_with_retry()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with health checks and retry logic"""
        conn = None
        attempt = 0
        
        while attempt < self._retry_count:
            try:
                # Ensure pool is healthy
                self._ensure_pool_health()
                
                # Get connection from pool
                conn = self.pool.getconn()
                
                # Test connection health
                if conn.closed:
                    logger.warning("Got closed connection from pool, getting new one...")
                    self.pool.putconn(conn, close=True)
                    conn = self.pool.getconn()
                
                # Set connection properties for reliability
                conn.set_session(autocommit=False, readonly=False)
                conn.set_client_encoding('UTF8')
                
                yield conn
                conn.commit()
                break  # Success, exit retry loop
                
            except OperationalError as e:
                attempt += 1
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                
                logger.error(f"Database operational error (attempt {attempt}/{self._retry_count}): {e}")
                
                if attempt < self._retry_count:
                    time.sleep(self._retry_delay * attempt)
                    # Try to refresh the connection
                    if conn:
                        self.pool.putconn(conn, close=True)
                        conn = None
                else:
                    raise DatabaseError(f"Database operation failed after {self._retry_count} attempts: {e}")
                    
            except Exception as e:
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                logger.error(f"Database error: {e}")
                raise DatabaseError(f"Database operation failed: {e}")
                
            finally:
                if conn and attempt == self._retry_count - 1:  # Last attempt
                    try:
                        self.pool.putconn(conn)
                    except:
                        pass
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None) -> Union[List[Dict], Dict, int, None]:
        """Execute database query with enhanced error handling and retry logic"""
        # SECURITY: Validate that query uses parameterized queries only
        if '%s' not in query and params:
            raise DatabaseError("Query parameters provided but query doesn't use parameterized placeholders")
        
        # SECURITY: Basic SQL injection pattern detection
        dangerous_patterns = [
            r';\s*DROP\s+TABLE', r';\s*DELETE\s+FROM', r';\s*INSERT\s+INTO',
            r'UNION\s+SELECT', r'OR\s+1\s*=\s*1', r'AND\s+1\s*=\s*1',
            r';\s*--', r'/\*.*\*/', r'EXEC\s*\(', r'SP_EXECUTESQL'
        ]
        
        import re
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper):
                logger.error(f"SECURITY: Potentially dangerous SQL pattern detected: {pattern}")
                raise DatabaseError("Query contains potentially dangerous SQL patterns")
        
        # Add query timeout for long-running queries
        if "SELECT" in query.upper() and "COUNT" not in query.upper():
            query = f"SET LOCAL statement_timeout = '10s'; {query}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
                
                if fetch == 'one':
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch == 'all':
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    return cursor.rowcount
            finally:
                cursor.close()
    
    def init_database(self):
        """Initialize clean MVP database schema with fiction-specific enhancements"""
        
        # CLEAN SLATE MVP SCHEMA - Enhanced for fiction writers
        schema_queries = [
            # 1. USERS TABLE - Essential authentication only
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
                last_login TIMESTAMPTZ,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMPTZ
            )
            ''',
            
            # 2. DOCUMENTS TABLE - Enhanced for fiction writing
            '''
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(36) PRIMARY KEY,  -- UUID as string for simplicity
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(500) NOT NULL,
                content TEXT DEFAULT '',
                document_type VARCHAR(50) DEFAULT 'novel',  -- Fiction-specific types
                folder_id VARCHAR(36) REFERENCES folders(id) ON DELETE SET NULL,
                status VARCHAR(20) DEFAULT 'draft',
                word_count INTEGER DEFAULT 0,
                word_count_target INTEGER,  -- Target word count for goals
                tags JSONB DEFAULT '[]'::jsonb,  -- Tags for organization
                series_name VARCHAR(100),  -- Series this document belongs to
                chapter_number INTEGER,  -- Chapter number if applicable
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # 3. FOLDERS TABLE - Enhanced with types and descriptions
            '''
            CREATE TABLE IF NOT EXISTS folders (
                id VARCHAR(36) PRIMARY KEY,  -- UUID as string
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                folder_type VARCHAR(50) DEFAULT 'general',  -- project, series, characters, etc.
                parent_id VARCHAR(36) REFERENCES folders(id) ON DELETE CASCADE,
                color VARCHAR(7) DEFAULT '#3B82F6',
                description TEXT,  -- Folder description
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # 4. REFRESH TOKENS - JWT authentication
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
            
            # 5. LOGIN LOGS - Basic security tracking
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
            
            # 6. USER PREFERENCES - Minimal MVP preferences
            '''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                user_corrections TEXT[] DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
            ''',
            
            # 7. USER FEEDBACK - Essential for AI learning
            '''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id VARCHAR(255) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                original_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                user_feedback TEXT NOT NULL,
                correction_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            '''
        ]
        
        # Essential performance indexes only
        index_queries = [
            # User indexes
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
            
            # Document indexes - Enhanced for fiction
            'CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_folder_id ON documents(folder_id)',
            'CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents(updated_at)',
            'CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type)',
            'CREATE INDEX IF NOT EXISTS idx_documents_series_name ON documents(series_name)',
            'CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)',
            'CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents USING GIN(tags)',  # JSONB index for tags
            
            # Folder indexes
            'CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON folders(parent_id)',
            'CREATE INDEX IF NOT EXISTS idx_folders_folder_type ON folders(folder_type)',
            
            # Auth indexes
            'CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at)',
            'CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs(user_id)',
            
            # Preference indexes
            'CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id)'
        ]
        
        # Migration queries to add new columns to existing documents table
        migration_queries = [
            'ALTER TABLE documents ADD COLUMN IF NOT EXISTS document_type VARCHAR(50) DEFAULT \'novel\'',
            'ALTER TABLE documents ADD COLUMN IF NOT EXISTS word_count_target INTEGER',
            'ALTER TABLE documents ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT \'[]\'::jsonb',
            'ALTER TABLE documents ADD COLUMN IF NOT EXISTS series_name VARCHAR(100)',
            'ALTER TABLE documents ADD COLUMN IF NOT EXISTS chapter_number INTEGER',
            'ALTER TABLE folders ADD COLUMN IF NOT EXISTS folder_type VARCHAR(50) DEFAULT \'general\'',
            'ALTER TABLE folders ADD COLUMN IF NOT EXISTS description TEXT'
        ]
        
        # DROP old tables that are no longer needed for MVP
        cleanup_queries = [
            'DROP TABLE IF EXISTS document_versions CASCADE',
            'DROP TABLE IF EXISTS series CASCADE', 
            'DROP TABLE IF EXISTS user_sessions CASCADE'
        ]
        
        logger.info("🗄️ Creating enhanced fiction-focused database schema...")
        
        # Execute cleanup first
        for query in cleanup_queries:
            try:
                self.execute_query(query)
                logger.info(f"✅ Cleaned up unused table: {query.split()[4]}")
            except Exception as e:
                logger.warning(f"Cleanup query failed (might not exist): {e}")
        
        # Execute schema creation
        for i, query in enumerate(schema_queries, 1):
            try:
                self.execute_query(query)
                table_name = query.split()[5]  # Extract table name
                logger.info(f"✅ {i}/7 Created table: {table_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create table {i}/7: {e}")
                raise DatabaseError(f"Schema creation failed: {e}")
        
        # Execute migrations for existing tables
        logger.info("🔄 Running fiction-specific migrations...")
        for i, query in enumerate(migration_queries, 1):
            try:
                self.execute_query(query)
                logger.info(f"✅ {i}/{len(migration_queries)} Migration completed")
            except Exception as e:
                logger.warning(f"Migration {i} failed (might already exist): {e}")
        
        # Execute indexes
        for i, query in enumerate(index_queries, 1):
            try:
                self.execute_query(query)
                index_name = query.split()[5]  # Extract index name
                logger.info(f"📊 {i}/{len(index_queries)} Created index: {index_name}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
        
        logger.info("🚀 Fiction-focused database schema initialized successfully!")
        logger.info("📋 Enhanced Tables: users, documents (fiction-enhanced), folders (typed), refresh_tokens, login_logs, user_preferences, user_feedback")
        logger.info("📚 Fiction Features: document_type, word_count_target, tags, series_name, chapter_number, folder_type")
        logger.info("🗑️ Removed: document_versions, series, user_sessions (not needed for MVP)")
    
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
            folder_count = self.execute_query("SELECT COUNT(*) as count FROM folders", fetch='one')
            
            return {
                "status": "healthy",
                "database_version": result['version'] if result else "unknown",
                "total_users": user_count['count'] if user_count else 0,
                "total_documents": doc_count['count'] if doc_count else 0,
                "total_folders": folder_count['count'] if folder_count else 0,
                "schema": "MVP_v3.0",
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
        if self.pool:
            try:
                self.pool.closeall()
                logger.info("Database connections closed")
            except Exception as e:
                logger.error(f"Error closing connections: {e}")

    # === USER PREFERENCES METHODS (Essential for MVP) ===
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get simplified user preferences from database"""
        try:
            result = self.execute_query(
                """SELECT user_corrections 
                   FROM user_preferences WHERE user_id = %s""",
                (user_id,),
                fetch='one'
            )
            
            if not result:
                return None
                
            return {
                "user_corrections": result.get('user_corrections', [])
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    def create_default_preferences(self, user_id: int) -> Dict[str, Any]:
        """Create minimal default preferences for new user"""
        try:
            default_prefs = {
                "user_corrections": []
            }
            
            # Insert default preferences
            self.execute_query(
                """INSERT INTO user_preferences 
                   (user_id, user_corrections, created_at, updated_at)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (user_id) DO NOTHING""",
                (user_id, "[]", datetime.utcnow(), datetime.utcnow())
            )
            
            return default_prefs
        except Exception as e:
            logger.error(f"Error creating default preferences: {e}")
            return {}
    
    def add_user_feedback(self, user_id: int, original_message: str, ai_response: str, 
                         user_feedback: str, correction_type: str) -> bool:
        """Add user feedback for AI responses"""
        try:
            feedback_id = f"feedback_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            self.execute_query(
                """INSERT INTO user_feedback 
                   (id, user_id, original_message, ai_response, user_feedback, 
                    correction_type, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (feedback_id, user_id, original_message, ai_response, user_feedback, 
                 correction_type, datetime.utcnow())
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user feedback: {e}")
            return False

# Global database service instance
db_service = PostgreSQLService() 