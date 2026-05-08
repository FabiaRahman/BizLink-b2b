from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.order import Order
from app.models.lead import Lead
from app.models.refund import Refund
from app.models.error_log import ErrorLog
from app.models.manual_review import ManualReview
from app.schemas.dashboard import (
    AdminStats, OperationsStats, ITStats,
    RecentActivityResponse, ActivityItem, WorkflowStatusResponse
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_today_start():
    now = datetime.now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)

@router.get("/stats", response_model=AdminStats | OperationsStats | ITStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today_start = get_today_start()
    active_statuses = ["received", "processing", "enriched", "pending", "notified"]

    # Triggers today
    triggers_today = (
        db.query(func.count(Order.id)).filter(Order.created_at >= today_start).scalar() or 0
    ) + (
        db.query(func.count(Lead.id)).filter(Lead.submitted_at >= today_start).scalar() or 0
    ) + (
        db.query(func.count(Refund.id)).filter(Refund.requested_at >= today_start).scalar() or 0
    )

    errors_today = db.query(func.count(ErrorLog.id)).filter(
        ErrorLog.created_at >= today_start
    ).scalar() or 0

    error_rate = (errors_today / triggers_today * 100) if triggers_today > 0 else 0.0

    active_workflows = (
        db.query(func.count(Order.id)).filter(Order.workflow_status.in_(active_statuses)).scalar() or 0
    ) + (
        db.query(func.count(Lead.id)).filter(Lead.status.in_(active_statuses)).scalar() or 0
    ) + (
        db.query(func.count(Refund.id)).filter(Refund.refund_status.in_(active_statuses)).scalar() or 0
    )

    base_data = {
        "active_workflows": active_workflows,
        "triggers_today": triggers_today,
        "actions_executed": triggers_today - errors_today,
        "error_rate": round(error_rate, 2)
    }

    if current_user.role == "admin":
        pending_reviews = db.query(func.count(ManualReview.id)).filter(
            ManualReview.status == "pending"
        ).scalar() or 0
        return AdminStats(
            **base_data,
            system_health="Optimal",
            total_users=db.query(func.count(User.id)).scalar() or 0,
            pending_reviews=pending_reviews
        )
    elif current_user.role in ["operations", "manager"]:
        pending_reviews = db.query(func.count(ManualReview.id)).filter(
            ManualReview.status == "pending"
        ).scalar() or 0
        return OperationsStats(
            **base_data,
            pending_manual_reviews=pending_reviews,
            my_assigned_tasks=0
        )
    elif current_user.role == "it":
        api_failures = db.query(func.count(ErrorLog.id)).filter(
            ErrorLog.created_at >= today_start,
            ErrorLog.error_type == "api_failure"
        ).scalar() or 0
        return ITStats(
            **base_data,
            error_logs_today=errors_today,
            api_failures=api_failures
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Role '{current_user.role}' not authorized for dashboard access"
    )

@router.get("/recent-activity", response_model=RecentActivityResponse)
async def get_recent_activity(db: Session = Depends(get_db)):
    activities = []
    errors = db.query(ErrorLog).order_by(ErrorLog.created_at.desc()).limit(5).all()
    for err in errors:
        activities.append(ActivityItem(
            timestamp=err.created_at,
            status="failed",
            workflow_type=err.workflow_type,
            action=f"{err.step_name}: {err.error_type}",
            duration_ms=None
        ))
    reviews = db.query(ManualReview).filter(
        ManualReview.status == "pending"
    ).order_by(ManualReview.created_at.desc()).limit(5).all()
    for rev in reviews:
        activities.append(ActivityItem(
            timestamp=rev.created_at,
            status="pending",
            workflow_type=rev.workflow_type,
            action=f"Review Required: {rev.entity_id}",
            duration_ms=None
        ))
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    return RecentActivityResponse(activities=activities[:10])

@router.get("/workflow-status/{w_type}/{record_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(w_type: str, record_id: int, db: Session = Depends(get_db)):
    if w_type == "order":
        rec = db.query(Order).filter(Order.id == record_id).first()
        if not rec: raise HTTPException(404, "Order not found")
        return WorkflowStatusResponse(id=rec.id, type="order", current_status=rec.workflow_status, last_updated=rec.created_at)
    elif w_type == "lead":
        rec = db.query(Lead).filter(Lead.id == record_id).first()
        if not rec: raise HTTPException(404, "Lead not found")
        return WorkflowStatusResponse(id=rec.id, type="lead", current_status=rec.status, last_updated=rec.submitted_at)
    elif w_type == "refund":
        rec = db.query(Refund).filter(Refund.id == record_id).first()
        if not rec: raise HTTPException(404, "Refund not found")
        return WorkflowStatusResponse(id=rec.id, type="refund", current_status=rec.refund_status, last_updated=rec.requested_at)
    raise HTTPException(400, "Invalid workflow_type. Use: order, lead, or refund")