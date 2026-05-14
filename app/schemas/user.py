from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "operator"  # "admin", "manager", or "operator"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    """Full user info returned after registration or profile fetch"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInLogin(BaseModel):
    """Minimal user info returned in login response for frontend"""
    name: str        # Maps to username
    email: EmailStr
    role: str

# =============================================================================
# Token Schemas (for JWT Authentication)
# =============================================================================

class Token(BaseModel):
    """Basic token response - used internally"""
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    """
    Combined response for /auth/login endpoint.
    Returns both JWT token AND user info so frontend can populate dashboard immediately.
    SRS 3.1.4: RBAC + Frontend Integration
    """
    access_token: str
    token_type: str = "bearer"
    user: UserInLogin  # 👈 This is what frontend needs!
    
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    """Internal schema for decoding JWT payload"""
    email: str | None = None
    role: str | None = None