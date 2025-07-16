#!/usr/bin/env python3
"""
Test for Material creation API fix
"""

import requests
import json

def test_material_creation():
    """Test Material creation API"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Material Creation API Fix")
    print("=" * 60)
    
    # Test 1: Get units first to get a valid unit_id
    print("\n1️⃣ Getting units to find a valid unit_id")
    try:
        response = requests.get(f"{base_url}/units/", params={"limit": 1})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['units']:
                unit = data['units'][0]
                unit_id = unit['unit_id']
                unit_name = unit['name']
                print(f"   ✅ Found unit: {unit_name} ({unit_id})")
                
                # Test 2: Create material with unit
                print(f"\n2️⃣ Creating material with unit_id: {unit_id}")
                
                material_data = {
                    "name": "Test Material API Fix",
                    "status": "active",
                    "image_url": "https://example.com/test.jpg",
                    "unit_id": unit_id
                }
                
                create_response = requests.post(f"{base_url}/materials/", json=material_data)
                print(f"   Status: {create_response.status_code}")
                
                if create_response.status_code == 201:
                    material = create_response.json()
                    print(f"   ✅ Success! Material created:")
                    print(f"      ID: {material['material_id']}")
                    print(f"      Name: {material['name']}")
                    print(f"      Unit ID: {material['unit_id']}")
                    print(f"      Unit Name: {material['unit_name']}")
                    print(f"      Status: {material['status']}")
                    
                    # Verify unit_name is present
                    if 'unit_name' in material and material['unit_name']:
                        print(f"   ✅ Unit name is present: {material['unit_name']}")
                        return True
                    else:
                        print(f"   ❌ Unit name is missing!")
                        return False
                else:
                    print(f"   ❌ Failed: {create_response.text}")
                    return False
            else:
                print(f"   ❌ No units found in database")
                return False
        else:
            print(f"   ❌ Failed to get units: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - Server not running")
        print(f"   💡 Start server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_material_creation() 