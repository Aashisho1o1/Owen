"""
Database Service - Minimal PostgreSQL integration
Handles users, character profiles, and documents
"""

import os
import logging
from typing import List, Dict, Any, Optional
import asyncpg
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    """Minimal database service for competition."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv("DATABASE_URL")

    async def connect(self):
        """Initialize database connection pool."""
        if not self.database_url:
            logger.warning("⚠️ DATABASE_URL not set - database disabled")
            return

        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=30,
                max_queries=50000,
                max_inactive_connection_lifetime=300
            )
            logger.info("✅ Database connected with optimized pool")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.pool = None

    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database disconnected")

    def is_available(self) -> bool:
        """Check if database is available."""
        return self.pool is not None

    # === USER METHODS ===

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        if not self.pool:
            return None

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT id, email, password_hash, created_at FROM users WHERE email = $1",
                    email
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Get user failed: {e}")
            return None

    async def create_user(self, email: str, password_hash: str) -> Optional[int]:
        """Create new user and return user ID."""
        if not self.pool:
            return None

        try:
            async with self.pool.acquire() as conn:
                user_id = await conn.fetchval(
                    "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id",
                    email, password_hash
                )
                logger.info(f"✅ User created: {email}")
                return user_id
        except Exception as e:
            logger.error(f"❌ Create user failed: {e}")
            return None

    # === CHARACTER PROFILE METHODS ===

    async def get_character_profiles(self, user_id: int) -> List[Dict]:
        """Get all character profiles for a user."""
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, character_name, dialogue_samples, voice_traits,
                           sample_count, last_updated
                    FROM character_profiles
                    WHERE user_id = $1
                    ORDER BY last_updated DESC
                    """,
                    user_id
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Get profiles failed: {e}")
            return []

    async def upsert_character_profile(
        self,
        user_id: int,
        character_name: str,
        dialogue_samples: List[str],
        voice_traits: Dict[str, Any]
    ) -> bool:
        """Create or update character profile."""
        if not self.pool:
            return False

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO character_profiles
                        (user_id, character_name, dialogue_samples, voice_traits, sample_count, last_updated)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_id, character_name)
                    DO UPDATE SET
                        dialogue_samples = EXCLUDED.dialogue_samples,
                        voice_traits = EXCLUDED.voice_traits,
                        sample_count = EXCLUDED.sample_count,
                        last_updated = EXCLUDED.last_updated
                    """,
                    user_id,
                    character_name,
                    dialogue_samples,
                    voice_traits,
                    len(dialogue_samples),
                    datetime.now()
                )
                return True
        except Exception as e:
            logger.error(f"❌ Upsert profile failed: {e}")
            return False

    async def delete_character_profile(self, user_id: int, character_name: str) -> bool:
        """Delete a character profile."""
        if not self.pool:
            return False

        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM character_profiles WHERE user_id = $1 AND character_name = $2",
                    user_id, character_name
                )
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"❌ Delete profile failed: {e}")
            return False

    # === DOCUMENT METHODS (OPTIONAL) ===

    async def create_document(
        self,
        user_id: int,
        title: str,
        content: str = ""
    ) -> Optional[int]:
        """Create a new document."""
        if not self.pool:
            return None

        try:
            async with self.pool.acquire() as conn:
                doc_id = await conn.fetchval(
                    """
                    INSERT INTO documents (user_id, title, content)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    user_id, title, content
                )
                return doc_id
        except Exception as e:
            logger.error(f"❌ Create document failed: {e}")
            return None

    async def get_documents(self, user_id: int) -> List[Dict]:
        """Get all documents for a user."""
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, title, content, created_at, updated_at
                    FROM documents
                    WHERE user_id = $1
                    ORDER BY updated_at DESC
                    """,
                    user_id
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Get documents failed: {e}")
            return []

# Global instance
db_service = DatabaseService()
