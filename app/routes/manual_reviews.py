# app/routes/manual_reviews.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.manual_review import ManualReview, ReviewStatus
from app.models.error_log import ErrorLog, ResolutionStatus
from app.schemas.manual_review import ManualReviewResponse, ReviewAction

router = APIRouter(prefix="/manual-reviews", tags=["Manual Review & Approval"])

@router.get("/", response_model=List[ManualReviewResponse])
def get_manual_reviews(
    workflow_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    SRS 3.2.3 FR-8: GET /manual-reviews with filtering
    """
    query = db.query(ManualReview)
    
    if workflow_type:
        query = query.filter(ManualReview.workflow_type == workflow_type)
    if status:
        query = query.filter(ManualReview.status == status)
        
    return query.offset(skip).limit(limit).all()

@router.post("/{review_id}/approve", response_model=ManualReviewResponse)
def approve_review(
    review_id: int,
    action: ReviewAction,
    db: Session = Depends(get_db)
):
    """
    SRS 3.2.3 FR-9 & FR-11: Approve review and resume workflow
    """
    db_review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if db_review.status != ReviewStatus.pending:
        raise HTTPException(status_code=400, detail="Review is already processed")

    # Update Review
    db_review.status = ReviewStatus.approved
    db_review.reviewer_notes = action.reviewer_notes
    db_review.resolved_at = datetime.utcnow()
    
    # Update linked Error Log (SRS 3.2.3 FR-10)
    db_error = db.query(ErrorLog).filter(ErrorLog.id == db_review.error_log_id).first()
    if db_error:
        db_error.resolution_status = ResolutionStatus.resolved
        db_error.resolution_note = f"Approved by reviewer: {action.reviewer_notes}"
        db_error.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_review)
    return db_review

@router.post("/{review_id}/reject", response_model=ManualReviewResponse)
def reject_review(
    review_id: int,
    action: ReviewAction,
    db: Session = Depends(get_db)
):
    """
    SRS 3.2.3 FR-12: Reject review (Escalates error)
    """
    db_review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.status != ReviewStatus.pending:
        raise HTTPException(status_code=400, detail="Review is already processed")

    # Update Review
    db_review.status = ReviewStatus.rejected
    db_review.reviewer_notes = action.reviewer_notes
    db_review.resolved_at = datetime.utcnow()

    # Update linked Error Log
    db_error = db.query(ErrorLog).filter(ErrorLog.id == db_review.error_log_id).first()
    if db_error:
        db_error.resolution_status = ResolutionStatus.escalated
        db_error.resolution_note = f"Rejected by reviewer: {action.reviewer_notes}"
        db_error.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(db_review)
    return db_review