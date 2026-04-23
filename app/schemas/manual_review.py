# app/schemas/manual_review.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ManualReviewResponse(BaseModel):
    id: int
    error_log_id: int
    workflow_type: str
    entity_id: str
    assigned_reviewer: Optional[str]
    status: ReviewStatus
    reviewer_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReviewAction(BaseModel):
    """Used for Approve/Reject request body"""
    reviewer_notes: Optional[str] = None