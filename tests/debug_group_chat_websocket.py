#!/usr/bin/env python3
"""
Debug Script for Group Chat WebSocket Issues
"""

import asyncio
import json
import websockets
import requests
import logging
from typing import Optional

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def login_user(username: str, password: str) -> Optional[str]:
    """Login user and return JWT token"""
    try:
        response = requests.post(f"{API_BASE}/auth/access-token", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed for {username}: {response.status_code} - {response.text}")
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
            print(f"Failed to get user info: {response.status_code} - {response.text}")
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
            print(f"Failed to get groups: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting groups: {e}")
        return None

def get_group_members(token: str, group_id: str) -> Optional[list]:
    """Get group members"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/group-chat/{group_id}/members", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get group members: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting group members: {e}")
        return None

async def debug_websocket_connection(token: str, group_id: str, username: str):
    """Debug WebSocket connection and events"""
    ws_url = f"{WS_BASE_URL}/api/v1/group-chat/ws/group/{group_id}?token={token}"
    
    print(f"\n🔍 Debugging WebSocket for {username}")
    print(f"URL: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ [{username}] WebSocket connected successfully!")
            
            # Listen for incoming messages
            async def listen_for_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"📥 [{username}] Received: {json.dumps(data, indent=2)}")
                        
                        if data.get("type") == "connection_established":
                            print(f"✅ [{username}] Connection established to group: {data.get('group_name')}")
                            
                        elif data.get("type") == "online_members":
                            member_count = len(data.get('members', []))
                            print(f"👥 [{username}] Online members: {member_count} - {data.get('members')}")
                            
                        elif data.get("type") == "group_message":
                            sender_name = data['data']['sender']['username']
                            content = data['data']['content']
                            print(f"💬 [{username}] New message from {sender_name}: {content}")
                            
                        elif data.get("type") == "typing_indicator":
                            user_id = data['user_id']
                            is_typing = data['is_typing']
                            print(f"⌨️ [{username}] User {user_id} is typing: {is_typing}")
                            
                        elif data.get("type") == "error":
                            print(f"❌ [{username}] Error: {data.get('message')}")
                            
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"🔌 [{username}] WebSocket connection closed: {e}")
                except Exception as e:
                    print(f"❌ [{username}] Error in message listener: {e}")
            
            # Start listening for messages
            listener_task = asyncio.create_task(listen_for_messages())
            
            # Wait for connection events
            await asyncio.sleep(3)
            
            # Send a test message
            print(f"\n📤 [{username}] Sending test message...")
            message_data = {
                "type": "send_message",
                "content": f"Test message from {username} at {asyncio.get_event_loop().time()}"
            }
            await websocket.send(json.dumps(message_data))
            print(f"✅ [{username}] Test message sent")
            
            # Send typing indicator
            print(f"\n⌨️ [{username}] Sending typing indicator...")
            typing_data = {
                "type": "typing",
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_data))
            print(f"✅ [{username}] Typing indicator sent")
            
            # Wait a bit then stop typing
            await asyncio.sleep(2)
            typing_data["is_typing"] = False
            await websocket.send(json.dumps(typing_data))
            print(f"✅ [{username}] Typing stopped")
            
            # Keep connection alive for a while
            await asyncio.sleep(10)
            
    except Exception as e:
        print(f"❌ [{username}] WebSocket error: {e}")

async def debug_multiple_users():
    """Debug multiple users connecting to the same group"""
    print("🐛 DEBUG: Multiple Users Group Chat")
    print("=" * 50)
    
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
        print(f"\n🔐 Logging in as {user['username']}...")
        token = login_user(user['username'], user['password'])
        if token:
            tokens.append(token)
            user_info = get_user_info(token)
            if user_info:
                user_infos.append(user_info)
                print(f"✅ Logged in as: {user_info['username']} (ID: {user_info['account_id']})")
            else:
                print(f"❌ Failed to get user info for {user['username']}")
        else:
            print(f"❌ Failed to login {user['username']}")
    
    if not tokens:
        print("❌ No users logged in successfully")
        return
    
    # Get groups for first user
    print(f"\n📋 Getting groups for {user_infos[0]['username']}...")
    groups = get_my_groups(tokens[0])
    
    if not groups:
        print("❌ No groups found. Please create a group chat first.")
        return
    
    group = groups[0]  # Use first group
    group_id = group['group_id']
    print(f"✅ Using group: {group['name']} (ID: {group_id})")
    
    # Get group members
    print(f"\n👥 Getting group members...")
    members = get_group_members(tokens[0], group_id)
    if members:
        print(f"✅ Group has {len(members)} members:")
        for member in members:
            print(f"  - {member['username']} ({member['role']})")
    
    # Connect multiple users to WebSocket
    print(f"\n🔌 Connecting multiple users to WebSocket...")
    tasks = []
    
    for i, (token, user_info) in enumerate(zip(tokens, user_infos)):
        task = debug_websocket_connection(token, group_id, user_info['username'])
        tasks.append(task)
    
    # Run all WebSocket connections concurrently
    await asyncio.gather(*tasks)

def main():
    """Main debug function"""
    print("🐛 GROUP CHAT WEBSOCKET DEBUG SCRIPT")
    print("=" * 50)
    
    # Test single user first
    print("1. Testing single user WebSocket connection...")
    
    username = "user1"
    password = "password123"
    
    print(f"🔐 Logging in as {username}...")
    token = login_user(username, password)
    if not token:
        print("❌ Failed to login")
        return
    
    user_info = get_user_info(token)
    print(f"✅ Logged in as: {user_info['username']} (ID: {user_info['account_id']})")
    
    # Get groups
    print("\n📋 Getting groups...")
    groups = get_my_groups(token)
    if not groups:
        print("❌ No groups found. Please create a group chat first.")
        return
    
    group = groups[0]  # Use first group
    group_id = group['group_id']
    print(f"✅ Using group: {group['name']} (ID: {group_id})")
    
    # Test WebSocket functionality
    print("\n2. Testing WebSocket functionality...")
    asyncio.run(debug_websocket_connection(token, group_id, user_info['username']))
    
    # Test multiple users
    print("\n3. Testing multiple users...")
    asyncio.run(debug_multiple_users())

if __name__ == "__main__":
    main() 