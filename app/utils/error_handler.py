# app/utils/error_handler.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime

from app.models.error_log import ErrorLog, ErrorType, ResolutionStatus
from app.models.manual_review import ManualReview, ReviewStatus

def handle_workflow_error(
    db: Session,
    workflow_type: str,  # "order", "refund", "lead", "email"
    entity_id: Optional[int],
    step_name: str,
    error_type: str,
    error_message: str,
    workflow_run_id: Optional[str] = None,
    is_critical: bool = False
) -> Tuple[ErrorLog, Optional[ManualReview]]:
    """
    Universal error handler for all workflows
    Creates error log and manual review if critical
    """
    
    # Create error log
    error_log = ErrorLog(
        workflow_type=workflow_type,
        workflow_run_id=workflow_run_id or "unknown",
        step_name=step_name,
        error_type=error_type,
        error_message=error_message,
        http_status_code=500,
        resolution_status=ResolutionStatus.unresolved
    )
    db.add(error_log)
    db.commit()
    db.refresh(error_log)
    
    # Create manual review for critical errors
    manual_review = None
    
    if is_critical or error_type in ["api_failure", "database_error", "integration_failure"]:
        manual_review = ManualReview(
            error_log_id=error_log.id,
            workflow_type=workflow_type,
            entity_id=str(entity_id) if entity_id else "unknown",
            status=ReviewStatus.pending
        )
        db.add(manual_review)
        db.commit()
    
    return error_log, manual_review