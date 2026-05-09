# app/routes/leads.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.schemas.lead import LeadCreate, LeadResponse, LeadListResponse
from app.models.lead import Lead, LeadStatus
from app.utils.error_handler import handle_workflow_error  # ✅ UPDATED IMPORT
# from app.utils.notifications import send_slack_lead_notification  # Commented per your note

router = APIRouter(prefix="/leads", tags=["Lead Capture Workflow"])
DUPLICATE_WINDOW_DAYS = 30

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # === STEP 1: Duplicate Detection ===
    duplicate_window = datetime.utcnow() - timedelta(days=DUPLICATE_WINDOW_DAYS)
    existing = db.query(Lead).filter(
        Lead.email == lead_data.email.lower(),
        Lead.submitted_at >= duplicate_window
    ).first()
    
    if existing:
        # ✅ UPDATED: Use universal handler
        error_log, manual_review = handle_workflow_error(
            db=db,
            workflow_type="lead_capture",
            entity_id=None,
            step_name="duplicate_detection",
            error_type="duplicate_entry",
            error_message=f"Duplicate: {lead_data.email} exists within {DUPLICATE_WINDOW_DAYS} days",
            workflow_run_id=None,
            is_critical=False
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Duplicate lead submission",
                "existing_lead_id": existing.id
            }
        )
    
    # === STEP 2: Create Lead Record ===
    try:
        workflow_run_id = f"lead_{uuid.uuid4().hex[:12]}"
        
        new_lead = Lead(
            name=lead_data.name,
            company=lead_data.company,
            email=lead_data.email.lower(),
            phone=lead_data.phone,
            area_of_interest=lead_data.area_of_interest,
            source=lead_data.source,
            source_url=lead_data.source_url,
            workflow_run_id=workflow_run_id,
            status=LeadStatus.captured
        )
        
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
    except Exception as e:
        db.rollback()
        # ✅ UPDATED: Use universal handler for DB errors
        error_log, manual_review = handle_workflow_error(
            db=db,
            workflow_type="lead_capture",
            entity_id=None,
            step_name="database_insert",
            error_type="api_failure",  # or "database_error"
            error_message=f"DB error: {str(e)}",
            workflow_run_id=None,
            is_critical=True  # ✅ Critical = auto-create manual review
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lead"
        )
    
    # === STEP 3: Enrichment ===
    try:
        new_lead.status = LeadStatus.enriched
        db.commit()
    except:
        db.rollback()
    
    # === STEP 4: Slack Notification (Background) ===
    # background_tasks.add_task(...)  # Uncomment when notifications.py is ready
    
    try:
        new_lead.status = LeadStatus.notified
        db.commit()
    except:
        db.rollback()
    
    return new_lead

# ... rest of the file unchanged ...


@router.get("/", response_model=List[LeadListResponse])
def list_leads(
    status_filter: Optional[LeadStatus] = None,
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Lead)
    
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    if source:
        query = query.filter(Lead.source == source)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead