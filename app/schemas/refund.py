# app/schemas/refund.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RefundBase(BaseModel):
    order_id: int = Field(..., ge=1, description="Original order ID")
    customer_contact: str = Field(..., description="Customer email or phone number")
    refund_amount: float = Field(..., gt=0, description="Refund amount must be positive")
    refund_reason: str = Field(..., description="Reason for refund request")

class RefundCreate(RefundBase):
    pass

class RefundResponse(RefundBase):
    id: int
    refund_status: str
    policy_violation: Optional[str] = None
    reviewer_notes: Optional[str] = None
    requested_at: datetime
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True

class RefundUpdate(BaseModel):
    refund_status: Optional[str] = None
    reviewer_notes: Optional[str] = None