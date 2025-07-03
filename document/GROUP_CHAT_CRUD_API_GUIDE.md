# GROUP CHAT CRUD API GUIDE

## 1. Tổng quan

Hướng dẫn 4 API chính cho group chat:

- **Xem**: Lấy thông tin group chat
- **Sửa**: Cập nhật thông tin group chat
- **Xóa**: Xóa group chat (chỉ admin)
- **Tạo**: Tạo group chat mới (moderator/admin)

---

## 2. API Xem Group Chat

### a. Lấy thông tin group chat

```
GET /api/v1/group-chat/{group_id}
```

**Quyền**: Tất cả user đã đăng nhập
**Response**:

```json
{
  "group_id": "uuid",
  "topic_id": "uuid",
  "name": "Tên group chat",
  "description": "Mô tả group",
  "group_leader": "uuid",
  "created_by": "uuid",
  "is_chat_group": true,
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z",
  "topic_name": "Tên topic",
  "leader_name": "Tên leader",
  "member_count": 5
}
```

### b. Lấy danh sách thành viên

```
GET /api/v1/group-chat/{group_id}/members
```

**Quyền**: Thành viên của group
**Response**: List các thành viên với role, username, avatar

### c. Lấy lịch sử chat

```
GET /api/v1/group-chat/{group_id}/messages?skip=0&limit=50
```

**Quyền**: Thành viên của group
**Response**: Tin nhắn với thông tin sender

---

## 3. API Sửa Group Chat

### Cập nhật thông tin group

```
PUT /api/v1/group-chat/{group_id}
```

**Quyền**: Leader hoặc moderator của group
**Request Body**:

```json
{
  "name": "Tên group mới",
  "description": "Mô tả mới"
}
```

**Response**: Thông tin group đã cập nhật

---

## 4. API Xóa Group Chat

### Xóa group chat

```
DELETE /api/v1/group-chat/{group_id}
```

**Quyền**: Chỉ admin mới có quyền xóa
**Response**: 204 No Content
**Lưu ý**:

- Xóa tất cả thành viên, tin nhắn, và group
- Cần xác nhận trước khi xóa

---

## 5. API Tạo Group Chat (Flow mới)

### Bước 1: Lấy danh sách topic có thể tạo group

```
GET /api/v1/group-chat/topics/available
```

**Quyền**: Moderator/Admin
**Response**: List topic active chưa có group chat

```json
[
  {
    "topic_id": "uuid",
    "topic_name": "Tên topic",
    "status": "active",
    "can_create": true
  }
]
```

### Bước 2: Tạo group chat từ topic đã chọn

```
POST /api/v1/group-chat/create-transaction
```

**Quyền**: Moderator/Admin
**Request Body**:

```json
{
  "topic_id": "uuid-topic",
  "name": "Tên group chat",
  "description": "Mô tả group",
  "member_ids": ["uuid-user-1", "uuid-user-2"]
}
```

**Điều kiện**:

- Topic phải active và chưa có group chat
- Phải thêm ít nhất 2 thành viên
- Tổng thành viên (bao gồm creator) tối đa 50
- Tất cả member_ids phải là user hợp lệ

**Response**:

```json
{
  "group": {
    "group_id": "uuid",
    "name": "Tên group chat",
    "member_count": 3
    // ... thông tin group
  },
  "members": [
    {
      "account_id": "uuid",
      "role": "leader",
      "username": "creator"
      // ... thông tin member
    }
    // ... danh sách members
  ]
}
```

---

## 6. Flow UI/UX Tạo Group Chat

### Bước 1: Chọn topic

- Bấm "Tạo Group Chat" → Hiển thị danh sách topic active chưa có group chat
- Chọn 1 topic từ danh sách

### Bước 2: Nhập thông tin

- Nhập tên group chat (bắt buộc, max 100 ký tự)
- Nhập mô tả (tùy chọn, max 500 ký tự)

### Bước 3: Thêm thành viên

- Search user bằng `GET /api/v1/accounts/search/?name={query}`
- Chọn ít nhất 2 thành viên
- Tổng thành viên tối đa 50

### Bước 4: Xác nhận & tạo

- Kiểm tra lại thông tin
- Bấm "Tạo" để gửi request

---

## 7. Quyền hạn chi tiết

### Tạo group chat

- **Moderator/Admin**: Có thể tạo group chat
- **User thường**: Không có quyền

### Xem group chat

- **Tất cả user**: Xem thông tin group
- **Thành viên group**: Xem lịch sử chat, danh sách thành viên

### Sửa group chat

- **Leader/Moderator**: Cập nhật thông tin group
- **Member**: Không có quyền

### Xóa group chat

- **Admin**: Có thể xóa group chat
- **Leader/Moderator/Member**: Không có quyền

---

## 8. Lỗi thường gặp

### Tạo group chat

```json
{
  "detail": "Topic already has a chat group"
}
```

```json
{
  "detail": "Cannot create group chat for inactive topic"
}
```

```json
{
  "detail": "Must add at least 2 members"
}
```

### Xóa group chat

```json
{
  "detail": "Only admin can delete group chat"
}
```

---

## 9. Flow Tạo Group Chat Mới (Chi tiết)

### Quy trình tạo group chat mới:

1. **Bấm "Tạo Group Chat"** → Hiển thị modal/dialog
2. **Gọi API lấy danh sách topic**: `GET /api/v1/group-chat/topics/available`
3. **Hiển thị danh sách topic** có thể tạo group chat
4. **Chọn topic** từ danh sách
5. **Nhập thông tin group**: tên, mô tả
6. **Thêm thành viên**: search và chọn user
7. **Xác nhận và tạo**: gọi API transaction

### API Endpoints cần thiết:

- `GET /api/v1/group-chat/topics/available` - Lấy topic có thể tạo group
- `GET /api/v1/accounts/search/?name={query}` - Search user để thêm
- `POST /api/v1/group-chat/create-transaction` - Tạo group chat

### Validation rules:

- Topic phải active và chưa có group chat
- Tên group: 1-100 ký tự
- Mô tả: tối đa 500 ký tự (tùy chọn)
- Thành viên: ít nhất 2, tối đa 50 (bao gồm creator)
- Creator tự động là leader

### Error handling:

- 400: Topic đã có group chat
- 400: Topic không active
- 422: Validation errors (tên, số lượng member)
- 403: Không có quyền tạo group

---

Nếu cần thêm ví dụ hoặc hướng dẫn chi tiết, liên hệ backend.
