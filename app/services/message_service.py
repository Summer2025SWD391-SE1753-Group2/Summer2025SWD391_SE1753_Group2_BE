from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
import asyncio

from app.db.models.message import Message, MessageStatusEnum
from app.db.models.friend import Friend, FriendStatusEnum
from app.db.models.account import Account
from app.schemas.message import MessageCreate, MessageUpdate, MessageOut, MessageList
from app.core.websocket_manager import manager

async def send_message(db: Session, message_data: MessageCreate, sender_id: UUID) -> MessageOut:
    """Send a message to a friend"""
    # Check if receiver exists
    receiver = db.query(Account).filter(Account.account_id == message_data.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    # Check if they are friends
    friendship = db.query(Friend).filter(
        ((Friend.sender_id == sender_id) & (Friend.receiver_id == message_data.receiver_id)) |
        ((Friend.sender_id == message_data.receiver_id) & (Friend.receiver_id == sender_id)),
        Friend.status == FriendStatusEnum.accepted
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send messages to your friends"
        )
    
    # Create the message
    message = Message(
        sender_id=sender_id,
        receiver_id=message_data.receiver_id,
        content=message_data.content
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Check if receiver is online and send via WebSocket
    if manager.is_user_online(message_data.receiver_id):
        message.status = MessageStatusEnum.delivered
        db.commit()
        
        # Send real-time message
        websocket_message = {
            "type": "new_message",
            "message": {
                "message_id": str(message.message_id),
                "sender_id": str(message.sender_id),
                "receiver_id": str(message.receiver_id),
                "content": message.content,
                "status": message.status.value,
                "created_at": message.created_at.isoformat(),
                "sender": {
                    "account_id": str(message.sender.account_id),
                    "username": message.sender.username,
                    "full_name": message.sender.full_name,
                    "avatar": message.sender.avatar
                }
            }
        }
        
        # Send to receiver
        await manager.send_personal_message(websocket_message, message_data.receiver_id)
    
    return get_message_by_id(db, message.message_id)

def get_message_by_id(db: Session, message_id: UUID) -> MessageOut:
    """Get a specific message by ID with related account information"""
    message = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver)
    ).filter(Message.message_id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return MessageOut.model_validate(message)

def get_chat_history(
    db: Session, 
    user_id: UUID, 
    friend_id: UUID,
    skip: int = 0, 
    limit: int = 50
) -> MessageList:
    """Get chat history between two friends"""
    # Check if they are friends
    friendship = db.query(Friend).filter(
        ((Friend.sender_id == user_id) & (Friend.receiver_id == friend_id)) |
        ((Friend.sender_id == friend_id) & (Friend.receiver_id == user_id)),
        Friend.status == FriendStatusEnum.accepted
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view chat history with your friends"
        )
    
    # Get messages between the two users
    query = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver)
    ).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == user_id)),
        Message.is_deleted == False
    )
    
    total = query.count()
    messages = query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    # Mark messages as read if they were sent to the current user
    for message in messages:
        if message.receiver_id == user_id and message.status != MessageStatusEnum.read:
            message.status = MessageStatusEnum.read
            message.read_at = datetime.now(timezone.utc)
    
    db.commit()
    
    message_outs = [MessageOut.model_validate(message) for message in messages]
    
    return MessageList(
        messages=message_outs,
        total=total,
        skip=skip,
        limit=limit
    )

def mark_message_as_read(db: Session, message_id: UUID, user_id: UUID) -> MessageOut:
    """Mark a message as read"""
    message = db.query(Message).filter(
        Message.message_id == message_id,
        Message.receiver_id == user_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    message.status = MessageStatusEnum.read
    message.read_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(message)
    
    return get_message_by_id(db, message_id)

def delete_message(db: Session, message_id: UUID, user_id: UUID) -> bool:
    """Delete a message (soft delete)"""
    message = db.query(Message).filter(
        Message.message_id == message_id,
        Message.sender_id == user_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or you don't have permission to delete it"
        )
    
    message.is_deleted = True
    message.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return True

def get_unread_message_count(db: Session, user_id: UUID) -> int:
    """Get count of unread messages for a user"""
    return db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.status != MessageStatusEnum.read,
        Message.is_deleted == False
    ).count()

def update_user_friends_in_manager(db: Session, user_id: UUID):
    """Update the user's friends list in the WebSocket manager"""
    from app.services.friend_service import get_friends
    
    friends = get_friends(db, user_id)
    friend_ids = [friend.account_id for friend in friends]
    manager.update_user_friends(user_id, friend_ids)

def search_chat_messages(
    db: Session,
    user_id: UUID,
    friend_id: UUID,
    keyword: str,
    skip: int = 0,
    limit: int = 50
) -> MessageList:
    """Search chat messages between two friends by keyword"""
    # Check if they are friends
    friendship = db.query(Friend).filter(
        ((Friend.sender_id == user_id) & (Friend.receiver_id == friend_id)) |
        ((Friend.sender_id == friend_id) & (Friend.receiver_id == user_id)),
        Friend.status == FriendStatusEnum.accepted
    ).first()
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only search chat messages with your friends"
        )
    # Search messages between the two users containing the keyword
    query = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver)
    ).filter(
        (((Message.sender_id == user_id) & (Message.receiver_id == friend_id)) |
         ((Message.sender_id == friend_id) & (Message.receiver_id == user_id))),
        Message.is_deleted == False,
        Message.content.ilike(f"%{keyword}%")
    )
    total = query.count()
    messages = query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    message_outs = [MessageOut.model_validate(message) for message in messages]
    return MessageList(
        messages=message_outs,
        total=total,
        skip=skip,
        limit=limit
    ) 