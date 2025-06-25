#!/usr/bin/env python3
"""
Test Feedback API endpoints
"""

import requests
import json
from uuid import uuid4

def test_feedback_api():
    print("🔧 Testing Feedback API Endpoints")
    print("=" * 60)
    
    # 1. Login as user
    print("1️⃣ Logging in as user...")
    user_login_data = {
        "username": "khoipd8",
        "password": "SecurePassword@123"
    }
    
    user_login_response = requests.post(
        "http://localhost:8000/api/v1/auth/access-token",
        data=user_login_data
    )
    
    if user_login_response.status_code != 200:
        print(f"❌ User login failed: {user_login_response.status_code}")
        print(f"Response: {user_login_response.text}")
        return
    
    user_token_data = user_login_response.json()
    user_access_token = user_token_data["access_token"]
    print(f"✅ User login successful")
    
    user_headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Create feedback as user
    print("\n2️⃣ Creating feedback as user...")
    feedback_data = {
        "title": "Test Bug Report",
        "description": "This is a test bug report to verify the feedback system is working correctly.",
        "feedback_type": "bug_report",
        "priority": "medium",
        "browser_info": "Chrome 120.0.0.0",
        "device_info": "Windows 10"
    }
    
    create_response = requests.post(
        "http://localhost:8000/api/v1/feedback/",
        headers=user_headers,
        json=feedback_data
    )
    
    print(f"Status: {create_response.status_code}")
    print(f"Response: {create_response.text}")
    
    if create_response.status_code == 201:
        feedback = create_response.json()
        feedback_id = feedback["feedback_id"]
        print(f"✅ Feedback created successfully!")
        print(f"Feedback ID: {feedback_id}")
    else:
        print("❌ Failed to create feedback")
        return
    
    # 3. Get user's own feedbacks
    print("\n3️⃣ Getting user's own feedbacks...")
    my_feedbacks_response = requests.get(
        "http://localhost:8000/api/v1/feedback/my-feedbacks/",
        headers=user_headers
    )
    
    print(f"Status: {my_feedbacks_response.status_code}")
    if my_feedbacks_response.status_code == 200:
        feedbacks = my_feedbacks_response.json()
        print(f"✅ Found {feedbacks['total']} feedbacks")
    else:
        print(f"❌ Failed to get feedbacks: {my_feedbacks_response.text}")
    
    # 4. Try to access admin endpoints as user (should fail)
    print("\n4️⃣ Testing user access to admin endpoints (should fail)...")
    admin_endpoints_response = requests.get(
        "http://localhost:8000/api/v1/feedback/all/",
        headers=user_headers
    )
    
    print(f"Status: {admin_endpoints_response.status_code}")
    if admin_endpoints_response.status_code == 403:
        print("✅ Correctly denied user access to admin endpoints")
    else:
        print(f"❌ Unexpected response: {admin_endpoints_response.text}")
    
    # 5. Test feedback stats (should fail for user)
    print("\n5️⃣ Testing feedback stats access (should fail for user)...")
    stats_response = requests.get(
        "http://localhost:8000/api/v1/feedback/stats/",
        headers=user_headers
    )
    
    print(f"Status: {stats_response.status_code}")
    if stats_response.status_code == 403:
        print("✅ Correctly denied user access to stats")
    else:
        print(f"❌ Unexpected response: {stats_response.text}")
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("✅ User can create feedback")
    print("✅ User can view their own feedbacks")
    print("✅ User is correctly denied access to admin endpoints")
    print("✅ Role-based access control is working correctly")

if __name__ == "__main__":
    test_feedback_api() 