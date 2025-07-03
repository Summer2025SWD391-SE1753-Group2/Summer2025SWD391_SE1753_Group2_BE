#!/usr/bin/env python3
"""
Test WebSocket Group Chat with Real Users
"""

import asyncio
import json
import websockets
import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Real user credentials
TEST_USERS = [
    {
        "username": "khoipd11",
        "password": "SecurePassword@123",
        "role": "moderator"
    },
    {
        "username": "khoipd10", 
        "password": "SecurePassword@123",
        "role": "user"
    }
]

# Group information
TOPIC_ID = "91bbc9c4-a815-4dd5-ae57-b22ad66f0272"
GROUP_ID = "aac94f36-4f7a-432a-b417-bb2bd0f1ac76"

def login_user(username: str, password: str):
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
            print(f"❌ Login failed for {username}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error for {username}: {e}")
        return None

def get_user_info(token: str):
    """Get user information"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/accounts/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get user info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return None

def get_group_info(token: str, group_id: str):
    """Get group information"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/group-chat/{group_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get group info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting group info: {e}")
        return None

def get_group_members(token: str, group_id: str):
    """Get group members"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/group-chat/{group_id}/members", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get group members: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting group members: {e}")
        return None

async def test_websocket_connection(token: str, username: str, role: str):
    """Test WebSocket connection for a user"""
    ws_url = f"{WS_BASE_URL}/api/v1/group-chat/ws/group/{GROUP_ID}?token={token}"
    
    print(f"\n🔍 Testing WebSocket for {username} ({role})")
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
                            
                        elif data.get("type") == "message_sent":
                            print(f"✅ [{username}] Message sent confirmation: {data.get('message_id')}")
                            
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
                "content": f"Hello from {username} ({role}) at {time.time()}"
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
            await asyncio.sleep(15)
            
    except Exception as e:
        print(f"❌ [{username}] WebSocket error: {e}")

async def test_multiple_users():
    """Test multiple users connecting to the same group"""
    print("🐛 TESTING: Real Users Group Chat WebSocket")
    print("=" * 60)
    print(f"Topic ID: {TOPIC_ID}")
    print(f"Group ID: {GROUP_ID}")
    print("=" * 60)
    
    tokens = []
    user_infos = []
    
    # Login all users
    for user_data in TEST_USERS:
        print(f"\n🔐 Logging in as {user_data['username']} ({user_data['role']})...")
        token = login_user(user_data['username'], user_data['password'])
        if token:
            tokens.append(token)
            user_info = get_user_info(token)
            if user_info:
                user_infos.append({
                    'username': user_data['username'],
                    'role': user_data['role'],
                    'user_info': user_info
                })
                print(f"✅ Logged in as: {user_info['username']} (ID: {user_info['account_id']})")
            else:
                print(f"❌ Failed to get user info for {user_data['username']}")
        else:
            print(f"❌ Failed to login {user_data['username']}")
    
    if not tokens:
        print("❌ No users logged in successfully")
        return
    
    # Get group info
    print(f"\n📋 Getting group information...")
    group_info = get_group_info(tokens[0], GROUP_ID)
    if group_info:
        print(f"✅ Group: {group_info['name']}")
        print(f"✅ Description: {group_info['description']}")
        print(f"✅ Leader: {group_info['leader_name']}")
        print(f"✅ Member count: {group_info['member_count']}")
    else:
        print("❌ Failed to get group info")
        return
    
    # Get group members
    print(f"\n👥 Getting group members...")
    members = get_group_members(tokens[0], GROUP_ID)
    if members:
        print(f"✅ Group has {len(members)} members:")
        for member in members:
            print(f"  - {member['username']} ({member['role']})")
    else:
        print("❌ Failed to get group members")
        return
    
    # Connect multiple users to WebSocket
    print(f"\n🔌 Connecting multiple users to WebSocket...")
    tasks = []
    
    for user_data in user_infos:
        task = test_websocket_connection(tokens[len(tasks)], user_data['username'], user_data['role'])
        tasks.append(task)
    
    # Run all WebSocket connections concurrently
    await asyncio.gather(*tasks)

def main():
    """Main test function"""
    print("🐛 REAL USERS WEBSOCKET GROUP CHAT TEST")
    print("=" * 60)
    
    # Test multiple users
    asyncio.run(test_multiple_users())

if __name__ == "__main__":
    main() 