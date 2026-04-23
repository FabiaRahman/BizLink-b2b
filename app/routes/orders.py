# app/routes/orders.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.order import Order, PaymentStatus, WorkflowStatus
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(
        customer_name=order.customer_name,
        customer_contact=order.customer_contact,
        product_details=order.product_details,
        quantity=order.quantity,
        total_price=order.total_price,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        workflow_status=WorkflowStatus.received
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    status: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.workflow_status == status)
    return query.all()

# ✅ ADD THIS NEW ENDPOINT
@router.put("/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: WorkflowStatus,
    db: Session = Depends(get_db)
):
    """Update order workflow status (e.g., mark as completed for refund testing)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.workflow_status = status
    db.commit()
    db.refresh(db_order)
    return db_order