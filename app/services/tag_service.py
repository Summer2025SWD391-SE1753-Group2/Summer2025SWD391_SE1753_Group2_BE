from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timezone
from app.db.models.tag import Tag, TagStatusEnum
from app.schemas.tag import TagCreate, TagUpdate


def check_tag_name_unique(db: Session, name: str):
    existing_tag = db.execute(
        text("SELECT 1 FROM tag WHERE name = :name"),
        {"name": name}
    ).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag name already exists")


def create_tag(db: Session, tag_data: TagCreate, created_by: UUID) -> Tag:
    try:
        check_tag_name_unique(db, name=tag_data.name)

        db_tag = Tag(
            name=tag_data.name,
            status=tag_data.status or TagStatusEnum.active,
            created_by=created_by,
            updated_by=created_by
        )

        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    except IntegrityError as e:
        db.rollback()
        if "tag_name_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Tag name already exists")
        raise HTTPException(status_code=400, detail="Failed to create tag")


def get_tag_by_id(db: Session, tag_id: UUID) -> Tag:
    tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


def get_all_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tag).offset(skip).limit(limit).all()


def update_tag(db: Session, tag_id: UUID, tag_update: TagUpdate, updated_by: UUID) -> Tag:
    tag = get_tag_by_id(db, tag_id)

    if tag_update.name and tag_update.name != tag.name:
        check_tag_name_unique(db, name=tag_update.name)
        tag.name = tag_update.name

    if tag_update.status:
        tag.status = tag_update.status

    # Use the authenticated user's ID
    tag.updated_by = updated_by
    tag.updated_at = datetime.now(timezone.utc)  # Add this line to update timestamp
    
    db.commit()
    db.refresh(tag)
    return tag

def delete_tag(db: Session, tag_id: UUID):
    tag = get_tag_by_id(db, tag_id)
    db.delete(tag)
    db.commit()