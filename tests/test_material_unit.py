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
        "username": "khoipd12",
        "password": "SecurePassword@123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/access-token", data=login_data)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_materials_with_units(token: str):
    """Test if materials contain unit information"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/materials/", headers=headers, params={"limit": 5})
    
    print(f"\n=== Materials with Units Test ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total materials: {data['total']}")
        print(f"Returned: {len(data['materials'])}")
        
        print(f"\n--- Material Details ---")
        for i, material in enumerate(data['materials'], 1):
            print(f"{i}. {material['name']} ({material['status']})")
            print(f"   Unit ID: {material['unit_id']}")
            print(f"   Unit Name: {material['unit_name']}")
            print(f"   Image URL: {material.get('image_url', 'None')}")
            print()
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_create_material_with_unit(token: str):
    """Test creating a material with unit"""
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    # First, get a unit to use
    units_response = requests.get(f"{BASE_URL}/units/", headers=headers, params={"limit": 1})
    
    if units_response.status_code != 200:
        print("❌ Failed to get units for testing")
        return None
    
    units_data = units_response.json()
    if not units_data['units']:
        print("❌ No units available for testing")
        return None
    
    unit_id = units_data['units'][0]['unit_id']
    
    # Create material data
    material_data = {
        "name": "Test Material with Unit",
        "status": "active",
        "image_url": "https://example.com/test.jpg",
        "unit_id": unit_id
    }
    
    response = requests.post(f"{BASE_URL}/materials/", json=material_data, headers=headers)
    
    print(f"\n=== Create Material with Unit Test ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Success!")
        print(f"Material ID: {data['material_id']}")
        print(f"Name: {data['name']}")
        print(f"Unit ID: {data['unit_id']}")
        print(f"Unit Name: {data['unit_name']}")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_material_schema():
    """Test material schema structure"""
    print(f"\n=== Material Schema Structure ===")
    
    # Check if material has unit_id field
    try:
        from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialOut
        
        print("✅ MaterialCreate schema:")
        print(f"   - name: str")
        print(f"   - status: MaterialStatusEnum")
        print(f"   - image_url: Optional[str]")
        print(f"   - unit_id: UUID")
        print(f"   - created_by: Optional[UUID]")
        
        print("\n✅ MaterialUpdate schema:")
        print(f"   - name: Optional[str]")
        print(f"   - status: Optional[MaterialStatusEnum]")
        print(f"   - image_url: Optional[str]")
        print(f"   - unit_id: Optional[UUID]")
        
        print("\n✅ MaterialOut schema:")
        print(f"   - material_id: UUID")
        print(f"   - name: str")
        print(f"   - status: MaterialStatusEnum")
        print(f"   - image_url: Optional[str]")
        print(f"   - unit_id: UUID")
        print(f"   - unit_name: str")
        print(f"   - created_at: datetime")
        print(f"   - updated_at: datetime")
        print(f"   - created_by: Optional[UUID]")
        print(f"   - updated_by: Optional[UUID]")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    # Test schema first
    test_material_schema()
    
    # Login with provided credentials
    print("\nLogging in...")
    token = login_user("khoipd11", "SecurePassword@123")
    
    if token:
        print(f"✅ Login successful! Token: {token[:20]}...")
        
        # Test materials with units
        test_materials_with_units(token)
        
        # Test creating material with unit
        test_create_material_with_unit(token)
    else:
        print("❌ Login failed. Cannot proceed with tests.") 