from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.account import Account
from app.core.deps import get_db
from app.apis.v1.endpoints.check_role import get_current_user  # Add this import

from app.schemas.tag import TagCreate, TagUpdate, TagOut, TagListResponse
from app.services.tag_service import (
    create_tag,
    get_tag_by_id,
    get_all_tags,
    update_tag,
    delete_tag,
)

router = APIRouter()
@router.post("/", response_model=TagOut)
def create_tag_endpoint(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
):
    dummy_user_id = tag_data.created_by or UUID("00000000-0000-0000-0000-000000000000")
    return create_tag(db, tag_data, created_by=dummy_user_id)

@router.get("/{tag_id}", response_model=TagOut)
def get_tag_by_id_endpoint(tag_id: UUID, db: Session = Depends(get_db)):
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.get("/", response_model=TagListResponse)
def get_all_tags_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_tags(db, skip=skip, limit=limit) 

@router.put("/{tag_id}", response_model=TagOut)
def update_tag_endpoint(
    tag_id: UUID,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)  # Add authentication
):
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Use the authenticated user's ID
    return update_tag(db, tag_id, tag_data, updated_by=current_user.account_id)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_endpoint(tag_id: UUID, db: Session = Depends(get_db)):
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    delete_tag(db, tag_id)
    return
