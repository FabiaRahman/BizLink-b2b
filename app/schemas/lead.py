from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LeadStatus(str, Enum):
    captured = "captured"
    enriched = "enriched"
    notified = "notified"
    converted = "converted"

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    email: EmailStr = Field(...)
    phone: Optional[str] = Field(None, max_length=50)
    area_of_interest: Optional[str] = Field(None, max_length=255)
    source: str = Field(..., min_length=1, max_length=100)
    source_url: Optional[str] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('email')
    def email_lowercase(cls, v):
        return v.lower()

class LeadResponse(BaseModel):
    id: int
    name: str
    company: Optional[str]
    email: str
    phone: Optional[str]
    area_of_interest: Optional[str]
    source: str
    submitted_at: datetime
    source_url: Optional[str]
    workflow_run_id: Optional[str]
    status: LeadStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str]
    status: LeadStatus
    submitted_at: datetime
    source: str
    
    class Config:
        from_attributes = True