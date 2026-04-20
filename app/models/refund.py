from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

class RefundStatus(PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    processing = "processing"
    completed = "completed"

class RefundReason(PyEnum):
    defective_product = "defective_product"
    wrong_item = "wrong_item"
    not_as_described = "not_as_described"
    customer_changed_mind = "customer_changed_mind"
    duplicate_order = "duplicate_order"
    other = "other"

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_contact = Column(String, nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_reason = Column(Enum(RefundReason), nullable=False)
    refund_status = Column(Enum(RefundStatus), default=RefundStatus.pending)
    policy_violation = Column(String, nullable=True)
    reviewer_notes = Column(String, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)

    # Bidirectional relationship to Order
    order = relationship("Order", back_populates="refunds")