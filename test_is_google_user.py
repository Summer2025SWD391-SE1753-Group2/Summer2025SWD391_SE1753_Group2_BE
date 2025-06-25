#!/usr/bin/env python3
import requests
import json

def test_is_google_user_endpoint():
    """Test the is-google-user endpoint with different scenarios"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing /api/v1/accounts/is-google-user endpoint")
    print("=" * 60)
    
    # Test 1: Without authentication
    print("\n1️⃣ Testing without authentication:")
    try:
        response = requests.get(f"{base_url}/api/v1/accounts/is-google-user")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: With invalid token
    print("\n2️⃣ Testing with invalid token:")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check if endpoint exists
    print("\n3️⃣ Testing endpoint availability:")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("   ✅ FastAPI docs are accessible")
        else:
            print("   ❌ FastAPI docs not accessible")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check other endpoints for comparison
    print("\n4️⃣ Testing other endpoints for comparison:")
    try:
        # Test a simple endpoint that should work
        response = requests.get(f"{base_url}/api/v1/accounts/me", headers={"Authorization": "Bearer invalid_token"})
        print(f"   /me endpoint status: {response.status_code}")
    except Exception as e:
        print(f"   Error testing /me: {e}")

def test_authentication_flow():
    """Test the complete authentication flow"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔐 Testing Authentication Flow")
    print("=" * 60)
    
    # Test login endpoint with provided credentials
    print("\n1️⃣ Testing login endpoint:")
    try:
        login_data = {
            "username": "khoipd8",  # Updated with provided credentials
            "password": "SecurePassword@123"
        }
        response = requests.post(f"{base_url}/api/v1/auth/access-token", data=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"   ✅ Got access token: {access_token[:20]}...")
            
            # Test is-google-user with valid token
            print("\n2️⃣ Testing is-google-user with valid token:")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Test /me endpoint for comparison
            print("\n3️⃣ Testing /me endpoint for comparison:")
            response = requests.get(f"{base_url}/api/v1/accounts/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   Username: {user_data.get('username')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Role: {user_data.get('role', {}).get('role_name')}")
                print(f"   Is Google User: {user_data.get('username', '').startswith('google_')}")
        else:
            print(f"   ❌ Login failed: {response.text}")
            
            # Try with email instead of username
            print("\n4️⃣ Trying login with email:")
            login_data_email = {
                "username": "khoipdse184586@fpt.edu.vn",
                "password": "SecurePassword@123"
            }
            response = requests.post(f"{base_url}/api/v1/auth/access-token", data=login_data_email)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"   ✅ Got access token with email: {access_token[:20]}...")
                
                # Test is-google-user with valid token
                print("\n5️⃣ Testing is-google-user with valid token (email login):")
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
            else:
                print(f"   ❌ Login with email failed: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_is_google_user_endpoint()
    test_authentication_flow() 