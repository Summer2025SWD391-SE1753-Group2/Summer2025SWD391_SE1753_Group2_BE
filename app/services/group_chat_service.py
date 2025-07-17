from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from app.db.models.group import Group
from app.db.models.group_member import GroupMember, GroupMemberRoleEnum
from app.db.models.group_message import GroupMessage, GroupMessageStatusEnum
from app.db.models.topic import Topic
from app.db.models.account import Account
from app.schemas.group import GroupCreate, GroupOut, GroupMemberCreate, GroupMemberOut
from app.schemas.group_message import GroupMessageCreate, GroupMessageOut, GroupMessageList
from app.schemas.account import RoleNameEnum
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def create_chat_group_from_topic(
    db: Session, 
    group_data: GroupCreate, 
    creator_id: UUID,
    creator_role: RoleNameEnum
) -> GroupOut:
    """Create a chat group from topic (only moderator and admin can create)"""
    
    # Check if creator has permission
    if creator_role not in [RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can create chat groups"
        )
    
    # Check if topic exists
    topic = db.query(Topic).filter(Topic.topic_id == group_data.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check if topic is inactive
    if hasattr(topic, 'status') and str(topic.status) == 'inactive':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create group chat for inactive topic"
        )
    
    # Check if topic already has a chat group
    existing_group = db.query(Group).filter(
        Group.topic_id == group_data.topic_id,
        Group.is_chat_group == True
    ).first()
    
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic already has a chat group"
        )
    
    # Create the group
    group = Group(
        topic_id=group_data.topic_id,
        name=group_data.name,
        description=group_data.description,
        group_leader=creator_id,
        created_by=creator_id,
        max_members=group_data.max_members,
        is_chat_group=True
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Add creator as leader member
    leader_member = GroupMember(
        account_id=creator_id,
        group_id=group.group_id,
        role=GroupMemberRoleEnum.leader
    )
    
    db.add(leader_member)
    db.commit()
    
    return get_group_by_id(db, group.group_id)

def get_group_by_id(db: Session, group_id: UUID) -> GroupOut:
    """Get a specific group by ID with related information"""
    group = db.query(Group).options(
        joinedload(Group.topic),
        joinedload(Group.leader)
    ).filter(Group.group_id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Get member count
    member_count = db.query(GroupMember).filter(
        GroupMember.group_id == group_id
    ).count()
    
    group_out = GroupOut.model_validate(group)
    group_out.topic_name = group.topic.name if group.topic else None
    group_out.leader_name = group.leader.full_name if group.leader else None
    group_out.member_count = member_count
    
    return group_out

def add_member_to_group(
    db: Session, 
    group_id: UUID, 
    member_data: GroupMemberCreate,
    current_user_id: UUID
) -> GroupMemberOut:
    """Add a member to group (only leader and moderators can add members)"""
    
    # Check if group exists
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if current user has permission to add members
    current_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == current_user_id
    ).first()
    
    if not current_member or current_member.role not in [GroupMemberRoleEnum.leader, GroupMemberRoleEnum.moderator]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and moderators can add members"
        )
    
    # Check if account exists
    account = db.query(Account).filter(Account.account_id == member_data.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check if member already exists
    existing_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == member_data.account_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member already exists in group"
        )
    
    # Check if group is full
    member_count = db.query(GroupMember).filter(
        GroupMember.group_id == group_id
    ).count()
    
    if member_count >= group.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group is full"
        )
    
    # Add member
    member = GroupMember(
        account_id=member_data.account_id,
        group_id=group_id,
        role=member_data.role
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return get_group_member_by_id(db, member.group_member_id)

def get_group_member_by_id(db: Session, member_id: UUID) -> GroupMemberOut:
    """Get a specific group member by ID with account information"""
    member = db.query(GroupMember).options(
        joinedload(GroupMember.account)
    ).filter(GroupMember.group_member_id == member_id).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group member not found"
        )
    
    member_out = GroupMemberOut.model_validate(member)
    if member.account:
        member_out.username = member.account.username
        member_out.full_name = member.account.full_name
        member_out.avatar = member.account.avatar
    
    return member_out

