#!/usr/bin/env python3
import requests
import jwt
from app.core.settings import settings

def debug_user_role():
    """Debug user role and token information"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging User Role and Token")
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
            print(f"Access Token: {access_token[:50]}...")
            
            # Decode token to see payload
            try:
                payload = jwt.decode(
                    access_token, 
                    settings.JWT_SECRET_KEY, 
                    algorithms=[settings.JWT_ALGORITHM]
                )
                print(f"\n📋 Token Payload:")
                print(f"   sub (username): {payload.get('sub')}")
                print(f"   user_id: {payload.get('user_id')}")
                print(f"   role: {payload.get('role')}")
                print(f"   scopes: {payload.get('scopes')}")
                print(f"   exp: {payload.get('exp')}")
                
            except Exception as e:
                print(f"❌ Error decoding token: {e}")
            
            # Test /me endpoint to get user info from database
            print(f"\n🔍 Testing /me endpoint:")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/api/v1/accounts/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ /me endpoint successful")
                print(f"   Username: {user_data.get('username')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Role: {user_data.get('role', {}).get('role_name')}")
                print(f"   Role ID: {user_data.get('role', {}).get('role_id')}")
                print(f"   Status: {user_data.get('status')}")
                
                # Compare token role with database role
                token_role = payload.get('role')
                db_role = user_data.get('role', {}).get('role_name')
                
                print(f"\n🔍 Role Comparison:")
                print(f"   Token Role: {token_role}")
                print(f"   Database Role: {db_role}")
                print(f"   Match: {token_role == db_role}")
                
                if token_role != db_role:
                    print(f"   ❌ ROLE MISMATCH - This is causing the 403 error!")
                else:
                    print(f"   ✅ Roles match")
                    
            else:
                print(f"❌ /me endpoint failed: {response.status_code} - {response.text}")
                
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_user_role() 