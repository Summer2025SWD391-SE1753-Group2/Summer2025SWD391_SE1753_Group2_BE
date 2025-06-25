#!/usr/bin/env python3
import requests
import json

def test_fixed_is_google_user():
    """Test the fixed /is-google-user endpoint with an existing account"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Testing Fixed /is-google-user endpoint (with existing account)")
    print("=" * 60)
    
    # Login with the provided account
    print("\n1️⃣ Logging in with provided account:")
    login_data = {
        "username": "khoipd8",
        "password": "SecurePassword@123"
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
            print("\n2️⃣ Testing fixed /is-google-user endpoint:")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Endpoint works!")
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                # Verify response structure
                if "is_google_user" in result and "username" in result and "email" in result:
                    print(f"   ✅ Response structure is correct")
                else:
                    print(f"   ❌ Response structure is missing required fields")
                    
            else:
                print(f"   ❌ Endpoint still fails: {response.text}")
                
            # Test /me endpoint for comparison
            print("\n3️⃣ Testing /me endpoint for comparison:")
            response = requests.get(f"{base_url}/api/v1/accounts/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ /me works")
                print(f"   Username: {user_data.get('username')}")
                print(f"   Is Google User: {user_data.get('username', '').startswith('google_')}")
            else:
                print(f"   ❌ /me failed: {response.text}")
                
            # Test with invalid token
            print("\n4️⃣ Testing with invalid token:")
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=invalid_headers)
            print(f"   Status: {response.status_code}")
            if response.status_code in [401, 403]:
                print(f"   ✅ Properly rejects invalid token")
            else:
                print(f"   ❌ Should reject invalid token but got: {response.status_code}")
                
            # Test without token
            print("\n5️⃣ Testing without token:")
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user")
            print(f"   Status: {response.status_code}")
            if response.status_code in [401, 403]:
                print(f"   ✅ Properly rejects missing token")
            else:
                print(f"   ❌ Should reject missing token but got: {response.status_code}")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_is_google_user() 