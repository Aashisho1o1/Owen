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
        """Initialize PostgreSQL service with lazy connection pool"""
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            logger.error("DATABASE_URL environment variable not set")
            raise DatabaseError("DATABASE_URL environment variable is required")
        
        # Parse database URL for logging (without exposing credentials)
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            logger.info(f"Database configured: {parsed.hostname}:{parsed.port}/{parsed.path[1:]}")
        except Exception as e:
            logger.warning(f"Could not parse database URL for logging: {e}")
        
        # Connection pool settings
        self.pool = None  # Lazy initialization
        self._connection_timeout = 30  # seconds
        self._retry_count = 3
        self._retry_delay = 2  # Increased retry delay
        
        # Don't initialize connection pool here - do it lazily when first needed
        logger.info("PostgreSQL service initialized (connection pool will be created lazily)")
    

    
    def _init_connection_pool(self):
        """Initialize or re-initialize the connection pool."""
        # Safely close any existing pool before creating a new one
        if self.pool and not self.pool.closed:
            logger.warning("Existing connection pool found. Closing before re-initializing.")
            self.pool.closeall()

        try:
            # Optimized for Railway's hobby tier:
            # - minconn=1: Keep one connection warm to reduce latency.
            # - maxconn=5: A small pool to prevent overwhelming the DB's connection limit.
            logger.info("Initializing connection pool (min=1, max=5)...")
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=self.database_url,
                cursor_factory=RealDictCursor
            )
            # Test the connection to ensure the pool is valid
            conn = self.pool.getconn()
            conn.close() # Close immediately, just a health check
            logger.info("✅ Connection pool initialized and tested successfully.")
        except OperationalError as e:
            logger.critical(f"CRITICAL: Could not connect to database at {self.database_url}. Error: {e}")
            self.pool = None
            raise DatabaseError(f"Failed to initialize database connection pool: {e}")
    
    def _close_pool_safely(self):
        """Safely close the connection pool to prevent resource leaks"""
        if self.pool:
            try:
                logger.info("Closing existing connection pool...")
                self.pool.closeall()
                self.pool = None
                logger.info("Connection pool closed successfully")
            except Exception as e:
                logger.warning(f"Error closing connection pool: {e}")
                self.pool = None  # Force reset even if close failed
    
    def _ensure_pool_health(self):
        """Ensure connection pool is healthy, recreate if needed"""
        logger.info('Checking pool health')
        if not self.pool:
            logger.info("Connection pool not initialized, creating now...")
            self._init_connection_pool()
            return
        
        conn = None
        try:
            conn = self.pool.getconn()
            if conn:
                # RAILWAY FIX: Check if connection is closed before using it
                if hasattr(conn, 'closed') and conn.closed:
                    logger.warning("Got closed connection from pool during health check")
                    self.pool.putconn(conn, close=True)
                    conn = None
                    raise DatabaseError("Connection was closed")
                
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                
                # RAILWAY FIX: Only return to pool if connection is still valid
                if hasattr(conn, 'closed') and not conn.closed:
                    self.pool.putconn(conn)
                else:
                    self.pool.putconn(conn, close=True)
                conn = None
            else:
                raise DatabaseError("Failed to get connection from pool")
        except Exception as e:
            if conn:
                try:
                    # RAILWAY FIX: Always close invalid connections instead of returning to pool
                    if hasattr(conn, 'closed') and conn.closed:
                        self.pool.putconn(conn, close=True)
                    else:
                        self.pool.putconn(conn)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up connection during health check: {cleanup_error}")
            logger.error(f"Connection pool health check failed: {e}")
            logger.info("Recreating connection pool...")
            # RAILWAY FIX: Properly close old pool before creating new one
            self._close_pool_safely()
            self._init_connection_pool()
    
    @contextmanager
    def get_connection(self):
        """
        Provides a database connection from the pool.
        This is the most critical method for preventing connection leaks.
        It uses a context manager to GUARANTEE that the connection is
        returned to the pool, even if errors occur.
        """
        if self.pool is None:
            logger.info("Connection pool does not exist. Initializing now.")
            self._init_connection_pool()
        
        if self.pool is None:
            raise DatabaseError("Database connection pool is unavailable.")

        conn = None
        try:
            # Get a connection from the pool
            conn = self.pool.getconn()
            yield conn # Hand over control to the calling method
            conn.commit()
        except OperationalError as e:
            logger.error(f"Database OperationalError: {e}. Rolling back transaction.")
            if conn:
                conn.rollback()
            # This could be a transient network issue. We'll let the caller retry.
            raise DatabaseError(f"A database network error occurred: {e}")
        except Exception as e:
            logger.error(f"An unexpected database error occurred: {e}. Rolling back.")
            if conn:
                conn.rollback()
            # Re-raise the exception to be handled by the caller
            raise DatabaseError(f"An unexpected database error occurred: {e}")
        finally:
            # THIS BLOCK IS GUARANTEED TO RUN.
            # It ensures the connection is always returned to the pool.
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None) -> Union[List[Dict], Dict, int, None]:
        """Execute database query with enhanced error handling and retry logic"""
        print(f"💾 DB STEP 1: Executing query: {query[:100]}...")
        print(f"💾 DB STEP 1a: Query params: {params}")
        
        # SECURITY: Validate that query uses parameterized queries only
        if '%s' not in query and params:
            print(f"💾 DB ❌ SECURITY ERROR: Query parameters provided but query doesn't use parameterized placeholders")
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
                print(f"💾 DB ❌ SECURITY ERROR: Potentially dangerous SQL pattern detected: {pattern}")
                logger.error(f"SECURITY: Potentially dangerous SQL pattern detected: {pattern}")
                raise DatabaseError("Query contains potentially dangerous SQL patterns")
        
        print(f"💾 DB STEP 2: Security checks passed")
        
        # Add query timeout for long-running queries
        if "SELECT" in query.upper() and "COUNT" not in query.upper():
            query = f"SET LOCAL statement_timeout = '10s'; {query}"
        
        print(f"💾 DB STEP 3: Getting database connection...")
        
        with self.get_connection() as conn:
            print(f"💾 DB STEP 3: ✅ Connection obtained")
            print(f"💾 DB STEP 4: Creating cursor...")
            cursor = conn.cursor()
            print(f"💾 DB STEP 4: ✅ Cursor created")
            
            print(f"💾 DB STEP 5: Executing query...")
            cursor.execute(query, params)
            print(f"💾 DB STEP 5: ✅ Query executed")
            
            print(f"💾 DB STEP 6: Processing results (fetch={fetch})...")
            if fetch == 'one':
                result = cursor.fetchone()
                final_result = dict(result) if result else None
                print(f"💾 DB STEP 6: ✅ Fetched one result: {bool(final_result)}")
                return final_result
            elif fetch == 'all':
                results = cursor.fetchall()
                final_results = [dict(row) for row in results] if results else []
                print(f"💾 DB STEP 6: ✅ Fetched all results: {len(final_results)} rows")
                return final_results
            elif fetch == 'none':
                row_count = cursor.rowcount
                print(f"💾 DB STEP 6: ✅ Query executed, affected rows: {row_count}")
                return row_count
            else:
                row_count = cursor.rowcount
                print(f"💾 DB STEP 6: ✅ Query executed, affected rows: {row_count}")
                return row_count
    

    
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
            ''',
            
            # 8. CHARACTER VOICE PROFILES - For voice consistency detection with Gemini
            '''
            CREATE TABLE IF NOT EXISTS character_voice_profiles (
                character_id VARCHAR(64) PRIMARY KEY,  -- MD5 hash of user_id + character_name
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                character_name VARCHAR(100) NOT NULL,
                dialogue_samples JSONB NOT NULL DEFAULT '[]'::jsonb,  -- Array of dialogue samples
                voice_embedding JSONB NOT NULL,  -- Legacy field, now unused (kept for compatibility)
                voice_characteristics JSONB DEFAULT '{}'::jsonb,  -- Character voice metadata
                sample_count INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
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
            'CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id)',
            
            # Character voice profiles indexes
            'CREATE INDEX IF NOT EXISTS idx_character_voice_profiles_user_id ON character_voice_profiles(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_character_voice_profiles_character_name ON character_voice_profiles(character_name)',
            'CREATE INDEX IF NOT EXISTS idx_character_voice_profiles_sample_count ON character_voice_profiles(sample_count)',
            'CREATE INDEX IF NOT EXISTS idx_character_voice_profiles_last_updated ON character_voice_profiles(last_updated)'
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
        
        # Template system cleanup - remove template_id column if it exists
        template_cleanup_queries = [
            'ALTER TABLE documents DROP COLUMN IF EXISTS template_id',
            'DROP TABLE IF EXISTS templates CASCADE',
            'DROP TABLE IF EXISTS template_categories CASCADE'
        ]
        
        # DROP old tables that are no longer needed for MVP
        cleanup_queries = [
            'DROP TABLE IF EXISTS document_versions CASCADE',
            'DROP TABLE IF EXISTS series CASCADE', 
            'DROP TABLE IF EXISTS user_sessions CASCADE'
        ]
        
        logger.info("🗄️ Creating enhanced fiction-focused database schema...")
        
        # Execute template cleanup first
        logger.info("🧹 Cleaning up template system...")
        for query in template_cleanup_queries:
            try:
                self.execute_query(query)
                logger.info(f"✅ Template cleanup: {query}")
            except Exception as e:
                logger.warning(f"Template cleanup query failed (might not exist): {e}")
        
        # Execute general cleanup
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
        
        # Initialize connection pool if not already done
        if not self.pool:
            try:
                logger.info("Connection pool not initialized, initializing for health check...")
                self._init_connection_pool()
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": f"Failed to initialize connection pool: {str(e)}",
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
        """Close connection pool and cleanup resources"""
        if self.pool:
            try:
                logger.info("Closing database connection pool...")
                self.pool.closeall()
                logger.info("✅ Database connection pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")
            finally:
                self.pool = None

    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status for monitoring"""
        if not self.pool:
            return {"status": "not_initialized", "connections": 0}
        
        try:
            # Note: psycopg2 ThreadedConnectionPool doesn't expose detailed stats
            # We can only check if pool exists and is working
            return {
                "status": "healthy",
                "pool_initialized": True,
                "min_connections": getattr(self.pool, 'minconn', 'unknown'),
                "max_connections": getattr(self.pool, 'maxconn', 'unknown')
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def is_available(self) -> bool:
        """Check if the database service is available and healthy"""
        try:
            if not self.database_url:
                return False
            
            # Initialize pool if needed
            if not self.pool:
                self._init_connection_pool()
            
            # Quick health check
            result = self.execute_query("SELECT 1", fetch='one')
            return result is not None
        except Exception as e:
            logger.warning(f"Database availability check failed: {e}")
            return False

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
                (user_id, [], datetime.utcnow(), datetime.utcnow())
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
            logger.error(f"Failed to add user feedback: {e}")
            return False

    # Character Voice Profile Management Methods
    
    async def get_character_profiles(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all character profiles for a user"""
        try:
            logger.info(f"📚 Fetching character profiles for user {user_id}")
            
            profiles = self.execute_query(
                """SELECT character_id, character_name, user_id, dialogue_samples, 
                          voice_characteristics, sample_count, last_updated, created_at
                   FROM character_voice_profiles 
                   WHERE user_id = %s 
                   ORDER BY last_updated DESC""",
                (user_id,),
                fetch='all'
            )
            
            logger.info(f"✅ Found {len(profiles)} character profiles for user {user_id}")
            return profiles or []
            
        except Exception as e:
            logger.error(f"❌ Failed to get character profiles for user {user_id}: {e}")
            return []
    
    async def get_character_profile(self, user_id: int, character_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific character profile"""
        try:
            logger.info(f"📚 Fetching profile for character '{character_name}' (user {user_id})")
            
            profile = self.execute_query(
                """SELECT character_id, character_name, user_id, dialogue_samples, 
                          voice_characteristics, sample_count, last_updated, created_at
                   FROM character_voice_profiles 
                   WHERE user_id = %s AND character_name = %s""",
                (user_id, character_name),
                fetch='one'
            )
            
            if profile:
                logger.info(f"✅ Found profile for character '{character_name}'")
            else:
                logger.info(f"ℹ️ No profile found for character '{character_name}'")
                
            return profile
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile for character '{character_name}': {e}")
            return None
    
    async def upsert_character_profile(self, user_id: int, character_name: str, 
                                     dialogue_samples: List[str], 
                                     voice_traits: Dict[str, Any]) -> bool:
        """Insert or update a character profile"""
        try:
            import hashlib
            
            # Generate character_id as MD5 hash of user_id + character_name
            character_id = hashlib.md5(f"{user_id}_{character_name}".encode()).hexdigest()[:16]
            
            logger.info(f"💾 Upserting profile for character '{character_name}' (user {user_id})")
            logger.debug(f"   Character ID: {character_id}")
            logger.debug(f"   Dialogue samples: {len(dialogue_samples)}")
            logger.debug(f"   Voice traits keys: {list(voice_traits.keys())}")
            
            # CRITICAL FIX: Convert Python objects to JSON for PostgreSQL compatibility
            import json
            dialogue_samples_json = json.dumps(dialogue_samples) if dialogue_samples else '[]'
            voice_traits_json = json.dumps(voice_traits) if voice_traits else '{}'
            
            logger.debug(f"   Converting to JSON - Dialogue samples: {len(dialogue_samples_json)} chars, Voice traits: {len(voice_traits_json)} chars")
            
            # Use PostgreSQL UPSERT (INSERT ... ON CONFLICT DO UPDATE)
            self.execute_query(
                """INSERT INTO character_voice_profiles 
                   (character_id, character_name, user_id, dialogue_samples, 
                    voice_embedding, voice_characteristics, sample_count, last_updated, created_at)
                   VALUES (%s, %s, %s, %s::jsonb, '{}'::jsonb, %s::jsonb, %s, %s, %s)
                   ON CONFLICT (character_id) DO UPDATE SET
                       dialogue_samples = EXCLUDED.dialogue_samples,
                       voice_characteristics = EXCLUDED.voice_characteristics,
                       sample_count = EXCLUDED.sample_count,
                       last_updated = EXCLUDED.last_updated""",
                (character_id, character_name, user_id, dialogue_samples_json, 
                 voice_traits_json, len(dialogue_samples), datetime.utcnow(), datetime.utcnow())
            )
            
            logger.info(f"✅ Successfully upserted profile for character '{character_name}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upsert profile for character '{character_name}': {e}")
            logger.exception("Full traceback:")
            return False
    
    async def update_character_profile(self, user_id: int, character_name: str,
                                     dialogue_samples: List[str] = None,
                                     voice_traits: Dict[str, Any] = None) -> bool:
        """Update specific fields of a character profile"""
        try:
            logger.info(f"📝 Updating profile for character '{character_name}' (user {user_id})")
            
            # Build dynamic update query based on provided parameters
            update_fields = []
            params = []
            
            if dialogue_samples is not None:
                update_fields.append("dialogue_samples = %s")
                params.append(dialogue_samples)
                update_fields.append("sample_count = %s")
                params.append(len(dialogue_samples))
                logger.debug(f"   Updating dialogue samples: {len(dialogue_samples)} samples")
            
            if voice_traits is not None:
                update_fields.append("voice_characteristics = %s")
                params.append(voice_traits)
                logger.debug(f"   Updating voice traits: {list(voice_traits.keys())}")
            
            if not update_fields:
                logger.warning(f"⚠️ No fields to update for character '{character_name}'")
                return True  # Nothing to update is not an error
            
            # Always update the timestamp
            update_fields.append("last_updated = %s")
            params.append(datetime.utcnow())
            
            # Add WHERE clause parameters
            params.extend([user_id, character_name])
            
            query = f"""UPDATE character_voice_profiles 
                       SET {', '.join(update_fields)}
                       WHERE user_id = %s AND character_name = %s"""
            
            result = self.execute_query(query, tuple(params))
            
            logger.info(f"✅ Successfully updated profile for character '{character_name}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update profile for character '{character_name}': {e}")
            logger.exception("Full traceback:")
            return False
    
    async def delete_character_profile(self, user_id: int, character_name: str) -> bool:
        """Delete a character profile"""
        try:
            logger.info(f"🗑️ Deleting profile for character '{character_name}' (user {user_id})")
            
            self.execute_query(
                """DELETE FROM character_voice_profiles 
                   WHERE user_id = %s AND character_name = %s""",
                (user_id, character_name)
            )
            
            logger.info(f"✅ Successfully deleted profile for character '{character_name}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete profile for character '{character_name}': {e}")
            return False

# Global service instance - initialized lazily to prevent import-time failures
_db_service = None

def get_db_service():
    """Get or create the database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = PostgreSQLService() 
    return _db_service

# Create a property-like access for direct imports
# This allows "from services.database import db_service" to work
# but delays initialization until first access
class DatabaseServiceProxy:
    def __getattr__(self, name):
        return getattr(get_db_service(), name)
    
    def __call__(self, *args, **kwargs):
        return get_db_service()(*args, **kwargs)

# This allows direct import without immediate initialization
db_service = DatabaseServiceProxy() 