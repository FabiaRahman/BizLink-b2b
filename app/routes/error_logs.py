# app/routes/error_logs.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.error_log import ErrorLog, ErrorType, ResolutionStatus
from app.models.manual_review import ManualReview, ReviewStatus  # ✅ ADDED THIS IMPORT
from app.schemas.error_log import ErrorLogCreate, ErrorLogResponse

router = APIRouter(prefix="/error-logs", tags=["Error Detection & Logging"])

@router.post("/", response_model=ErrorLogResponse, status_code=201)
def create_error_log(error: ErrorLogCreate, db: Session = Depends(get_db)):
    """
    SRS 3.2.3 FR-2 & FR-7: Log error and auto-create Manual Review
    """
    db_error = ErrorLog(
        workflow_type=error.workflow_type,
        workflow_run_id=error.workflow_run_id,
        step_name=error.step_name,
        error_type=error.error_type,
        error_message=error.error_message,
        http_status_code=error.http_status_code,
        resolution_status=ResolutionStatus.unresolved
    )
    
    db.add(db_error)
    db.commit()
    db.refresh(db_error)
    
    # ✅ AUTO-CREATE MANUAL REVIEW RECORD
    manual_review = ManualReview(
        error_log_id=db_error.id,
        workflow_type=error.workflow_type,
        entity_id=error.workflow_run_id,
        status=ReviewStatus.pending
    )
    db.add(manual_review)
    db.commit()
    
    return db_error

@router.get("/", response_model=List[ErrorLogResponse])
def get_error_logs(
    workflow_type: Optional[str] = None,
    error_type: Optional[str] = None,
    resolution_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    SRS 3.2.3 FR-4: GET /error-logs with filtering
    """
    query = db.query(ErrorLog)
    
    if workflow_type:
        query = query.filter(ErrorLog.workflow_type == workflow_type)
    if error_type:
        query = query.filter(ErrorLog.error_type == error_type)
    if resolution_status:
        query = query.filter(ErrorLog.resolution_status == resolution_status)
    
    return query.offset(skip).limit(limit).all()

@router.put("/{error_id}/resolve", response_model=ErrorLogResponse)
def resolve_error(
    error_id: int,
    resolution_note: str,
    db: Session = Depends(get_db)
):
    """
    SRS 3.2.3 FR-6: Mark error as resolved
    """
    db_error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()
    if not db_error:
        raise HTTPException(status_code=404, detail="Error log not found")
    
    db_error.resolution_status = ResolutionStatus.resolved
    db_error.resolution_note = resolution_note
    db_error.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(db_error)
    
    return db_error