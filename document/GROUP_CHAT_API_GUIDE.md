# Hướng dẫn sử dụng API Chat Group

## 1. Tổng quan tính năng

- **Moderator và Admin** có thể tạo group chat từ topic.
- **1 topic = 1 group chat** (tối đa).
- **1 group chat = 50 thành viên** (tối đa).
- **Người tạo = Leader** của nhóm.
- **Leader và Moderator** có thể thêm thành viên.

## 2. Quyền và vai trò

### a. Vai trò trong group:

- **Leader**: Người tạo group, có quyền cao nhất.
- **Moderator**: Có thể quản lý thành viên.
- **Member**: Thành viên thường.

### b. Quyền tạo group:

- Chỉ **Moderator** và **Admin** mới có thể tạo group chat.

## 3. API Endpoints

### a. Tạo group chat từ topic

```
POST /group-chat/create
```

**Request Body:**

```json
{
  "topic_id": "uuid-of-topic",
  "name": "Tên group chat",
  "description": "Mô tả group (optional)",
  "max_members": 50
}
```

**Response:**

```json
{
  "group_id": "uuid",
  "topic_id": "uuid",
  "name": "Tên group chat",
  "description": "Mô tả group",
  "max_members": 50,
  "group_leader": "uuid",
  "created_by": "uuid",
  "is_chat_group": true,
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z",
  "topic_name": "Tên topic",
  "leader_name": "Tên leader",
  "member_count": 1
}
```

### b. Lấy thông tin group

```
GET /group-chat/{group_id}
```

### c. Thêm thành viên vào group

```
POST /group-chat/{group_id}/members
```

**Request Body:**

```json
{
  "account_id": "uuid-of-user",
  "role": "member" // "leader", "moderator", "member"
}
```

### d. Lấy danh sách thành viên

```
GET /group-chat/{group_id}/members
```

**Response:**

```json
[
  {
    "group_member_id": "uuid",
    "account_id": "uuid",
    "group_id": "uuid",
    "role": "leader",
    "joined_at": "2024-07-05T12:00:00Z",
    "username": "user123",
    "full_name": "Tên đầy đủ",
    "avatar": "avatar_url"
  }
]
```

### e. Gửi tin nhắn trong group

```
POST /group-chat/{group_id}/messages
```

**Request Body:**

```json
{
  "content": "Nội dung tin nhắn"
}
```

**Response:**

```json
{
  "message_id": "uuid",
  "group_id": "uuid",
  "sender_id": "uuid",
  "content": "Nội dung tin nhắn",
  "status": "sent",
  "is_deleted": false,
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:00:00Z",
  "sender": {
    "account_id": "uuid",
    "username": "user123",
    "full_name": "Tên đầy đủ",
    "avatar": "avatar_url"
  }
}
```

### f. Lấy lịch sử chat của group

```
GET /group-chat/{group_id}/messages?skip=0&limit=50
```

**Response:**

```json
{
  "messages": [
    {
      "message_id": "uuid",
      "group_id": "uuid",
      "sender_id": "uuid",
      "content": "Nội dung tin nhắn",
      "status": "sent",
      "is_deleted": false,
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z",
      "sender": {
        "account_id": "uuid",
        "username": "user123",
        "full_name": "Tên đầy đủ",
        "avatar": "avatar_url"
      }
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

## 4. Ràng buộc và lưu ý

### a. Ràng buộc:

- **1 topic chỉ có thể có 1 group chat**.
- **Group chat tối đa 50 thành viên**.
- **Chỉ thành viên mới có thể gửi tin nhắn**.
- **Chỉ Leader và Moderator mới có thể thêm thành viên**.

### b. Lưu ý:

- Khi tạo group, người tạo tự động trở thành Leader.
- Group chat được đánh dấu bằng trường `is_chat_group = true`.
- Tin nhắn có trạng thái: `sent`, `delivered`, `read`.

## 5. Gợi ý UI/UX cho FE

### a. Tạo group:

- Hiển thị danh sách topic chưa có group chat.
- Form tạo group với validation.
- Hiển thị thông báo nếu topic đã có group.

### b. Quản lý thành viên:

- Hiển thị danh sách thành viên với vai trò.
- Form thêm thành viên (chỉ Leader/Moderator thấy).
- Hiển thị số lượng thành viên hiện tại/tối đa.

### c. Chat interface:

- Hiển thị tin nhắn với thông tin người gửi.
- Phân biệt vai trò bằng màu sắc hoặc icon.
- Hiển thị trạng thái tin nhắn.

---

Nếu cần thêm ví dụ hoặc hướng dẫn chi tiết, vui lòng liên hệ backend.
