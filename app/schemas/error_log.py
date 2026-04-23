# app/schemas/error_log.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ErrorType(str, Enum):
    validation_error = "validation_error"
    duplicate_entry = "duplicate_entry"
    api_failure = "api_failure"
    timeout = "timeout"
    manual_intervention_required = "manual_intervention_required"

class ResolutionStatus(str, Enum):
    unresolved = "unresolved"
    resolved = "resolved"
    escalated = "escalated"

class ErrorLogCreate(BaseModel):
    workflow_type: str
    workflow_run_id: str
    step_name: str
    error_type: ErrorType
    error_message: str
    http_status_code: Optional[int] = None

class ErrorLogResponse(BaseModel):
    id: int
    workflow_type: str
    workflow_run_id: str
    step_name: str
    error_type: ErrorType
    error_message: str
    http_status_code: Optional[int]
    resolution_status: ResolutionStatus
    resolution_note: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True