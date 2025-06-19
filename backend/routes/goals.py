"""Writing Goals API for DOG Writer"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from services.auth_service import auth_service

security = HTTPBearer()
def get_current_user_id(credentials = Depends(security)) -> int:
    try:
        user_data = auth_service.verify_token(credentials.credentials)
        return user_data["user_id"]
    except:
        return None

router = APIRouter()

@router.get("/")
async def get_goals(user_id: int = Depends(get_current_user_id)):
    return []
