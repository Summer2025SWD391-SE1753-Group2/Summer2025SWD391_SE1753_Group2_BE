#!/usr/bin/env python3
"""
Test script for Group Chat WebSocket functionality
"""

import asyncio
import json
import websockets
import requests
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def login_user(username: str, password: str) -> Optional[str]:
    """Login user and return JWT token"""
    try:
        response = requests.post(f"{API_BASE}/auth/access-token", data={
            "username": "khoipd1",
            "password": "SecurePassword@123"
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed for {username}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error for {username}: {e}")
        return None

def get_user_info(token: str) -> Optional[dict]:
    """Get user information"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/accounts/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get user info: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None

def get_my_groups(token: str) -> Optional[list]:
    """Get user's groups"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/group-chat/my-groups", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get groups: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting groups: {e}")
        return None

def send_group_message_rest(token: str, group_id: str, content: str) -> Optional[dict]:
    """Send message to group via REST API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"content": content}
        response = requests.post(f"{API_BASE}/group-chat/{group_id}/messages", 
                               headers=headers, json=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to send message: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

async def websocket_group_chat_demo(token: str, group_id: str, username: str):
    """Demonstrate WebSocket group chat functionality"""
    ws_url = f"{WS_BASE_URL}/api/v1/group-chat/ws/group/{group_id}?token={token}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"[{username}] Connected to group chat WebSocket!")
            
            # Listen for incoming messages
            async def listen_for_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"[{username}] Received: {data}")
                        
                        if data.get("type") == "group_message":
                            sender_name = data['data']['sender']['username']
                            content = data['data']['content']
                            print(f"[{username}] New message from {sender_name}: {content}")
                            
                        elif data.get("type") == "typing_indicator":
                            user_id = data['user_id']
                            is_typing = data['is_typing']
                            print(f"[{username}] User {user_id} is typing: {is_typing}")
                            
                        elif data.get("type") == "connection_established":
                            print(f"[{username}] Connection established to group: {data['group_name']}")
                            
                        elif data.get("type") == "online_members":
                            member_count = len(data['members'])
                            print(f"[{username}] Online members: {member_count}")
                            
                except websockets.exceptions.ConnectionClosed:
                    print(f"[{username}] WebSocket connection closed")
            
            # Start listening for messages
            listener_task = asyncio.create_task(listen_for_messages())
            
            # Wait a bit for connection to establish
            await asyncio.sleep(2)
            
            # Send a message via WebSocket
            message_data = {
                "type": "send_message",
                "content": f"Hello from {username} via WebSocket! This is a real-time group message."
            }
            await websocket.send(json.dumps(message_data))
            print(f"[{username}] Sent message via WebSocket")
            
            # Send typing indicator
            typing_data = {
                "type": "typing",
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_data))
            print(f"[{username}] Sent typing indicator")
            
            # Wait a bit then stop typing
            await asyncio.sleep(3)
            typing_data["is_typing"] = False
            await websocket.send(json.dumps(typing_data))
            print(f"[{username}] Stopped typing")
            
            # Keep connection alive for a while
            await asyncio.sleep(10)
            
    except Exception as e:
        print(f"[{username}] WebSocket error: {e}")

async def test_multiple_users_group_chat():
    """Test multiple users in the same group chat"""
    print("=== Testing Multiple Users Group Chat ===\n")
    
    # Test credentials (replace with actual user credentials)
    users = [
        {"username": "user1", "password": "password123"},
        {"username": "user2", "password": "password123"},
        {"username": "moderator1", "password": "password123"}
    ]
    
    tokens = []
    user_infos = []
    
    # Login all users
    for user in users:
        print(f"Logging in as {user['username']}...")
        token = login_user(user['username'], user['password'])
        if token:
            tokens.append(token)
            user_info = get_user_info(token)
            if user_info:
                user_infos.append(user_info)
                print(f"Logged in as: {user_info['username']} (ID: {user_info['account_id']})")
        else:
            print(f"Failed to login {user['username']}")
            return
    
    if not tokens:
        print("No users logged in successfully")
        return
    
    # Get groups for first user
    print(f"\nGetting groups for {user_infos[0]['username']}...")
    groups = get_my_groups(tokens[0])
    
    if not groups:
        print("No groups found. Please create a group chat first.")
        return
    
    group = groups[0]  # Use first group
    group_id = group['group_id']
    print(f"Using group: {group['name']} (ID: {group_id})")
    
    # Send a message via REST API first
    print(f"\nSending message via REST API...")
    message = send_group_message_rest(tokens[0], group_id, "Hello from REST API! This is a test message.")
    if message:
        print(f"Message sent successfully! Message ID: {message['message_id']}")
    
    # Connect multiple users to WebSocket
    print(f"\nConnecting multiple users to WebSocket...")
    tasks = []
    
    for i, (token, user_info) in enumerate(zip(tokens, user_infos)):
        task = websocket_group_chat_demo(token, group_id, user_info['username'])
        tasks.append(task)
    
    # Run all WebSocket connections concurrently
    await asyncio.gather(*tasks)

def main():
    """Main test function"""
    print("=== Group Chat WebSocket Test Script ===\n")
    
    # Test single user first
    print("1. Testing single user WebSocket connection...")
    
    username = "user1"
    password = "password123"
    
    print(f"Logging in as {username}...")
    token = login_user(username, password)
    if not token:
        print("Failed to login")
        return
    
    user_info = get_user_info(token)
    print(f"Logged in as: {user_info['username']} (ID: {user_info['account_id']})")
    
    # Get groups
    print("\nGetting groups...")
    groups = get_my_groups(token)
    if not groups:
        print("No groups found. Please create a group chat first.")
        return
    
    group = groups[0]  # Use first group
    group_id = group['group_id']
    print(f"Using group: {group['name']} (ID: {group_id})")
    
    # Test WebSocket functionality
    print("\n2. Testing WebSocket functionality...")
    print("This will connect to WebSocket and send a real-time message...")
    
    # Run the WebSocket demo
    asyncio.run(websocket_group_chat_demo(token, group_id, user_info['username']))
    
    # Test multiple users
    print("\n3. Testing multiple users...")
    asyncio.run(test_multiple_users_group_chat())

if __name__ == "__main__":
    main() 