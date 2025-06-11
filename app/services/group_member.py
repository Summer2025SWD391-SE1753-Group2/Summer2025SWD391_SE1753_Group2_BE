from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models.group_member import GroupMember
from app.db.models.group import Group
from app.db.models.account import Account
from app.schemas.group_member import GroupMemberCreate, GroupMemberUpdate
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy import and_

def create_group_member(db: Session, member: GroupMemberCreate) -> GroupMember:
    # Check if group exists
    group = db.query(Group).filter(Group.group_id == member.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {member.group_id} not found"
        )

    # Check if account exists and is active
    account = db.query(Account).filter(Account.account_id == member.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {member.account_id} not found"
        )
    if account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account with id {member.account_id} is not active"
        )

    # Check if member already exists in group
    existing_member = db.query(GroupMember).filter(
        and_(
            GroupMember.group_id == member.group_id,
            GroupMember.account_id == member.account_id
        )
    ).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member already exists in this group"
        )

    db_member = GroupMember(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_group_member(db: Session, group_member_id: UUID) -> Optional[GroupMember]:
    return db.query(GroupMember).filter(GroupMember.group_member_id == group_member_id).first()

def get_group_members(
    db: Session,
    group_id: Optional[UUID] = None,
    account_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[GroupMember]:
    query = db.query(GroupMember)
    if group_id:
        query = query.filter(GroupMember.group_id == group_id)
    if account_id:
        query = query.filter(GroupMember.account_id == account_id)
    return query.offset(skip).limit(limit).all()

def search_group_members(
    db: Session,
    group_id: UUID,
    account_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 10
) -> Dict[str, Any]:
    query = db.query(GroupMember).filter(GroupMember.group_id == group_id)
    
    if account_id:
        query = query.filter(GroupMember.account_id == account_id)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

def delete_group_member(db: Session, group_member_id: UUID) -> None:
    db_member = get_group_member(db, group_member_id)
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group member not found"
        )
    
    db.delete(db_member)
    db.commit() 