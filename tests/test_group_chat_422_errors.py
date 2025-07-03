#!/usr/bin/env python3
"""
Test script for group chat 422 validation errors
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
        "username": "khoipd11",  # Thay bằng tài khoản moderator thực tế
        "password": "SecurePassword@123"
    }
    # Đăng nhập bằng form-data
    response = requests.post(f"{BASE_URL}/api/v1/auth/access-token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_422_validation_errors(token: str):
    """Test various 422 validation errors"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    print("=== Testing 422 Validation Errors ===")
    
    # Test 1: Missing required fields
    print("\n1. Testing missing required fields:")
    invalid_data1 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        # Missing name
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data1, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for missing name")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 2: Invalid UUID format
    print("\n2. Testing invalid UUID format:")
    invalid_data2 = {
        "topic_id": "invalid-uuid",
        "name": "Test Group",
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data2, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for invalid UUID")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 3: Invalid max_members (too high)
    print("\n3. Testing max_members > 50:")
    invalid_data3 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Group",
        "max_members": 100
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data3, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for max_members > 50")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 4: Invalid max_members (too low)
    print("\n4. Testing max_members < 1:")
    invalid_data4 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Group",
        "max_members": 0
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data4, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for max_members < 1")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 5: Name too long
    print("\n5. Testing name too long (> 100 chars):")
    invalid_data5 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "A" * 101,  # 101 characters
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data5, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for name too long")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 6: Description too long
    print("\n6. Testing description too long (> 500 chars):")
    invalid_data6 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Group",
        "description": "A" * 501,  # 501 characters
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data6, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for description too long")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 7: Empty name
    print("\n7. Testing empty name:")
    invalid_data7 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "",
        "max_members": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data7, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for empty name")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test 8: Wrong data types
    print("\n8. Testing wrong data types:")
    invalid_data8 = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Group",
        "max_members": "50"  # String instead of number
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=invalid_data8, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for wrong data type")
        print(f"Error details: {response.json()}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")

def test_valid_data(token: str):
    """Test with valid data to ensure it works"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Valid Data ===")
    
    # Get available topics first
    response = requests.get(f"{BASE_URL}/api/v1/group-chat/topics/available", headers=headers)
    if response.status_code == 200:
        topics = response.json()
        if topics:
            topic_id = topics[0]["topic_id"]
            
            valid_data = {
                "topic_id": topic_id,
                "name": "Test Group Valid",
                "description": "Test description",
                "max_members": 50
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=valid_data, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Valid data test passed")
                print(f"Group created: {response.json()}")
            elif response.status_code == 400:
                print("⚠️ Topic already has a group (expected)")
                print(f"Error: {response.json()}")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print("⚠️ No available topics found")
    else:
        print(f"❌ Failed to get available topics: {response.status_code}")

def test_missing_headers():
    """Test without proper headers"""
    print("\n=== Testing Missing Headers ===")
    
    valid_data = {
        "topic_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Group",
        "max_members": 50
    }
    
    # Test without Authorization header
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=valid_data, headers=HEADERS)
    print(f"Status without auth: {response.status_code}")
    if response.status_code == 401:
        print("✅ Expected 401 error for missing auth")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    # Test without Content-Type header
    response = requests.post(f"{BASE_URL}/api/v1/group-chat/create", json=valid_data)
    print(f"Status without content-type: {response.status_code}")
    if response.status_code == 422:
        print("✅ Expected 422 error for missing content-type")
    else:
        print(f"❌ Unexpected status: {response.status_code}")

def main():
    """Main test function"""
    print("=== Group Chat 422 Error Test ===")
    
    # Login as moderator
    token = login_as_moderator()
    if not token:
        print("Failed to login. Please check moderator credentials.")
        return
    
    # Test 422 validation errors
    test_422_validation_errors(token)
    
    # Test valid data
    test_valid_data(token)
    
    # Test missing headers
    test_missing_headers()
    
    print("\n=== Test Summary ===")
    print("✅ All 422 validation error tests completed")
    print("📝 Check the output above for any unexpected results")

if __name__ == "__main__":
    main() 