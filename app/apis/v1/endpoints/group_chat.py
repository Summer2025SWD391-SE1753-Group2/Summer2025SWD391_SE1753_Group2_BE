from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import json
import logging
import asyncio

from app.core.deps import get_db, get_current_active_account
from app.core.websocket_deps import get_current_user_websocket
from app.core.websocket_manager import manager
from app.schemas.group import GroupCreate, GroupOut, GroupMemberCreate, GroupMemberOut, GroupChatCreateTransaction, GroupChatTransactionOut, GroupUpdate, GroupMembersSearchOut, GroupChatListResponse
from app.schemas.group_message import GroupMessageCreate, GroupMessageOut, GroupMessageList
from app.schemas.account import RoleNameEnum
from app.services.group_chat_service import (
    create_chat_group_from_topic,
    get_group_by_id,
    add_member_to_group,
    get_group_members,
    get_group_members_with_search,
    send_group_message,
    get_group_chat_history,
    check_topic_can_create_chat_group,
    get_available_topics_for_chat_group,
    get_topics_with_chat_groups,
    get_all_topics_with_group_chat,
    create_group_chat_transaction,
    get_my_group_chats,
    delete_group_chat,
    update_group_chat,
    remove_member_from_group,
    update_user_groups_in_manager,
    get_all_group_chats,
    join_group_chat
)
from app.apis.v1.endpoints.check_role import check_roles
from app.db.database import SessionLocal
from app.db.models.group_member import GroupMember

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket endpoint for real-time group chat
@router.websocket("/ws/group/{group_id}")
async def websocket_group_chat_endpoint(websocket: WebSocket, group_id: UUID):
    """WebSocket endpoint for real-time group chat"""
    try:
        # Authenticate user
        current_user = await get_current_user_websocket(websocket)
        
        # Check if user is a member of the group
        db = SessionLocal()
        try:
            member = db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.account_id == current_user.account_id
            ).first()
            
            if not member:
                await websocket.close(code=4003, reason="Not a member of this group")
                return
                
            # Get group info
            group = get_group_by_id(db, group_id)
            
        finally:
            db.close()
        
        # Connect to WebSocket
        await manager.connect(websocket, current_user.account_id)
        
        # Update user's groups in manager first
        db = SessionLocal()
        try:
            update_user_groups_in_manager(db, current_user.account_id)
        finally:
            db.close()
        
        # Join the group (this will be handled by update_user_groups_in_manager)
        # But we need to ensure user is in this specific group
        if not manager.is_group_member(current_user.account_id, group_id):
            manager.join_group(current_user.account_id, group_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": str(current_user.account_id),
            "group_id": str(group_id),
            "group_name": group.name,
            "message": "Connected to group chat"
        }))
        
        # Send online members list
        online_members = manager.get_online_group_members(group_id)
        logger.info(f"User {current_user.account_id} connected to group {group_id}. Online members: {online_members}")
        await websocket.send_text(json.dumps({
            "type": "online_members",
            "group_id": str(group_id),
            "members": [str(member_id) for member_id in online_members]
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "send_message":
                    # Handle sending a message
                    await handle_send_group_message(message_data, current_user.account_id, group_id)
                    
                elif message_data.get("type") == "typing":
                    # Handle typing indicator
                    await handle_group_typing_indicator(message_data, current_user.account_id, group_id)
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {current_user.account_id if 'current_user' in locals() else 'unknown'} from group {group_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if 'current_user' in locals():
            manager.leave_group(current_user.account_id, group_id)
            manager.disconnect(current_user.account_id)

async def handle_send_group_message(message_data: dict, sender_id: UUID, group_id: UUID):
    """Handle sending a message to group via WebSocket"""
    try:
        content = message_data.get("content", "").strip()
        
        if not content:
            return
        
        # Create message data
        msg_data = GroupMessageCreate(
            group_id=group_id,
            content=content
        )
        
        # Send message
        db = SessionLocal()
        try:
            message = send_group_message(db, msg_data, sender_id)
            
            # Send confirmation back to sender
            await manager.send_personal_message({
                "type": "message_sent",
                "message_id": str(message.message_id),
                "group_id": str(group_id),
                "status": "sent"
            }, sender_id)
            
            # Broadcast to all group members
            group_message = {
                "type": "group_message",
                "data": {
                    "message_id": str(message.message_id),
                    "group_id": str(message.group_id),
                    "sender_id": str(message.sender_id),
                    "content": message.content,
                    "status": message.status.value,
                    "is_deleted": message.is_deleted,
                    "created_at": message.created_at.isoformat(),
                    "updated_at": message.updated_at.isoformat(),
                    "sender": {
                        "account_id": str(message.sender.account_id),
                        "username": message.sender.username,
                        "full_name": message.sender.full_name,
                        "avatar": message.sender.avatar
                    }
                }
            }
            
            logger.info(f"Broadcasting message to group {group_id} from user {sender_id}")
            await manager.broadcast_to_group(group_message, group_id, exclude_user=sender_id)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error sending group message: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "Failed to send message"
        }, sender_id)

async def handle_group_typing_indicator(message_data: dict, user_id: UUID, group_id: UUID):
    """Handle typing indicator for group chat"""
    try:
        is_typing = message_data.get("is_typing", False)
        
        # Broadcast typing indicator to all group members except sender
        typing_message = {
            "type": "typing_indicator",
            "group_id": str(group_id),
            "user_id": str(user_id),
            "is_typing": is_typing
        }
        
        await manager.broadcast_to_group(typing_message, group_id, exclude_user=user_id)
        
    except Exception as e:
        logger.error(f"Error handling typing indicator: {e}")

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
    message = send_group_message(db, message_data, current_user.account_id)
    
    # Send real-time message via WebSocket if members are online
    try:
        group_message = {
            "type": "group_message",
            "data": {
                "message_id": str(message.message_id),
                "group_id": str(message.group_id),
                "sender_id": str(message.sender_id),
                "content": message.content,
                "status": message.status.value,
                "is_deleted": message.is_deleted,
                "created_at": message.created_at.isoformat(),
                "updated_at": message.updated_at.isoformat(),
                "sender": {
                    "account_id": str(message.sender.account_id),
                    "username": message.sender.username,
                    "full_name": message.sender.full_name,
                    "avatar": message.sender.avatar
                }
            }
        }
        
        asyncio.create_task(
            manager.broadcast_to_group(group_message, group_id, exclude_user=current_user.account_id)
        )
    except Exception as e:
        logger.error(f"Failed to send group message via WebSocket: {e}")
    
    return message

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

@router.get("/all", response_model=GroupChatListResponse)
def get_all_group_chats_endpoint(
    skip: int = Query(0, ge=0, description="Number of groups to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of groups to return"),
    search: str = Query(None, description="Tìm kiếm theo tên group chat (có thể để rỗng hoặc bất kỳ độ dài nào)"),
    topic_id: UUID = Query(None, description="Filter by topic ID"),
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Lấy danh sách tất cả group chat với phân trang và tìm kiếm (user, moderator, admin).
    - Nếu search rỗng hoặc không truyền: trả về tất cả group.
    - Nếu search có giá trị: lọc theo tên group chat (không giới hạn độ dài).
    """
    return get_all_group_chats(db, skip=skip, limit=limit, search=search, topic_id=topic_id)

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

@router.get("/{group_id}/members/search", response_model=GroupMembersSearchOut)
def search_group_members(
    group_id: UUID,
    skip: int = Query(0, ge=0, description="Number of members to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of members to return"),
    search: str = Query(None, description="Search term for username, full name, or email"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Get group members with search and pagination"""
    return get_group_members_with_search(db, group_id, skip=skip, limit=limit, search=search)

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group_chat_endpoint(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.admin]))
):
    """Xóa group chat (chỉ admin mới có quyền)"""
    delete_group_chat(db, group_id, current_user.account_id, current_user.role.role_name)
    return None

@router.delete("/{group_id}/members/{account_id}", status_code=204)
def remove_member(
    group_id: UUID,
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    """Xóa thành viên khỏi group (chỉ leader/moderator)"""
    remove_member_from_group(db, group_id, account_id, current_user.account_id)
    return None

@router.post("/{group_id}/join", response_model=GroupMemberOut, status_code=status.HTTP_201_CREATED)
def join_group_chat_endpoint(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Join a group chat (user, moderator, admin) - tối đa 50 người"""
    return join_group_chat(db, group_id, current_user.account_id) 

@router.get("/{group_id}/membership")
def check_group_membership(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == current_user.account_id
    ).first()
    if member:
        return {
            "is_member": True,
            "role": member.role,
            "joined_at": member.joined_at
        }
    else:
        return {"is_member": False}

@router.post("/membership/batch")
def check_group_membership_batch(
    group_ids: List[UUID] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    memberships = []
    for group_id in group_ids:
        member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.account_id == current_user.account_id
        ).first()
        memberships.append({
            "group_id": str(group_id),
            "is_member": bool(member),
            "role": member.role if member else None
        })
    return {"memberships": memberships} 