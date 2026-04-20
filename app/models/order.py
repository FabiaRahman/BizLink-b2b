from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

class OrderStatus(PyEnum):
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
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    payment_status = Column(String, default="pending")
    workflow_status = Column(Enum(OrderStatus), default=OrderStatus.received)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    # ← Bidirectional relationship to Refund
    refunds = relationship("Refund", back_populates="order")