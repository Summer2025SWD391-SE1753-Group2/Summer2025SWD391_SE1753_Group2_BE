#!/usr/bin/env python3
import requests
import json

def test_fixed_endpoint():
    """Test the fixed is-google-user endpoint"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Testing Fixed /is-google-user endpoint")
    print("=" * 60)
    
    # First, create a test account
    print("\n1️⃣ Creating test account:")
    account_data = {
        "username": "testuser123",
        "email": "testuser123@gmail.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/accounts/", json=account_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Account created successfully")
        else:
            print(f"   ❌ Account creation failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error creating account: {e}")
        return
    
    # Login with the new account
    print("\n2️⃣ Logging in with test account:")
    login_data = {
        "username": "testuser123",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/access-token", data=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"   ✅ Login successful")
            print(f"   Access Token: {access_token[:20]}...")
            
            # Test the fixed endpoint
            print("\n3️⃣ Testing fixed /is-google-user endpoint:")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Endpoint works!")
                print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"   ❌ Endpoint still fails: {response.text}")
                
            # Test /me endpoint for comparison
            print("\n4️⃣ Testing /me endpoint for comparison:")
            response = requests.get(f"{base_url}/api/v1/accounts/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ /me works")
                print(f"   Username: {user_data.get('username')}")
                print(f"   Is Google User: {user_data.get('username', '').startswith('google_')}")
            else:
                print(f"   ❌ /me failed: {response.text}")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_endpoint() 