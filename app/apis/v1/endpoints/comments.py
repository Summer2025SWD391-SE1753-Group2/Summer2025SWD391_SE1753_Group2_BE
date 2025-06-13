from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_account
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    Comment,
    CommentStatusUpdate
)
from app.services.comment import CommentService
from app.db.models.account import Account
from app.db.models.role import RoleNameEnum
from typing import List

router = APIRouter()

@router.post("/", response_model=Comment)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account)
):
    """
    Create new comment.
    Only users with role user or higher can create comments.
    """
    # Check if user has permission to comment
    if current_user.role.role_name not in [RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(
            status_code=403,
            detail="Only users with role 'user' or higher can create comments"
        )
    
    return CommentService.create_comment(db, comment, current_user.account_id)

@router.get("/{comment_id}", response_model=Comment)
def get_comment(
    comment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get comment by ID.
    """
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    return comment

@router.get("/post/{post_id}", response_model=List[Comment])
def get_comments_by_post(
    post_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get comments for a post.
    If parent_id is provided, returns replies to that comment.
    Otherwise returns top-level comments.
    """
    return CommentService.get_comments_by_post(db, post_id, skip, limit)

@router.get("/post/{post_id}/nested", response_model=List[Comment])
def get_nested_comments(
    post_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all comments for a post with their nested replies up to 3 levels.
    """
    return CommentService.get_nested_comments(db, post_id)

@router.put("/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: str,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account)
):
    """
    Update comment.
    Only the comment owner can update their comment.
    """
    db_comment = CommentService.get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    if db_comment.account_id != current_user.account_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return CommentService.update_comment(db, comment_id, comment)

@router.put("/{comment_id}/status", response_model=Comment)
def update_comment_status(
    comment_id: str,
    status: CommentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account)
):
    """
    Update comment status.
    Only moderators and admins can update comment status.
    """
    if current_user.role.role_name not in [RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    db_comment = CommentService.get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    if db_comment.account_id != current_user.account_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return CommentService.update_comment(db, comment_id, status)

@router.delete("/{comment_id}", response_model=Comment)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account)
):
    """
    Delete comment.
    Only the comment owner, moderators, and admins can delete comments.
    """
    db_comment = CommentService.get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    if db_comment.account_id != current_user.account_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return CommentService.delete_comment(db, comment_id) 