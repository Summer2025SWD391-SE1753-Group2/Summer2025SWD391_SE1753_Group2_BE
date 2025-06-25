from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from app.db.models.feedback import Feedback, FeedbackStatusEnum, FeedbackPriorityEnum
from app.db.models.feedback_type import FeedbackType, FeedbackTypeStatusEnum
from app.db.models.account import Account
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResolution, FeedbackOut, FeedbackList
from app.schemas.account import AccountSummary

def create_feedback(db: Session, feedback_data: FeedbackCreate, user_id: UUID) -> FeedbackOut:
    """Create a new feedback entry"""
    try:
        # Validate feedback type exists and is active
        feedback_type = db.query(FeedbackType).filter(
            FeedbackType.feedback_type_id == feedback_data.feedback_type_id,
            FeedbackType.status == FeedbackTypeStatusEnum.active
        ).first()
        
        if not feedback_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive feedback type"
            )

        feedback = Feedback(
            title=feedback_data.title,
            description=feedback_data.description,
            feedback_type_id=feedback_data.feedback_type_id,
            priority=feedback_data.priority,
            screenshot_url=feedback_data.screenshot_url,
            browser_info=feedback_data.browser_info,
            device_info=feedback_data.device_info,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return get_feedback_by_id(db, feedback.feedback_id)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create feedback: {str(e)}"
        )

def get_feedback_by_id(db: Session, feedback_id: UUID) -> FeedbackOut:
    """Get a specific feedback by ID with related account information"""
    feedback = db.query(Feedback).options(
        joinedload(Feedback.creator),
        joinedload(Feedback.updater),
        joinedload(Feedback.resolver),
        joinedload(Feedback.feedback_type_rel)
    ).filter(Feedback.feedback_id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    return FeedbackOut.model_validate(feedback)

def get_user_feedbacks(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> FeedbackList:
    """Get all feedbacks created by a specific user"""
    query = db.query(Feedback).options(
        joinedload(Feedback.creator),
        joinedload(Feedback.updater),
        joinedload(Feedback.resolver),
        joinedload(Feedback.feedback_type_rel)
    ).filter(Feedback.created_by == user_id)
    
    total = query.count()
    feedbacks = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    
    feedback_outs = [FeedbackOut.model_validate(feedback) for feedback in feedbacks]
    
    return FeedbackList(
        feedbacks=feedback_outs,
        total=total,
        skip=skip,
        limit=limit
    )

def get_all_feedbacks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[FeedbackStatusEnum] = None,
    type_filter: Optional[UUID] = None,
    priority_filter: Optional[FeedbackPriorityEnum] = None
) -> FeedbackList:
    """Get all feedbacks with optional filters (for moderators/admins)"""
    query = db.query(Feedback).options(
        joinedload(Feedback.creator),
        joinedload(Feedback.updater),
        joinedload(Feedback.resolver),
        joinedload(Feedback.feedback_type_rel)
    )
    
    # Apply filters
    if status_filter:
        query = query.filter(Feedback.status == status_filter)
    if type_filter:
        query = query.filter(Feedback.feedback_type_id == type_filter)
    if priority_filter:
        query = query.filter(Feedback.priority == priority_filter)
    
    total = query.count()
    feedbacks = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    
    feedback_outs = [FeedbackOut.model_validate(feedback) for feedback in feedbacks]
    
    return FeedbackList(
        feedbacks=feedback_outs,
        total=total,
        skip=skip,
        limit=limit
    )

def update_feedback(
    db: Session, 
    feedback_id: UUID, 
    feedback_data: FeedbackUpdate, 
    user_id: UUID
) -> FeedbackOut:
    """Update a feedback entry"""
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Validate feedback type if being updated
    if feedback_data.feedback_type_id:
        feedback_type = db.query(FeedbackType).filter(
            FeedbackType.feedback_type_id == feedback_data.feedback_type_id,
            FeedbackType.status == FeedbackTypeStatusEnum.active
        ).first()
        
        if not feedback_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive feedback type"
            )
    
    # Update fields
    update_data = feedback_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    feedback.updated_by = user_id
    feedback.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(feedback)
    
    return get_feedback_by_id(db, feedback_id)

def resolve_feedback(
    db: Session, 
    feedback_id: UUID, 
    resolution_data: FeedbackResolution, 
    resolver_id: UUID
) -> FeedbackOut:
    """Resolve a feedback (for moderators/admins)"""
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Update status and resolution info
    feedback.status = resolution_data.status
    feedback.resolution_note = resolution_data.resolution_note
    feedback.resolved_by = resolver_id
    feedback.resolved_at = datetime.now(timezone.utc)
    feedback.updated_by = resolver_id
    feedback.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(feedback)
    
    return get_feedback_by_id(db, feedback_id)

def delete_feedback(db: Session, feedback_id: UUID, user_id: UUID) -> bool:
    """Delete a feedback (only creator or admin can delete)"""
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Check if user is creator or admin
    user = db.query(Account).filter(Account.account_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if feedback.created_by != user_id and user.role.role_name not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin can delete this feedback"
        )
    
    db.delete(feedback)
    db.commit()
    
    return True

def get_feedback_stats(db: Session) -> dict:
    """Get feedback statistics (for dashboard)"""
    total_feedbacks = db.query(Feedback).count()
    pending_feedbacks = db.query(Feedback).filter(Feedback.status == FeedbackStatusEnum.pending).count()
    in_progress_feedbacks = db.query(Feedback).filter(Feedback.status == FeedbackStatusEnum.in_progress).count()
    resolved_feedbacks = db.query(Feedback).filter(Feedback.status == FeedbackStatusEnum.resolved).count()
    
    # Count by type
    type_stats = {}
    feedback_types = db.query(FeedbackType).filter(FeedbackType.status == FeedbackTypeStatusEnum.active).all()
    for feedback_type in feedback_types:
        count = db.query(Feedback).filter(Feedback.feedback_type_id == feedback_type.feedback_type_id).count()
        type_stats[feedback_type.name] = count
    
    # Count by priority
    priority_stats = {}
    for priority in FeedbackPriorityEnum:
        count = db.query(Feedback).filter(Feedback.priority == priority).count()
        priority_stats[priority.value] = count
    
    return {
        "total": total_feedbacks,
        "pending": pending_feedbacks,
        "in_progress": in_progress_feedbacks,
        "resolved": resolved_feedbacks,
        "by_type": type_stats,
        "by_priority": priority_stats
    } 