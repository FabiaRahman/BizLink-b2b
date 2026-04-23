# app/models/order.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

# ✅ CRITICAL: Import Base from database.py
from app.database import Base

class PaymentStatus(str, PyEnum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"

class WorkflowStatus(str, PyEnum):
    received = "received"
    processing = "processing"
    notified = "notified"
    paused = "paused"
    manual_review = "manual_review"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_contact = Column(String, nullable=False)
    product_details = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # ← This was missing!
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.pending)
    workflow_status = Column(SAEnum(WorkflowStatus), default=WorkflowStatus.received)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Refund
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")