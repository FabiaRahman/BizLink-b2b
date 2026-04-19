from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class OrderStatus(str, enum.Enum):
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
    payment_status = Column(String, default="pending")
    workflow_status = Column(Enum(OrderStatus), default=OrderStatus.received)
    created_at = Column(DateTime(timezone=True), server_default=func.now())