# app/models/error_log.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship  # ← Keep this import for future use
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

class ErrorType(str, PyEnum):
    validation_error = "validation_error"
    duplicate_entry = "duplicate_entry"
    api_failure = "api_failure"
    timeout = "timeout"
    manual_intervention_required = "manual_intervention_required"

class ResolutionStatus(str, PyEnum):
    unresolved = "unresolved"
    resolved = "resolved"
    escalated = "escalated"

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_type = Column(String, nullable=False)
    workflow_run_id = Column(String, nullable=False, index=True)
    step_name = Column(String, nullable=False)
    error_type = Column(SAEnum(ErrorType), nullable=False)
    error_message = Column(String, nullable=False)
    http_status_code = Column(Integer, nullable=True)
    resolution_status = Column(SAEnum(ResolutionStatus), default=ResolutionStatus.unresolved)
    resolution_note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # ⚠️ COMMENT OUT THIS LINE FOR NOW - ManualReview not implemented yet
    # manual_review = relationship("ManualReview", back_populates="error_log", uselist=False)