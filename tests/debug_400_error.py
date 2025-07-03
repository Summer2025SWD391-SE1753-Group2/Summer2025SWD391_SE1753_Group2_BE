#!/usr/bin/env python3
"""
Debug script for 400 error when creating group chat
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json"
}

def login_as_moderator() -> str:
    """Login as moderator and return access token"""
    login_data = {
        "username": "khoipd11",
        "password": "SecurePassword@123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/access-token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_create_group_with_400_debug(token: str, topic_id: str):
    """Test creating group and debug 400 error"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    group_data = {
        "topic_id": topic_id,
        "name": "Test Group Debug 400",
        "description": "Test description",
        "max_members": 50
    }
    
    print(f"\n=== Testing Create Group with Topic: {topic_id} ===")
    print(f"Request data: {json.dumps(group_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=group_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Group created successfully")
        result = response.json()
        print(f"Group ID: {result['group_id']}")
        print(f"Group Name: {result['name']}")
        print(f"Member Count: {result['member_count']}")
        return result
    elif response.status_code == 400:
        print("❌ 400 Bad Request")
        error_detail = response.json()
        print(f"Error: {json.dumps(error_detail, indent=2)}")
        
        # Debug based on error message
        if "Topic already has a chat group" in error_detail.get("detail", ""):
            print("\n🔍 Debug: Topic already has a chat group")
            print("Solution: Choose another topic or join existing group")
            
            # Get existing group info
            test_get_existing_group(token, topic_id)
        else:
            print(f"\n🔍 Debug: Unknown 400 error - {error_detail.get('detail', '')}")
        
        return None
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_existing_group(token: str, topic_id: str):
    """Get existing group for the topic"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    print(f"\n=== Getting Existing Group for Topic: {topic_id} ===")
    
    # Get topics with groups
    response = requests.get(f"{BASE_URL}/api/v1/group-chat/topics/with-groups", headers=headers)
    if response.status_code == 200:
        topics = response.json()
        for topic in topics:
            if topic["topic_id"] == topic_id:
                print(f"✅ Found existing group:")
                print(f"  - Group ID: {topic['group_id']}")
                print(f"  - Group Name: {topic['group_name']}")
                print(f"  - Member Count: {topic['member_count']}/{topic['max_members']}")
                print(f"  - Created: {topic['created_at']}")
                return topic
    
    print("❌ No existing group found for this topic")

def test_available_topics(token: str):
    """Test getting available topics"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/group-chat/topics/available", headers=headers)
    print(f"\n=== Available Topics ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        topics = response.json()
        print(f"✅ Found {len(topics)} available topics:")
        for topic in topics:
            print(f"  - {topic['topic_name']} (ID: {topic['topic_id']})")
        return topics
    else:
        print(f"❌ Failed: {response.text}")
        return []

def test_topic_check(token: str, topic_id: str):
    """Test topic availability check"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/group-chat/topics/{topic_id}/check", headers=headers)
    print(f"\n=== Topic Check for {topic_id} ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Topic check result: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"❌ Topic check failed: {response.text}")
        return None

def main():
    """Main debug function"""
    print("=== 400 Error Debug for Group Chat ===")
    
    # Login
    token = login_as_moderator()
    if not token:
        print("Failed to login")
        return
    
    # Get available topics
    available_topics = test_available_topics(token)
    
    if available_topics:
        # Test with first available topic
        first_topic = available_topics[0]
        topic_id = first_topic["topic_id"]
        
        # Check topic first
        topic_check = test_topic_check(token, topic_id)
        
        # Try to create group
        result = test_create_group_with_400_debug(token, topic_id)
        
        if result:
            print("\n✅ Success! Group created without 400 error")
        else:
            print("\n❌ Group creation failed with 400 error")
    else:
        print("\n❌ No available topics found")
    
    print("\n=== Debug Summary ===")
    print("If you're getting 400 error, check:")
    print("1. Topic already has a chat group")
    print("2. Group is full (max 50 members)")
    print("3. Member already exists in group")

if __name__ == "__main__":
    main() 