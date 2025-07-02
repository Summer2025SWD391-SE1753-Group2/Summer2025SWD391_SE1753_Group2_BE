from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.db.models.account import Account
from app.core.deps import get_db
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackResolution, 
    FeedbackOut, FeedbackList, FeedbackStatusEnum, 
    FeedbackPriorityEnum
)
from app.services.feedback_service import (
    create_feedback, get_feedback_by_id, get_user_feedbacks,
    get_all_feedbacks, update_feedback, resolve_feedback,
    delete_feedback, get_feedback_stats
)
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

# User endpoints (only users can create feedback)
@router.post("/", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback_endpoint(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Create a new feedback (only users can create feedback)"""
    return create_feedback(db, feedback_data, current_user.account_id)

@router.get("/my-feedbacks/", response_model=FeedbackList)
def get_my_feedbacks_endpoint(
    skip: int = Query(0, ge=0, description="Number of feedbacks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of feedbacks to return"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Get all feedbacks created by the current user (only users can view their own feedbacks)"""
    return get_user_feedbacks(db, current_user.account_id, skip=skip, limit=limit)

@router.get("/my-feedbacks/{feedback_id}", response_model=FeedbackOut)
def get_my_feedback_endpoint(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Get a specific feedback created by the current user (only users can view their own feedbacks)"""
    feedback = get_feedback_by_id(db, feedback_id)
    
    # Check if the feedback belongs to the current user
    if feedback.created_by != current_user.account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own feedbacks"
        )
    
    return feedback

# Admin/Moderator endpoints (for viewing and responding to all feedbacks)
@router.get("/all/", response_model=FeedbackList)
def get_all_feedbacks_endpoint(
    skip: int = Query(0, ge=0, description="Number of feedbacks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of feedbacks to return"),
    status_filter: Optional[FeedbackStatusEnum] = Query(None, description="Filter by status"),
    type_filter: Optional[UUID] = Query(None, description="Filter by feedback type ID"),
    priority_filter: Optional[FeedbackPriorityEnum] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get all feedbacks with optional filters (moderator/admin only)"""
    return get_all_feedbacks(
        db, skip=skip, limit=limit, 
        status_filter=status_filter, 
        type_filter=type_filter, 
        priority_filter=priority_filter
    )

@router.get("/all/{feedback_id}", response_model=FeedbackOut)
def get_feedback_by_id_endpoint(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get a specific feedback by ID (moderator/admin only)"""
    return get_feedback_by_id(db, feedback_id)

@router.put("/all/{feedback_id}/resolve", response_model=FeedbackOut)
def resolve_feedback_endpoint(
    feedback_id: UUID,
    resolution_data: FeedbackResolution,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Resolve a feedback (moderator/admin only)"""
    return resolve_feedback(db, feedback_id, resolution_data, current_user.account_id)

@router.delete("/all/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_endpoint(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Delete any feedback (admin only)"""
    delete_feedback(db, feedback_id, current_user.account_id)
    return {"message": "Feedback deleted successfully"}

# Statistics endpoint (for dashboard)
@router.get("/stats/")
def get_feedback_stats_endpoint(
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get feedback statistics for dashboard (moderator/admin only)"""
    return get_feedback_stats(db) 