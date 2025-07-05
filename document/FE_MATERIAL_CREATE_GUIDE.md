# Hướng dẫn Frontend: Tạo Material với Unit Information

## Tổng quan

API tạo material yêu cầu `unit_id` và sẽ trả về cả `unit_name` trong response. Frontend cần:

1. Lấy danh sách units để hiển thị cho user chọn
2. Gửi request tạo material với `unit_id`
3. Nhận response chứa `unit_name`

## 1. API Endpoints

### 1.1 Lấy danh sách Units (để chọn)

```
GET /api/v1/units/
```

**Parameters:**

- `skip` (optional): Số units bỏ qua (default: 0)
- `limit` (optional): Số units trả về (default: 100)

**Response:**

```json
{
  "units": [
    {
      "unit_id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Lít",
      "description": "Đơn vị đo thể tích",
      "status": "active",
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z",
      "created_by": "uuid",
      "updated_by": "uuid"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 100,
  "has_more": false
}
```

### 1.2 Tạo Material

```
POST /api/v1/materials/
```

**Headers:**

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "Tên material",
  "status": "active",
  "image_url": "https://example.com/image.jpg",
  "unit_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response (201 Created):**

```json
{
  "material_id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "Tên material",
  "status": "active",
  "image_url": "https://example.com/image.jpg",
  "unit_id": "123e4567-e89b-12d3-a456-426614174000",
  "unit_name": "Lít",
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z",
  "created_by": "uuid",
  "updated_by": "uuid"
}
```

## 2. Flow Frontend

### 2.1 Bước 1: Lấy danh sách Units

```javascript
// Lấy danh sách units để hiển thị dropdown
const fetchUnits = async () => {
  try {
    const response = await fetch("/api/v1/units/?limit=100", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data.units; // Array of units
    } else {
      throw new Error("Failed to fetch units");
    }
  } catch (error) {
    console.error("Error fetching units:", error);
    throw error;
  }
};
```

### 2.2 Bước 2: Hiển thị Form tạo Material

```javascript
// Component form tạo material
const CreateMaterialForm = () => {
  const [units, setUnits] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    status: "active",
    image_url: "",
    unit_id: "",
  });
  const [loading, setLoading] = useState(false);

  // Load units khi component mount
  useEffect(() => {
    const loadUnits = async () => {
      try {
        const unitsData = await fetchUnits();
        setUnits(unitsData);
      } catch (error) {
        // Handle error
      }
    };
    loadUnits();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("/api/v1/materials/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.status === 201) {
        const material = await response.json();
        console.log("Material created:", material);
        // Success: material.unit_name sẽ có sẵn
        alert(
          `Material "${material.name}" created successfully with unit "${material.unit_name}"`
        );
      } else {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create material");
      }
    } catch (error) {
      console.error("Error creating material:", error);
      alert("Failed to create material: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Material Name:</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          maxLength={150}
        />
      </div>

      <div>
        <label>Status:</label>
        <select
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value })}
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div>
        <label>Image URL:</label>
        <input
          type="url"
          value={formData.image_url}
          onChange={(e) =>
            setFormData({ ...formData, image_url: e.target.value })
          }
          maxLength={500}
        />
      </div>

      <div>
        <label>Unit:</label>
        <select
          value={formData.unit_id}
          onChange={(e) =>
            setFormData({ ...formData, unit_id: e.target.value })
          }
          required
        >
          <option value="">Select a unit</option>
          {units.map((unit) => (
            <option key={unit.unit_id} value={unit.unit_id}>
              {unit.name} {unit.description && `(${unit.description})`}
            </option>
          ))}
        </select>
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Creating..." : "Create Material"}
      </button>
    </form>
  );
};
```

## 3. Validation Rules

### 3.1 Material Name

- **Required**: Có
- **Max length**: 150 ký tự
- **Unique**: Tên material phải unique trong hệ thống

### 3.2 Status

- **Required**: Có
- **Values**: `"active"` hoặc `"inactive"`
- **Default**: `"active"`

### 3.3 Image URL

- **Required**: Không
- **Max length**: 500 ký tự
- **Format**: URL hợp lệ

### 3.4 Unit ID

- **Required**: Có
- **Format**: UUID hợp lệ
- **Validation**: Unit phải tồn tại trong database

## 4. Error Handling

### 4.1 Common Errors

**400 Bad Request:**

```json
{
  "detail": "Material name already exists"
}
```

**400 Bad Request:**

```json
{
  "detail": "Unit with ID {unit_id} not found"
}
```

