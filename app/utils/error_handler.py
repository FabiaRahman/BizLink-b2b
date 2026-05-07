from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime

from app.models.error_log import ErrorLog, ErrorType, ResolutionStatus
from app.models.manual_review import ManualReview, ReviewStatus

def handle_lead_workflow_error(
    db: Session,
    lead_id: Optional[int],
    step_name: str,
    error_type: str,
    error_message: str,
    workflow_run_id: Optional[str] = None
) -> Tuple[ErrorLog, Optional[ManualReview]]:
    """
    Specialized error handler for lead workflow
    Creates error log and manual review if critical
    Returns: (ErrorLog, ManualReview or None)
    """
    
    # Create error log
    error_log = ErrorLog(
        workflow_type="lead_capture",
        workflow_run_id=workflow_run_id,
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
    critical_types = ["api_failure", "database_error", "integration_failure"]
    manual_review = None
    
    if error_type in critical_types:
        manual_review = ManualReview(
            error_log_id=error_log.id,
            workflow_type="lead_capture",
            entity_id=str(lead_id) if lead_id else "unknown",
            status=ReviewStatus.pending
        )
        db.add(manual_review)
        db.commit()
    
    return error_log, manual_review