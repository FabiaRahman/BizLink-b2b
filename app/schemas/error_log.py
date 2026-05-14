from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class ErrorType(str, Enum):
    validation_error = "validation_error"
    duplicate_entry = "duplicate_entry"
    api_failure = "api_failure"
    timeout = "timeout"
    payment_failure = "payment_failure" 
    database_error = "database_error"
    integration_failure = "integration_failure"
    manual_intervention_required = "manual_intervention_required"

class ResolutionStatus(str, Enum):
    unresolved = "unresolved"
    resolved = "resolved"
    ignored = "ignored"
    escalated = "escalated" 

class ErrorLogBase(BaseModel):
    workflow_type: str
    step_name: str
    error_type: ErrorType
    error_message: str
    http_status_code: Optional[int] = None

class ErrorLogCreate(ErrorLogBase):
    workflow_run_id: Optional[str] = None

class ErrorLogResponse(BaseModel):
    id: int
    workflow_type: str
    workflow_run_id: Optional[str]
    step_name: str
    error_type: str
    error_message: str
    http_status_code: Optional[int]
    resolution_status: str
    resolved_at: Optional[datetime]
    resolution_note: Optional[str]
    created_at: Optional[datetime]  

class Config:
        from_attributes = True

class ErrorLogUpdate(BaseModel):
    resolution_status: Optional[ResolutionStatus] = None
    resolution_note: Optional[str] = None