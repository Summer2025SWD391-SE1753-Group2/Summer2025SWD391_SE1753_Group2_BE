from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.deps import get_db, get_current_active_account
from app.schemas.group import GroupCreate, GroupOut, GroupMemberCreate, GroupMemberOut
from app.schemas.group_message import GroupMessageCreate, GroupMessageOut, GroupMessageList
from app.schemas.account import RoleNameEnum
from app.services.group_chat_service import (
    create_chat_group_from_topic,
    get_group_by_id,
    add_member_to_group,
    get_group_members,
    send_group_message,
    get_group_chat_history
)
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

# Group management endpoints
@router.post("/create", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_chat_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Create a chat group from topic (only moderator and admin)"""
    return create_chat_group_from_topic(db, group_data, current_user.account_id, current_user.role)

@router.get("/{group_id}", response_model=GroupOut)
def get_group_info(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Get group information"""
    return get_group_by_id(db, group_id)

@router.post("/{group_id}/members", response_model=GroupMemberOut, status_code=status.HTTP_201_CREATED)
def add_member(
    group_id: UUID,
    member_data: GroupMemberCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Add a member to group (only leader and moderators)"""
    return add_member_to_group(db, group_id, member_data, current_user.account_id)

@router.get("/{group_id}/members", response_model=List[GroupMemberOut])
def list_group_members(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Get all members of a group"""
    return get_group_members(db, group_id)

# Group chat endpoints
@router.post("/{group_id}/messages", response_model=GroupMessageOut, status_code=status.HTTP_201_CREATED)
def send_message_to_group(
    group_id: UUID,
    message_data: GroupMessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Send a message to a group"""
    # Override group_id from URL
    message_data.group_id = group_id
    return send_group_message(db, message_data, current_user.account_id)

@router.get("/{group_id}/messages", response_model=GroupMessageList)
def get_group_messages(
    group_id: UUID,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Get chat history of a group"""
    return get_group_chat_history(db, group_id, current_user.account_id, skip=skip, limit=limit) 