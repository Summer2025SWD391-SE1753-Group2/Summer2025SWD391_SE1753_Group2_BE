from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.db.models.account import Account
from app.core.deps import get_db
from app.schemas.feedback_type import (
    FeedbackTypeCreate, FeedbackTypeUpdate, FeedbackTypeOut, FeedbackTypeList
)
from app.services.feedback_type_service import (
    create_feedback_type, get_feedback_type_by_id, get_all_feedback_types,
    update_feedback_type, delete_feedback_type, get_active_feedback_types
)
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

# Public endpoint (for getting active feedback types)
@router.get("/active/", response_model=list[FeedbackTypeOut])
def get_active_feedback_types_endpoint(
    db: Session = Depends(get_db)
):
    """Get all active feedback types (public endpoint for frontend forms)"""
    return get_active_feedback_types(db)

# Admin endpoints (for managing feedback types)
@router.post("/", response_model=FeedbackTypeOut, status_code=status.HTTP_201_CREATED)
def create_feedback_type_endpoint(
    feedback_type_data: FeedbackTypeCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Create a new feedback type (admin only)"""
    feedback_type_data.created_by = current_user.account_id
    return create_feedback_type(db, feedback_type_data)

@router.get("/", response_model=FeedbackTypeList)
def get_all_feedback_types_endpoint(
    skip: int = Query(0, ge=0, description="Number of feedback types to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of feedback types to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Get all feedback types with optional filters (admin only)"""
    return get_all_feedback_types(db, skip=skip, limit=limit, status_filter=status_filter)

@router.get("/{feedback_type_id}", response_model=FeedbackTypeOut)
def get_feedback_type_by_id_endpoint(
    feedback_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Get a specific feedback type by ID (admin only)"""
    return get_feedback_type_by_id(db, feedback_type_id)

@router.put("/{feedback_type_id}", response_model=FeedbackTypeOut)
def update_feedback_type_endpoint(
    feedback_type_id: UUID,
    feedback_type_data: FeedbackTypeUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Update a feedback type (admin only)"""
    feedback_type_data.updated_by = current_user.account_id
    return update_feedback_type(db, feedback_type_id, feedback_type_data)

@router.delete("/{feedback_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_type_endpoint(
    feedback_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Delete a feedback type (admin only, cannot delete default types)"""
    delete_feedback_type(db, feedback_type_id, current_user.account_id)
    return {"message": "Feedback type deleted successfully"} 