#!/usr/bin/env python3
"""
Test /is-google-user endpoint with curl-like requests
"""

import requests
import json

def test_is_google_user():
    print("🔧 Testing /is-google-user endpoint with requests")
    print("=" * 60)
    
    # 1. Login to get token
    login_data = {
        "username": "khoipd8",
        "password": "SecurePassword@123"
    }
    
    print("1️⃣ Logging in...")
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/access-token",
        data=login_data  # Use form data, not JSON
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful")
    print(f"Token: {access_token[:50]}...")
    
    # 2. Test /is-google-user endpoint
    print("\n2️⃣ Testing /is-google-user endpoint...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "http://localhost:8000/api/v1/accounts/is-google-user",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Endpoint works!")
    else:
        print("❌ Endpoint failed!")
    
    # 3. Test /me endpoint for comparison
    print("\n3️⃣ Testing /me endpoint for comparison...")
    me_response = requests.get(
        "http://localhost:8000/api/v1/accounts/me",
        headers=headers
    )
    
    print(f"Status: {me_response.status_code}")
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"Username: {me_data.get('username')}")
        print(f"Is Google User: {me_data.get('is_google_user')}")
        print("✅ /me works")
    else:
        print(f"❌ /me failed: {me_response.text}")

if __name__ == "__main__":
    test_is_google_user() 