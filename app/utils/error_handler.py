# app/utils/error_handler.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime

from app.models.error_log import ErrorLog, ErrorType, ResolutionStatus
from app.models.manual_review import ManualReview, ReviewStatus

def handle_workflow_error(
    db: Session,
    workflow_type: str,
    entity_id: Optional[int],
    step_name: str,
    error_type: str,
    error_message: str,
    workflow_run_id: Optional[str] = None,
    is_critical: bool = False
) -> Tuple[ErrorLog, Optional[ManualReview]]:
    
    # ✅ EXPLICITLY set created_at to ensure it always works
    current_time = datetime.utcnow()

    # 1. Create Error Log
    error_log = ErrorLog(
        workflow_type=workflow_type,
        workflow_run_id=workflow_run_id or "unknown",
        step_name=step_name,
        error_type=error_type,
        error_message=error_message,
        http_status_code=500,
        resolution_status=ResolutionStatus.unresolved,
        created_at=current_time  # ✅ Manually set timestamp
    )
    db.add(error_log)
    db.flush()
    
    # 2. Create Manual Review if Critical
    manual_review = None
    
    if is_critical or error_type in ["payment_failure", "duplicate_entry", "api_failure", "database_error"]:
        manual_review = ManualReview(
            error_log_id=error_log.id,
            workflow_type=workflow_type,
            entity_id=str(entity_id) if entity_id is not None else "unknown",
            assigned_reviewer=None,
            status=ReviewStatus.pending,
            created_at=current_time  # ✅ Set timestamp for review too
        )
        db.add(manual_review)
        db.flush()
    
    # 3. Commit everything
    try:
        db.commit()
        db.refresh(error_log)
        if manual_review:
            db.refresh(manual_review)
        return error_log, manual_review
    except Exception as e:
        db.rollback()
        print(f"Error Handler Failed: {str(e)}")
        return error_log, None