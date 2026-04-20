from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class RefundReason(str, Enum):
    defective_product = "defective_product"
    wrong_item = "wrong_item"
    not_as_described = "not_as_described"
    customer_changed_mind = "customer_changed_mind"
    duplicate_order = "duplicate_order"
    other = "other"

class RefundStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    processing = "processing"
    completed = "completed"

class RefundBase(BaseModel):
    order_id: int = Field(..., ge=1, description="Original order ID")
    customer_contact: EmailStr = Field(..., description="Customer email")
    refund_amount: float = Field(..., gt=0, description="Refund amount must be positive")
    refund_reason: RefundReason

class RefundCreate(RefundBase):
    pass

class RefundResponse(RefundBase):
    id: int
    refund_status: RefundStatus
    policy_violation: Optional[str] = None
    reviewer_notes: Optional[str] = None
    requested_at: datetime
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True

class RefundUpdate(BaseModel):
    refund_status: Optional[RefundStatus] = None
    reviewer_notes: Optional[str] = None