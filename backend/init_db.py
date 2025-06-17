"""
Database initialization script for DOG Writer authentication system
Creates the necessary tables for user management
"""

import sqlite3
import os
import logging
from datetime import datetime

# Conditional PostgreSQL import
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with proper tables and indexes for SQLite or PostgreSQL"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    db_type = "postgresql" if DATABASE_URL else "sqlite"
    
    if db_type == "postgresql" and not POSTGRES_AVAILABLE:
        logger.error("PostgreSQL requested but psycopg2 not available. Install with: pip install psycopg2-binary")
        return False
    
    conn = None

    try:
        if db_type == "postgresql":
            conn = psycopg2.connect(DATABASE_URL)
        else:
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'auth.db')
            db_dir = os.path.dirname(db_path)
            # Ensure database directory exists
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            conn = sqlite3.connect(db_path)
        
        cursor = conn.cursor()
        
        def execute_adapted_query(query, params=None):
            if db_type == "postgresql":
                cursor.execute(query.replace('?', '%s'), params or ())
            else:
                cursor.execute(query, params or ())

        # Create users table
        users_table_sql = '''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                onboarding_completed BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMPTZ,
                login_count INTEGER DEFAULT 0,
                failed_login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMPTZ,
                account_locked_until TIMESTAMPTZ,
                password_reset_token TEXT,
                password_reset_expires TIMESTAMPTZ,
                email_verification_token TEXT,
                email_verification_expires TIMESTAMPTZ,
                preferences JSONB DEFAULT '{}',
                subscription_tier TEXT DEFAULT 'free',
                subscription_expires TIMESTAMPTZ
            )
        '''
        if db_type == 'sqlite':
            users_table_sql = users_table_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            users_table_sql = users_table_sql.replace('TIMESTAMPTZ', 'TIMESTAMP')
            users_table_sql = users_table_sql.replace('JSONB', 'TEXT')
            
        execute_adapted_query(users_table_sql)
        
        # Create refresh_tokens table for JWT token management
        refresh_tokens_sql = '''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                revoked BOOLEAN DEFAULT FALSE,
                device_info TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        '''
        if db_type == 'sqlite':
            refresh_tokens_sql = refresh_tokens_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            refresh_tokens_sql = refresh_tokens_sql.replace('TIMESTAMPTZ', 'TIMESTAMP')

        execute_adapted_query(refresh_tokens_sql)
        
        # Create login_logs table
        login_logs_sql = '''
            CREATE TABLE IF NOT EXISTS login_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                email TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                attempted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                failure_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        '''
        if db_type == 'sqlite':
            login_logs_sql = login_logs_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            login_logs_sql = login_logs_sql.replace('TIMESTAMPTZ', 'TIMESTAMP')
        execute_adapted_query(login_logs_sql)
        
        # Create password_history table
        password_history_sql = '''
            CREATE TABLE IF NOT EXISTS password_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        '''
        if db_type == 'sqlite':
            password_history_sql = password_history_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            password_history_sql = password_history_sql.replace('TIMESTAMPTZ', 'TIMESTAMP')
        execute_adapted_query(password_history_sql)
        
        # Create user_sessions table
        user_sessions_sql = '''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMPTZ NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                ip_address TEXT,
                user_agent TEXT,
                last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        '''
        if db_type == 'sqlite':
            user_sessions_sql = user_sessions_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            user_sessions_sql = user_sessions_sql.replace('TIMESTAMPTZ', 'TIMESTAMP')
        execute_adapted_query(user_sessions_sql)
        
        # Create indexes for better performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)',
            'CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)',
            'CREATE INDEX IF NOT EXISTS idx_users_active ON users (is_active)',
            'CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id)',
            'CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens (expires_at)',
            'CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs (user_id)',
            'CREATE INDEX IF NOT EXISTS idx_login_logs_attempted_at ON login_logs (attempted_at)',
            'CREATE INDEX IF NOT EXISTS idx_password_history_user_id ON password_history (user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions (session_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions (expires_at)',
        ]
        
        for index_sql in indexes:
            execute_adapted_query(index_sql)
        
        # Triggers are SQLite specific and might not be needed or compatible with PostgreSQL
        if db_type == 'sqlite':
            # Create triggers to update the updated_at timestamp
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_users_updated_at 
                AFTER UPDATE ON users 
                FOR EACH ROW 
                BEGIN 
                    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
                END
            ''')
            
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_user_sessions_last_activity 
                AFTER UPDATE ON user_sessions 
                FOR EACH ROW 
                BEGIN 
                    UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = NEW.id; 
                END
            ''')
        
        # Commit all changes
        conn.commit()
        
        logger.info("✅ Database initialized successfully!")
        logger.info("📋 Created tables: users, refresh_tokens, login_logs, password_history, user_sessions")
        logger.info("📊 Created indexes for optimal performance")
        logger.info("⚡ Created triggers for automatic timestamp updates")
        
        # Initialize document service database schema
        logger.info("🚀 Initializing document service database schema...")
        # Import here to avoid circular imports
        from services.document_service import document_service
        document_service.init_database()
        logger.info("✅ Document service database schema initialized successfully!")
        
        # Display table info for SQLite
        if db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"📁 Database contains {len(tables)} tables: {[table[0] for table in tables]}")
        else:
            # For PostgreSQL, we can query information_schema
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            logger.info(f"📁 Database contains {len(tables)} tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def check_database_health():
    """Check if the database is properly initialized and accessible"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'auth.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM refresh_tokens")
        token_count = cursor.fetchone()[0]
        
        logger.info(f"📊 Database health check passed!")
        logger.info(f"👥 Users: {user_count}")
        logger.info(f"🔑 Refresh tokens: {token_count}")
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database health check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during health check: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Initializing DOG Writer Authentication Database...")
    
    if init_database():
        print("\n✅ Database initialization completed successfully!")
        
        # Run health check
        print("\n🔍 Running database health check...")
        if check_database_health():
            print("\n🎉 Authentication system is ready!")
        else:
            print("\n❌ Database health check failed!")
    else:
        print("\n❌ Database initialization failed!")
        
    print("\n📚 Next steps:")
    print("1. Start your FastAPI server")
    print("2. Test user registration at /api/auth/register")
    print("3. Test user login at /api/auth/login")
    print("4. Monitor authentication logs in the database") 