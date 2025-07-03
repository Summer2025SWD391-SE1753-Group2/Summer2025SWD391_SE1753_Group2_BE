#!/usr/bin/env python3
"""
Create test data for WebSocket group chat debugging
"""

import requests
import json
from uuid import UUID

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def create_test_user(username: str, password: str, email: str, full_name: str):
    """Create a test user"""
    try:
        data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "phone_number": "0123456789"
        }
        
        response = requests.post(f"{API_BASE}/accounts/", json=data)
        
        if response.status_code == 201:
            print(f"✅ Created user: {username}")
            return response.json()
        else:
            print(f"❌ Failed to create user {username}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating user {username}: {e}")
        return None

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

def create_test_topic(token: str):
    """Create a test topic"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": "Test Topic for Group Chat",
            "description": "A test topic for debugging group chat WebSocket"
        }
        
        response = requests.post(f"{API_BASE}/topics/", headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Created topic: {data['name']}")
            return response.json()
        else:
            print(f"❌ Failed to create topic: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating topic: {e}")
        return None

def create_test_group(token: str, topic_id: str):
    """Create a test group chat"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "topic_id": topic_id,
            "name": "Test Group Chat",
            "description": "A test group for debugging WebSocket",
            "max_members": 10
        }
        
        response = requests.post(f"{API_BASE}/group-chat/create", headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Created group: {data['name']}")
            return response.json()
        else:
            print(f"❌ Failed to create group: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating group: {e}")
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

def main():
    """Main function to create test data"""
    print("🔧 Creating Test Data for WebSocket Group Chat Debugging")
    print("=" * 60)
    
    # Test users data
    test_users = [
        {
            "username": "user1",
            "password": "password123",
            "email": "user1@test.com",
            "full_name": "Test User 1"
        },
        {
            "username": "user2", 
            "password": "password123",
            "email": "user2@test.com",
            "full_name": "Test User 2"
        },
        {
            "username": "moderator1",
            "password": "password123", 
            "email": "moderator1@test.com",
            "full_name": "Test Moderator 1"
        }
    ]
    
    created_users = []
    
    # Create test users
    print("\n👥 Creating test users...")
    for user_data in test_users:
        user = create_test_user(**user_data)
        if user:
            created_users.append(user)
    
    if not created_users:
        print("❌ No users created. Cannot proceed.")
        return
    
    # Login as moderator to create topic and group
    print(f"\n🔐 Logging in as {created_users[0]['username']}...")
    token = login_user(created_users[0]['username'], created_users[0]['password'])
    if not token:
        print("❌ Failed to login. Cannot create topic/group.")
        return
    
    user_info = get_user_info(token)
    print(f"✅ Logged in as: {user_info['username']} (Role: {user_info['role']['role_name']})")
    
    # Create topic
    print(f"\n📝 Creating test topic...")
    topic = create_test_topic(token)
    if not topic:
        print("❌ Failed to create topic. Cannot proceed.")
        return
    
    # Create group
    print(f"\n👥 Creating test group...")
    group = create_test_group(token, topic['topic_id'])
    if not group:
        print("❌ Failed to create group. Cannot proceed.")
        return
    
    # Add other users to group
    print(f"\n➕ Adding users to group...")
    for user in created_users[1:]:  # Skip the first user (already leader)
        add_member_to_group(token, group['group_id'], user['account_id'])
    
    # Test login for all users
    print(f"\n🔐 Testing login for all users...")
    tokens = {}
    for user in created_users:
        user_token = login_user(user['username'], user['password'])
        if user_token:
            tokens[user['username']] = user_token
            print(f"✅ {user['username']} can login")
        else:
            print(f"❌ {user['username']} cannot login")
    
    # Print summary
    print(f"\n" + "=" * 60)
    print("📋 TEST DATA SUMMARY")
    print("=" * 60)
    print(f"✅ Created {len(created_users)} users:")
    for user in created_users:
        print(f"  - {user['username']} ({user['email']})")
    
    print(f"\n✅ Created topic: {topic['name']} (ID: {topic['topic_id']})")
    print(f"✅ Created group: {group['name']} (ID: {group['group_id']})")
    
    print(f"\n🔑 Test credentials:")
    for user in created_users:
        print(f"  - {user['username']}: password123")
    
    print(f"\n🧪 Ready for WebSocket testing!")
    print(f"Run: python debug_group_chat_websocket.py")

if __name__ == "__main__":
    main() 