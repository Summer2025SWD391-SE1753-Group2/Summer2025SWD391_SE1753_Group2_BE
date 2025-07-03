#!/usr/bin/env python3
"""
Debug script for moderator permission issue
"""

import requests
import json
import jwt
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json"
}

# Test token from the curl request
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraG9pcGQxMSIsInVzZXJfaWQiOiI5MGE1MjUxNC0xMTQ1LTRiMDItOWFkMS04MDAxZGQxMTU5NDUiLCJyb2xlIjoibW9kZXJhdG9yIiwiZXhwIjoxNzUyMTg0Njg4LCJzY29wZXMiOltdfQ.X2bUe8zom0dq8Mj5y2C6mrDAQ2KTJngcTX9bRv-arDw"

def decode_jwt_token(token: str):
    """Decode JWT token without verification to see payload"""
    try:
        # Decode without verification to see payload
        payload = jwt.decode(token, options={"verify_signature": False})
        print("=== JWT Token Payload ===")
        print(json.dumps(payload, indent=2))
        return payload
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def test_moderator_login():
    """Test moderator login"""
    login_data = {
        "username": "khoipd11@gmail.com",
        "password": "SecurePassword@123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/access-token", data=login_data)
    print(f"\n=== Login Test ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful")
        print(f"Token: {token_data['access_token'][:50]}...")
        
        # Decode the new token
        decode_jwt_token(token_data['access_token'])
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_available_topics(token: str):
    """Test getting available topics with moderator token"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/group-chat/topics/available", headers=headers)
    print(f"\n=== Available Topics Test ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        topics = response.json()
        print(f"✅ Success - Found {len(topics)} available topics")
        if topics:
            print(f"First topic: {topics[0]}")
        return topics
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_create_group_with_moderator(token: str):
    """Test creating group with moderator token"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    group_data = {
        "topic_id": "130d1248-c7bd-49a8-8222-d58e2f29a078",
        "name": "Test Group from Moderator",
        "description": "Test description",
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=group_data, headers=headers)
    print(f"\n=== Create Group Test ===")
    print(f"Status: {response.status_code}")
    print(f"Request data: {json.dumps(group_data, indent=2)}")
    
    if response.status_code == 201:
        print("✅ Group created successfully")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Permission denied")
        print(f"Error: {response.json()}")
    elif response.status_code == 400:
        print("⚠️ 400 Bad Request - Business logic error")
        print(f"Error: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(f"Response: {response.text}")

def test_user_info(token: str):
    """Test getting current user info"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/accounts/me", headers=headers)
    print(f"\n=== Current User Info ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_info = response.json()
        print("✅ User info retrieved")
        print(f"User: {json.dumps(user_info, indent=2)}")
        return user_info
    else:
        print(f"❌ Failed to get user info: {response.text}")
        return None

def test_topic_check(token: str):
    """Test topic availability check"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    topic_id = "130d1248-c7bd-49a8-8222-d58e2f29a078"
    response = requests.get(f"{BASE_URL}/api/v1/group-chat/topics/{topic_id}/check", headers=headers)
    print(f"\n=== Topic Check Test ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Topic check successful")
        print(f"Result: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"❌ Topic check failed: {response.text}")
        return None

def main():
    """Main debug function"""
    print("=== Moderator Permission Debug ===")
    
    # 1. Decode the test token
    print("\n1. Decoding test token...")
    decode_jwt_token(TEST_TOKEN)
    
    # 2. Test login to get fresh token
    print("\n2. Testing login...")
    fresh_token = test_moderator_login()
    
    if fresh_token:
        # 3. Test user info
        print("\n3. Testing user info...")
        user_info = test_user_info(fresh_token)
        
        # 4. Test available topics
        print("\n4. Testing available topics...")
        topics = test_available_topics(fresh_token)
        
        # 5. Test topic check
        print("\n5. Testing topic check...")
        topic_check = test_topic_check(fresh_token)
        
        # 6. Test create group
        print("\n6. Testing create group...")
        test_create_group_with_moderator(fresh_token)
    
    print("\n=== Debug Summary ===")
    print("Check the output above for any permission issues")

if __name__ == "__main__":
    main() 