**401 Unauthorized:**

```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**

```json
{
  "detail": "Not enough permissions"
}
```

### 4.2 Error Handling trong Frontend

```javascript
const handleCreateMaterial = async (formData) => {
  try {
    const response = await fetch("/api/v1/materials/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      const material = await response.json();
      return { success: true, data: material };
    } else {
      const errorData = await response.json();

      switch (response.status) {
        case 400:
          if (errorData.detail.includes("already exists")) {
            return { success: false, error: "Material name already exists" };
          } else if (errorData.detail.includes("Unit with ID")) {
            return { success: false, error: "Selected unit not found" };
          }
          break;
        case 401:
          return { success: false, error: "Please login again" };
        case 403:
          return {
            success: false,
            error: "You do not have permission to create materials",
          };
        default:
          return { success: false, error: errorData.detail || "Unknown error" };
      }
    }
  } catch (error) {
    return { success: false, error: "Network error" };
  }
};
```

## 5. Success Response

Khi tạo material thành công, response sẽ chứa đầy đủ thông tin:

```json
{
  "material_id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "Sữa tươi",
  "status": "active",
  "image_url": "https://example.com/milk.jpg",
  "unit_id": "123e4567-e89b-12d3-a456-426614174000",
  "unit_name": "Lít",
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z",
  "created_by": "uuid",
  "updated_by": "uuid"
}
```

**Lưu ý quan trọng:**

- `unit_name` sẽ có sẵn trong response
- Không cần gọi thêm API để lấy unit_name
- Có thể hiển thị ngay: `"Sữa tươi (Lít)"`

## 6. Ví dụ hoàn chỉnh

```javascript
// React component hoàn chỉnh
import React, { useState, useEffect } from "react";

const MaterialCreator = () => {
  const [units, setUnits] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    status: "active",
    image_url: "",
    unit_id: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchUnits();
  }, []);

  const fetchUnits = async () => {
    try {
      const response = await fetch("/api/v1/units/");
      const data = await response.json();
      setUnits(data.units);
    } catch (error) {
      setMessage("Error loading units");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch("/api/v1/materials/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.status === 201) {
        const material = await response.json();
        setMessage(`✅ Created: ${material.name} (${material.unit_name})`);
        setFormData({ name: "", status: "active", image_url: "", unit_id: "" });
      } else {
        const error = await response.json();
        setMessage(`❌ Error: ${error.detail}`);
      }
    } catch (error) {
      setMessage("❌ Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Create New Material</h2>

      {message && (
        <div className={message.includes("✅") ? "success" : "error"}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div>
          <label>Name: *</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            maxLength={150}
          />
        </div>

        <div>
          <label>Unit: *</label>
          <select
            value={formData.unit_id}
            onChange={(e) =>
              setFormData({ ...formData, unit_id: e.target.value })
            }
            required
          >
            <option value="">Select unit</option>
            {units.map((unit) => (
              <option key={unit.unit_id} value={unit.unit_id}>
                {unit.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Status:</label>
          <select
            value={formData.status}
            onChange={(e) =>
              setFormData({ ...formData, status: e.target.value })
            }
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

        <div>
          <label>Image URL:</label>
          <input
            type="url"
            value={formData.image_url}
            onChange={(e) =>
              setFormData({ ...formData, image_url: e.target.value })
            }
            placeholder="https://example.com/image.jpg"
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Material"}
        </button>
      </form>
    </div>
  );
};

export default MaterialCreator;
```

## 7. Testing

### 7.1 Test với cURL

```bash
# 1. Lấy units
curl -X GET "http://localhost:8000/api/v1/units/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Tạo material
curl -X POST "http://localhost:8000/api/v1/materials/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Material",
    "status": "active",
    "image_url": "https://example.com/test.jpg",
    "unit_id": "UNIT_ID_FROM_STEP_1"
  }'
```

### 7.2 Test với Postman

1. **GET** `/api/v1/units/` - Lấy danh sách units
2. **POST** `/api/v1/materials/` - Tạo material với unit_id từ step 1

## 8. Lưu ý quan trọng

1. **Authentication**: Cần có token hợp lệ (admin/moderator role)
2. **Unit ID**: Phải là UUID hợp lệ và tồn tại trong database
3. **Material Name**: Phải unique trong hệ thống
4. **Response**: Sẽ có sẵn `unit_name` trong response, không cần gọi thêm API
5. **Error Handling**: Luôn xử lý các trường hợp lỗi network và validation
