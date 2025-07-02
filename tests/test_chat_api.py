#!/usr/bin/env python3
"""
Test script for the Chat API
This script demonstrates how to use the real-time chat feature
"""

import requests
import json
import asyncio
import websockets
import time
from uuid import UUID

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/api/v1/chat/ws/chat"

def login_user(username: str, password: str) -> str:
    """Login and get access token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/access-token", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def get_user_info(token: str) -> dict:
    """Get current user information"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/accounts/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get user info: {response.text}")
        return None

def get_friends(token: str) -> list:
    """Get user's friends list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/friends/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get friends: {response.text}")
        return []

def send_message_rest(token: str, receiver_id: str, content: str) -> dict:
    """Send a message using REST API"""
    headers = {"Authorization": f"Bearer {token}"}
    message_data = {
        "receiver_id": receiver_id,
        "content": content
    }
    
    response = requests.post(f"{BASE_URL}/chat/messages/", json=message_data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to send message: {response.text}")
        return None

def get_chat_history(token: str, friend_id: str) -> dict:
    """Get chat history with a friend"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/chat/messages/history/{friend_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get chat history: {response.text}")
        return None

async def websocket_chat_demo(token: str, friend_id: str):
    """Demonstrate WebSocket chat functionality"""
    ws_url_with_token = f"{WS_URL}?token={token}"
    
    try:
        async with websockets.connect(ws_url_with_token) as websocket:
            print("Connected to WebSocket chat!")
            
            # Listen for incoming messages
            async def listen_for_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"Received: {data}")
                        
                        if data.get("type") == "new_message":
                            print(f"New message from {data['message']['sender']['username']}: {data['message']['content']}")
                            
                        elif data.get("type") == "typing_indicator":
                            print(f"User {data['user_id']} is typing: {data['is_typing']}")
                            
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
            
            # Start listening for messages
            listener_task = asyncio.create_task(listen_for_messages())
            
            # Send a message via WebSocket
            message_data = {
                "type": "send_message",
                "receiver_id": friend_id,
                "content": "Hello from WebSocket! This is a real-time message."
            }
            await websocket.send(json.dumps(message_data))
            print("Sent message via WebSocket")
            
            # Send typing indicator
            typing_data = {
                "type": "typing",
                "receiver_id": friend_id,
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_data))
            print("Sent typing indicator")
            
            # Wait a bit, then stop typing
            await asyncio.sleep(2)
            typing_data["is_typing"] = False
            await websocket.send(json.dumps(typing_data))
            print("Stopped typing indicator")
            
            # Keep connection alive for a while
            await asyncio.sleep(10)
            
            # Cancel the listener task
            listener_task.cancel()
            
    except Exception as e:
        print(f"WebSocket error: {e}")

def main():
    """Main test function"""
    print("=== Chat API Test Script ===\n")
    
    # Test credentials (replace with actual user credentials)
    username1 = "user1"
    password1 = "password123"
    username2 = "user2" 
    password2 = "password123"
    
    print("1. Testing REST API endpoints...")
    
    # Login user 1
    print(f"\nLogging in as {username1}...")
    token1 = login_user(username1, password1)
    if not token1:
        print("Failed to login user 1")
        return
    
    user1_info = get_user_info(token1)
    print(f"Logged in as: {user1_info['username']} (ID: {user1_info['account_id']})")
    
    # Get friends
    print("\nGetting friends list...")
    friends = get_friends(token1)
    if not friends:
        print("No friends found. Please add some friends first.")
        return
    
    friend = friends[0]  # Use first friend
    friend_id = friend['account_id']
    print(f"Using friend: {friend['username']} (ID: {friend_id})")
    
    # Send a message via REST API
    print("\nSending message via REST API...")
    message = send_message_rest(token1, friend_id, "Hello from REST API! This is a test message.")
    if message:
        print(f"Message sent successfully! Message ID: {message['message_id']}")
    
    # Get chat history
    print("\nGetting chat history...")
    history = get_chat_history(token1, friend_id)
    if history:
        print(f"Found {history['total']} messages in chat history")
        for msg in history['messages'][:3]:  # Show first 3 messages
            print(f"- {msg['sender']['username']}: {msg['content']}")
    
    # Test WebSocket functionality
    print("\n2. Testing WebSocket functionality...")
    print("This will connect to WebSocket and send a real-time message...")
    
    try:
        asyncio.run(websocket_chat_demo(token1, friend_id))
    except KeyboardInterrupt:
        print("\nWebSocket test interrupted by user")
    except Exception as e:
        print(f"WebSocket test failed: {e}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main() 