# 📋 User Profile APIs Documentation

## 🔐 Authentication

Tất cả các API đều yêu cầu JWT Bearer token:

```http
Authorization: Bearer {access_token}
```

---

## 📖 API Endpoints

### 1. **GET /api/v1/accounts/me** - Xem profile của user đang đăng nhập

**Mô tả:** Lấy thông tin chi tiết của user đang đăng nhập

**Request:**

```http
GET /api/v1/accounts/me
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": "https://example.com/avatar.jpg",
  "background_url": "https://example.com/background.jpg",
  "bio": "Hello, I'm John!",
  "status": "active",
  "role": {
    "role_id": 1,
    "role_name": "user"
  },
  "email_verified": true,
  "phone_verified": false,
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "friend_count": 15,
  "is_friend": null
}
```

**Error Responses:**

- `401 Unauthorized`: Token không hợp lệ hoặc hết hạn
- `403 Forbidden`: Không có quyền truy cập

---

### 2. **GET /api/v1/accounts/profiles/{username}** - Xem profile của user khác

**Mô tả:** Xem thông tin profile của một user khác theo username

**Request:**

```http
GET /api/v1/accounts/profiles/jane_smith
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440001",
  "username": "jane_smith",
  "email": "jane@example.com",
  "full_name": "Jane Smith",
  "avatar": "https://example.com/jane_avatar.jpg",
  "background_url": "https://example.com/jane_bg.jpg",
  "bio": "Food lover and chef!",
  "status": "active",
  "role": {
    "role_id": 1,
    "role_name": "user"
  },
  "email_verified": true,
  "phone_verified": true,
  "phone_number": "+1234567891",
  "date_of_birth": "1992-05-15",
  "created_at": "2024-01-02T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z",
  "friend_count": 8,
  "is_friend": true
}
```

**Error Responses:**

- `401 Unauthorized`: Token không hợp lệ
- `404 Not Found`: User không tồn tại
- `400 Bad Request`: User không active

---

### 3. **PUT /api/v1/accounts/me** - Cập nhật profile của user đang đăng nhập

**Mô tả:** Cập nhật thông tin profile của user đang đăng nhập

**Request:**

```http
PUT /api/v1/accounts/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "new_email@example.com",
  "phone": "+1234567890",
  "full_name": "John Updated Doe",
  "date_of_birth": "1990-01-01",
  "avatar": "https://example.com/new_avatar.jpg",
  "background_url": "https://example.com/new_bg.jpg",
  "bio": "Updated bio information"
}
```

**Response (200 OK):**

```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "new_email@example.com",
  "full_name": "John Updated Doe",
  "avatar": "https://example.com/new_avatar.jpg",
  "background_url": "https://example.com/new_bg.jpg",
  "bio": "Updated bio information",
  "status": "active",
  "role": {
    "role_id": 1,
    "role_name": "user"
  },
  "email_verified": false,
  "phone_verified": false,
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "friend_count": 15,
  "is_friend": null
}
```

**Lưu ý:**

- Khi cập nhật email, hệ thống sẽ gửi email xác thực và set `email_verified = false`
- Khi cập nhật phone, hệ thống sẽ set `phone_verified = false`

**Error Responses:**

- `401 Unauthorized`: Token không hợp lệ
- `400 Bad Request`: Dữ liệu không hợp lệ hoặc email/phone đã tồn tại
- `422 Validation Error`: Dữ liệu không đúng format

---

### 4. **POST /api/v1/accounts/update-password** - Cập nhật mật khẩu

**Mô tả:** Cập nhật mật khẩu cho user đang đăng nhập

**Request:**

```http
POST /api/v1/accounts/update-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "old_password123",
  "new_password": "new_password123"
}
```

**Cho Google Users:**

```json
{
  "new_password": "new_password123"
}
```

**Response (200 OK):**

```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": "https://example.com/avatar.jpg",
  "background_url": "https://example.com/background.jpg",
  "bio": "Hello, I'm John!",
  "status": "active",
  "role": {
    "role_id": 1,
    "role_name": "user"
  },
  "email_verified": true,
  "phone_verified": false,
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "friend_count": 15,
  "is_friend": null
}
```

**Error Responses:**

- `401 Unauthorized`: Token không hợp lệ
- `400 Bad Request`: Mật khẩu hiện tại không đúng (cho regular users)
- `422 Validation Error`: Mật khẩu không đúng format

---

### 5. **POST /api/v1/accounts/update-username** - Cập nhật username

**Mô tả:** Cập nhật username cho user đang đăng nhập

**Request:**

```http
POST /api/v1/accounts/update-username
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "new_username": "john_updated"
}
```

