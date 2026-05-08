from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "operator"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

    # =============================================================================
# Token Schemas (for JWT Authentication)
# =============================================================================

class Token(BaseModel):
    """Response schema for login endpoint - SRS 3.1.4"""
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Internal schema for decoding JWT payload"""
    email: str | None = None
    role: str | None = None