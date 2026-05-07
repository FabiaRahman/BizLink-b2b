from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional


from app.database import get_db  # ← Import from database.py
from app.utils.security import oauth2_scheme, decode_token
from app.models.user import User


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
   
    payload = decode_token(token)
    email: Optional[str] = payload.get("sub")
   
    if email is None:
        raise credentials_exception
   
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
   
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
   
    return user


def require_role(allowed_roles: list[str]):
    """
    Dependency factory: Check if current user has required role(s)
    Usage: Depends(require_role(['admin', 'manager']))
    """
    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_roles}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker