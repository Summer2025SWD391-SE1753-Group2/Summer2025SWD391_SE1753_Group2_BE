from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timezone

from app.db.models.topic import Topic, TopicStatusEnum
from app.schemas.topic import TopicCreate, TopicUpdate, TopicListResponse


def check_topic_name_unique(db: Session, name: str):
    existing_topic = db.execute(
        text("SELECT 1 FROM topic WHERE name = :name"),
        {"name": name}
    ).first()
    if existing_topic:
        raise HTTPException(status_code=400, detail="Topic name already exists")


def create_topic(db: Session, topic_data: TopicCreate, created_by: UUID) -> Topic:
    try:
        check_topic_name_unique(db, name=topic_data.name)

        db_topic = Topic(
            name=topic_data.name,
            status=topic_data.status or TopicStatusEnum.active,
            created_by=created_by,
            updated_by=created_by
        )

        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic

    except IntegrityError as e:
        db.rollback()
        if "topic_name_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Topic name already exists")
        raise HTTPException(status_code=400, detail="Failed to create topic")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_topic_by_id(db: Session, topic_id: UUID) -> Topic:
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


def get_all_topics(db: Session, skip: int = 0, limit: int = 100) -> TopicListResponse:
    # Get total count
    total = db.query(Topic).count()
    
    # Get paginated results
    topics = db.query(Topic).offset(skip).limit(limit).all()
    
    return TopicListResponse(
        topics=topics,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )


def update_topic(db: Session, topic_id: UUID, topic_update: TopicUpdate, updated_by: UUID) -> Topic:
    topic = get_topic_by_id(db, topic_id)

    if topic_update.name and topic_update.name != topic.name:
        check_topic_name_unique(db, name=topic_update.name)
        topic.name = topic_update.name

    if topic_update.status:
        topic.status = topic_update.status

    # Update timestamp and user
    topic.updated_by = updated_by
    topic.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(topic)
    return topic


def delete_topic(db: Session, topic_id: UUID):
    topic = get_topic_by_id(db, topic_id)
    db.delete(topic)
    db.commit()