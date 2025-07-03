# Group Chat Debug Guide

## 🔍 Debug lỗi 422 - Unprocessable Content

### 1. Kiểm tra Request Body

**Lỗi 422 thường xảy ra khi:**

- Thiếu field bắt buộc
- Field có giá trị không hợp lệ
- Format dữ liệu sai

**Request body chuẩn:**

```json
{
  "topic_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Tên Group Chat",
  "description": "Mô tả group (tùy chọn)",
  "max_members": 50
}
```

### 2. Validation Rules

| Field         | Type    | Required | Min | Max | Format           |
| ------------- | ------- | -------- | --- | --- | ---------------- |
| `topic_id`    | UUID    | ✅       | -   | -   | UUID string      |
| `name`        | String  | ✅       | 1   | 100 | Non-empty string |
| `description` | String  | ❌       | 0   | 500 | Optional string  |
| `max_members` | Integer | ✅       | 1   | 50  | Number 1-50      |

### 3. Common 422 Errors & Solutions

#### Error: "field required"

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution:** Điền đầy đủ các field bắt buộc

#### Error: "ensure this value is less than or equal to 50"

```json
{
  "detail": [
    {
      "loc": ["body", "max_members"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Solution:** Đặt `max_members` từ 1-50

#### Error: "value is not a valid uuid"

```json
{
  "detail": [
    {
      "loc": ["body", "topic_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

**Solution:** Đảm bảo `topic_id` là UUID hợp lệ

### 4. Debug Checklist

#### ✅ Kiểm tra trước khi gửi request:

```javascript
const validateBeforeSend = (groupData) => {
  const errors = [];

  // Check topic_id
  if (!groupData.topic_id) {
    errors.push("topic_id is required");
  } else if (!isValidUUID(groupData.topic_id)) {
    errors.push("topic_id must be valid UUID");
  }

  // Check name
  if (!groupData.name || groupData.name.trim() === "") {
    errors.push("name is required");
  } else if (groupData.name.length > 100) {
    errors.push("name must be <= 100 characters");
  }

  // Check max_members
  if (!groupData.max_members) {
    errors.push("max_members is required");
  } else if (groupData.max_members < 1 || groupData.max_members > 50) {
    errors.push("max_members must be between 1-50");
  }

  // Check description (optional)
  if (groupData.description && groupData.description.length > 500) {
    errors.push("description must be <= 500 characters");
  }

  return errors;
};

const isValidUUID = (uuid) => {
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};
```

#### ✅ Log request để debug:

```javascript
const createGroupWithDebug = async (groupData) => {
  // Log request data
  console.log("Request data:", JSON.stringify(groupData, null, 2));

  // Validate before send
  const validationErrors = validateBeforeSend(groupData);
  if (validationErrors.length > 0) {
    console.error("Validation errors:", validationErrors);
    throw new Error("Validation failed: " + validationErrors.join(", "));
  }

  try {
    const response = await axios.post("/api/v1/group-chat/create", groupData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Request failed:", {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
    });
    throw error;
  }
};
```

### 5. Test Cases để Debug

#### Test Case 1: Valid Data

```javascript
const validData = {
  topic_id: "550e8400-e29b-41d4-a716-446655440000",
  name: "Test Group",
  description: "Test description",
  max_members: 50,
};
// Expected: Success (200)
```

#### Test Case 2: Missing Required Fields

```javascript
const invalidData1 = {
  topic_id: "550e8400-e29b-41d4-a716-446655440000",
  // Missing name
  max_members: 50,
};
// Expected: 422 - "field required" for name
```

#### Test Case 3: Invalid UUID

```javascript
const invalidData2 = {
  topic_id: "invalid-uuid",
  name: "Test Group",
  max_members: 50,
};
// Expected: 422 - "value is not a valid uuid"
```

#### Test Case 4: Invalid max_members

```javascript
const invalidData3 = {
  topic_id: "550e8400-e29b-41d4-a716-446655440000",
  name: "Test Group",
  max_members: 100, // > 50
};
// Expected: 422 - "ensure this value is less than or equal to 50"
```

### 6. Network Debug

#### Kiểm tra request trong Browser DevTools:

1. **Network Tab:**

   - Method: POST
   - URL: `/api/v1/group-chat/create`
   - Status: 422
   - Request Headers: `Content-Type: application/json`
   - Request Payload: Kiểm tra JSON format

2. **Console Log:**

```javascript
// Thêm vào code để debug
console.log("Request URL:", "/api/v1/group-chat/create");
console.log("Request Method:", "POST");
console.log("Request Headers:", {
  Authorization: `Bearer ${token}`,
  "Content-Type": "application/json",
});
console.log("Request Body:", groupData);
```

### 7. Backend Log Check

Kiểm tra backend logs để xem chi tiết lỗi:

```bash
# Trong terminal backend
tail -f logs/app.log | grep "422"
```

### 8. Quick Fix Script

```javascript
const quickFix422 = async (groupData) => {
  // Ensure all required fields
  const fixedData = {
    topic_id: groupData.topic_id || null,
    name: groupData.name || "",
    description: groupData.description || "",
    max_members: groupData.max_members || 50,
  };

  // Validate and fix
  if (!fixedData.topic_id) {
    throw new Error("topic_id is required");
  }

  if (!fixedData.name.trim()) {
    throw new Error("name is required");
  }

  if (fixedData.name.length > 100) {
    fixedData.name = fixedData.name.substring(0, 100);
  }

  if (fixedData.description.length > 500) {
    fixedData.description = fixedData.description.substring(0, 500);
  }

  if (fixedData.max_members < 1) {
    fixedData.max_members = 1;
  } else if (fixedData.max_members > 50) {
    fixedData.max_members = 50;
  }

  return fixedData;
};
```

### 9. Common Frontend Mistakes

#### ❌ Sai: Gửi string thay vì number

```javascript
// Wrong
const data = {
  topic_id: "uuid",
  name: "Group",
  max_members: "50", // String instead of number
};

// Correct
const data = {
  topic_id: "uuid",
  name: "Group",
  max_members: 50, // Number
};
```

#### ❌ Sai: Thiếu Content-Type header

```javascript
// Wrong
const response = await axios.post("/api/v1/group-chat/create", data);

// Correct
const response = await axios.post("/api/v1/group-chat/create", data, {
  headers: { "Content-Type": "application/json" },
});
```

#### ❌ Sai: Gửi FormData thay vì JSON

```javascript
// Wrong
const formData = new FormData();
formData.append("topic_id", topicId);
formData.append("name", name);

// Correct
const jsonData = {
  topic_id: topicId,
  name: name,
};
```

### 10. Success Debug

Khi thành công, response sẽ có format:

```json
{
  "group_id": "uuid",
  "name": "Group Name",
  "description": "Description",
  "topic_id": "topic-uuid",
  "topic_name": "Topic Name",
  "group_leader": "leader-uuid",
  "leader_name": "Leader Name",
  "member_count": 1,
  "max_members": 50,
  "is_chat_group": true,
  "created_at": "2024-07-05T12:00:00Z"
}
```

**Kiểm tra:**

- `group_id` có được tạo không?
- `member_count` có = 1 (creator) không?
- `is_chat_group` có = true không?
