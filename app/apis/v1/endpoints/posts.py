from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.account import Account
from app.core.deps import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.services.post_service import (
    create_post, get_post_by_id, get_all_posts, update_post, delete_post
)
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles
router = APIRouter()
@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post_endpoint(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([
        RoleNameEnum.user_l2,
        RoleNameEnum.moderator,
        RoleNameEnum.admin
    ]))
):
    # Automatically set created_by to current user's ID
    post_data.created_by = current_user.account_id
    return await create_post(db, post_data)


@router.get("/{post_id}", response_model=PostOut)
async def get_post_by_id_endpoint(post_id: UUID, db: Session = Depends(get_db)):
    return get_post_by_id(db, post_id)


@router.get("/", response_model=List[PostOut])
async def get_all_posts_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_posts(db, skip=skip, limit=limit)


@router.put("/{post_id}", response_model=PostOut)
async def update_post_endpoint(post_id: UUID, post_data: PostUpdate, db: Session = Depends(get_db)):
    return await update_post(db, post_id, post_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(post_id: UUID, db: Session = Depends(get_db)):
    delete_post(db, post_id)
    return
