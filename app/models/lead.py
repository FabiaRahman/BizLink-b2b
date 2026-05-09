from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Text
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base

class LeadStatus(str, PyEnum):
    captured = "captured"
    enriched = "enriched"
    notified = "notified"
    converted = "converted"

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, index=True)  # Already exists, verify it has index=True
    phone = Column(String(50), nullable=True)
    area_of_interest = Column(String(255), nullable=True)
    source = Column(String(100), nullable=False)
    
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    source_url = Column(Text, nullable=True)
    workflow_run_id = Column(String(100), nullable=True, index=True)
    
    status = Column(SAEnum(LeadStatus), default=LeadStatus.captured, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    converted_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Lead(id={self.id}, email={self.email}, status={self.status})>"