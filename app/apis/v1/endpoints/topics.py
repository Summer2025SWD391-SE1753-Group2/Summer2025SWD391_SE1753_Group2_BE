from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.account import Account
from app.apis.v1.endpoints.check_role import get_current_user
from app.core.deps import get_db
from app.schemas.topic import TopicCreate, TopicUpdate, TopicOut, TopicListResponse
from app.services.topic_service import (
    create_topic,
    get_topic_by_id,
    get_all_topics,
    update_topic,
    delete_topic,
)

router = APIRouter()


@router.post("/", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic_endpoint(
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    return create_topic(db, topic_data, created_by=current_user.account_id)

@router.get("/{topic_id}", response_model=TopicOut)
def get_topic_by_id_endpoint(
    topic_id: UUID, 
    db: Session = Depends(get_db)
):
    topic = get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/", response_model=TopicListResponse)
def get_all_topics_endpoint(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return get_all_topics(db, skip=skip, limit=limit)

@router.put("/{topic_id}", response_model=TopicOut)
def update_topic_endpoint(
    topic_id: UUID,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    topic = get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return update_topic(db, topic_id, topic_data, updated_by=current_user.account_id)

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic_endpoint(
    topic_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    topic = get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    delete_topic(db, topic_id)
    return
