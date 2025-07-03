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
    messages = query.order_by(GroupMessage.created_at.desc()).offset(skip).limit(limit).all()
    
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