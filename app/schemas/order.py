from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_contact: str
    product_details: str
    quantity: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_contact: str
    product_details: str
    quantity: int
    total_price: float
    payment_status: str
    workflow_status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True