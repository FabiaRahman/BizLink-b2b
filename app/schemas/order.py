# app/schemas/order.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.order import PaymentStatus, WorkflowStatus

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_contact: str
    product_details: str
    quantity: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    payment_method: str  # ← Required field
    payment_status: PaymentStatus = PaymentStatus.pending

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_contact: str
    product_details: str
    quantity: int
    total_price: float
    payment_method: str
    payment_status: PaymentStatus
    workflow_status: WorkflowStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True