from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.deps import get_db
from app.schemas.topic import TopicCreate, TopicUpdate, TopicOut
from app.services.topic_service import (
    create_topic,
    get_topic_by_id,
    get_all_topics,
    update_topic,
    delete_topic,
)

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post("/", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
async def create_topic_endpoint(
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
):
    dummy_user_id = topic_data.created_by or UUID("00000000-0000-0000-0000-000000000000")
    return await create_topic(db, topic_data, created_by=dummy_user_id)


@router.get("/{topic_id}", response_model=TopicOut)
async def get_topic_by_id_endpoint(topic_id: UUID, db: Session = Depends(get_db)):
    topic = get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/", response_model=List[TopicOut])
async def get_all_topics_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_topics(db, skip=skip, limit=limit)


@router.put("/{topic_id}", response_model=TopicOut)
async def update_topic_endpoint(
    topic_id: UUID,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
):
    existing_topic = get_topic_by_id(db, topic_id)
    if not existing_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    dummy_user_id = topic_data.updated_by or UUID("00000000-0000-0000-0000-000000000000")
    return await update_topic(db, topic_id, topic_data, updated_by=dummy_user_id)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic_endpoint(topic_id: UUID, db: Session = Depends(get_db)):
    topic = get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    delete_topic(db, topic_id)
    return
