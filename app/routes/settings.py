from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["Settings"])

# ✅ শুধু Admin access  পারবে
@router.get("/workflow-rules")
async def get_workflow_rules(
    current_user: User = Depends(require_role(["admin"]))
):
    return {"message": "Workflow rules", "user": current_user.username}

# ✅ Admin + Manager access করতে পারবে
@router.get("/integrations")
async def get_integrations(
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    return {"integrations": [...]}

# ✅ সবাই (Admin + Manager + Operator) access করতে পারবে
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return {"profile": current_user}