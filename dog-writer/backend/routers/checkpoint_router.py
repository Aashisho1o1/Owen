from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models.schemas import CheckpointRequest, CheckpointResponse

router = APIRouter(prefix="/api/checkpoint", tags=["checkpoint"])

@router.post("", response_model=CheckpointResponse)
async def create_checkpoint(request: CheckpointRequest) -> Dict[str, Any]:
    """
    Creates a checkpoint with the current editor text and chat history.
    
    In a production app, this would save to a database.
    Currently just logs the data and returns success.
    """
    try:
        print("Checkpoint data received:")
        print(f"Editor text: {request.editor_text[:100]}...")
        print(f"Chat history length: {len(request.chat_history)} messages")
        
        # TODO: In a production app, implement actual storage logic
        # For example:
        # checkpoint_id = await checkpoint_service.save_checkpoint(request.editor_text, request.chat_history)
        # return {"status": "success", "message": f"Checkpoint saved with ID: {checkpoint_id}"}
        
        return {"status": "success", "message": "Checkpoint saved successfully"}
    except Exception as e:
        print(f"Error in checkpoint creation: {e}")
        # In production, use a more specific error message based on the exception type
        raise HTTPException(status_code=500, detail=f"Failed to create checkpoint: {str(e)}")
