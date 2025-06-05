from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.deps import get_db
from app.schemas.tag import TagCreate, TagUpdate, TagOut
from app.services.tag_service import (
    create_tag,
    get_tag_by_id,
    get_all_tags,
    update_tag,
    delete_tag,
)

router = APIRouter()

@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag_endpoint(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
):
    dummy_user_id = tag_data.created_by or UUID("00000000-0000-0000-0000-000000000000")
    return await create_tag(db, tag_data, created_by=dummy_user_id)

@router.get("/{tag_id}", response_model=TagOut)
async def get_tag_by_id_endpoint(tag_id: UUID, db: Session = Depends(get_db)):
    tag = await get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.get("/", response_model=List[TagOut])
def get_all_tags_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_tags(db, skip=skip, limit=limit) 

@router.put("/{tag_id}", response_model=TagOut)
async def update_tag_endpoint(tag_id: UUID, tag_data: TagUpdate, db: Session = Depends(get_db)):
    tag = await get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return await update_tag(db, tag_id, tag_data)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_endpoint(tag_id: UUID, db: Session = Depends(get_db)):
    tag = await get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await delete_tag(db, tag_id)
    return
