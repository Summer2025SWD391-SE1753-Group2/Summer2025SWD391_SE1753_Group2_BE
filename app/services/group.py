from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models.group import Group
from app.db.models.topic import Topic
from app.db.models.account import Account
from app.schemas.group import GroupCreate, GroupUpdate
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy import and_

def create_group(db: Session, group: GroupCreate, created_by: UUID, role: str) -> Group:
    # Check if user has permission
    if role not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or moderator can create groups"
        )

    # Validate topic exists
    topic = db.query(Topic).filter(Topic.topic_id == group.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {group.topic_id} not found"
        )

    # Validate group leader exists and is active
    leader = db.query(Account).filter(Account.account_id == group.group_leader).first()
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group leader with id {group.group_leader} not found"
        )
    if leader.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Group leader with id {group.group_leader} is not active"
        )

    # Check if group name already exists in the same topic
    existing_group = db.query(Group).filter(
        and_(
            Group.topic_id == group.topic_id,
            Group.name == group.name
        )
    ).first()
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Group with name '{group.name}' already exists in this topic"
        )

    db_group = Group(
        topic_id=group.topic_id,
        name=group.name,
        group_leader=group.group_leader,
        created_by=created_by
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def get_group(db: Session, group_id: UUID) -> Optional[Group]:
    return db.query(Group).filter(Group.group_id == group_id).first()

def get_groups(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    topic_id: Optional[UUID] = None
) -> List[Group]:
    query = db.query(Group)
    if topic_id:
        query = query.filter(Group.topic_id == topic_id)
    return query.offset(skip).limit(limit).all()

def search_groups(
    db: Session,
    topic_id: Optional[UUID] = None,
    group_leader_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search groups with pagination
    Returns a dictionary containing:
    - items: List of groups
    - total: Total number of groups matching the criteria
    - skip: Number of items skipped
    - limit: Maximum number of items per page
    """
    # Build base query
    query = db.query(Group)

    # Apply filters
    if topic_id:
        query = query.filter(Group.topic_id == topic_id)
    if group_leader_id:
        query = query.filter(Group.group_leader == group_leader_id)

    # Get total count
    total = query.count()

    # Apply pagination
    groups = query.offset(skip).limit(limit).all()

    return {
        "items": groups,
        "total": total,
        "skip": skip,
        "limit": limit
    }

def update_group(
    db: Session,
    group_id: UUID,
    group_update: GroupUpdate,
    role: str
) -> Optional[Group]:
    # Check if user has permission
    if role not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or moderator can update groups"
        )

    db_group = get_group(db, group_id)
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Validate topic if provided
    if group_update.topic_id:
        topic = db.query(Topic).filter(Topic.topic_id == group_update.topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with id {group_update.topic_id} not found"
            )

    # Validate group leader if provided
    if group_update.group_leader:
        leader = db.query(Account).filter(Account.account_id == group_update.group_leader).first()
        if not leader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group leader with id {group_update.group_leader} not found"
            )
        if leader.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group leader with id {group_update.group_leader} is not active"
            )

    # Check if new group name already exists in the same topic
    if group_update.name:
        topic_id = group_update.topic_id or db_group.topic_id
        existing_group = db.query(Group).filter(
            and_(
                Group.topic_id == topic_id,
                Group.name == group_update.name,
                Group.group_id != group_id  # Exclude current group
            )
        ).first()
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group with name '{group_update.name}' already exists in this topic"
            )
    
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group, field, value)
    
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_group(db: Session, group_id: UUID, role: str) -> bool:
    # Check if user has permission
    if role not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or moderator can delete groups"
        )

    db_group = get_group(db, group_id)
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    db.delete(db_group)
    db.commit()
    return True 