from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.comment import Comment, CommentStatusEnum
from app.schemas.comment import CommentCreate, CommentUpdate, CommentStatusUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_comment(db: Session, comment_data: CommentCreate) -> Comment:
    try:
        # Check if parent comment exists and get its level
        level = 1
        if comment_data.parent_comment_id:
            parent_comment = db.query(Comment).filter(
                Comment.comment_id == comment_data.parent_comment_id
            ).first()
            
            if not parent_comment:
                raise HTTPException(
                    status_code=404,
                    detail="Parent comment not found"
                )
            
            # Check nesting level
            if parent_comment.level >= 3:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum nesting level (3) exceeded"
                )
            
            level = parent_comment.level + 1

        comment = Comment(
            post_id=comment_data.post_id,
            account_id=comment_data.account_id,
            content=comment_data.content,
            parent_comment_id=comment_data.parent_comment_id,
            level=level
        )

        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def get_comment_by_id(db: Session, comment_id: int) -> Optional[Comment]:
    return db.query(Comment).filter(Comment.comment_id == comment_id).first()

def get_comments_by_post(
    db: Session, 
    post_id: int, 
    skip: int = 0, 
    limit: int = 100,
    parent_id: Optional[int] = None
) -> List[Comment]:
    query = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.status == CommentStatusEnum.active
    )
    
    if parent_id is None:
        # Get only top-level comments
        query = query.filter(Comment.parent_comment_id.is_(None))
    else:
        # Get replies to a specific comment
        query = query.filter(Comment.parent_comment_id == parent_id)
    
    return query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

def update_comment(
    db: Session, 
    comment_id: int, 
    comment_data: CommentUpdate
) -> Comment:
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    
    if comment.status != CommentStatusEnum.active:
        raise HTTPException(
            status_code=400,
            detail="Cannot update inactive comment"
        )
    
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)
    return comment

def update_comment_status(
    db: Session, 
    comment_id: int, 
    status_data: CommentStatusUpdate
) -> Comment:
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    
    comment.status = status_data.status
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id: int) -> Comment:
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    
    # Soft delete by updating status
    comment.status = CommentStatusEnum.deleted
    db.commit()
    db.refresh(comment)
    return comment

def get_nested_comments(db: Session, post_id: int) -> List[Comment]:
    """Get all comments for a post with their nested replies up to 3 levels"""
    # Get all active comments for the post
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.status == CommentStatusEnum.active
    ).order_by(Comment.created_at.desc()).all()
    
    # Create a dictionary to store comments by their ID
    comment_dict = {comment.comment_id: comment for comment in comments}
    
    # Organize comments into a tree structure
    root_comments = []
    for comment in comments:
        if comment.parent_comment_id is None:
            root_comments.append(comment)
        else:
            parent = comment_dict.get(comment.parent_comment_id)
            if parent:
                if not hasattr(parent, 'replies'):
                    parent.replies = []
                parent.replies.append(comment)
    
    return root_comments 