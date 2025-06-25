#!/usr/bin/env python3
"""
Test create post endpoint
"""

import requests
import json
from uuid import uuid4

def test_create_post():
    print("🔧 Testing Create Post Endpoint")
    print("=" * 50)
    
    # 1. Login to get token
    login_data = {
        "username": "khoipd8",
        "password": "Admin@123"
    }
    
    print("1️⃣ Logging in...")
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/access-token",
        data=login_data
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful")
    
    # 2. Get some materials for testing
    print("\n2️⃣ Getting materials...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    materials_response = requests.get(
        "http://localhost:8000/api/v1/materials/",
        headers=headers
    )
    
    if materials_response.status_code != 200:
        print(f"❌ Failed to get materials: {materials_response.status_code}")
        return
    
    materials = materials_response.json()
    if not materials:
        print("❌ No materials available")
        return
    
    print(f"✅ Found {len(materials)} materials")
    
    # 3. Get some topics for testing
    print("\n3️⃣ Getting topics...")
    topics_response = requests.get(
        "http://localhost:8000/api/v1/topics/",
        headers=headers
    )
    
    if topics_response.status_code != 200:
        print(f"❌ Failed to get topics: {topics_response.status_code}")
        return
    
    topics = topics_response.json()
    if not topics:
        print("❌ No topics available")
        return
    
    print(f"✅ Found {len(topics)} topics")
    
    # 4. Create test post
    print("\n4️⃣ Creating test post...")
    post_data = {
        "title": "Test Post - Fixed Status Issue",
        "content": "This is a test post to verify the status field issue is fixed.",
        "materials": [
            {
                "material_id": str(materials[0]["material_id"]),
                "quantity": 2.5
            }
        ],
        "topic_ids": [str(topics[0]["topic_id"])],
        "tag_ids": [],
        "images": [],
        "steps": [
            {
                "order_number": 1,
                "content": "Step 1: Test step"
            }
        ]
    }
    
    create_response = requests.post(
        "http://localhost:8000/api/v1/posts/",
        headers=headers,
        json=post_data
    )
    
    print(f"Status: {create_response.status_code}")
    print(f"Response: {create_response.text}")
    
    if create_response.status_code == 201:
        post = create_response.json()
        print("✅ Post created successfully!")
        print(f"Post ID: {post['post_id']}")
        print(f"Status: {post['status']}")
        print(f"Title: {post['title']}")
    else:
        print("❌ Failed to create post")

if __name__ == "__main__":
    test_create_post() 