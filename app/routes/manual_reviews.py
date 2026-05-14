# app/routes/manual_reviews.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.manual_review import ManualReview, ReviewStatus
from app.models.order import Order, WorkflowStatus
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
    query = db.query(ManualReview)
    if workflow_type:
        query = query.filter(ManualReview.workflow_type == workflow_type)
    if status:
        query = query.filter(ManualReview.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{review_id}", response_model=ManualReviewResponse)
def get_manual_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    db_review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@router.post("/{review_id}/approve", response_model=ManualReviewResponse)
def approve_review(
    review_id: int,
    action: ReviewAction,
    db: Session = Depends(get_db)
):
    # 1. Get the review
    db_review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if db_review.status != ReviewStatus.pending:
        raise HTTPException(status_code=400, detail="Review is already processed")

    # 2. Update Review
    db_review.status = ReviewStatus.approved
    db_review.reviewer_notes = action.reviewer_notes
    db_review.resolved_at = datetime.utcnow()
    
    # 3. ✅ FIX: Resume the linked workflow (Order)
    if db_review.workflow_type == "order" and db_review.entity_id and db_review.entity_id != "unknown":
        try:
            order_id = int(db_review.entity_id)
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                # ✅ Change workflow status from paused to received (resume)
                order.workflow_status = WorkflowStatus.received
                order.updated_at = datetime.utcnow()
                db.add(order)
        except (ValueError, TypeError) as e:
            print(f"Could not update order: {str(e)}")
    
    # 4. Update linked Error Log
    db_error = db.query(ErrorLog).filter(ErrorLog.id == db_review.error_log_id).first()
    if db_error:
        db_error.resolution_status = ResolutionStatus.resolved
        db_error.resolution_note = f"Approved by reviewer: {action.reviewer_notes}"
        db_error.resolved_at = datetime.utcnow()
        db.add(db_error)
    
    # 5. Commit all changes
    db.commit()
    db.refresh(db_review)
    return db_review

@router.post("/{review_id}/reject", response_model=ManualReviewResponse)
def reject_review(
    review_id: int,
    action: ReviewAction,
    db: Session = Depends(get_db)
):
    # 1. Get the review
    db_review = db.query(ManualReview).filter(ManualReview.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.status != ReviewStatus.pending:
        raise HTTPException(status_code=400, detail="Review is already processed")

    # 2. Update Review
    db_review.status = ReviewStatus.rejected
    db_review.reviewer_notes = action.reviewer_notes
    db_review.resolved_at = datetime.utcnow()

    # 3. ✅ FIX: Cancel the linked workflow (Order)
    if db_review.workflow_type == "order" and db_review.entity_id and db_review.entity_id != "unknown":
        try:
            order_id = int(db_review.entity_id)
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                # ✅ Change workflow status to cancelled
                order.workflow_status = WorkflowStatus.cancelled
                order.updated_at = datetime.utcnow()
                db.add(order)
        except (ValueError, TypeError) as e:
            print(f"Could not update order: {str(e)}")

    # Update linked Error Log
    db_error = db.query(ErrorLog).filter(ErrorLog.id == db_review.error_log_id).first()
    if db_error:
        db_error.resolution_status = ResolutionStatus.escalated  # ✅ CHANGE THIS
        db_error.resolution_note = f"Rejected by reviewer: {action.reviewer_notes}"
        db_error.resolved_at = datetime.utcnow()
        db.add(db_error)

    # 5. Commit all changes
    db.commit()
    db.refresh(db_review)
    return db_review