# app/models/manual_review.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base  # ← CRITICAL: Shared Base import

class ReviewStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(Integer, primary_key=True, index=True)
    error_log_id = Column(Integer, ForeignKey("error_logs.id"), nullable=False, unique=True)
    workflow_type = Column(String, nullable=False)  # "order", "refund", "lead", "email"
    entity_id = Column(String, nullable=False)      # The specific Order/Refund ID involved
    assigned_reviewer = Column(String, nullable=True)
    status = Column(SAEnum(ReviewStatus), default=ReviewStatus.pending)
    reviewer_notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Bidirectional relationship to ErrorLog
    error_log = relationship("ErrorLog", back_populates="manual_review")