"""
Document Management Service for DOG Writer

Comprehensive document storage and management with version control,
full-text search, and advanced organization features.
Supports both SQLite (development) and PostgreSQL (production).
"""

import os
import json
import uuid
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from dataclasses import dataclass

# Database imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3
from contextlib import contextmanager

# Pydantic models
from pydantic import BaseModel
# from models.schemas import UserProfile # This causes circular import, will get user profile from auth service

logger = logging.getLogger(__name__)

# Document Models
@dataclass
class Document:
    id: str
    user_id: str
    title: str
    content: str
    document_type: str  # 'novel', 'chapter', 'character_sheet', 'outline', 'notes'
    folder_id: Optional[str] = None
    series_id: Optional[str] = None
    chapter_number: Optional[int] = None
    status: str = 'draft'  # 'draft', 'revision', 'final', 'published'
    tags: List[str] = None
    is_favorite: bool = False
    word_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class DocumentVersion:
    id: str
    document_id: str
    version_number: int
    title: str
    content: str
    word_count: int
    change_summary: str
    is_auto_save: bool
    created_at: datetime

@dataclass 
class DocumentFolder:
    id: str
    user_id: str
    name: str
    parent_id: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime = None
    children: List['DocumentFolder'] = None

@dataclass
class DocumentSeries:
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    total_chapters: int = 0
    total_words: int = 0
    created_at: datetime = None

class DocumentError(Exception):
    """Custom exception for document operations"""
    pass

