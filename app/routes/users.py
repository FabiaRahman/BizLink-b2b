from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.utils.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's profile"""
    return current_user


@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin']))
):
    """List all users (Admin only - RBAC protected per SRS FR-01)"""
    users = db.query(User).all()
    return users