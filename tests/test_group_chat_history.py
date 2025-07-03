#!/usr/bin/env python3
"""
Test Group Chat Message History API
Kiểm tra API lấy lịch sử tin nhắn của group chat
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
GROUP_ID = "aac94f36-4f7a-432a-b417-bb2bd0f1ac76"  # Test 4 group

def login_user(username: str, password: str):
    """Login user and return access token (using /auth/access-token)"""
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/access-token", data=data)
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"❌ Login failed for {username}: {response.status_code}")
        print(response.text)
        return None

def get_group_messages(token: str, group_id: str, skip: int = 0, limit: int = 50):
    """Get group chat message history"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/group-chat/{group_id}/messages",
        headers=headers,
        params={"skip": skip, "limit": limit}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get messages: {response.status_code}")
        print(response.text)
        return None

def test_group_chat_history():
    """Test group chat message history functionality"""
    print("🐛 GROUP CHAT MESSAGE HISTORY TEST")
    print("=" * 60)
    
    # Test with khoipd11 (moderator)
    print("🔐 Testing with khoipd11 (moderator)...")
    token1 = login_user("khoipd11", "SecurePassword@123")
    
    if not token1:
        print("❌ Cannot continue without valid token")
        return
    
    print("✅ Logged in as khoipd11")
    
    # Get message history
    print(f"\n📋 Getting message history for group {GROUP_ID}...")
    history = get_group_messages(token1, GROUP_ID)
    
    if history:
        print("✅ Message history retrieved successfully!")
        print(f"📊 Total messages: {history['total']}")
        print(f"📄 Messages in response: {len(history['messages'])}")
        print(f"🔢 Skip: {history['skip']}, Limit: {history['limit']}")
        
        print("\n📝 Recent messages:")
        for i, msg in enumerate(history['messages'][:5]):  # Show first 5 messages
            print(f"  {i+1}. [{msg['created_at']}] {msg['sender']['username']}: {msg['content'][:50]}...")
        
        if len(history['messages']) > 5:
            print(f"  ... and {len(history['messages']) - 5} more messages")
    
    # Test pagination
    print(f"\n📄 Testing pagination (skip=5, limit=10)...")
    paginated_history = get_group_messages(token1, GROUP_ID, skip=5, limit=10)
    
    if paginated_history:
        print("✅ Pagination works!")
        print(f"📊 Total: {paginated_history['total']}")
        print(f"📄 Messages: {len(paginated_history['messages'])}")
        print(f"🔢 Skip: {paginated_history['skip']}, Limit: {paginated_history['limit']}")
    
    # Test with khoipd10 (user)
    print(f"\n🔐 Testing with khoipd10 (user)...")
    token2 = login_user("khoipd10", "SecurePassword@123")
    
    if token2:
        print("✅ Logged in as khoipd10")
        
        # Get message history
        print(f"\n📋 Getting message history for group {GROUP_ID}...")
        history2 = get_group_messages(token2, GROUP_ID)
        
        if history2:
            print("✅ Message history retrieved successfully!")
            print(f"📊 Total messages: {history2['total']}")
            print(f"📄 Messages in response: {len(history2['messages'])}")
            
            # Verify both users see the same messages
            if history and history2:
                if history['total'] == history2['total']:
                    print("✅ Both users see the same message count!")
                else:
                    print("❌ Users see different message counts!")
    
    print("\n" + "=" * 60)
    print("🎉 Group Chat Message History Test Completed!")

if __name__ == "__main__":
    test_group_chat_history() 