**Response (200 OK):**

```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_updated",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": "https://example.com/avatar.jpg",
  "background_url": "https://example.com/background.jpg",
  "bio": "Hello, I'm John!",
  "status": "active",
  "role": {
    "role_id": 1,
    "role_name": "user"
  },
  "email_verified": true,
  "phone_verified": false,
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "friend_count": 15,
  "is_friend": null
}
```

**Error Responses:**

- `401 Unauthorized`: Token không hợp lệ
- `400 Bad Request`: Username đã tồn tại
- `422 Validation Error`: Username không đúng format

---

### 6. **GET /api/v1/accounts/is-google-user** - Kiểm tra Google User

**Mô tả:** Kiểm tra xem user đang đăng nhập có phải là Google user không

**Request:**

```http
GET /api/v1/accounts/is-google-user
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "is_google_user": true,
  "username": "john_doe",
  "email": "john@gmail.com"
}
```

**Response cho Regular User:**

```json
{
  "is_google_user": false,
  "username": "john_doe",
  "email": "john@example.com"
}
```

---

## 🔍 **Tìm kiếm Users**

### **GET /api/v1/accounts/search/** - Tìm kiếm users theo tên

**Mô tả:** Tìm kiếm users theo username hoặc full name

**Request:**

```http
GET /api/v1/accounts/search/?name=john&skip=0&limit=10
Authorization: Bearer {access_token}
```

**Query Parameters:**

- `name` (required): Từ khóa tìm kiếm
- `skip` (optional): Số lượng records bỏ qua (default: 0)
- `limit` (optional): Số lượng records trả về (default: 100)

**Response (200 OK):**

```json
[
  {
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "avatar": "https://example.com/avatar.jpg",
    "background_url": "https://example.com/background.jpg",
    "bio": "Hello, I'm John!",
    "status": "active",
    "role": {
      "role_id": 1,
      "role_name": "user"
    },
    "email_verified": true,
    "phone_verified": false,
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "friend_count": 15,
    "is_friend": true
  }
]
```

---

## 📊 **Data Models**

### AccountOut Schema

```json
{
  "account_id": "UUID",
  "username": "string",
  "email": "string",
  "full_name": "string | null",
  "avatar": "string | null",
  "background_url": "string | null",
  "bio": "string | null",
  "status": "active | inactive | banned",
  "role": {
    "role_id": "integer",
    "role_name": "user | moderator | admin"
  },
  "email_verified": "boolean",
  "phone_verified": "boolean",
  "phone_number": "string | null",
  "date_of_birth": "date | null",
  "created_at": "datetime",
  "updated_at": "datetime",
  "friend_count": "integer | null",
  "is_friend": "boolean | null"
}
```

### AccountUpdate Schema

```json
{
  "email": "string | null",
  "phone": "string | null",
  "full_name": "string | null",
  "date_of_birth": "date | null",
  "avatar": "string | null",
  "background_url": "string | null",
  "bio": "string | null"
}
```

---

## 🚀 **Usage Examples**

### JavaScript/TypeScript

```javascript
// Lấy profile của user đang đăng nhập
const getMyProfile = async (token) => {
  const response = await fetch("/api/v1/accounts/me", {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return response.json();
};

// Cập nhật profile
const updateProfile = async (token, profileData) => {
  const response = await fetch("/api/v1/accounts/me", {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profileData),
  });
  return response.json();
};

// Tìm kiếm users
const searchUsers = async (token, name) => {
  const response = await fetch(`/api/v1/accounts/search/?name=${name}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.json();
};
```

### Python

```python
import requests

# Lấy profile của user đang đăng nhập
def get_my_profile(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('/api/v1/accounts/me', headers=headers)
    return response.json()

# Cập nhật profile
def update_profile(token, profile_data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.put('/api/v1/accounts/me',
                           headers=headers,
                           json=profile_data)
    return response.json()
```

---

## ⚠️ **Important Notes**

1. **Authentication:** Tất cả API đều yêu cầu JWT Bearer token
2. **Permissions:**
   - User chỉ có thể cập nhật profile của chính mình
   - Moderator/Admin có thể xem profile của tất cả users
3. **Email Verification:** Khi cập nhật email, user cần xác thực lại
4. **Google Users:** Google users có thể cập nhật password mà không cần current_password
5. **Rate Limiting:** Có thể có giới hạn số request để tránh spam

---

## 🔗 **Related APIs**

- **Authentication:** `/api/v1/auth/access-token`
- **Google OAuth:** `/api/v1/auth/google/login`
- **Friends:** `/api/v1/friends/list`
- **Groups:** `/api/v1/groups/`

---

_Last updated: January 2025_
