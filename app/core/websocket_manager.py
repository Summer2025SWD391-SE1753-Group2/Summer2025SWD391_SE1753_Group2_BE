from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
from uuid import UUID
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: WebSocket}
        self.active_connections: Dict[UUID, WebSocket] = {}
        # Store user's friends for quick lookup: {user_id: Set[friend_ids]}
        self.user_friends: Dict[UUID, Set[UUID]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID):
        """Connect a user to the WebSocket"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to WebSocket")
    
    def disconnect(self, user_id: UUID):
        """Disconnect a user from the WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_friends:
            del self.user_friends[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    def update_user_friends(self, user_id: UUID, friend_ids: List[UUID]):
        """Update the list of friends for a user"""
        self.user_friends[user_id] = set(friend_ids)
        logger.info(f"Updated friends for user {user_id}: {friend_ids}")
    
    def are_friends(self, user_id: UUID, friend_id: UUID) -> bool:
        """Check if two users are friends"""
        if user_id in self.user_friends:
            return friend_id in self.user_friends[user_id]
        return False
    
    async def send_personal_message(self, message: dict, user_id: UUID):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                logger.info(f"Message sent to user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                # Remove the connection if it's broken
                self.disconnect(user_id)
                return False
        return False
    
    async def broadcast_to_friends(self, message: dict, sender_id: UUID):
        """Broadcast a message to all friends of the sender"""
        if sender_id not in self.user_friends:
            return
        
        sent_count = 0
        for friend_id in self.user_friends[sender_id]:
            if await self.send_personal_message(message, friend_id):
                sent_count += 1
        
        logger.info(f"Broadcasted message from {sender_id} to {sent_count} friends")
    
    def get_online_friends(self, user_id: UUID) -> List[UUID]:
        """Get list of online friends for a user"""
        if user_id not in self.user_friends:
            return []
        
        online_friends = []
        for friend_id in self.user_friends[user_id]:
            if friend_id in self.active_connections:
                online_friends.append(friend_id)
        
        return online_friends
    
    def is_user_online(self, user_id: UUID) -> bool:
        """Check if a user is currently online"""
        return user_id in self.active_connections

# Global connection manager instance
manager = ConnectionManager() 