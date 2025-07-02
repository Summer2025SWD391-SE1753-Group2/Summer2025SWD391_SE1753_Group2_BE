#!/usr/bin/env python3
import requests
import jwt
from app.core.settings import settings

def debug_check_roles():
    """Debug the check_roles function directly"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging check_roles Function")
    print("=" * 60)
    
    # Login to get token
    login_data = {
        "username": "khoipd8",
        "password": "SecurePassword@123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/access-token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            print(f"✅ Login successful")
            
            # Test different endpoints that use check_roles
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print(f"\n🔍 Testing endpoints that use check_roles:")
            
            # Test /me endpoint (should work)
            print(f"\n1️⃣ Testing /me endpoint:")
            response = requests.get(f"{base_url}/api/v1/accounts/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ /me works")
            else:
                print(f"   ❌ /me failed: {response.text}")
            
            # Test /is-google-user endpoint (failing)
            print(f"\n2️⃣ Testing /is-google-user endpoint:")
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Test /update-password endpoint (should work)
            print(f"\n3️⃣ Testing /update-password endpoint:")
            response = requests.post(f"{base_url}/api/v1/accounts/update-password", 
                                   headers=headers,
                                   json={"new_password": "test123"})
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 400]:  # 400 is expected for invalid password
                print(f"   ✅ /update-password works (got expected response)")
            else:
                print(f"   ❌ /update-password failed: {response.text}")
            
            # Test /update-username endpoint (should work)
            print(f"\n4️⃣ Testing /update-username endpoint:")
            response = requests.post(f"{base_url}/api/v1/accounts/update-username", 
                                   headers=headers,
                                   json={"new_username": "test_username"})
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 400]:  # 400 is expected for invalid username
                print(f"   ✅ /update-username works (got expected response)")
            else:
                print(f"   ❌ /update-username failed: {response.text}")
                
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_check_roles() 