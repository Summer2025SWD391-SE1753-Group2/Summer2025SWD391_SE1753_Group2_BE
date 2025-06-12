from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.account import Account
from app.core.deps import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut, PostModeration
from app.services.post_service import (
    create_post, get_post_by_id, get_all_posts,
    update_post, delete_post, search_posts,
    search_posts_by_tag_name, search_posts_by_topic_name, get_my_posts,
    moderate_post
)
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post_endpoint(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Create a new post"""
    post_data.created_by = current_user.account_id
    return create_post(db, post_data)

@router.get("/search/", response_model=List[PostOut])
def search_posts_endpoint(
    title: str = Query(..., min_length=1, description="Search query for post title"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search posts by title"""
    return search_posts(db, title, skip=skip, limit=limit)

@router.get("/search/by-tag/", response_model=List[PostOut])
def search_posts_by_tag_endpoint(
    tag_name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search posts by tag name"""
    return search_posts_by_tag_name(db, tag_name, skip=skip, limit=limit)

@router.get("/search/by-topic/", response_model=List[PostOut])
def search_posts_by_topic_endpoint(
    topic_name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search posts by topic name"""
    return search_posts_by_topic_name(db, topic_name, skip=skip, limit=limit)
@router.get("/my-posts/", response_model=List[PostOut])
def get_my_posts_endpoint(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to return"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get all posts created by the current user"""
    return get_my_posts(db, current_user.account_id, skip=skip, limit=limit)
@router.get("/{post_id}", response_model=PostOut)
def get_post_by_id_endpoint(
    post_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific post by ID"""
    return get_post_by_id(db, post_id)

@router.get("/", response_model=List[PostOut])
def get_all_posts_endpoint(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to return"),
    db: Session = Depends(get_db)
):
    """Get all posts with pagination"""
    return get_all_posts(db, skip=skip, limit=limit)

@router.put("/{post_id}", response_model=PostOut)
def update_post_endpoint(
    post_id: UUID,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Update a post"""
    post_data.updated_by = current_user.account_id
    return update_post(db, post_id, post_data)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_endpoint(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Delete a post"""
    delete_post(db, post_id)
    return {"message": "Post deleted successfully"}

@router.put("/{post_id}/moderate", response_model=PostOut)
def moderate_post_endpoint(
    post_id: UUID,
    moderation_data: PostModeration,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Moderate a post (approve/reject)"""
    moderation_data.approved_by = current_user.account_id
    return moderate_post(db, post_id, moderation_data)