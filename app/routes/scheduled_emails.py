from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.database import get_db
from app.models.scheduled_email import ScheduledEmail
from app.models.error_log import ErrorLog, ErrorType, ResolutionStatus
from app.models.manual_review import ManualReview, ReviewStatus
from app.schemas.scheduled_email import ScheduledEmailCreate, ScheduledEmailResponse

router = APIRouter(prefix="/scheduled-emails", tags=["Scheduled Email Workflow"])

# ✅ SIMULATION MODE: Set to True for demo/testing, False for production
SIMULATION_MODE = True

# ⚠️ NOTE: In production, load these from .env variables
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"


def send_email_simulation(to_email: str, subject: str, body: str, recipient_name: str):
    """
    Simulates email sending for demo purposes.
    Logs what WOULD have been sent without actually sending.
    """
    print(f"\n📧 [SIMULATION MODE] Would send email:")
    print(f"   To: {recipient_name} <{to_email}>")
    print(f"   Subject: {subject}")
    print(f"   Body preview: {body[:100]}...")
    print(f"   Time: {datetime.utcnow().isoformat()}\n")
    # Always "succeeds" in simulation mode
    return {"status": "success", "simulated": True}


def send_email_via_smtp(to_email: str, subject: str, body: str, recipient_name: str):
    """
    Helper function to send email via Gmail/SMTP (REAL sending)
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
   
    # Support {{name}} template replacement
    personalized_body = body.replace("{{name}}", recipient_name)
    msg.attach(MIMEText(personalized_body, 'html' if '<' in body else 'plain'))
   
    # Connect & send
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()


@router.post("/", response_model=ScheduledEmailResponse, status_code=201)
def create_scheduled_email(email: ScheduledEmailCreate, db: Session = Depends(get_db)):
    """
    SRS 3.3.3 FR-9: Create a scheduled email entry
    """
    db_email = ScheduledEmail(
        recipient_name=email.recipient_name,
        recipient_email=email.recipient_email,
        send_date=email.send_date,
        email_subject=email.email_subject,
        email_body=email.email_body,
        sent_status=False
    )
   
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email


@router.get("/", response_model=List[ScheduledEmailResponse])
def get_scheduled_emails(
    status_filter: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    SRS 3.3.3 FR-9: GET /scheduled-emails with filtering
    """
    query = db.query(ScheduledEmail)
   
    if status_filter is not None:
        query = query.filter(ScheduledEmail.sent_status == status_filter)
   
    return query.offset(skip).limit(limit).all()


@router.post("/send-due-emails")
def send_due_emails(db: Session = Depends(get_db)):
    """
    SRS 3.3.3 FR-9: Process & send emails due today.
    On failure: creates ErrorLog + auto-creates ManualReview (SRS 3.2.3 FR-7)
    
    ✅ SIMULATION MODE: When SIMULATION_MODE=True, emails are "sent" without real SMTP calls.
    """
    today = date.today()
   
    # Find emails due today that haven't been sent
    due_emails = db.query(ScheduledEmail).filter(
        ScheduledEmail.send_date >= datetime.combine(today, datetime.min.time()),
        ScheduledEmail.send_date < datetime.combine(today, datetime.max.time()),
        ScheduledEmail.sent_status == False
    ).all()
   
    sent_count = 0
    failed_count = 0
   
    for email_task in due_emails:
        try:
            # ✅ Choose simulation or real sending based on flag
            if SIMULATION_MODE:
                send_email_simulation(
                    to_email=email_task.recipient_email,
                    subject=email_task.email_subject,
                    body=email_task.email_body,
                    recipient_name=email_task.recipient_name
                )
            else:
                send_email_via_smtp(
                    to_email=email_task.recipient_email,
                    subject=email_task.email_subject,
                    body=email_task.email_body,
                    recipient_name=email_task.recipient_name
                )
           
            # Mark as successfully sent
            email_task.sent_status = True
            email_task.sent_at = datetime.utcnow()
            email_task.error_message = None
            sent_count += 1
           
        except Exception as e:
            # Mark task as failed
            email_task.error_message = str(e)
            failed_count += 1
           
            # 1️⃣ Create Error Log
            error_log = ErrorLog(
                workflow_type="scheduled_email",
                workflow_run_id=email_task.workflow_run_id or f"email_{email_task.id}",
                step_name="email_dispatch",
                error_type=ErrorType.api_failure,
                error_message=f"Failed to send email to {email_task.recipient_email}: {str(e)}",
                http_status_code=500,
                resolution_status=ResolutionStatus.unresolved
            )
            db.add(error_log)
            db.commit()
            db.refresh(error_log)
           
            # 2️⃣ Auto-Create Manual Review (SRS 3.2.3 FR-7)
            manual_review = ManualReview(
                error_log_id=error_log.id,
                workflow_type="scheduled_email",
                entity_id=f"email_{email_task.id}",
                status=ReviewStatus.pending
            )
            db.add(manual_review)
            db.commit()
       
        # Commit email task status changes
        db.commit()
   
    mode_text = "[SIMULATION]" if SIMULATION_MODE else "[LIVE]"
    return {
        "message": f"{mode_text} Processed {len(due_emails)} emails",
        "sent": sent_count,
        "failed": failed_count,
        "simulation_mode": SIMULATION_MODE
    }