def get_group_members(db: Session, group_id: UUID) -> List[GroupMemberOut]:
    """Get all members of a group"""
    members = db.query(GroupMember).options(
        joinedload(GroupMember.account)
    ).filter(GroupMember.group_id == group_id).all()
    
    result = []
    for member in members:
        member_out = GroupMemberOut.model_validate(member)
        if member.account:
            member_out.username = member.account.username
            member_out.full_name = member.account.full_name
            member_out.avatar = member.account.avatar
        result.append(member_out)
    
    return result

def get_group_members_with_search(
    db: Session, 
    group_id: UUID, 
    skip: int = 0, 
    limit: int = 20,
    search: str = None
) -> dict:
    """Get group members with search and pagination"""
    from app.db.models.account import Account
    
    # Check if group exists
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Build query
    query = db.query(GroupMember).options(
        joinedload(GroupMember.account)
    ).filter(GroupMember.group_id == group_id)
    
    # Add search filter if provided
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.join(Account).filter(
            db.or_(
                Account.username.ilike(search_term),
                Account.full_name.ilike(search_term),
                Account.email.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    members = query.order_by(GroupMember.joined_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to output format
    result = []
    for member in members:
        member_out = GroupMemberOut.model_validate(member)
        if member.account:
            member_out.username = member.account.username
            member_out.full_name = member.account.full_name
            member_out.avatar = member.account.avatar
            member_out.email = member.account.email
        result.append(member_out)
    
    return {
        "members": result,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }

def send_group_message(
    db: Session, 
    message_data: GroupMessageCreate, 
    sender_id: UUID
) -> GroupMessageOut:
    """Send a message to a group"""
    
    # Check if group exists
    group = db.query(Group).filter(Group.group_id == message_data.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if sender is a member of the group
    member = db.query(GroupMember).filter(
        GroupMember.group_id == message_data.group_id,
        GroupMember.account_id == sender_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of the group to send messages"
        )
    
    # Create the message
    message = GroupMessage(
        group_id=message_data.group_id,
        sender_id=sender_id,
        content=message_data.content
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return get_group_message_by_id(db, message.message_id)

def get_group_message_by_id(db: Session, message_id: UUID) -> GroupMessageOut:
    """Get a specific group message by ID with sender information"""
    message = db.query(GroupMessage).options(
        joinedload(GroupMessage.sender)
    ).filter(GroupMessage.message_id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return GroupMessageOut.model_validate(message)

def get_group_chat_history(
    db: Session, 
    group_id: UUID,
    user_id: UUID,
    skip: int = 0, 
    limit: int = 50
) -> GroupMessageList:
    """Get chat history of a group"""
    
    # Check if user is a member of the group
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of the group to view chat history"
        )
    
    # Get messages
    query = db.query(GroupMessage).options(
        joinedload(GroupMessage.sender)
    ).filter(
        GroupMessage.group_id == group_id,
        GroupMessage.is_deleted == False
    )
    
    total = query.count()
    messages = query.order_by(GroupMessage.created_at.asc()).offset(skip).limit(limit).all()
    
    message_outs = [GroupMessageOut.model_validate(message) for message in messages]
    
    return GroupMessageList(
        messages=message_outs,
        total=total,
        skip=skip,
        limit=limit
    )

def check_topic_can_create_chat_group(db: Session, topic_id: UUID) -> dict:
    """Check if a topic can create a chat group"""
    # Check if topic exists
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        return {
            "can_create": False,
            "reason": "Topic not found"
        }
    
    # Check if topic is inactive
    if hasattr(topic, 'status') and str(topic.status) == 'inactive':
        return {
            "can_create": False,
            "reason": "Topic is inactive"
        }
    
    # Check if topic already has a chat group
    existing_group = db.query(Group).filter(
        Group.topic_id == topic_id,
        Group.is_chat_group == True
    ).first()
    
    if existing_group:
        return {
            "can_create": False,
            "reason": "Topic already has a chat group",
            "existing_group_id": str(existing_group.group_id),
            "existing_group_name": existing_group.name
        }
    
    return {
        "can_create": True,
        "reason": "Topic is available for creating chat group",
        "topic_name": topic.name
    }

def get_available_topics_for_chat_group(db: Session) -> List[dict]:
    """Get list of topics that can create chat groups"""
    # Get all topics
    all_topics = db.query(Topic).filter(Topic.status == "active").all()
    
    # Get topics that already have chat groups
    topics_with_groups = db.query(Group.topic_id).filter(
        Group.is_chat_group == True
    ).distinct().all()
    
    topics_with_groups_ids = [str(topic_id[0]) for topic_id in topics_with_groups]
    
    available_topics = []
    for topic in all_topics:
        if str(topic.topic_id) not in topics_with_groups_ids:
            available_topics.append({
                "topic_id": str(topic.topic_id),
                "topic_name": topic.name,
                "status": topic.status,
                "can_create": True
            })
    
    return available_topics

def get_topics_with_chat_groups(db: Session) -> List[dict]:
    """Get list of topics that already have chat groups"""
    # Get topics with chat groups
    topics_with_groups = db.query(Topic, Group).join(
        Group, Topic.topic_id == Group.topic_id
    ).filter(
        Group.is_chat_group == True
    ).all()
    
    result = []
    for topic, group in topics_with_groups:
        # Get member count
        member_count = db.query(GroupMember).filter(
            GroupMember.group_id == group.group_id
        ).count()
        
        result.append({
            "topic_id": str(topic.topic_id),
            "topic_name": topic.name,
            "group_id": str(group.group_id),
            "group_name": group.name,
            "group_description": group.description,
            "member_count": member_count,
            "max_members": group.max_members,
            "created_at": group.created_at
        })
    
    return result

def get_all_topics_with_group_chat(db: Session) -> list:
    """Return all topics and, for each, the group chat info if it exists (or null if not)"""
    topics = db.query(Topic).all()
    result = []
    for topic in topics:
        group = db.query(Group).filter(
            Group.topic_id == topic.topic_id,
            Group.is_chat_group == True
        ).first()
        group_info = None
        if group:
            member_count = db.query(GroupMember).filter(
                GroupMember.group_id == group.group_id
            ).count()
            group_info = {
                "group_id": str(group.group_id),
                "group_name": group.name,
                "group_description": group.description,
                "member_count": member_count,
                "max_members": group.max_members,
                "created_at": group.created_at,
            }
        result.append({
            "topic_id": str(topic.topic_id),
            "topic_name": topic.name,
            "status": topic.status.value if hasattr(topic.status, 'value') else str(topic.status),
            "group_chat": group_info
        })
    return result

def create_group_chat_transaction(
    db: Session,
    data,
    creator_id: UUID,
    creator_role: RoleNameEnum
):
    """Tạo group chat mới (transaction): tạo group, add leader, add members, rollback nếu lỗi"""
    from app.db.models.account import Account
    from app.schemas.group import GroupChatTransactionOut, GroupOut, GroupMemberOut
    if creator_role not in [RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(status_code=403, detail="Only moderators and admins can create group chats")
    topic = db.query(Topic).filter(Topic.topic_id == data.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if hasattr(topic, 'status') and str(topic.status) == 'inactive':
        raise HTTPException(status_code=400, detail="Cannot create group chat for inactive topic")
    existing_group = db.query(Group).filter(
        Group.topic_id == data.topic_id,
        Group.is_chat_group == True
    ).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Topic already has a chat group")
    # Validate name
    if not data.name or not data.name.strip() or len(data.name) > 100:
        raise HTTPException(status_code=422, detail="Invalid group name")
    # Validate members
    member_ids = set(str(mid) for mid in data.member_ids)
    if len(member_ids) < 2:
        raise HTTPException(status_code=422, detail="Must add at least 2 members")
    if len(member_ids) > 49:
        raise HTTPException(status_code=422, detail="Too many members")
    if str(creator_id) in member_ids:
        member_ids.remove(str(creator_id))
    # Check valid accounts
    accounts = db.query(Account).filter(Account.account_id.in_(member_ids)).all()
    if len(accounts) != len(member_ids):
        raise HTTPException(status_code=422, detail="Some member accounts not found")
    try:
        # Start transaction
        group = Group(
            topic_id=data.topic_id,
            name=data.name.strip(),
            description=data.description,
            group_leader=creator_id,
            created_by=creator_id,
            max_members=len(member_ids) + 1,
            is_chat_group=True
        )
        db.add(group)
        db.flush()  # get group_id
        # Add leader
        leader_member = GroupMember(
            account_id=creator_id,
            group_id=group.group_id,
            role=GroupMemberRoleEnum.leader
        )
        db.add(leader_member)
        # Add members
        member_objs = []
        for acc in accounts:
            m = GroupMember(
                account_id=acc.account_id,
                group_id=group.group_id,
                role=GroupMemberRoleEnum.member
            )
            db.add(m)
            member_objs.append(m)
        db.commit()
        db.refresh(group)
        # Prepare output
        group_out = get_group_by_id(db, group.group_id)
        members_out = [GroupMemberOut.model_validate(leader_member)]
        for m in member_objs:
            db.refresh(m)
            members_out.append(GroupMemberOut.model_validate(m))
        return GroupChatTransactionOut(group=group_out, members=members_out)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create group chat: {str(e)}")

def get_my_group_chats(db: Session, user_id: UUID) -> List[dict]:
    """Lấy danh sách group chat mà user hiện tại tham gia"""
    from app.db.models.account import Account
    # Lấy tất cả group chat mà user tham gia
    my_groups = db.query(Group, GroupMember).join(
        GroupMember, Group.group_id == GroupMember.group_id
    ).filter(
        GroupMember.account_id == user_id,
        Group.is_chat_group == True
    ).all()
    
    result = []
    for group, member in my_groups:
        # Lấy thông tin topic
        topic = db.query(Topic).filter(Topic.topic_id == group.topic_id).first()
        
        # Đếm số thành viên
        member_count = db.query(GroupMember).filter(
            GroupMember.group_id == group.group_id
        ).count()
        
        # Lấy thông tin leader
        leader = db.query(Account).filter(Account.account_id == group.group_leader).first()
        
        result.append({
            "group_id": str(group.group_id),
            "group_name": group.name,
            "group_description": group.description,
            "topic_id": str(group.topic_id),
            "topic_name": topic.name if topic else None,
            "member_count": member_count,
            "max_members": group.max_members,
            "my_role": member.role.value if hasattr(member.role, 'value') else str(member.role),
            "leader_name": leader.full_name if leader else None,
            "created_at": group.created_at,
            "joined_at": member.joined_at
        })
    
    return result

def update_group_chat(
    db: Session, 
    group_id: UUID, 
    update_data: dict,
    current_user_id: UUID
) -> GroupOut:
    """Cập nhật thông tin group chat (chỉ leader và moderator mới có quyền)"""
    
    # Check if group exists
    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.is_chat_group == True
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group chat not found"
        )
    
    # Check if current user has permission to update
    current_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == current_user_id
    ).first()
    
    if not current_member or current_member.role not in [GroupMemberRoleEnum.leader, GroupMemberRoleEnum.moderator]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and moderators can update group information"
        )
    
    # Update group information
    if 'name' in update_data:
        group.name = update_data['name']
    if 'description' in update_data:
        group.description = update_data['description']
    
    group.updated_at = datetime.now(timezone.utc)
    
    try:
        db.commit()
        db.refresh(group)
        return get_group_by_id(db, group_id)
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating group chat: {str(e)}"
        )

def delete_group_chat(db: Session, group_id: UUID, user_id: UUID, user_role: RoleNameEnum) -> bool:
    """Xóa group chat (chỉ admin mới có quyền)"""
    from app.db.models.group_message import GroupMessage
    from sqlalchemy.exc import SQLAlchemyError
    
    # Chỉ admin mới có quyền xóa group chat
    if user_role != RoleNameEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete group chat"
        )
    
    # Kiểm tra group tồn tại
    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.is_chat_group == True
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group chat not found"
        )
    
    try:
        # Xóa tất cả messages trong group
        db.query(GroupMessage).filter(
            GroupMessage.group_id == group_id
        ).delete()
        
        # Xóa tất cả members trong group
        db.query(GroupMember).filter(
            GroupMember.group_id == group_id
        ).delete()
        
        # Xóa group
        db.delete(group)
        db.commit()
        
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete group chat: {str(e)}"
        )

