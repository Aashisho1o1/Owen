"""
Folder Router
Handles all folder-related endpoints including CRUD operations.
Extracted from main.py as part of God File refactoring.
"""

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Union

# Import models from centralized schemas
from models.schemas import FolderCreate, FolderUpdate

# Import services
from services.database import db_service, DatabaseError

# Import centralized authentication dependency
from dependencies import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/folders",
    tags=["folders"],
)

@router.get("")
async def get_folders(user_id: Union[str, int] = Depends(get_current_user_id)):
    """Get all folders for the authenticated user"""
    try:
        # Handle guest users: return empty folders list
        if isinstance(user_id, str):
            logger.info(f"Guest user {user_id} requesting folders - returning empty list")
            return []
        folders = db_service.execute_query(
            """SELECT f.*, 
               (SELECT COUNT(*) FROM documents d WHERE d.folder_id = f.id) as document_count
               FROM folders f 
               WHERE f.user_id = %s 
               ORDER BY f.created_at DESC""",
            (user_id,),
            fetch='all'
        )
        return folders
    except DatabaseError as e:
        logger.error(f"Error fetching folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch folders")

@router.post("")
async def create_folder(folder_data: FolderCreate, user_id: int = Depends(get_current_user_id)):
    """Create a new folder"""
    try:
        folder_id = str(uuid.uuid4())
        
        result = db_service.execute_query(
            """INSERT INTO folders (id, user_id, name, parent_id, color, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING id, name, parent_id, color, created_at""",
            (folder_id, user_id, folder_data.name, folder_data.parent_id, folder_data.color, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create folder")
            
        return {
            "id": result['id'],
            "name": result['name'],
            "parent_id": result['parent_id'],
            "color": result['color'],
            "created_at": result['created_at'].isoformat() if result['created_at'] else None,
            "document_count": 0
        }
        
    except DatabaseError as e:
        logger.error(f"Error creating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to create folder")

@router.put("/{folder_id}")
async def update_folder(folder_id: str, folder_data: FolderUpdate, user_id: int = Depends(get_current_user_id)):
    """Update a folder"""
    try:
        # Check if folder exists and belongs to user
        folder = db_service.execute_query(
            "SELECT id, name, color FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id),
            fetch='one'
        )
        
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Update fields
        updates = []
        params = []
        
        if folder_data.name is not None:
            updates.append("name = %s")
            params.append(folder_data.name)
        if folder_data.color is not None:
            updates.append("color = %s")
            params.append(folder_data.color)
        
        if not updates:
            return folder
        
        updates.append("updated_at = %s")
        params.extend([datetime.utcnow(), folder_id, user_id])
        
        result = db_service.execute_query(
            f"UPDATE folders SET {', '.join(updates)} WHERE id = %s AND user_id = %s RETURNING id, name, color, updated_at",
            params,
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update folder")
        
        return result
        
    except DatabaseError as e:
        logger.error(f"Error updating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to update folder")

@router.delete("/{folder_id}")
async def delete_folder(folder_id: str, user_id: int = Depends(get_current_user_id)):
    """Delete a folder"""
    try:
        # Check if folder exists and belongs to user
        folder = db_service.execute_query(
            "SELECT id FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id),
            fetch='one'
        )
        
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Move documents out of this folder
        db_service.execute_query(
            "UPDATE documents SET folder_id = NULL WHERE folder_id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        
        # Delete the folder
        db_service.execute_query(
            "DELETE FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        
        return {"message": "Folder deleted successfully"}
        
    except DatabaseError as e:
        logger.error(f"Error deleting folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete folder") 
 