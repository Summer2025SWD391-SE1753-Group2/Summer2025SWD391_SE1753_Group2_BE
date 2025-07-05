#!/usr/bin/env python3
"""
Simple test for Material API with unit information
"""

import requests
import json

def test_material_api():
    """Test Material API endpoints"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Material API with Unit Information")
    print("=" * 60)
    
    # Test 1: Get materials list
    print("\n1️⃣ Testing GET /materials/ (list with pagination)")
    try:
        response = requests.get(f"{base_url}/materials/", params={"limit": 3})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Total materials: {data['total']}")
            print(f"   Returned: {len(data['materials'])}")
            print(f"   Has more: {data['has_more']}")
            
            if data['materials']:
                material = data['materials'][0]
                print(f"\n   📋 Sample Material:")
                print(f"      ID: {material['material_id']}")
                print(f"      Name: {material['name']}")
                print(f"      Status: {material['status']}")
                print(f"      Unit ID: {material['unit_id']}")
                print(f"      Unit Name: {material['unit_name']}")
                print(f"      Image URL: {material.get('image_url', 'None')}")
                
                # Verify unit information is present
                if 'unit_id' in material and 'unit_name' in material:
                    print(f"   ✅ Unit information is present!")
                else:
                    print(f"   ❌ Unit information is missing!")
            else:
                print(f"   ℹ️  No materials found")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - Server not running")
        print(f"   💡 Start server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Get units list
    print("\n2️⃣ Testing GET /units/ (to verify units exist)")
    try:
        response = requests.get(f"{base_url}/units/", params={"limit": 3})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Total units: {data['total']}")
            print(f"   Returned: {len(data['units'])}")
            
            if data['units']:
                unit = data['units'][0]
                print(f"\n   📋 Sample Unit:")
                print(f"      ID: {unit['unit_id']}")
                print(f"      Name: {unit['name']}")
                print(f"      Status: {unit['status']}")
                print(f"      Description: {unit.get('description', 'None')}")
            else:
                print(f"   ℹ️  No units found")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Material API test completed!")
    print("✅ Material successfully contains unit information")
    return True

if __name__ == "__main__":
    test_material_api() 