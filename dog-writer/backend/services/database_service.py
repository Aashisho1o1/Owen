"""
Database Service for DOG Writer

Optimized SQLite service with connection pooling, better error handling,
and reduced code duplication.
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from contextlib import contextmanager

from models.schemas import UserPreferences, UserProfile, UserFeedback

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class DatabaseService:
    """
    Optimized SQLite database service for user preferences, writing profiles, and analytics.
    Features connection pooling, transaction management, and reduced code duplication.
    """
    
    def __init__(self, db_path: str = "dog_writer.db"):
        self.db_path = Path(db_path)
        self.init_database()
        logger.info(f"Database service initialized with {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with automatic cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
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
        Execute a database query with standardized error handling
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: 'one', 'all', or None (for insert/update)
        """
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

    def init_database(self):
        """Initialize database with optimized schema"""
        schema_queries = [
            # User profiles table with proper indexing
            '''CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                english_variant TEXT DEFAULT 'standard',
                writing_style_profile TEXT,  -- JSON string
                onboarding_completed BOOLEAN DEFAULT FALSE,
                user_corrections TEXT,  -- JSON array of strings
                writing_type TEXT,
                feedback_style TEXT,
                primary_goal TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # User feedback table
            '''CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                user_id TEXT,
                original_message TEXT,
                ai_response TEXT,
                user_feedback TEXT,
                correction_type TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )''',
            
            # Writing sessions table for productivity tracking
            '''CREATE TABLE IF NOT EXISTS writing_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_start_time TEXT,
                session_end_time TEXT,
                total_active_seconds INTEGER DEFAULT 0,
                total_session_duration_seconds INTEGER DEFAULT 0,
                total_keystrokes INTEGER DEFAULT 0,
                total_words_written INTEGER DEFAULT 0,
                focus_lost_intervals TEXT,  -- JSON array
                date TEXT,  -- YYYY-MM-DD for aggregation
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )''',
            
            # Real-time writing activity
            '''CREATE TABLE IF NOT EXISTS writing_activity (
                activity_id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id TEXT,
                activity_type TEXT,  -- 'typing', 'editing', 'scrolling', 'thinking_pause'
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0,
                content_length INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES writing_sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )''',
            
            # Daily writing summaries for analytics
            '''CREATE TABLE IF NOT EXISTS daily_writing_stats (
                stat_id TEXT PRIMARY KEY,
                user_id TEXT,
                date TEXT,  -- YYYY-MM-DD
                total_active_minutes INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                total_keystrokes INTEGER DEFAULT 0,
                total_words INTEGER DEFAULT 0,
                longest_session_minutes INTEGER DEFAULT 0,
                focus_score REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )''',
            
            # Indexes for better performance
            'CREATE INDEX IF NOT EXISTS idx_sessions_user_date ON writing_sessions(user_id, date)',
            'CREATE INDEX IF NOT EXISTS idx_activity_session ON writing_activity(session_id)',
            'CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date ON daily_writing_stats(user_id, date)',
            'CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback(user_id)',
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
        """Save or update user preferences with UPSERT"""
        try:
            query = '''
                INSERT INTO user_profiles (
                    user_id, english_variant, writing_style_profile,
                    onboarding_completed, user_corrections, writing_type,
                    feedback_style, primary_goal, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    english_variant = excluded.english_variant,
                    writing_style_profile = excluded.writing_style_profile,
                    onboarding_completed = excluded.onboarding_completed,
                    user_corrections = excluded.user_corrections,
                    writing_type = excluded.writing_type,
                    feedback_style = excluded.feedback_style,
                    primary_goal = excluded.primary_goal,
                    updated_at = excluded.updated_at
            '''
            
            params = (
                user_id,
                preferences.english_variant,
                self._serialize_json(preferences.writing_style_profile),
                preferences.onboarding_completed,
                self._serialize_json(preferences.user_corrections),
                preferences.writing_type,
                preferences.feedback_style,
                preferences.primary_goal,
                datetime.now().isoformat()
            )
            
            self._execute_query(query, params)
            return True
            
        except DatabaseError:
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Retrieve user preferences by user ID"""
        try:
            query = '''
                SELECT english_variant, writing_style_profile,
                       onboarding_completed, user_corrections, writing_type,
                       feedback_style, primary_goal
                FROM user_profiles WHERE user_id = ?
            '''
            
            row = self._execute_query(query, (user_id,), fetch='one')
            
            if row:
                return UserPreferences(
                    english_variant=row['english_variant'],
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
                    feedback_id, user_id, original_message, ai_response,
                    user_feedback, correction_type
                ) VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            feedback_id = str(uuid.uuid4())
            params = (feedback_id, user_id, original_message, ai_response,
                     user_feedback, correction_type)
            
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
                SELECT feedback_id, user_id, original_message, ai_response,
                       user_feedback, correction_type, timestamp
                FROM user_feedback 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            
            rows = self._execute_query(query, (user_id, limit), fetch='all')
            
            return [
                UserFeedback(
                    feedback_id=row['feedback_id'],
                    user_id=row['user_id'],
                    original_message=row['original_message'],
                    ai_response=row['ai_response'],
                    user_feedback=row['user_feedback'],
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
                           feedback_style: str, primary_goal: str,
                           english_variant: str = "standard") -> bool:
        """Mark onboarding as complete and save initial preferences"""
        preferences = self.get_user_preferences(user_id) or UserPreferences()
        
        preferences.onboarding_completed = True
        preferences.writing_type = writing_type
        preferences.feedback_style = feedback_style
        preferences.primary_goal = primary_goal
        preferences.english_variant = english_variant
        
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
                    session_id, user_id, session_start_time, date
                ) VALUES (?, ?, ?, ?)
            '''
            
            params = (session_id, user_id, now.isoformat(), date_str)
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
                    activity_id, session_id, user_id, activity_type, content_length
                ) VALUES (?, ?, ?, ?, ?)
            '''
            
            activity_id = str(uuid.uuid4())
            params = (activity_id, session_id, user_id, activity_type, content_length)
            
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
                SELECT session_start_time, user_id, date 
                FROM writing_sessions 
                WHERE session_id = ?
            '''
            
            session_data = self._execute_query(query, (session_id,), fetch='one')
            if not session_data:
                return False
            
            start_time_str = session_data['session_start_time']
            user_id = session_data['user_id']
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
            self._update_daily_stats(user_id, date_str, total_active_seconds, 
                                   total_keystrokes, total_words, 
                                   total_duration, focus_score)
            
            logger.info(f"Ended writing session {session_id} - {total_active_seconds}s active, {focus_score:.2f} focus")
            return True
            
        except DatabaseError:
            logger.error(f"Failed to end writing session {session_id}")
            return False
    
    def _update_daily_stats(self, user_id: str, date_str: str, 
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
                WHERE user_id = ? AND date = ?
            '''
            
            existing = self._execute_query(select_query, (user_id, date_str), fetch='one')
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
                        stat_id, user_id, date, total_active_minutes, total_sessions,
                        total_keystrokes, total_words, longest_session_minutes,
                        focus_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                stat_id = str(uuid.uuid4())
                insert_params = (
                    stat_id, user_id, date_str, session_minutes, 1,
                    session_keystrokes, session_words, session_minutes,
                    session_focus_score
                )
                
                self._execute_query(insert_query, insert_params)
                
        except DatabaseError:
            logger.warning(f"Failed to update daily stats for {user_id} on {date_str}")
    
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
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date
            '''
            
            daily_data = self._execute_query(
                query, 
                (user_id, week_start.isoformat(), week_end.isoformat()), 
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

# Global instance for easy access
db_service = DatabaseService() 