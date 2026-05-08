from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Literal

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Literal["admin", "manager", "operator"] = "operator"

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Literal["admin", "manager", "operator"]
    is_active: bool
    created_at: datetime  # Added for audit trails (NFR-09)

    model_config = ConfigDict(from_attributes=True)  # Pydantic V2 style

class Token(BaseModel):
    access_token: str
    token_type: str