class DocumentService:
    """
    Advanced document management service with version control and organization.
    Supports both SQLite (development) and PostgreSQL (production).
    """
    
    def __init__(self, db_type: str = "sqlite", db_config: Dict[str, Any] = None):
        self.db_type = db_type.lower()
        self.db_config = db_config or {}
        
        if self.db_type == "postgresql" and not POSTGRES_AVAILABLE:
            logger.warning("PostgreSQL requested but psycopg2 not available, falling back to SQLite")
            self.db_type = "sqlite"
        
        # self.init_database() # This is now called from the main init_db.py
        logger.info(f"Document service configured for {self.db_type}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections supporting both SQLite and PostgreSQL"""
        conn = None
        try:
            if self.db_type == "postgresql":
                conn = psycopg2.connect(self.db_config['url'], cursor_factory=RealDictCursor)
            else:
                # SQLite
                db_path = self.db_config.get('path', 'database/auth.db')
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(db_path, timeout=30.0)
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.row_factory = sqlite3.Row
            
            yield conn
            if self.db_type == 'postgresql':
                conn.commit()
            
        except Exception as e:
            if conn and self.db_type == 'postgresql':
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DocumentError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def _execute_query(self, query: str, params: tuple = (), fetch: str = None) -> Union[List[sqlite3.Row], Any, int, None]:
        """Execute database query with support for both SQLite and PostgreSQL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Adapt query for PostgreSQL vs SQLite differences
            if self.db_type == "postgresql":
                # Convert SQLite ? placeholders to PostgreSQL %s
                pg_query = query.replace('?', '%s')
                cursor.execute(pg_query, params)
            else:
                cursor.execute(query, params)
            
            if fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'all':
                return cursor.fetchall()
            else:
                if self.db_type != "postgresql":
                    conn.commit()
                return cursor.rowcount

    def init_database(self):
        """Initialize database with comprehensive document management schema"""
        
        # Common SQL for both databases with slight variations
        if self.db_type == "postgresql":
            timestamp_type = "TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP"
            text_type = "TEXT"
            json_type = "JSONB"
        else:
            timestamp_type = "TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))"
            text_type = "TEXT"
            json_type = "TEXT"
        
        schema_queries = [
            # Documents table
            f'''CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content {text_type},
                document_type TEXT DEFAULT 'novel',
                folder_id TEXT,
                series_id TEXT,
                chapter_number INTEGER,
                status TEXT DEFAULT 'draft',
                tags {json_type},
                is_favorite BOOLEAN DEFAULT FALSE,
                word_count INTEGER DEFAULT 0,
                created_at {timestamp_type},
                updated_at {timestamp_type}
            )''',
            
            # Document versions for change tracking
            f'''CREATE TABLE IF NOT EXISTS document_versions (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                content {text_type},
                word_count INTEGER DEFAULT 0,
                change_summary TEXT,
                is_auto_save BOOLEAN DEFAULT FALSE,
                created_at {timestamp_type},
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )''',
        ]
        
        index_queries = [
            'CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id)',
        ]
        
        for query in schema_queries + index_queries:
            self._execute_query(query)

    def _calculate_word_count(self, content: str) -> int:
        """Calculate word count from text content"""
        if not content:
            return 0
        return len(content.strip().split())

    def _serialize_tags(self, tags: List[str]) -> str:
        """Serialize tags list for storage"""
        return json.dumps(tags or [])

    def _deserialize_tags(self, tags_json: str) -> List[str]:
        """Deserialize tags from storage"""
        if not tags_json:
            return []
        try:
            return json.loads(tags_json)
        except (TypeError, ValueError):
            return []

    # ============= DOCUMENT OPERATIONS =============
    
    def create_document(self, user_id: str, title: str, content: str = "", 
                       document_type: str = "novel", folder_id: str = None, 
                       series_id: str = None, chapter_number: int = None) -> Document:
        """Create a new document"""
        try:
            doc_id = str(uuid.uuid4())
            word_count = self._calculate_word_count(content)
            now = datetime.now().isoformat()
            
            query = '''
                INSERT INTO documents (
                    id, user_id, title, content, document_type, folder_id,
                    series_id, chapter_number, word_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            self._execute_query(query, (
                doc_id, user_id, title, content, document_type, folder_id,
                series_id, chapter_number, word_count, now, now
            ))
            
            # Create initial version
            self._create_version(doc_id, 1, title, content, word_count, "Initial version", False)
            
            return self.get_document(doc_id)
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise DocumentError(f"Failed to create document: {e}")

    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID"""
        try:
            query = "SELECT * FROM documents WHERE id = ?"
            row = self._execute_query(query, (document_id,), fetch='one')
            
            if row:
                return Document(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    content=row['content'],
                    document_type=row['document_type'],
                    folder_id=row['folder_id'],
                    series_id=row['series_id'],
                    chapter_number=row['chapter_number'],
                    status=row['status'],
                    tags=self._deserialize_tags(row['tags']),
                    is_favorite=bool(row['is_favorite']),
                    word_count=row['word_count'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            raise DocumentError(f"Failed to retrieve document: {e}")

    def update_document(self, document_id: str, **updates) -> Document:
        """Update document with change tracking"""
        try:
            current_doc = self.get_document(document_id)
            if not current_doc:
                raise DocumentError(f"Document {document_id} not found")
            
            update_fields = []
            update_values = []
            
            allowed_fields = {
                'title', 'content', 'document_type', 'folder_id', 'series_id',
                'chapter_number', 'status', 'tags', 'is_favorite'
            }
            
            for field, value in updates.items():
                if field in allowed_fields:
                    if field == 'tags':
                        value = self._serialize_tags(value)
                    elif field == 'content' and value != current_doc.content:
                        updates['word_count'] = self._calculate_word_count(value)
                        # Add word_count to allowed fields for this update
                        if 'word_count' not in [f.split(' = ?')[0] for f in update_fields]:
                            update_fields.append('word_count = ?')
                            update_values.append(updates['word_count'])
                    
                    update_fields.append(f'{field} = ?')
                    update_values.append(value)
                else:
                    logger.warning(f"Attempted to update disallowed field: {field}")
                    continue
            
            if not update_fields:
                return current_doc
            
            update_fields.append('updated_at = ?')
            update_values.append(datetime.now().isoformat())
            update_values.append(document_id)
            
            # Fixed: Validate all field names against allowlist before building query
            safe_update_fields = []
            for field_clause in update_fields:
                field_name = field_clause.split(' = ?')[0]
                # Include 'updated_at' as it's always safe and added by us
                if field_name in allowed_fields or field_name in {'updated_at', 'word_count'}:
                    safe_update_fields.append(field_clause)
                else:
                    logger.error(f"Unauthorized field in UPDATE query: {field_name}")
                    raise DocumentError(f"Unauthorized field update attempted: {field_name}")
            
            query = f"UPDATE documents SET {', '.join(safe_update_fields)} WHERE id = ?"
            self._execute_query(query, tuple(update_values))
            
            if 'content' in updates or 'title' in updates:
                latest_version = self._get_latest_version_number(document_id)
                new_title = updates.get('title', current_doc.title)
                new_content = updates.get('content', current_doc.content)
                new_word_count = updates.get('word_count', current_doc.word_count)
                
                self._create_version(
                    document_id, 
                    latest_version + 1,
                    new_title,
                    new_content,
                    new_word_count,
                    "Auto-save update",
                    True
                )
            
            return self.get_document(document_id)
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise DocumentError(f"Failed to update document: {e}")

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its versions"""
        try:
            query = "DELETE FROM documents WHERE id = ?"
            result = self._execute_query(query, (document_id,))
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise DocumentError(f"Failed to delete document: {e}")

    def get_user_documents(self, user_id: str, folder_id: str = None, 
                          series_id: str = None, document_type: str = None) -> List[Document]:
        """Get all documents for a user with optional filtering"""
        try:
            # Fixed: Use predefined conditions instead of dynamic string building
            base_query = "SELECT * FROM documents WHERE user_id = ?"
            params = [user_id]
            
            # Build WHERE clause safely with predefined conditions
            additional_conditions = []
            if folder_id:
                additional_conditions.append("folder_id = ?")
                params.append(folder_id)
            if series_id:
                additional_conditions.append("series_id = ?")
                params.append(series_id)
            if document_type:
                # Validate document_type against allowed values
                allowed_types = {'novel', 'chapter', 'character_sheet', 'outline', 'notes'}
                if document_type not in allowed_types:
                    logger.warning(f"Invalid document_type filter: {document_type}")
                    raise DocumentError(f"Invalid document type: {document_type}")
                additional_conditions.append("document_type = ?")
                params.append(document_type)
            
            # Safely build the final query
            if additional_conditions:
                query = f"{base_query} AND {' AND '.join(additional_conditions)} ORDER BY updated_at DESC"
            else:
                query = f"{base_query} ORDER BY updated_at DESC"
                
            rows = self._execute_query(query, tuple(params), fetch='all')
            
            documents = []
            for row in rows:
                documents.append(Document(
                    id=row['id'], user_id=row['user_id'], title=row['title'],
                    content=row['content'], document_type=row['document_type'],
                    folder_id=row['folder_id'], series_id=row['series_id'],
                    chapter_number=row['chapter_number'], status=row['status'],
                    tags=self._deserialize_tags(row['tags']), is_favorite=bool(row['is_favorite']),
                    word_count=row['word_count'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                ))
            
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving user documents: {e}")
            raise DocumentError(f"Failed to retrieve documents: {e}")

    # ============= VERSION MANAGEMENT =============
    
    def _create_version(self, document_id: str, version_number: int, title: str, 
                       content: str, word_count: int, change_summary: str, is_auto_save: bool):
        """Create a new document version"""
        version_id = str(uuid.uuid4())
        query = '''
            INSERT INTO document_versions (id, document_id, version_number, title, content,
                word_count, change_summary, is_auto_save, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self._execute_query(query, (
            version_id, document_id, version_number, title, content,
            word_count, change_summary, is_auto_save, datetime.now().isoformat()
        ))

    def _get_latest_version_number(self, document_id: str) -> int:
        """Get the latest version number for a document"""
        query = "SELECT MAX(version_number) as max_version FROM document_versions WHERE document_id = ?"
        result = self._execute_query(query, (document_id,), fetch='one')
        return result['max_version'] if result and result['max_version'] else 0

    def get_document_versions(self, document_id: str) -> List[DocumentVersion]:
        """Get all versions of a document"""
        try:
            query = "SELECT * FROM document_versions WHERE document_id = ? ORDER BY version_number DESC"
            rows = self._execute_query(query, (document_id,), fetch='all')
            
            versions = []
            for row in rows:
                versions.append(DocumentVersion(
                    id=row['id'], document_id=row['document_id'],
                    version_number=row['version_number'], title=row['title'], content=row['content'],
                    word_count=row['word_count'], change_summary=row['change_summary'],
                    is_auto_save=bool(row['is_auto_save']),
                    created_at=datetime.fromisoformat(row['created_at'])
                ))
            return versions
            
        except Exception as e:
            logger.error(f"Error retrieving document versions: {e}")
            raise DocumentError(f"Failed to retrieve versions: {e}")

    def restore_version(self, document_id: str, version_id: str) -> Document:
        """Restore a document to a previous version"""
        try:
            query = "SELECT * FROM document_versions WHERE id = ? AND document_id = ?"
            version = self._execute_query(query, (version_id, document_id), fetch='one')
            if not version:
                raise DocumentError(f"Version {version_id} not found")
            
            updated_doc = self.update_document(
                document_id,
                title=version['title'],
                content=version['content']
            )
            
            latest_version = self._get_latest_version_number(document_id)
            self._create_version(
                document_id, latest_version + 1, version['title'], version['content'],
                version['word_count'], f"Restored from version {version['version_number']}", False
            )
            return updated_doc
            
        except Exception as e:
            logger.error(f"Error restoring version: {e}")
            raise DocumentError(f"Failed to restore version: {e}")

# Determine database configuration based on environment
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DB_TYPE = "postgresql"
    DB_CONFIG = {'url': DATABASE_URL}
else:
    DB_TYPE = "sqlite"
    DB_CONFIG = {'path': 'database/auth.db'}

# Global service instance
document_service = DocumentService(
    db_type=DB_TYPE,
    db_config=DB_CONFIG
) 