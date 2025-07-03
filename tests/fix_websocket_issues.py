#!/usr/bin/env python3
"""
Fix WebSocket Group Chat Issues
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server responded with {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

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

def get_my_groups(token: str):
    """Get user's groups"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/group-chat/my-groups", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get groups: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting groups: {e}")
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

async def test_websocket_basic(token: str, group_id: str, username: str):
    """Basic WebSocket test"""
    ws_url = f"{WS_BASE_URL}/api/v1/group-chat/ws/group/{group_id}?token={token}"
    
    print(f"\n🔍 Basic WebSocket test for {username}")
    print(f"URL: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ [{username}] WebSocket connected!")
            
            # Wait for initial messages
            await asyncio.sleep(2)
            
            # Try to receive messages
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📥 [{username}] Received: {json.dumps(data, indent=2)}")
                
                if data.get("type") == "connection_established":
                    print(f"✅ [{username}] Connection established!")
                    
                if data.get("type") == "online_members":
                    member_count = len(data.get('members', []))
                    print(f"👥 [{username}] Online members: {member_count}")
                    
            except asyncio.TimeoutError:
                print(f"⏰ [{username}] No messages received within 5 seconds")
            
            # Send a simple message
            print(f"\n📤 [{username}] Sending test message...")
            message_data = {
                "type": "send_message",
                "content": f"Hello from {username}!"
            }
            await websocket.send(json.dumps(message_data))
            print(f"✅ [{username}] Message sent")
            
            # Wait for response
            await asyncio.sleep(3)
            
    except Exception as e:
        print(f"❌ [{username}] WebSocket error: {e}")

def diagnose_issues():
    """Diagnose common WebSocket issues"""
    print("🔍 DIAGNOSING WEBSOCKET ISSUES")
    print("=" * 50)
    
    # 1. Check server status
    print("\n1. Checking server status...")
    if not check_server_status():
        print("❌ Server is not running. Please start the server first.")
        return False
    
    # 2. Test login
    print("\n2. Testing login...")
    username = "khoipd11"  # Replace with actual username
    password = "password123"  # Replace with actual password
    
    token = login_user(username, password)
    if not token:
        print("❌ Login failed. Please check credentials.")
        return False
    
    user_info = get_user_info(token)
    if not user_info:
        print("❌ Cannot get user info.")
        return False
    
    print(f"✅ Logged in as: {user_info['username']} (ID: {user_info['account_id']})")
    
    # 3. Get groups
    print("\n3. Getting user groups...")
    groups = get_my_groups(token)
    if not groups:
        print("❌ No groups found. User needs to be in a group.")
        return False
    
    group = groups[0]
    print(f"✅ Found group: {group['name']} (ID: {group['group_id']})")
    
    # 4. Get group members
    print("\n4. Getting group members...")
    members = get_group_members(token, group['group_id'])
    if members:
        print(f"✅ Group has {len(members)} members:")
        for member in members:
            print(f"  - {member['username']} ({member['role']})")
    else:
        print("❌ Cannot get group members.")
        return False
    
    # 5. Test WebSocket
    print("\n5. Testing WebSocket connection...")
    asyncio.run(test_websocket_basic(token, group['group_id'], user_info['username']))
    
    return True

def main():
    """Main function"""
    print("🔧 WEBSOCKET GROUP CHAT ISSUE DIAGNOSIS")
    print("=" * 50)
    
    # Diagnose issues
    success = diagnose_issues()
    
    if success:
        print("\n✅ Diagnosis completed. Check the logs above for issues.")
    else:
        print("\n❌ Diagnosis failed. Please fix the issues above.")

if __name__ == "__main__":
    main() 