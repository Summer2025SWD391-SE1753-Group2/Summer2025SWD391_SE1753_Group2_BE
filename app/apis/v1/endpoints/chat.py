from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import json
import logging

from app.db.models.account import Account
from app.core.deps import get_db
from app.core.websocket_deps import get_current_user_websocket
from app.core.websocket_manager import manager
from app.schemas.message import MessageCreate, MessageOut, MessageList, ChatHistoryRequest
from app.schemas.common import AccountSummary
from app.services.message_service import (
    send_message, get_chat_history, mark_message_as_read, 
    delete_message, get_unread_message_count, update_user_friends_in_manager
)
from app.services.friend_service import get_friends
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket endpoint for real-time chat
@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    try:
        # Authenticate user
        current_user = await get_current_user_websocket(websocket)
        
        # Connect to WebSocket
        await manager.connect(websocket, current_user.account_id)
        
        # Update user's friends list in manager
        db = SessionLocal()
        try:
            update_user_friends_in_manager(db, current_user.account_id)
            
            # Send connection confirmation
            await websocket.send_text(json.dumps({
                "type": "connection_established",
                "user_id": str(current_user.account_id),
                "message": "Connected to chat server"
            }))
            
            # Send online friends list
            online_friends = manager.get_online_friends(current_user.account_id)
            await websocket.send_text(json.dumps({
                "type": "online_friends",
                "friends": [str(friend_id) for friend_id in online_friends]
            }))
            
        finally:
            db.close()
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "send_message":
                    # Handle sending a message
                    await handle_send_message(message_data, current_user.account_id)
                    
                elif message_data.get("type") == "mark_read":
                    # Handle marking message as read
                    await handle_mark_read(message_data, current_user.account_id)
                    
                elif message_data.get("type") == "typing":
                    # Handle typing indicator
                    await handle_typing_indicator(message_data, current_user.account_id)
                    
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
        logger.info(f"WebSocket disconnected for user {current_user.account_id if 'current_user' in locals() else 'unknown'}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if 'current_user' in locals():
            manager.disconnect(current_user.account_id)

async def handle_send_message(message_data: dict, sender_id: UUID):
    """Handle sending a message via WebSocket"""
    try:
        receiver_id = UUID(message_data.get("receiver_id"))
        content = message_data.get("content", "").strip()
        
        if not content:
            return
        
        # Create message data
        msg_data = MessageCreate(
            receiver_id=receiver_id,
            content=content
        )
        
        # Send message
        db = SessionLocal()
        try:
            message = await send_message(db, msg_data, sender_id)
            
            # Send confirmation back to sender
            await manager.send_personal_message({
                "type": "message_sent",
                "message_id": str(message.message_id),
                "status": "sent"
            }, sender_id)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "Failed to send message"
        }, sender_id)

async def handle_mark_read(message_data: dict, user_id: UUID):
    """Handle marking a message as read"""
    try:
        message_id = UUID(message_data.get("message_id"))
        
        db = SessionLocal()
        try:
            message = mark_message_as_read(db, message_id, user_id)
            
            # Notify sender that message was read
            await manager.send_personal_message({
                "type": "message_read",
                "message_id": str(message_id),
                "read_by": str(user_id)
            }, message.sender_id)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")

async def handle_typing_indicator(message_data: dict, user_id: UUID):
    """Handle typing indicator"""
    try:
        receiver_id = UUID(message_data.get("receiver_id"))
        is_typing = message_data.get("is_typing", False)
        
        # Check if they are friends
        if not manager.are_friends(user_id, receiver_id):
            return
        
        # Send typing indicator to receiver
        await manager.send_personal_message({
            "type": "typing_indicator",
            "user_id": str(user_id),
            "is_typing": is_typing
        }, receiver_id)
        
    except Exception as e:
        logger.error(f"Error handling typing indicator: {e}")

# REST endpoints for chat functionality

@router.post("/messages/", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message_endpoint(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Send a message to a friend (REST endpoint)"""
    return await send_message(db, message_data, current_user.account_id)

@router.get("/messages/history/{friend_id}", response_model=MessageList)
def get_chat_history_endpoint(
    friend_id: UUID,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Get chat history with a friend"""
    return get_chat_history(db, current_user.account_id, friend_id, skip=skip, limit=limit)

@router.put("/messages/{message_id}/read", response_model=MessageOut)
def mark_message_as_read_endpoint(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Mark a message as read"""
    return mark_message_as_read(db, message_id, current_user.account_id)

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_endpoint(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Delete a message (only sender can delete)"""
    delete_message(db, message_id, current_user.account_id)
    return {"message": "Message deleted successfully"}

@router.get("/messages/unread-count")
def get_unread_message_count_endpoint(
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Get count of unread messages"""
    count = get_unread_message_count(db, current_user.account_id)
    return {"unread_count": count}

@router.get("/friends/online")
def get_online_friends_endpoint(
    current_user: Account = Depends(check_roles([RoleNameEnum.user]))
):
    """Get list of online friends"""
    online_friends = manager.get_online_friends(current_user.account_id)
    return {"online_friends": [str(friend_id) for friend_id in online_friends]}

# Import SessionLocal for WebSocket endpoint
from app.db.database import SessionLocal 