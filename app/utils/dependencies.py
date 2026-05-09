# app/utils/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from jwt import PyJWTError  # ✅ Use PyJWT instead of jose
from app.database import get_db
from app.utils.auth import oauth2_scheme  # ✅ Import from auth.py (not security.py)
from app.models.user import User
from app.utils.config import get_settings

settings = get_settings()

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
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        
        if email is None:
            raise credentials_exception
            
    except PyJWTError:  # ✅ Use PyJWTError instead of InvalidTokenError
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
    async def role_checker(
        current_user: User = Depends(get_current_user),
        token: str = Depends(oauth2_scheme)
    ) -> User:
        # Decode token to get role
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_role = payload.get("role")
            
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operation not permitted. Required roles: {allowed_roles}. Your role: {user_role}"
                )
        except PyJWTError:  # ✅ Use PyJWTError
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
        return current_user
    return role_checker