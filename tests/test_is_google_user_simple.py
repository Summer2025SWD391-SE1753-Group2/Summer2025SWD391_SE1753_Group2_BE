#!/usr/bin/env python3
import requests
import json

def test_is_google_user_simple():
    """Simple test to debug the is-google-user endpoint"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Simple Test for /is-google-user endpoint")
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
            
            # Test the problematic endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print(f"\n🔍 Testing /is-google-user endpoint:")
            print(f"   URL: {base_url}/api/v1/accounts/is-google-user")
            print(f"   Method: GET")
            print(f"   Headers: Authorization: Bearer {access_token[:20]}...")
            
            response = requests.get(f"{base_url}/api/v1/accounts/is-google-user", headers=headers)
            
            print(f"\n📊 Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Body: {response.text}")
            
            # Try to parse JSON response
            try:
                json_response = response.json()
                print(f"   Parsed JSON: {json.dumps(json_response, indent=2)}")
            except:
                print(f"   Not valid JSON")
                
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_is_google_user_simple() 