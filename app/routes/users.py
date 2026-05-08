# app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# ✅ Corrected Imports
from app.database import get_db
from app.utils.auth import get_current_user
from app.utils.dependencies import require_role  # Added missing import
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.
    SRS FR-01: Users can view their own details.
    """
    return current_user

@router.get("/", response_model=list[UserResponse])
async def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'operator']))  # Allow both
):
    users = db.query(User).all()
    return users