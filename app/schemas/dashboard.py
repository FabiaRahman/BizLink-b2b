from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal

# Base stats shared by all roles
class DashboardStatsBase(BaseModel):
    active_workflows: int = Field(0)
    triggers_today: int = Field(0)
    actions_executed: int = Field(0)
    error_rate: float = Field(0.0)

# Admin view (SRS 3.4.1)
class AdminStats(DashboardStatsBase):
    view_type: Literal["admin"] = "admin"
    system_health: str = "Optimal"
    total_users: int = 0
    pending_reviews: int = 0

# Operations view (SRS 3.4.2)
class OperationsStats(DashboardStatsBase):
    view_type: Literal["operations"] = "operations"
    pending_manual_reviews: int = 0
    my_assigned_tasks: int = 0

# IT view (SRS 3.4.3)
class ITStats(DashboardStatsBase):
    view_type: Literal["it"] = "it"
    error_logs_today: int = 0
    api_failures: int = 0
    active_integrations: List[str] = ["Gmail/SMTP", "WhatsApp Business", "Slack", "Google Sheets"]

# Recent Activity
class ActivityItem(BaseModel):
    timestamp: datetime
    status: Literal["success", "failed", "pending"]
    workflow_type: str
    action: str
    duration_ms: Optional[int] = None

class RecentActivityResponse(BaseModel):
    activities: List[ActivityItem]

# Workflow State Tracking (SRS 3.1.3)
class WorkflowStatusResponse(BaseModel):
    id: int
    type: Literal["order", "lead", "refund"]
    current_status: str
    last_updated: datetime