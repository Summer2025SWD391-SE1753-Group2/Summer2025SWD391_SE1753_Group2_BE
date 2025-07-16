import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def login_as_admin() -> Optional[str]:
    """Login as admin and return token"""
    try:
        login_data = {
<<<<<<< HEAD
            "username": "admin",
            "password": "admin123"
=======
            "username": "khoipd12",
            "password": "SecurePassword@123"
>>>>>>> ff836887fb3e59d3fef93c625ac5913e8a6e8a90
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def login_as_moderator() -> Optional[str]:
    """Login as moderator and return token"""
    try:
        login_data = {
<<<<<<< HEAD
            "username": "moderator",
            "password": "moderator123"
=======
            "username": "khoipd11",
            "password": "SecurePassword@123"
>>>>>>> ff836887fb3e59d3fef93c625ac5913e8a6e8a90
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_get_all_group_chats(token: str, skip: int = 0, limit: int = 10, search: str = None, topic_id: str = None):
    """Test getting all group chats with pagination and filters"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    # Build query parameters
    params = {
        "skip": skip,
        "limit": limit
    }
    
    if search:
        params["search"] = search
    
    if topic_id:
        params["topic_id"] = topic_id
    
    response = requests.get(f"{BASE_URL}/group-chat/all", headers=headers, params=params)
    
    print(f"\n=== Get All Group Chats ===")
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total groups: {data['total']}")
        print(f"Returned: {len(data['groups'])}")
        print(f"Skip: {data['skip']}")
        print(f"Limit: {data['limit']}")
        print(f"Has more: {data['has_more']}")
        
        print(f"\n--- Group Details ---")
        for i, group in enumerate(data['groups'], 1):
            print(f"{i}. {group['group_name']}")
            print(f"   Topic: {group['topic_name']} ({group['topic_status']})")
            print(f"   Members: {group['member_count']}/{group['max_members']}")
            print(f"   Messages: {group['message_count']}")
            print(f"   Leader: {group['leader_name']} (@{group['leader_username']})")
            print(f"   Created: {group['created_at']}")
            if group['latest_message']:
                print(f"   Latest: {group['latest_message']['content'][:50]}... by {group['latest_message']['sender_name']}")
            print()
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

<<<<<<< HEAD
=======
def test_get_group_detail(token: str, group_id: str):
    """Test getting specific group detail"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/group-chat/{group_id}", headers=headers)
    
    print(f"\n=== Get Group Detail ===")
    print(f"Status: {response.status_code}")
    print(f"Group ID: {group_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Group Name: {data['name']}")
        print(f"Topic: {data['topic_name']}")
        print(f"Leader: {data['leader_name']}")
        print(f"Members: {data['member_count']}/{data['max_members']}")
        print(f"Created: {data['created_at']}")
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

>>>>>>> ff836887fb3e59d3fef93c625ac5913e8a6e8a90
def test_pagination(token: str):
    """Test pagination functionality"""
    print(f"\n=== Testing Pagination ===")
    
    # First page
    print(f"\n--- Page 1 (skip=0, limit=2) ---")
    page1 = test_get_all_group_chats(token, skip=0, limit=2)
    
    if page1 and page1['has_more']:
        # Second page
        print(f"\n--- Page 2 (skip=2, limit=2) ---")
        page2 = test_get_all_group_chats(token, skip=2, limit=2)
        
        # Third page
        print(f"\n--- Page 3 (skip=4, limit=2) ---")
        page3 = test_get_all_group_chats(token, skip=4, limit=2)

def test_search(token: str):
    """Test search functionality"""
    print(f"\n=== Testing Search ===")
    
    # Search by group name
    print(f"\n--- Search: 'group' ---")
    test_get_all_group_chats(token, search="group")
    
    # Search by description
    print(f"\n--- Search: 'chat' ---")
    test_get_all_group_chats(token, search="chat")

def test_permissions():
    """Test permission requirements"""
    print(f"\n=== Testing Permissions ===")
    
    # Test without token
    print(f"\n--- Without Token ---")
    response = requests.get(f"{BASE_URL}/group-chat/all")
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly requires authentication")
    else:
        print("❌ Should require authentication")
<<<<<<< HEAD
    
    # Test with regular user token (if available)
    # This would require a regular user account
=======
>>>>>>> ff836887fb3e59d3fef93c625ac5913e8a6e8a90

def main():
    """Main test function"""
    print("🧪 Testing All Group Chats API")
    print("=" * 50)
    
    # Test with admin token
    admin_token = login_as_admin()
    if admin_token:
        print(f"✅ Logged in as admin")
        
        # Basic test
<<<<<<< HEAD
        test_get_all_group_chats(admin_token)
=======
        result = test_get_all_group_chats(admin_token)
>>>>>>> ff836887fb3e59d3fef93c625ac5913e8a6e8a90
        
        # Test pagination
        test_pagination(admin_token)
        
        # Test search
        test_search(admin_token)
        
<<<<<<< HEAD
=======
        # Test group detail if we have groups
        if result and result['groups']:
            first_group_id = result['groups'][0]['group_id']
            test_get_group_detail(admin_token, first_group_id)
        
>>>>>>> ff836887fb3e59d3fef93c625ac5913e8a6e8a90
    else:
        print("❌ Failed to login as admin")
    
    # Test with moderator token
    moderator_token = login_as_moderator()
    if moderator_token:
        print(f"\n✅ Logged in as moderator")
        test_get_all_group_chats(moderator_token)
    else:
        print("❌ Failed to login as moderator")
    
    # Test permissions
    test_permissions()
    
    print(f"\n🎉 Testing completed!")

if __name__ == "__main__":
    main() 