#!/usr/bin/env python3
"""
Test for Material schema fix
"""

from app.schemas.material import MaterialOut, MaterialStatusEnum
from uuid import uuid4
from datetime import datetime, timezone

def test_material_schema():
    """Test MaterialOut schema"""
    
    print("🧪 Testing Material Schema Fix")
    print("=" * 60)
    
    # Create a mock material object with unit relationship
    class MockUnit:
        def __init__(self, name):
            self.name = name
    
    class MockMaterial:
        def __init__(self):
            self.material_id = uuid4()
            self.name = "Test Material"
            self.status = MaterialStatusEnum.active
            self.image_url = "https://example.com/test.jpg"
            self.unit_id = uuid4()
            self.unit = MockUnit("Test Unit")
            self.created_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
            self.created_by = uuid4()
            self.updated_by = uuid4()
    
    try:
        # Test MaterialOut.from_orm method
        mock_material = MockMaterial()
        material_out = MaterialOut.from_orm(mock_material)
        
        print(f"✅ Schema test passed!")
        print(f"   Material ID: {material_out.material_id}")
        print(f"   Name: {material_out.name}")
        print(f"   Unit ID: {material_out.unit_id}")
        print(f"   Unit Name: {material_out.unit_name}")
        print(f"   Status: {material_out.status}")
        
        # Verify unit_name is present
        if hasattr(material_out, 'unit_name') and material_out.unit_name:
            print(f"   ✅ Unit name is present: {material_out.unit_name}")
            return True
        else:
            print(f"   ❌ Unit name is missing!")
            return False
            
    except Exception as e:
        print(f"   ❌ Schema test failed: {e}")
        return False

if __name__ == "__main__":
    test_material_schema() 