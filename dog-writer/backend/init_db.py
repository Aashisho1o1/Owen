"""
Database initialization script for DOG Writer authentication system
Creates the necessary tables for user management
"""

import sqlite3
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the authentication database with proper tables and indexes"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'auth.db')
    db_dir = os.path.dirname(db_path)
    
    # Ensure database directory exists
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                onboarding_completed BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                failed_login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMP,
                account_locked_until TIMESTAMP,
                password_reset_token TEXT,
                password_reset_expires TIMESTAMP,
                email_verification_token TEXT,
                email_verification_expires TIMESTAMP,
                preferences TEXT DEFAULT '{}',  -- JSON string for user preferences
                subscription_tier TEXT DEFAULT 'free',
                subscription_expires TIMESTAMP
            )
        ''')
        
        # Create refresh_tokens table for JWT token management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                revoked BOOLEAN DEFAULT FALSE,
                device_info TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create login_logs table for security monitoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failure_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        
        # Create password_history table to prevent password reuse
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create user_sessions table for session management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                ip_address TEXT,
                user_agent TEXT,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
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
            cursor.execute(index_sql)
        
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
        
        # Display table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"📁 Database contains {len(tables)} tables: {[table[0] for table in tables]}")
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
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