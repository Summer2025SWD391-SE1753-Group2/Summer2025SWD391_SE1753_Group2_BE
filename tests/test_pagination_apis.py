import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def login_user(username: str, password: str) -> Optional[str]:
    """Login and return access token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_tags_pagination(token: str, skip: int = 0, limit: int = 10):
    """Test tags pagination"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    params = {
        "skip": skip,
        "limit": limit
    }
    
    response = requests.get(f"{BASE_URL}/tags/", headers=headers, params=params)
    
    print(f"\n=== Tags Pagination (skip={skip}, limit={limit}) ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total tags: {data['total']}")
        print(f"Returned: {len(data['tags'])}")
        print(f"Skip: {data['skip']}")
        print(f"Limit: {data['limit']}")
        print(f"Has more: {data['has_more']}")
        
        print(f"\n--- Tags ---")
        for i, tag in enumerate(data['tags'], 1):
            print(f"{i}. {tag['name']} ({tag['status']})")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_topics_pagination(token: str, skip: int = 0, limit: int = 10):
    """Test topics pagination"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    params = {
        "skip": skip,
        "limit": limit
    }
    
    response = requests.get(f"{BASE_URL}/topics/", headers=headers, params=params)
    
    print(f"\n=== Topics Pagination (skip={skip}, limit={limit}) ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total topics: {data['total']}")
        print(f"Returned: {len(data['topics'])}")
        print(f"Skip: {data['skip']}")
        print(f"Limit: {data['limit']}")
        print(f"Has more: {data['has_more']}")
        
        print(f"\n--- Topics ---")
        for i, topic in enumerate(data['topics'], 1):
            print(f"{i}. {topic['name']} ({topic['status']})")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_units_pagination(token: str, skip: int = 0, limit: int = 10):
    """Test units pagination"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    params = {
        "skip": skip,
        "limit": limit
    }
    
    response = requests.get(f"{BASE_URL}/units/", headers=headers, params=params)
    
    print(f"\n=== Units Pagination (skip={skip}, limit={limit}) ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total units: {data['total']}")
        print(f"Returned: {len(data['units'])}")
        print(f"Skip: {data['skip']}")
        print(f"Limit: {data['limit']}")
        print(f"Has more: {data['has_more']}")
        
        print(f"\n--- Units ---")
        for i, unit in enumerate(data['units'], 1):
            print(f"{i}. {unit['name']} ({unit['status']})")
            if unit.get('description'):
                print(f"   Description: {unit['description']}")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_materials_pagination(token: str, skip: int = 0, limit: int = 10):
    """Test materials pagination"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    params = {
        "skip": skip,
        "limit": limit
    }
    
    response = requests.get(f"{BASE_URL}/materials/", headers=headers, params=params)
    
    print(f"\n=== Materials Pagination (skip={skip}, limit={limit}) ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total materials: {data['total']}")
        print(f"Returned: {len(data['materials'])}")
        print(f"Skip: {data['skip']}")
        print(f"Limit: {data['limit']}")
        print(f"Has more: {data['has_more']}")
        
        print(f"\n--- Materials ---")
        for i, material in enumerate(data['materials'], 1):
            print(f"{i}. {material['name']} ({material['status']})")
            print(f"   Unit: {material['unit_name']}")
            if material.get('image_url'):
                print(f"   Image: {material['image_url']}")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_all_pagination(token: str):
    """Test pagination for all entities"""
    print(f"\n{'='*60}")
    print(f"TESTING PAGINATION FOR ALL ENTITIES")
    print(f"{'='*60}")
    
    # Test Tags
    print(f"\n{'='*20} TAGS {'='*20}")
    tags_page1 = test_tags_pagination(token, skip=0, limit=5)
    if tags_page1 and tags_page1['has_more']:
        test_tags_pagination(token, skip=5, limit=5)
    
    # Test Topics
    print(f"\n{'='*20} TOPICS {'='*20}")
    topics_page1 = test_topics_pagination(token, skip=0, limit=5)
    if topics_page1 and topics_page1['has_more']:
        test_topics_pagination(token, skip=5, limit=5)
    
    # Test Units
    print(f"\n{'='*20} UNITS {'='*20}")
    units_page1 = test_units_pagination(token, skip=0, limit=5)
    if units_page1 and units_page1['has_more']:
        test_units_pagination(token, skip=5, limit=5)
    
    # Test Materials
    print(f"\n{'='*20} MATERIALS {'='*20}")
    materials_page1 = test_materials_pagination(token, skip=0, limit=5)
    if materials_page1 and materials_page1['has_more']:
        test_materials_pagination(token, skip=5, limit=5)

if __name__ == "__main__":
    # Login with moderator credentials
    print("Logging in as moderator...")
    token = login_user("moderator", "moderator123")
    
    if token:
        print(f"✅ Login successful! Token: {token[:20]}...")
        test_all_pagination(token)
    else:
        print("❌ Login failed. Cannot proceed with tests.") 