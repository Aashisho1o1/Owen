"""
Document Service for DOG Writer
PostgreSQL-based document management with version control, organization,
and advanced features for creative writing.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4

from .database import db_service, DatabaseError

logger = logging.getLogger(__name__)

class DocumentError(Exception):
    """Custom exception for document operations"""
    pass

class DocumentService:
    """
    Advanced document management service using PostgreSQL.
    Features version control, organization, and collaborative writing tools.
    """
    
    def __init__(self):
        self.db = db_service
        logger.info("Document service initialized with PostgreSQL")
    
    def create_document(self, user_id: int, title: str, content: str = "", document_type: str = "novel", 
                       folder_id: str = None, series_id: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new document"""
        try:
            # Validate user exists
            user = self.db.execute_query(
                "SELECT id FROM users WHERE id = %s AND is_active = TRUE",
                (user_id,),
                fetch='one'
            )
            
            if not user:
                raise DocumentError("User not found or inactive")
            
            # Calculate word count
            word_count = len(content.split()) if content else 0
            
            # Generate UUID for document
            doc_id = str(uuid4())
            
            # Create document
            query = """
                INSERT INTO documents (id, user_id, title, content, document_type, folder_id, series_id, 
                                     tags, word_count, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, title, document_type, word_count, created_at
            """
            
            document = self.db.execute_query(
                query,
                (doc_id, user_id, title, content, document_type, folder_id, series_id, 
                 json.dumps(tags or []), word_count, datetime.utcnow(), datetime.utcnow()),
                fetch='one'
            )
            
            if not document:
                raise DocumentError("Failed to create document")
            
            # Create initial version
            self._create_document_version(doc_id, 1, title, content, word_count, "Initial version")
            
            logger.info(f"Document created successfully: {doc_id} for user {user_id}")
            
            return {
                "id": document['id'],
                "title": document['title'],
                "document_type": document['document_type'],
                "word_count": document['word_count'],
                "created_at": document['created_at'].isoformat(),
                "status": "success"
            }
            
        except DatabaseError as e:
            logger.error(f"Database error during document creation: {e}")
            raise DocumentError("Failed to create document due to database error")
        except Exception as e:
            logger.error(f"Unexpected error during document creation: {e}")
            raise DocumentError("Failed to create document")
    
    def get_user_documents(self, user_id: int, folder_id: str = None, series_id: str = None, 
                          document_type: str = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's documents with optional filtering"""
        try:
            # Build query with filters
            conditions = ["user_id = %s"]
            params = [user_id]
            
            if folder_id:
                conditions.append("folder_id = %s")
                params.append(folder_id)
            
            if series_id:
                conditions.append("series_id = %s")
                params.append(series_id)
            
            if document_type:
                conditions.append("document_type = %s")
                params.append(document_type)
            
            query = f"""
                SELECT id, title, document_type, status, tags, is_favorite, word_count, 
                       created_at, updated_at, folder_id, series_id
                FROM documents 
                WHERE {' AND '.join(conditions)}
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            documents = self.db.execute_query(query, tuple(params), fetch='all')
            
            # Format response
            result = []
            for doc in documents:
                result.append({
                    "id": doc['id'],
                    "title": doc['title'],
                    "document_type": doc['document_type'],
                    "status": doc['status'],
                    "tags": json.loads(doc['tags']) if doc['tags'] else [],
                    "is_favorite": doc['is_favorite'],
                    "word_count": doc['word_count'],
                    "created_at": doc['created_at'].isoformat(),
                    "updated_at": doc['updated_at'].isoformat(),
                    "folder_id": doc['folder_id'],
                    "series_id": doc['series_id']
                })
            
            return result
            
        except DatabaseError as e:
            logger.error(f"Database error getting user documents: {e}")
            raise DocumentError("Failed to retrieve documents")
        except Exception as e:
            logger.error(f"Unexpected error getting user documents: {e}")
            raise DocumentError("Failed to retrieve documents")
    
    def get_document(self, document_id: str, user_id: int) -> Dict[str, Any]:
        """Get a specific document"""
        try:
            query = """
                SELECT id, title, content, document_type, status, tags, is_favorite, 
                       word_count, created_at, updated_at, folder_id, series_id
                FROM documents 
                WHERE id = %s AND user_id = %s
            """
            
            document = self.db.execute_query(query, (document_id, user_id), fetch='one')
            
            if not document:
                raise DocumentError("Document not found or access denied")
            
            return {
                "id": document['id'],
                "title": document['title'],
                "content": document['content'],
                "document_type": document['document_type'],
                "status": document['status'],
                "tags": json.loads(document['tags']) if document['tags'] else [],
                "is_favorite": document['is_favorite'],
                "word_count": document['word_count'],
                "created_at": document['created_at'].isoformat(),
                "updated_at": document['updated_at'].isoformat(),
                "folder_id": document['folder_id'],
                "series_id": document['series_id'],
                "chapter_number": None  # Not in database schema yet
            }
            
        except DatabaseError as e:
            logger.error(f"Database error getting document: {e}")
            raise DocumentError("Failed to retrieve document")
        except Exception as e:
            logger.error(f"Unexpected error getting document: {e}")
            raise DocumentError("Failed to retrieve document")
    
    def update_document(self, document_id: str, user_id: int, title: str = None, content: str = None, 
                       status: str = None, tags: List[str] = None, is_favorite: bool = None,
                       auto_save: bool = False) -> Dict[str, Any]:
        """Update a document"""
        try:
            # First verify the document exists and belongs to the user
            existing_doc = self.get_document(document_id, user_id)
            
            # Build update query
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = %s")
                params.append(title)
            
            if content is not None:
                word_count = len(content.split()) if content else 0
                updates.append("content = %s")
                updates.append("word_count = %s")
                params.extend([content, word_count])
            
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            
            if tags is not None:
                updates.append("tags = %s")
                params.append(json.dumps(tags))
            
            if is_favorite is not None:
                updates.append("is_favorite = %s")
                params.append(is_favorite)
            
            if not updates:
                return existing_doc  # No changes to make
            
            # Add updated_at
            updates.append("updated_at = %s")
            params.append(datetime.utcnow())
            params.extend([document_id, user_id])
            
            query = f"""
                UPDATE documents 
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING word_count, updated_at
            """
            
            result = self.db.execute_query(query, tuple(params), fetch='one')
            
            if not result:
                raise DocumentError("Failed to update document")
            
            # Create version if not auto-save
            if not auto_save and content is not None:
                # Get latest version number
                latest_version = self.db.execute_query(
                    "SELECT COALESCE(MAX(version_number), 0) as max_version FROM document_versions WHERE document_id = %s",
                    (document_id,),
                    fetch='one'
                )
                
                new_version = (latest_version['max_version'] if latest_version else 0) + 1
                self._create_document_version(
                    document_id, new_version, title or existing_doc['title'], 
                    content, result['word_count'], "Manual save", auto_save
                )
            
            logger.info(f"Document updated successfully: {document_id}")
            
            # Return updated document
            return self.get_document(document_id, user_id)
            
        except DocumentError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating document: {e}")
            raise DocumentError("Failed to update document")
    
    def delete_document(self, document_id: str, user_id: int) -> bool:
        """Delete a document and all its versions"""
        try:
            # Verify document exists and belongs to user
            document = self.get_document(document_id, user_id)
            
            # Delete document (versions will be deleted by CASCADE)
            result = self.db.execute_query(
                "DELETE FROM documents WHERE id = %s AND user_id = %s",
                (document_id, user_id)
            )
            
            if result == 0:
                raise DocumentError("Document not found or access denied")
            
            logger.info(f"Document deleted successfully: {document_id}")
            return True
            
        except DocumentError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {e}")
            raise DocumentError("Failed to delete document")
    
    def _create_document_version(self, document_id: str, version_number: int, title: str, 
                                content: str, word_count: int, change_summary: str, is_auto_save: bool = False):
        """Create a new document version"""
        query = """
            INSERT INTO document_versions (id, document_id, version_number, title, content, 
                                         word_count, change_summary, is_auto_save, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.db.execute_query(
            query,
            (str(uuid4()), document_id, version_number, title, content, word_count, 
             change_summary, is_auto_save, datetime.utcnow())
        )
    
    def get_document_versions(self, document_id: str, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get document version history"""
        try:
            # Verify document belongs to user
            self.get_document(document_id, user_id)
            
            query = """
                SELECT id, version_number, title, word_count, change_summary, 
                       is_auto_save, created_at
                FROM document_versions 
                WHERE document_id = %s
                ORDER BY version_number DESC
                LIMIT %s
            """
            
            versions = self.db.execute_query(query, (document_id, limit), fetch='all')
            
            return [
                {
                    "id": v['id'],
                    "version_number": v['version_number'],
                    "title": v['title'],
                    "word_count": v['word_count'],
                    "change_summary": v['change_summary'],
                    "is_auto_save": v['is_auto_save'],
                    "created_at": v['created_at'].isoformat()
                }
                for v in versions
            ]
            
        except DocumentError:
            raise
        except Exception as e:
            logger.error(f"Error getting document versions: {e}")
            raise DocumentError("Failed to retrieve document versions")
    
    def create_folder(self, user_id: int, name: str, parent_id: str = None, color: str = None) -> Dict[str, Any]:
        """Create a new folder"""
        try:
            folder_id = str(uuid4())
            
            query = """
                INSERT INTO folders (id, user_id, name, parent_id, color, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, name, color, created_at
            """
            
            folder = self.db.execute_query(
                query,
                (folder_id, user_id, name, parent_id, color, datetime.utcnow()),
                fetch='one'
            )
            
            if not folder:
                raise DocumentError("Failed to create folder")
            
            return {
                "id": folder['id'],
                "name": folder['name'],
                "color": folder['color'],
                "created_at": folder['created_at'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            raise DocumentError("Failed to create folder")
    
    def get_user_folders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's folders"""
        try:
            query = """
                SELECT id, name, parent_id, color, created_at
                FROM folders 
                WHERE user_id = %s
                ORDER BY name
            """
            
            folders = self.db.execute_query(query, (user_id,), fetch='all')
            
            return [
                {
                    "id": f['id'],
                    "name": f['name'],
                    "parent_id": f['parent_id'],
                    "color": f['color'],
                    "created_at": f['created_at'].isoformat()
                }
                for f in folders
            ]
            
        except Exception as e:
            logger.error(f"Error getting folders: {e}")
            raise DocumentError("Failed to retrieve folders")

# Global document service instance
document_service = DocumentService() 