def remove_member_from_group(
    db: Session,
    group_id: UUID,
    account_id: UUID,
    current_user_id: UUID
) -> bool:
    """Xóa thành viên khỏi group (chỉ leader/moderator mới có quyền)"""
    from app.db.models.group_member import GroupMember, GroupMemberRoleEnum
    # Kiểm tra group tồn tại
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    # Kiểm tra quyền
    current_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == current_user_id
    ).first()
    if not current_member or current_member.role not in [GroupMemberRoleEnum.leader, GroupMemberRoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Only leader or moderator can remove members")
    # Không cho leader tự xóa mình
    if account_id == current_user_id and current_member.role == GroupMemberRoleEnum.leader:
        raise HTTPException(status_code=400, detail="Leader cannot remove themselves")
    # Kiểm tra thành viên cần xóa
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == account_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in group")
    db.delete(member)
    db.commit()
    return True

def get_all_group_chats(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    search: str = None,
    topic_id: UUID = None
) -> dict:
    """Get all group chats with pagination and search (search có thể rỗng hoặc bất kỳ độ dài nào)"""
    
    # Base query for group chats
    query = db.query(Group).options(
        joinedload(Group.topic),
        joinedload(Group.leader)
    ).filter(Group.is_chat_group == True)
    
    # Apply search filter if provided and not empty
    if search is not None and search.strip() != "":
        search_term = f"%{search.strip()}%"
        query = query.filter(
            Group.name.ilike(search_term)
        )
    
    # Apply topic filter if provided
    if topic_id:
        query = query.filter(Group.topic_id == topic_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    groups = query.order_by(Group.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for group in groups:
        # Get member count
        member_count = db.query(GroupMember).filter(
            GroupMember.group_id == group.group_id
        ).count()
        
        # Get message count
        message_count = db.query(GroupMessage).filter(
            GroupMessage.group_id == group.group_id,
            GroupMessage.is_deleted == False
        ).count()
        
        # Get latest message info
        latest_message = db.query(GroupMessage).filter(
            GroupMessage.group_id == group.group_id,
            GroupMessage.is_deleted == False
        ).order_by(GroupMessage.created_at.desc()).first()
        
        group_info = {
            "group_id": group.group_id,
            "group_name": group.name,
            "group_description": group.description,
            "topic_id": group.topic_id,
            "topic_name": group.topic.name if group.topic else None,
            "topic_status": str(group.topic.status) if group.topic and hasattr(group.topic.status, 'value') else str(group.topic.status) if group.topic else None,
            "member_count": member_count,
            "max_members": group.max_members,
            "message_count": message_count,
            "group_leader": group.group_leader,
            "leader_name": group.leader.full_name if group.leader else None,
            "leader_username": group.leader.username if group.leader else None,
            "created_by": group.created_by,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
            "latest_message": {
                "content": latest_message.content if latest_message else None,
                "sender_name": latest_message.sender.full_name if latest_message and latest_message.sender else None,
                "created_at": latest_message.created_at if latest_message else None
            } if latest_message else None,
            "is_active": group.is_active
        }
        
        result.append(group_info)
    
    return {
        "groups": result,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }

def join_group_chat(
    db: Session,
    group_id: UUID,
    user_id: UUID
) -> GroupMemberOut:
    """Join a group chat (user, moderator, admin can join)"""
    
    # Check if group exists and is a chat group
    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.is_chat_group == True
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group chat not found"
        )
    
    # Check if group is active
    if not group.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group chat is not active"
        )
    
    # Check if user is already a member
    existing_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.account_id == user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this group"
        )
    
    # Check if group is full
    member_count = db.query(GroupMember).filter(
        GroupMember.group_id == group_id
    ).count()
    
    if member_count >= group.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group is full (maximum 50 members)"
        )
    
    # Add user as member
    member = GroupMember(
        account_id=user_id,
        group_id=group_id,
        role=GroupMemberRoleEnum.member
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return get_group_member_by_id(db, member.group_member_id)

def update_user_groups_in_manager(db: Session, user_id: UUID):
    """Update the user's groups list in the WebSocket manager"""
    from app.core.websocket_manager import manager
    
    # Get user's groups where user is a member
    user_groups = db.query(Group).join(GroupMember).filter(
        GroupMember.account_id == user_id,
        Group.is_chat_group == True
    ).all()
    
    group_ids = [group.group_id for group in user_groups]
    
    # Add user to groups without removing from existing ones
    for group_id in group_ids:
        if not manager.is_group_member(user_id, group_id):
            manager.join_group(user_id, group_id)
    
    logger.info(f"Updated groups for user {user_id}: {group_ids}") 