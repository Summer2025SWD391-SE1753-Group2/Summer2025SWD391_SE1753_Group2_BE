#!/usr/bin/env python3
"""
Test script for group chat topic availability check
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
        "username": "moderator@example.com",  # Replace with actual moderator credentials
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_get_available_topics(token: str):
    """Test getting available topics for creating chat groups"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/group-chat/topics/available", headers=headers)
    print(f"\n=== Available Topics ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        topics = response.json()
        print(f"Found {len(topics)} available topics:")
        for topic in topics:
            print(f"  - {topic['topic_name']} (ID: {topic['topic_id']})")
    else:
        print(f"Error: {response.text}")

def test_get_topics_with_groups(token: str):
    """Test getting topics that already have chat groups"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/group-chat/topics/with-groups", headers=headers)
    print(f"\n=== Topics with Groups ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        topics = response.json()
        print(f"Found {len(topics)} topics with groups:")
        for topic in topics:
            print(f"  - {topic['topic_name']} -> Group: {topic['group_name']} ({topic['member_count']}/{topic['max_members']} members)")
    else:
        print(f"Error: {response.text}")

def test_check_topic_availability(token: str, topic_id: str):
    """Test checking if a specific topic can create a chat group"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/group-chat/topics/{topic_id}/check", headers=headers)
    print(f"\n=== Check Topic {topic_id} ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Can create: {result['can_create']}")
        print(f"Reason: {result['reason']}")
        if 'topic_name' in result:
            print(f"Topic name: {result['topic_name']}")
        if 'existing_group_name' in result:
            print(f"Existing group: {result['existing_group_name']}")
    else:
        print(f"Error: {response.text}")

def test_create_group_from_topic(token: str, topic_id: str, group_name: str):
    """Test creating a group from topic"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    group_data = {
        "topic_id": topic_id,
        "name": group_name,
        "description": f"Chat group for {group_name}",
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/group-chat/create", json=group_data, headers=headers)
    print(f"\n=== Create Group from Topic {topic_id} ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        group = response.json()
        print(f"Group created successfully:")
        print(f"  - ID: {group['group_id']}")
        print(f"  - Name: {group['name']}")
        print(f"  - Member count: {group['member_count']}")
    else:
        print(f"Error: {response.text}")

def main():
    """Main test function"""
    print("=== Group Chat Topic Availability Test ===")
    
    # Login as moderator
    token = login_as_moderator()
    if not token:
        print("Failed to login. Please check moderator credentials.")
        return
    
    # Test 1: Get available topics
    test_get_available_topics(token)
    
    # Test 2: Get topics with groups
    test_get_topics_with_groups(token)
    
    # Test 3: Check specific topic (replace with actual topic ID)
    # test_check_topic_availability(token, "your-topic-id-here")
    
    # Test 4: Try to create group (uncomment and replace with actual topic ID)
    # test_create_group_from_topic(token, "your-topic-id-here", "Test Group")

if __name__ == "__main__":
    main() 