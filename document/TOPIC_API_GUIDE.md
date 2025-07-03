# TOPIC API GUIDE

## 1. Tổng quan

Các API quản lý Topic cho phép FE thực hiện các thao tác:

- Tạo mới topic
- Lấy danh sách topic
- Lấy chi tiết topic
- Cập nhật topic
- Xóa topic

## 2. Danh sách API

### a. Tạo mới topic

```
POST /api/v1/topics/
```

**Request Body:**

```json
{
  "name": "Tên topic",
  "status": "active" // hoặc "inactive" (tùy chọn)
}
```

**Response:**

```json
{
  "topic_id": "uuid",
  "name": "Tên topic",
  "status": "active",
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z"
}
```

### b. Lấy danh sách topic

```
GET /api/v1/topics/?skip=0&limit=100
```

**Response:**

```json
[
  {
    "topic_id": "uuid",
    "name": "Tên topic",
    "status": "active",
    "created_at": "2024-07-05T12:00:00Z",
    "updated_at": "2024-07-05T12:00:00Z"
  }
]
```

### c. Lấy chi tiết topic

```
GET /api/v1/topics/{topic_id}
```

**Response:**

```json
{
  "topic_id": "uuid",
  "name": "Tên topic",
  "status": "active",
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z"
}
```

### d. Cập nhật topic

```
PUT /api/v1/topics/{topic_id}
```

**Request Body:**

```json
{
  "name": "Tên topic mới",
  "status": "inactive" // hoặc "active"
}
```

**Response:**

```json
{
  "topic_id": "uuid",
  "name": "Tên topic mới",
  "status": "inactive",
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:10:00Z"
}
```

### e. Xóa topic

```
DELETE /api/v1/topics/{topic_id}
```

**Response:**

- 204 No Content (Xóa thành công)

## 3. Lưu ý

- Trường `status` có thể là `active` hoặc `inactive`. Nếu không truyền sẽ mặc định là `active`.
- **Nếu topic có status là `inactive` thì KHÔNG thể tạo group chat từ topic đó. FE cần ẩn/disable nút tạo group chat với các topic này.**
- Khi tạo/cập nhật topic, tên topic phải là duy nhất.
- Khi xóa topic, các liên kết (post, group, ...) liên quan sẽ bị ảnh hưởng.
- Các API này yêu cầu xác thực (token) và phân quyền phù hợp (thường là admin hoặc moderator mới được tạo/xóa/cập nhật topic).

## 4. Ví dụ lỗi thường gặp

### a. Tên topic đã tồn tại

```json
{
  "detail": "Topic name already exists"
}
```

### b. Không tìm thấy topic

```json
{
  "detail": "Topic not found"
}
```

## 5. Cập nhật mới nhất

### Không thể tạo group chat với topic inactive

- Nếu topic có status là `inactive` thì KHÔNG thể tạo group chat từ topic đó.
- Khi gọi API tạo group chat với topic inactive, backend trả về lỗi:

```json
{
  "detail": "Cannot create group chat for inactive topic"
}
```

- Khi gọi API kiểm tra khả năng tạo group chat (`GET /api/v1/group-chat/topics/{topic_id}/check`), nếu topic inactive sẽ trả về:

```json
{
  "can_create": false,
  "reason": "Topic is inactive"
}
```

- FE cần ẩn/disable nút tạo group chat với các topic này và xử lý thông báo phù hợp.

---

Nếu cần thêm ví dụ hoặc hướng dẫn chi tiết, liên hệ backend.
