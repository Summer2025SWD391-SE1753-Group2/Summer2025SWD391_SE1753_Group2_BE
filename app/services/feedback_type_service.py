from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from app.db.models.feedback_type import FeedbackType, FeedbackTypeStatusEnum
from app.db.models.feedback import Feedback
from app.schemas.feedback_type import FeedbackTypeCreate, FeedbackTypeUpdate, FeedbackTypeOut, FeedbackTypeList

def create_feedback_type(db: Session, feedback_type_data: FeedbackTypeCreate) -> FeedbackTypeOut:
    """Create a new feedback type"""
    try:
        # Check if name already exists
        existing = db.query(FeedbackType).filter(FeedbackType.name == feedback_type_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback type name already exists"
            )
        
        feedback_type = FeedbackType(
            name=feedback_type_data.name,
            display_name=feedback_type_data.display_name,
            description=feedback_type_data.description,
            icon=feedback_type_data.icon,
            color=feedback_type_data.color,
            sort_order=feedback_type_data.sort_order,
            created_by=feedback_type_data.created_by,
            updated_by=feedback_type_data.created_by
        )
        
        db.add(feedback_type)
        db.commit()
        db.refresh(feedback_type)
        
        return get_feedback_type_by_id(db, feedback_type.feedback_type_id)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create feedback type: {str(e)}"
        )

def get_feedback_type_by_id(db: Session, feedback_type_id: UUID) -> FeedbackTypeOut:
    """Get a specific feedback type by ID"""
    feedback_type = db.query(FeedbackType).options(
        joinedload(FeedbackType.creator),
        joinedload(FeedbackType.updater)
    ).filter(FeedbackType.feedback_type_id == feedback_type_id).first()
    
    if not feedback_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback type not found"
        )
    
    return FeedbackTypeOut.model_validate(feedback_type)

def get_all_feedback_types(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None
) -> FeedbackTypeList:
    """Get all feedback types with optional filters"""
    query = db.query(FeedbackType).options(
        joinedload(FeedbackType.creator),
        joinedload(FeedbackType.updater)
    )
    
    # Apply status filter
    if status_filter:
        if status_filter == "active":
            query = query.filter(FeedbackType.status == FeedbackTypeStatusEnum.active)
        elif status_filter == "inactive":
            query = query.filter(FeedbackType.status == FeedbackTypeStatusEnum.inactive)
    
    total = query.count()
    feedback_types = query.order_by(FeedbackType.sort_order, FeedbackType.created_at).offset(skip).limit(limit).all()
    
    feedback_type_outs = [FeedbackTypeOut.model_validate(feedback_type) for feedback_type in feedback_types]
    
    return FeedbackTypeList(
        feedback_types=feedback_type_outs,
        total=total,
        skip=skip,
        limit=limit
    )

def get_active_feedback_types(db: Session) -> List[FeedbackTypeOut]:
    """Get all active feedback types (for frontend forms)"""
    feedback_types = db.query(FeedbackType).filter(
        FeedbackType.status == FeedbackTypeStatusEnum.active
    ).order_by(FeedbackType.sort_order, FeedbackType.created_at).all()
    
    return [FeedbackTypeOut.model_validate(feedback_type) for feedback_type in feedback_types]

def update_feedback_type(
    db: Session, 
    feedback_type_id: UUID, 
    feedback_type_data: FeedbackTypeUpdate
) -> FeedbackTypeOut:
    """Update a feedback type"""
    feedback_type = db.query(FeedbackType).filter(FeedbackType.feedback_type_id == feedback_type_id).first()
    
    if not feedback_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback type not found"
        )
    
    # Update fields
    update_data = feedback_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback_type, field, value)
    
    feedback_type.updated_by = feedback_type_data.updated_by
    feedback_type.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(feedback_type)
    
    return get_feedback_type_by_id(db, feedback_type_id)

def delete_feedback_type(db: Session, feedback_type_id: UUID, user_id: UUID) -> bool:
    """Delete a feedback type (cannot delete default types)"""
    feedback_type = db.query(FeedbackType).filter(FeedbackType.feedback_type_id == feedback_type_id).first()
    
    if not feedback_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback type not found"
        )
    
    # Check if it's a default type
    if feedback_type.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default feedback types"
        )
    
    # Check if there are any feedbacks using this type
    feedback_count = db.query(Feedback).filter(Feedback.feedback_type_id == feedback_type_id).count()
    if feedback_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete feedback type that has {feedback_count} associated feedbacks"
        )
    
    db.delete(feedback_type)
    db.commit()
    
    return True 