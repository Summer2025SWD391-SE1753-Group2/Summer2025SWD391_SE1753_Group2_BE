from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.deps import get_db, get_current_active_account
from app.schemas.group import GroupCreate, GroupOut, GroupMemberCreate, GroupMemberOut, GroupChatCreateTransaction, GroupChatTransactionOut, GroupUpdate
from app.schemas.group_message import GroupMessageCreate, GroupMessageOut, GroupMessageList
from app.schemas.account import RoleNameEnum
from app.services.group_chat_service import (
    create_chat_group_from_topic,
    get_group_by_id,
    add_member_to_group,
    get_group_members,
    send_group_message,
    get_group_chat_history,
    check_topic_can_create_chat_group,
    get_available_topics_for_chat_group,
    get_topics_with_chat_groups,
    get_all_topics_with_group_chat,
    create_group_chat_transaction,
    get_my_group_chats,
    delete_group_chat,
    update_group_chat
)
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

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

# Topic management endpoints
@router.get("/topics/available")
def get_available_topics(
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get list of topics that can create chat groups (only moderator and admin)"""
    return get_available_topics_for_chat_group(db)

@router.get("/topics/with-groups")
def get_topics_with_groups(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Get list of topics that already have chat groups"""
    return get_topics_with_chat_groups(db)

@router.get("/topics/{topic_id}/check")
def check_topic_availability(
    topic_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Check if a topic can create a chat group (only moderator and admin)"""
    return check_topic_can_create_chat_group(db, topic_id)

@router.get("/topics/with-or-without-group")
def get_topics_with_or_without_group(
    db: Session = Depends(get_db)
):
    """Get all topics and, for each, the group chat info if it exists (or null if not)"""
    return get_all_topics_with_group_chat(db)

@router.get("/my-groups")
def get_my_group_chats_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Lấy danh sách group chat mà user hiện tại tham gia"""
    return get_my_group_chats(db, current_user.account_id)

@router.post("/create-transaction", response_model=GroupChatTransactionOut, status_code=status.HTTP_201_CREATED)
def create_group_chat_transaction_endpoint(
    data: GroupChatCreateTransaction,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Tạo group chat mới (transaction): tạo group, add leader, add members, rollback nếu lỗi"""
    return create_group_chat_transaction(db, data, current_user.account_id, current_user.role.role_name)

# Group management endpoints
@router.post("/create", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_chat_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Create a chat group from topic (only moderator and admin)"""
    return create_chat_group_from_topic(db, group_data, current_user.account_id, current_user.role.role_name)

@router.get("/{group_id}", response_model=GroupOut)
def get_group_info(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Get group information"""
    return get_group_by_id(db, group_id)

@router.put("/{group_id}", response_model=GroupOut)
def update_group_info(
    group_id: UUID,
    update_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Update group information (only leader and moderator can update)"""
    # Convert Pydantic model to dict, excluding None values
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    return update_group_chat(db, group_id, update_dict, current_user.account_id)

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

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group_chat_endpoint(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.admin]))
):
    """Xóa group chat (chỉ admin mới có quyền)"""
    delete_group_chat(db, group_id, current_user.account_id, current_user.role.role_name)
    return None 