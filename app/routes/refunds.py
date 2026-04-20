from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Order, Refund
from app.schemas import RefundCreate, RefundResponse

router = APIRouter(prefix="/refunds", tags=["Refund Workflow"])

# SRS 3.3.3 FR-2: Configurable refund window (e.g., 30 days)
REFUND_WINDOW_DAYS = 30

@router.post("/", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
def request_refund(refund_data: RefundCreate, db: Session = Depends(get_db)):
    """
    SRS 3.3.3 FR-1: Capture refund request via POST /refunds
    """
    # 1. Verify Order Exists
    order = db.query(Order).filter(Order.id == refund_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. Validate Order Status (must be completed)
    if order.workflow_status != "completed":
        raise HTTPException(status_code=400, detail="Refund only allowed for completed orders")

    # 3. Validate Refund Amount (cannot exceed order total)
    if refund_data.refund_amount > order.total_price:
        raise HTTPException(status_code=400, detail="Refund amount cannot exceed order total")

    # 4. Validate Refund Time Window
    days_since_order = (datetime.utcnow() - order.created_at).days
    if days_since_order > REFUND_WINDOW_DAYS:
        raise HTTPException(status_code=400, detail="Refund request expired")

    # 5. Prevent Duplicate Refunds (SRS 3.3.3 FR-3)
    existing = db.query(Refund).filter(Refund.order_id == refund_data.order_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Refund already requested for this order")

    # 6. Create Refund Record
    # SRS 3.3.3 FR-4: Automatically approve refunds that pass all policy validations
    new_refund = Refund(
        order_id=refund_data.order_id,
        customer_contact=refund_data.customer_contact,
        refund_amount=refund_data.refund_amount,
        refund_reason=refund_data.refund_reason,
        refund_status="approved",  # Auto-approved per SRS 3.3.3 FR-4
        requested_at=datetime.utcnow(),
        approved_at=datetime.utcnow()
    )

    db.add(new_refund)
    db.commit()
    db.refresh(new_refund)

    # TODO: SRS 3.3.3 FR-6 → Trigger customer email notification here
    return new_refund

@router.get("/", response_model=List[RefundResponse])
def get_refunds(
    status_filter: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    SRS 3.3.3 FR-7: GET /refunds filterable by status, date range, and order ID
    """
    query = db.query(Refund)
    if status_filter:
        query = query.filter(Refund.refund_status == status_filter)
        
    return query.offset(skip).limit(limit).all()