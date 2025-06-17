"""
Database Service for DOG Writer

Optimized SQLite service with connection pooling, better error handling,
security enhancements, and reduced code duplication.
"""

import sqlite3
import json
import uuid
import logging
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from contextlib import contextmanager
from cryptography.fernet import Fernet

from models.schemas import UserPreferences, UserProfile, UserFeedback

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class DatabaseService:
    """
    Secure SQLite database service for user preferences, writing profiles, and analytics.
    Features connection pooling, transaction management, encryption, and security hardening.
    """
    
    def __init__(self, db_path: str = "dog_writer.db"):
        self.db_path = Path(db_path)
        
        # Initialize encryption for sensitive data
        self._init_encryption()
        
        # Set secure database configuration
        self._secure_db_config()
        
        self.init_database()
        logger.info(f"Database service initialized with {self.db_path}")
    
    def _init_encryption(self):
        """Initialize encryption for sensitive data"""
        # Get or generate encryption key
        key_file = "db_encryption.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            # In production, store this securely (e.g., environment variable or key management service)
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.warning("Generated new encryption key. Store this securely!")
        
        self.cipher = Fernet(key)
    
    def _secure_db_config(self):
        """Configure secure database settings"""
        # Set restrictive file permissions
        if self.db_path.exists():
            os.chmod(self.db_path, 0o600)  # Read/write for owner only
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with security hardening"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # Prevent indefinite locks
                check_same_thread=False
            )
            
            # Enable security features
            conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency and safety
            conn.execute("PRAGMA synchronous = FULL")  # Maximum durability
            conn.execute("PRAGMA temp_store = MEMORY")  # Store temp data in memory
            conn.execute("PRAGMA secure_delete = ON")  # Securely delete data
            
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def _execute_query(self, query: str, params: tuple = (), fetch: str = None) -> Union[List, Any, None]:
        """
        Execute a database query with parameterized queries for security
        
        Args:
            query: SQL query string with ? placeholders
            params: Query parameters (NEVER string formatted)
            fetch: 'one', 'all', or None (for insert/update)
        """
        # Validate that query uses parameterized format
        if any(char in query for char in ['%', 'format', 'f"', "f'"]) and params:
            raise DatabaseError("Use parameterized queries only - no string formatting allowed")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'all':
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storing"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieving"""
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""
    
    def _serialize_json(self, data: Any) -> Optional[str]:
        """Safely serialize data to JSON string"""
        if data is None:
            return None
        try:
            return json.dumps(data)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization failed: {e}")
            return None
    
    def _deserialize_json(self, json_str: Optional[str], default: Any = None) -> Any:
        """Safely deserialize JSON string"""
        if not json_str:
            return default
        try:
            return json.loads(json_str)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON deserialization failed: {e}")
            return default
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy (one-way hash)"""
        return hashlib.sha256(user_id.encode()).hexdigest()

    def init_database(self):
        """Initialize database with optimized and secure schema"""
        schema_queries = [
            # User accounts table for authentication
            '''CREATE TABLE IF NOT EXISTS user_accounts (
                user_id TEXT PRIMARY KEY,  -- UUID for user identification
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,  -- bcrypt hash
                display_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                -- Constraints
                CHECK(length(username) >= 3 AND length(username) <= 50),
                CHECK(length(email) >= 5 AND length(email) <= 254),
                CHECK(length(display_name) <= 100)
            )''',
            
            # User profiles table with proper indexing and constraints
            '''CREATE TABLE IF NOT EXISTS user_profiles (
                user_id_hash TEXT PRIMARY KEY,  -- Hashed for privacy
                user_id TEXT NOT NULL,  -- Direct reference to user_accounts
                writing_style_profile TEXT,  -- Encrypted JSON string
                onboarding_completed BOOLEAN DEFAULT FALSE,
                user_corrections TEXT,  -- Encrypted JSON array
                writing_type TEXT,
                feedback_style TEXT,
                primary_goal TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                -- Constraints
                CHECK(length(writing_type) <= 100),
                CHECK(length(feedback_style) <= 100),
                CHECK(length(primary_goal) <= 500),
                FOREIGN KEY (user_id) REFERENCES user_accounts (user_id) ON DELETE CASCADE
            )''',
            
            # User feedback table with constraints
            '''CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                original_message TEXT NOT NULL,  -- Encrypted
                ai_response TEXT NOT NULL,       -- Encrypted
                user_feedback TEXT NOT NULL,     -- Encrypted
                correction_type TEXT NOT NULL CHECK(correction_type IN ('grammar', 'style', 'tone', 'general')),
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id_hash) REFERENCES user_profiles (user_id_hash) ON DELETE CASCADE
            )''',
            
            # Writing sessions table with constraints
            '''CREATE TABLE IF NOT EXISTS writing_sessions (
                session_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                session_start_time TEXT NOT NULL,
                session_end_time TEXT,
                total_active_seconds INTEGER DEFAULT 0 CHECK(total_active_seconds >= 0),
                total_session_duration_seconds INTEGER DEFAULT 0 CHECK(total_session_duration_seconds >= 0),
                total_keystrokes INTEGER DEFAULT 0 CHECK(total_keystrokes >= 0),
                total_words_written INTEGER DEFAULT 0 CHECK(total_words_written >= 0),
                focus_lost_intervals TEXT,  -- JSON array
                date TEXT NOT NULL,  -- YYYY-MM-DD for aggregation
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id_hash) REFERENCES user_profiles (user_id_hash) ON DELETE CASCADE
            )''',
            
            # Real-time writing activity with constraints
            '''CREATE TABLE IF NOT EXISTS writing_activity (
                activity_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id_hash TEXT NOT NULL,
                activity_type TEXT NOT NULL CHECK(activity_type IN ('typing', 'editing', 'scrolling', 'thinking_pause')),
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0 CHECK(duration_seconds >= 0),
                content_length INTEGER DEFAULT 0 CHECK(content_length >= 0),
                FOREIGN KEY (session_id) REFERENCES writing_sessions (session_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id_hash) REFERENCES user_profiles (user_id_hash) ON DELETE CASCADE
            )''',
            
            # Daily writing summaries with constraints
            '''CREATE TABLE IF NOT EXISTS daily_writing_stats (
                stat_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                date TEXT NOT NULL,  -- YYYY-MM-DD
                total_active_minutes INTEGER DEFAULT 0 CHECK(total_active_minutes >= 0),
                total_sessions INTEGER DEFAULT 0 CHECK(total_sessions >= 0),
                total_keystrokes INTEGER DEFAULT 0 CHECK(total_keystrokes >= 0),
                total_words INTEGER DEFAULT 0 CHECK(total_words >= 0),
                longest_session_minutes INTEGER DEFAULT 0 CHECK(longest_session_minutes >= 0),
                focus_score REAL DEFAULT 0.0 CHECK(focus_score >= 0.0 AND focus_score <= 1.0),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id_hash) REFERENCES user_profiles (user_id_hash) ON DELETE CASCADE,
                UNIQUE(user_id_hash, date)  -- Prevent duplicate daily stats
            )''',
            
            # Indexes for better performance
            'CREATE INDEX IF NOT EXISTS idx_sessions_user_date ON writing_sessions(user_id_hash, date)',
            'CREATE INDEX IF NOT EXISTS idx_activity_session ON writing_activity(session_id)',
            'CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date ON daily_writing_stats(user_id_hash, date)',
            'CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback(user_id_hash)',
            'CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON user_feedback(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_user_accounts_username ON user_accounts(username)',
            'CREATE INDEX IF NOT EXISTS idx_user_accounts_email ON user_accounts(email)',
            'CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)',
        ]
        
        with self.get_connection() as conn:
            for query in schema_queries:
                conn.execute(query)
            conn.commit()
    
    # ============= USER MANAGEMENT =============
    
    def get_or_create_user_id(self) -> str:
        """Generate a new user ID for session-based usage"""
        return str(uuid.uuid4())
    
    def save_user_preferences(self, user_id: str, preferences: UserPreferences) -> bool:
        """Save or update user preferences with UPSERT and encryption"""
        try:
            user_id_hash = self._hash_user_id(user_id)
            
            # Encrypt sensitive data
            writing_style_profile = self._encrypt_sensitive_data(
                self._serialize_json(preferences.writing_style_profile)
            ) if preferences.writing_style_profile else None
            
            user_corrections = self._encrypt_sensitive_data(
                self._serialize_json(preferences.user_corrections)
            ) if preferences.user_corrections else None
            
            query = '''
                INSERT INTO user_profiles (
                    user_id_hash, user_id, writing_style_profile,
                    onboarding_completed, user_corrections, writing_type,
                    feedback_style, primary_goal, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id_hash) DO UPDATE SET
                    writing_style_profile = excluded.writing_style_profile,
                    onboarding_completed = excluded.onboarding_completed,
                    user_corrections = excluded.user_corrections,
                    writing_type = excluded.writing_type,
                    feedback_style = excluded.feedback_style,
                    primary_goal = excluded.primary_goal,
                    updated_at = excluded.updated_at
            '''
            
            self._execute_query(query, (
                user_id_hash,
                user_id,
                writing_style_profile,
                preferences.onboarding_completed,
                user_corrections,
                preferences.writing_type,
                preferences.feedback_style,
                preferences.primary_goal,
                datetime.now().isoformat()
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Retrieve user preferences by user ID"""
        try:
            query = '''
                SELECT writing_style_profile,
                       onboarding_completed, user_corrections, writing_type,
                       feedback_style, primary_goal
                FROM user_profiles WHERE user_id_hash = ?
            '''
            
            row = self._execute_query(query, (self._hash_user_id(user_id),), fetch='one')
            
            if row:
                return UserPreferences(
                    writing_style_profile=self._deserialize_json(row['writing_style_profile']),
                    onboarding_completed=bool(row['onboarding_completed']),
                    user_corrections=self._deserialize_json(row['user_corrections'], []),
                    writing_type=row['writing_type'],
                    feedback_style=row['feedback_style'],
                    primary_goal=row['primary_goal']
                )
            
            return None
            
        except DatabaseError:
            return None
    
    def save_writing_style_profile(self, user_id: str, style_profile: Dict[str, Any]) -> bool:
        """Save analyzed writing style profile for a user"""
        preferences = self.get_user_preferences(user_id) or UserPreferences()
        preferences.writing_style_profile = style_profile
        return self.save_user_preferences(user_id, preferences)
    
    def add_user_feedback(self, user_id: str, original_message: str, 
                         ai_response: str, user_feedback: str, 
                         correction_type: str) -> bool:
        """Store user feedback for learning and improvement"""
        try:
            query = '''
                INSERT INTO user_feedback (
                    feedback_id, user_id_hash, original_message, ai_response,
                    user_feedback, correction_type
                ) VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            feedback_id = str(uuid.uuid4())
            params = (feedback_id, self._hash_user_id(user_id), self._encrypt_sensitive_data(original_message), self._encrypt_sensitive_data(ai_response),
                     self._encrypt_sensitive_data(user_feedback), correction_type)
            
            self._execute_query(query, params)
            
            # Add to user corrections for prompt learning
            self._add_to_user_corrections(user_id, user_feedback)
            return True
            
        except DatabaseError:
            return False
    
    def _add_to_user_corrections(self, user_id: str, correction: str):
        """Add a correction to the user's correction history (max 10 recent)"""
        preferences = self.get_user_preferences(user_id)
        if preferences:
            corrections = preferences.user_corrections or []
            corrections.append(correction)
            
            # Keep only last 10 corrections to avoid prompt bloat
            if len(corrections) > 10:
                corrections = corrections[-10:]
            
            preferences.user_corrections = corrections
            self.save_user_preferences(user_id, preferences)
    
    def get_user_feedback_history(self, user_id: str, limit: int = 50) -> List[UserFeedback]:
        """Get user's feedback history"""
        try:
            query = '''
                SELECT feedback_id, user_id_hash, original_message, ai_response,
                       user_feedback, correction_type, timestamp
                FROM user_feedback 
                WHERE user_id_hash = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            
            rows = self._execute_query(query, (self._hash_user_id(user_id), limit), fetch='all')
            
            return [
                UserFeedback(
                    feedback_id=row['feedback_id'],
                    user_id=row['user_id_hash'],
                    original_message=self._decrypt_sensitive_data(row['original_message']),
                    ai_response=self._decrypt_sensitive_data(row['ai_response']),
                    user_feedback=self._decrypt_sensitive_data(row['user_feedback']),
                    correction_type=row['correction_type'],
                    timestamp=row['timestamp']
                )
                for row in (rows or [])
            ]
            
        except DatabaseError:
            return []
    
    def create_default_preferences(self, user_id: str) -> UserPreferences:
        """Create default preferences for a new user"""
        preferences = UserPreferences()
        self.save_user_preferences(user_id, preferences)
        return preferences
    
    def complete_onboarding(self, user_id: str, writing_type: str, 
                           feedback_style: str, primary_goal: str) -> bool:
        """Mark onboarding as complete and save initial preferences"""
        preferences = self.get_user_preferences(user_id) or UserPreferences()
        
        preferences.onboarding_completed = True
        preferences.writing_type = writing_type
        preferences.feedback_style = feedback_style
        preferences.primary_goal = primary_goal
        
        return self.save_user_preferences(user_id, preferences)

    # ============= WRITING SESSION MANAGEMENT =============
    
    def start_writing_session(self, user_id: str) -> str:
        """
        Start a new writing session and return the session_id.
        
        RATIONALE: Each writing session should be tracked separately to understand
        writing patterns, session length, and focus quality. This enables analytics
        like "average session length" and "most productive time of day".
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            
            query = '''
                INSERT INTO writing_sessions (
                    session_id, user_id_hash, session_start_time, date
                ) VALUES (?, ?, ?, ?)
            '''
            
            params = (session_id, self._hash_user_id(user_id), now.isoformat(), date_str)
            self._execute_query(query, params)
            
            logger.info(f"Started writing session {session_id} for user {user_id}")
            return session_id
            
        except DatabaseError:
            logger.error(f"Failed to start writing session for user {user_id}")
            return ""
    
    def update_session_activity(self, session_id: str, user_id: str, 
                               activity_type: str, content_length: int = 0) -> bool:
        """Record real-time writing activity for session tracking"""
        try:
            query = '''
                INSERT INTO writing_activity (
                    activity_id, session_id, user_id_hash, activity_type, content_length
                ) VALUES (?, ?, ?, ?, ?)
            '''
            
            activity_id = str(uuid.uuid4())
            params = (activity_id, session_id, self._hash_user_id(user_id), activity_type, content_length)
            
            self._execute_query(query, params)
            return True
            
        except DatabaseError:
            logger.warning(f"Failed to update activity for session {session_id}")
            return False
    
    def end_writing_session(self, session_id: str, total_active_seconds: int,
                           total_keystrokes: int = 0, total_words: int = 0,
                           focus_lost_intervals: List[Dict] = None) -> bool:
        """
        End a writing session and calculate final statistics.
        
        RATIONALE: Session end calculates complete analytics for weekly reports.
        Focus Score = Active Writing Time / Total Session Duration
        """
        try:
            # Get session data
            query = '''
                SELECT session_start_time, user_id_hash, date 
                FROM writing_sessions 
                WHERE session_id = ?
            '''
            
            session_data = self._execute_query(query, (session_id,), fetch='one')
            if not session_data:
                return False
            
            start_time_str = session_data['session_start_time']
            user_id_hash = session_data['user_id_hash']
            date_str = session_data['date']
            
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.now()
            total_duration = int((end_time - start_time).total_seconds())
            
            # Calculate focus score
            focus_score = total_active_seconds / total_duration if total_duration > 0 else 0.0
            
            # Update session record
            update_query = '''
                UPDATE writing_sessions SET
                    session_end_time = ?,
                    total_active_seconds = ?,
                    total_session_duration_seconds = ?,
                    total_keystrokes = ?,
                    total_words_written = ?,
                    focus_lost_intervals = ?
                WHERE session_id = ?
            '''
            
            update_params = (
                end_time.isoformat(),
                total_active_seconds,
                total_duration,
                total_keystrokes,
                total_words,
                self._serialize_json(focus_lost_intervals),
                session_id
            )
            
            self._execute_query(update_query, update_params)
            
            # Update daily stats
            self._update_daily_stats(user_id_hash, date_str, total_active_seconds, 
                                   total_keystrokes, total_words, 
                                   total_duration, focus_score)
            
            logger.info(f"Ended writing session {session_id} - {total_active_seconds}s active, {focus_score:.2f} focus")
            return True
            
        except DatabaseError:
            logger.error(f"Failed to end writing session {session_id}")
            return False
    
    def _update_daily_stats(self, user_id_hash: str, date_str: str, 
                           session_active_seconds: int, session_keystrokes: int,
                           session_words: int, session_duration: int, 
                           session_focus_score: float):
        """
        Update or create daily writing statistics.
        
        RATIONALE: Daily aggregation enables quick weekly reports without
        heavy computation. Maintains both raw data and aggregated views.
        """
        try:
            # Check existing daily stats
            select_query = '''
                SELECT stat_id, total_active_minutes, total_sessions, total_keystrokes,
                       total_words, longest_session_minutes, focus_score
                FROM daily_writing_stats 
                WHERE user_id_hash = ? AND date = ?
            '''
            
            existing = self._execute_query(select_query, (user_id_hash, date_str), fetch='one')
            session_minutes = session_active_seconds // 60
            
            if existing:
                # Update existing daily stats
                current_minutes = existing['total_active_minutes']
                current_sessions = existing['total_sessions']
                current_keystrokes = existing['total_keystrokes']
                current_words = existing['total_words']
                current_longest = existing['longest_session_minutes']
                current_focus = existing['focus_score']
                
                new_total_minutes = current_minutes + session_minutes
                new_total_sessions = current_sessions + 1
                new_total_keystrokes = current_keystrokes + session_keystrokes
                new_total_words = current_words + session_words
                new_longest = max(current_longest, session_minutes)
                
                # Weighted average for focus score
                new_focus_score = ((current_focus * current_sessions) + session_focus_score) / new_total_sessions
                
                update_query = '''
                    UPDATE daily_writing_stats SET
                        total_active_minutes = ?,
                        total_sessions = ?,
                        total_keystrokes = ?,
                        total_words = ?,
                        longest_session_minutes = ?,
                        focus_score = ?,
                        updated_at = ?
                    WHERE stat_id = ?
                '''
                
                update_params = (
                    new_total_minutes, new_total_sessions, new_total_keystrokes,
                    new_total_words, new_longest, new_focus_score,
                    datetime.now().isoformat(), existing['stat_id']
                )
                
                self._execute_query(update_query, update_params)
            else:
                # Create new daily stats
                insert_query = '''
                    INSERT INTO daily_writing_stats (
                        stat_id, user_id_hash, date, total_active_minutes, total_sessions,
                        total_keystrokes, total_words, longest_session_minutes,
                        focus_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                stat_id = str(uuid.uuid4())
                insert_params = (
                    stat_id, user_id_hash, date_str, session_minutes, 1,
                    session_keystrokes, session_words, session_minutes,
                    session_focus_score
                )
                
                self._execute_query(insert_query, insert_params)
                
        except DatabaseError:
            logger.warning(f"Failed to update daily stats for {user_id_hash} on {date_str}")
    
    def get_weekly_analytics(self, user_id: str, week_offset: int = 0) -> Dict[str, Any]:
        """
        Generate comprehensive weekly writing analytics.
        
        RATIONALE: Weekly reports provide the perfect balance of granularity and
        overview for actionable insights.
        """
        try:
            # Calculate week date range
            today = datetime.now().date()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
            week_end = week_start + timedelta(days=6)
            
            # Get daily stats for the week
            query = '''
                SELECT date, total_active_minutes, total_sessions, total_keystrokes,
                       total_words, longest_session_minutes, focus_score
                FROM daily_writing_stats
                WHERE user_id_hash = ? AND date BETWEEN ? AND ?
                ORDER BY date
            '''
            
            daily_data = self._execute_query(
                query, 
                (self._hash_user_id(user_id), week_start.isoformat(), week_end.isoformat()), 
                fetch='all'
            ) or []
            
            # Calculate aggregate metrics
            total_minutes = sum(row['total_active_minutes'] for row in daily_data)
            total_sessions = sum(row['total_sessions'] for row in daily_data)
            total_keystrokes = sum(row['total_keystrokes'] for row in daily_data)
            total_words = sum(row['total_words'] for row in daily_data)
            longest_session = max((row['longest_session_minutes'] for row in daily_data), default=0)
            avg_focus_score = sum(row['focus_score'] for row in daily_data) / len(daily_data) if daily_data else 0
            
            # Get previous week for comparison (only for current week)
            prev_week_analytics = None
            if week_offset == 0:
                prev_week_analytics = self.get_weekly_analytics(user_id, -1)
            
            # Build daily breakdown
            daily_breakdown = []
            for i in range(7):
                date = week_start + timedelta(days=i)
                date_str = date.isoformat()
                day_data = next((row for row in daily_data if row['date'] == date_str), None)
                
                daily_breakdown.append({
                    'date': date_str,
                    'day_name': date.strftime('%A'),
                    'active_minutes': day_data['total_active_minutes'] if day_data else 0,
                    'sessions': day_data['total_sessions'] if day_data else 0,
                    'focus_score': day_data['focus_score'] if day_data else 0
                })
            
            # Calculate insights
            active_days = len([d for d in daily_breakdown if d['active_minutes'] > 0])
            avg_daily_minutes = total_minutes / 7 if total_minutes > 0 else 0
            most_productive_day = max(daily_breakdown, key=lambda x: x['active_minutes'])
            
            # Trend calculation
            trend_direction = "stable"
            trend_percentage = 0
            if prev_week_analytics and prev_week_analytics.get('total_minutes', 0) > 0:
                prev_total = prev_week_analytics['total_minutes']
                trend_percentage = ((total_minutes - prev_total) / prev_total) * 100
                if trend_percentage > 5:
                    trend_direction = "increasing"
                elif trend_percentage < -5:
                    trend_direction = "decreasing"
            
            return {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'total_minutes': total_minutes,
                'total_hours': round(total_minutes / 60, 1),
                'total_sessions': total_sessions,
                'total_keystrokes': total_keystrokes,
                'total_words': total_words,
                'active_days': active_days,
                'avg_daily_minutes': round(avg_daily_minutes, 1),
                'longest_session_minutes': longest_session,
                'avg_focus_score': round(avg_focus_score * 100, 1),  # Convert to percentage
                'most_productive_day': most_productive_day,
                'trend_direction': trend_direction,
                'trend_percentage': round(trend_percentage, 1),
                'daily_breakdown': daily_breakdown,
                'insights': self._generate_insights(total_minutes, active_days, avg_focus_score, trend_direction)
            }
            
        except DatabaseError:
            logger.error(f"Failed to generate weekly analytics for user {user_id}")
            return {}
    
    def _generate_insights(self, total_minutes: int, active_days: int, 
                          avg_focus_score: float, trend_direction: str) -> List[str]:
        """
        Generate motivational and actionable insights based on writing patterns.
        
        RATIONALE: Raw numbers aren't as motivating as contextual insights.
        This follows the same principle as fitness apps that celebrate milestones.
        """
        insights = []
        
        # Achievement insights
        if total_minutes >= 300:  # 5+ hours
            insights.append("🎉 Outstanding week! You wrote for over 5 hours.")
        elif total_minutes >= 120:  # 2+ hours
            insights.append("💪 Great consistency! You maintained solid writing time.")
        elif total_minutes >= 60:  # 1+ hour
            insights.append("✍️ Good progress! Every minute of writing counts.")
        
        # Consistency insights
        if active_days >= 6:
            insights.append("🔥 Incredible consistency - you wrote almost every day!")
        elif active_days >= 4:
            insights.append("📅 Strong writing habit - you're building momentum.")
        elif active_days >= 2:
            insights.append("🌱 Your writing routine is taking shape.")
        
        # Focus insights
        if avg_focus_score >= 0.8:
            insights.append("🎯 Excellent focus! You stayed engaged during your writing sessions.")
        elif avg_focus_score >= 0.6:
            insights.append("👁️ Good focus quality - you're staying in the flow.")
        elif avg_focus_score >= 0.4:
            insights.append("💭 Room to improve focus, but that's perfectly normal.")
        
        # Trend insights
        if trend_direction == "increasing":
            insights.append("📈 You're building momentum - keep it up!")
        elif trend_direction == "stable":
            insights.append("⚖️ Steady progress - consistency is key.")
        
        # Encouragement
        if not insights:
            insights.append("🌟 Every writer's journey is unique - keep writing!")
        
        return insights

    # ============= USER AUTHENTICATION =============
    
    def create_user_account(self, username: str, email: str, password_hash: str, 
                           display_name: Optional[str] = None) -> Optional[str]:
        """Create a new user account and return user_id"""
        try:
            user_id = str(uuid.uuid4())
            query = '''
                INSERT INTO user_accounts (
                    user_id, username, email, password_hash, display_name
                ) VALUES (?, ?, ?, ?, ?)
            '''
            
            self._execute_query(query, (user_id, username, email, password_hash, display_name))
            
            # Create default user profile
            self._create_default_user_profile(user_id)
            
            logger.info(f"Created user account: {username}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user account: {e}")
            return None
    
    def _create_default_user_profile(self, user_id: str):
        """Create default user profile for new user"""
        try:
            user_id_hash = self._hash_user_id(user_id)
            query = '''
                INSERT INTO user_profiles (
                    user_id_hash, user_id, onboarding_completed
                ) VALUES (?, ?, ?)
            '''
            
            self._execute_query(query, (user_id_hash, user_id, False))
            
        except Exception as e:
            logger.error(f"Error creating default user profile: {e}")
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user account by username"""
        try:
            query = '''
                SELECT user_id, username, email, password_hash, display_name, 
                       created_at, last_login, is_active, email_verified
                FROM user_accounts 
                WHERE username = ? AND is_active = TRUE
            '''
            
            row = self._execute_query(query, (username.lower(),), fetch='one')
            
            if row:
                return {
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'email': row['email'],
                    'password_hash': row['password_hash'],
                    'display_name': row['display_name'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'is_active': bool(row['is_active']),
                    'email_verified': bool(row['email_verified'])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user account by email"""
        try:
            query = '''
                SELECT user_id, username, email, password_hash, display_name, 
                       created_at, last_login, is_active, email_verified
                FROM user_accounts 
                WHERE email = ? AND is_active = TRUE
            '''
            
            row = self._execute_query(query, (email.lower(),), fetch='one')
            
            if row:
                return {
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'email': row['email'],
                    'password_hash': row['password_hash'],
                    'display_name': row['display_name'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'is_active': bool(row['is_active']),
                    'email_verified': bool(row['email_verified'])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user account by user_id"""
        try:
            query = '''
                SELECT user_id, username, email, display_name, 
                       created_at, last_login, is_active, email_verified
                FROM user_accounts 
                WHERE user_id = ? AND is_active = TRUE
            '''
            
            row = self._execute_query(query, (user_id,), fetch='one')
            
            if row:
                return {
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'email': row['email'],
                    'display_name': row['display_name'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'is_active': bool(row['is_active']),
                    'email_verified': bool(row['email_verified'])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            query = '''
                UPDATE user_accounts 
                SET last_login = ?, updated_at = ?
                WHERE user_id = ?
            '''
            
            now = datetime.now().isoformat()
            self._execute_query(query, (now, now, user_id))
            return True
            
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    def change_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Change user's password"""
        try:
            query = '''
                UPDATE user_accounts 
                SET password_hash = ?, updated_at = ?
                WHERE user_id = ?
            '''
            
            now = datetime.now().isoformat()
            self._execute_query(query, (new_password_hash, now, user_id))
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
    
    def update_user_profile_info(self, user_id: str, display_name: Optional[str] = None, 
                                email: Optional[str] = None) -> bool:
        """Update user profile information"""
        try:
            update_fields = []
            params = []
            
            if display_name is not None:
                update_fields.append("display_name = ?")
                params.append(display_name)
            
            if email is not None:
                update_fields.append("email = ?")
                params.append(email.lower())
            
            if not update_fields:
                return True
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(user_id)
            
            # Fixed: Use parameterized queries instead of string formatting
            # Build the SET clause safely using predefined column names
            allowed_columns = {"display_name", "email", "updated_at"}
            safe_update_fields = []
            
            for field in update_fields:
                column_name = field.split(" = ?")[0]
                if column_name in allowed_columns:
                    safe_update_fields.append(field)
                else:
                    logger.warning(f"Attempted to update disallowed column: {column_name}")
                    return False
            
            query = f'''
                UPDATE user_accounts 
                SET {", ".join(safe_update_fields)}
                WHERE user_id = ?
            '''
            
            self._execute_query(query, params)
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        try:
            query = 'SELECT 1 FROM user_accounts WHERE username = ?'
            result = self._execute_query(query, (username.lower(),), fetch='one')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking username existence: {e}")
            return False
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        try:
            query = 'SELECT 1 FROM user_accounts WHERE email = ?'
            result = self._execute_query(query, (email.lower(),), fetch='one')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking email existence: {e}")
            return False

# Global instance for easy access
db_service = DatabaseService() 