#!/usr/bin/env python3
"""
Add user to group for testing
"""

import requests

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# User credentials
MODERATOR_USERNAME = "khoipd11"
MODERATOR_PASSWORD = "SecurePassword@123"
USER_TO_ADD = "khoipd8"

# Group information
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

def get_user_info(token: str, username: str):
    """Get user information by username"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/accounts/search?username={username}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
            else:
                print(f"❌ User {username} not found")
                return None
        else:
            print(f"❌ Failed to search user: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error searching user: {e}")
        return None

def add_member_to_group(token: str, group_id: str, account_id: str):
    """Add member to group"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "account_id": account_id,
            "role": "member"
        }
        
        response = requests.post(f"{API_BASE}/group-chat/{group_id}/members", headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Added member {account_id} to group {group_id}")
            return response.json()
        else:
            print(f"❌ Failed to add member: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error adding member: {e}")
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

def main():
    """Main function"""
    print("🔧 Adding user to group for testing")
    print("=" * 50)
    
    # Login as moderator
    print(f"🔐 Logging in as {MODERATOR_USERNAME}...")
    token = login_user(MODERATOR_USERNAME, MODERATOR_PASSWORD)
    if not token:
        print("❌ Failed to login as moderator")
        return
    
    print(f"✅ Logged in as {MODERATOR_USERNAME}")
    
    # Get current group members
    print(f"\n👥 Getting current group members...")
    members = get_group_members(token, GROUP_ID)
    if members:
        print(f"✅ Group has {len(members)} members:")
        for member in members:
            print(f"  - {member['username']} ({member['role']})")
    
    # Check if user is already in group
    user_in_group = False
    if members:
        for member in members:
            if member['username'] == USER_TO_ADD:
                user_in_group = True
                print(f"✅ User {USER_TO_ADD} is already in the group")
                break
    
    if not user_in_group:
        # Get user info
        print(f"\n🔍 Getting user info for {USER_TO_ADD}...")
        user_info = get_user_info(token, USER_TO_ADD)
        if not user_info:
            print(f"❌ User {USER_TO_ADD} not found")
            return
        
        print(f"✅ Found user: {user_info['username']} (ID: {user_info['account_id']})")
        
        # Add user to group
        print(f"\n➕ Adding {USER_TO_ADD} to group...")
        result = add_member_to_group(token, GROUP_ID, user_info['account_id'])
        if result:
            print(f"✅ Successfully added {USER_TO_ADD} to group")
        else:
            print(f"❌ Failed to add {USER_TO_ADD} to group")
            return
    
    # Get updated group members
    print(f"\n👥 Getting updated group members...")
    members = get_group_members(token, GROUP_ID)
    if members:
        print(f"✅ Group now has {len(members)} members:")
        for member in members:
            print(f"  - {member['username']} ({member['role']})")
    
    print(f"\n✅ Ready for WebSocket testing!")
    print(f"Run: python test_websocket_real_users.py")

if __name__ == "__main__":
    main() 