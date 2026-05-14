from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models.order import Order, PaymentStatus, WorkflowStatus
from app.schemas.order import OrderCreate, OrderResponse
from app.utils.error_handler import handle_workflow_error

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    status: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all orders with optional filtering by status
    SRS 3.1.3: The system shall expose a GET/orders endpoint returning all orders 
    with their current status, filterable by status and date range.
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.workflow_status == status)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # 1️⃣ Duplicate Order Detection (SRS 3.1.3 FR-5)
    duplicate_window = datetime.utcnow() - timedelta(days=30)
    existing = db.query(Order).filter(
        Order.customer_contact == order.customer_contact,
        Order.product_details == order.product_details,
        Order.created_at >= duplicate_window
    ).first()

    if existing:
        # ✅ For duplicate, we don't create a new order, so entity_id is the existing order
        handle_workflow_error(
            db=db, 
            workflow_type="order", 
            entity_id=existing.id,  # ✅ Use existing order ID
            step_name="duplicate_detection", 
            error_type="duplicate_entry",
            error_message=f"Duplicate order for {order.customer_contact}",
            is_critical=True
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate order detected. Workflow paused for manual review."
        )

    # 2️⃣ Payment Failure Exception (SRS 3.1.3 FR-5)
    if order.payment_status == PaymentStatus.failed:
        # FIRST: Create the order
        new_order = Order(
            customer_name=order.customer_name,
            customer_contact=order.customer_contact,
            product_details=order.product_details,
            quantity=order.quantity,
            total_price=order.total_price,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            workflow_status=WorkflowStatus.paused
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)  # ✅ Now new_order.id exists
        
        # ✅ SECOND: Call error handler WITH the order ID
        handle_workflow_error(
            db=db, 
            workflow_type="order", 
            entity_id=new_order.id,
            workflow_run_id=str(new_order.id),  # ✅ ADD THIS LINE
            step_name="payment_validation", 
            error_type="payment_failure",
            error_message="Payment failed. Workflow paused for manual approval.",
            is_critical=True
        )
        
        return new_order

    # 3️⃣ Normal Flow (SRS 3.1.3 FR-3)
    new_order = Order(
        customer_name=order.customer_name,
        customer_contact=order.customer_contact,
        product_details=order.product_details,
        quantity=order.quantity,
        total_price=order.total_price,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        workflow_status=WorkflowStatus.received
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # TODO: Add email/WhatsApp triggers here (Day 4)
    return new_order

# ✅ NEW: Endpoint to mark order as completed (for testing refund workflow)
@router.put("/{order_id}/mark-complete", response_model=OrderResponse)
def mark_order_complete(order_id: int, db: Session = Depends(get_db)):
    """
    Helper endpoint to manually mark an order as completed
    (For testing Refund workflows)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update status to completed
    order.workflow_status = WorkflowStatus.completed
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order