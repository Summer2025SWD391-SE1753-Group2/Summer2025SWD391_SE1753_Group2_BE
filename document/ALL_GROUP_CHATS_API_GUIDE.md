# API List Tất Cả Group Chat

## Tổng quan

API này cho phép **Moderator** và **Admin** lấy danh sách tất cả group chat trong hệ thống với đầy đủ thông tin, phân trang và tìm kiếm.

---

## Endpoint

```
GET /api/v1/group-chat/all
```

## Quyền truy cập

- **Moderator**: ✅ Có quyền truy cập
- **Admin**: ✅ Có quyền truy cập
- **User thường**: ❌ Không có quyền truy cập

---

## Parameters

| Parameter  | Type     | Required | Default | Description                                 |
| ---------- | -------- | -------- | ------- | ------------------------------------------- |
| `skip`     | `int`    | ❌       | `0`     | Số group chat bỏ qua (cho phân trang)       |
| `limit`    | `int`    | ❌       | `20`    | Số group chat trả về (tối đa 100)           |
| `search`   | `string` | ❌       | `null`  | Từ khóa tìm kiếm trong tên hoặc mô tả group |
| `topic_id` | `UUID`   | ❌       | `null`  | Lọc theo topic ID                           |

---

## Response

### Success Response (200)

```json
{
  "groups": [
    {
      "group_id": "uuid",
      "group_name": "Tên group chat",
      "group_description": "Mô tả group chat",
      "topic_id": "uuid",
      "topic_name": "Tên topic",
      "topic_status": "active",
      "member_count": 5,
      "max_members": 50,
      "message_count": 25,
      "group_leader": "uuid",
      "leader_name": "Tên leader",
      "leader_username": "username_leader",
      "created_by": "uuid",
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z",
      "latest_message": {
        "content": "Nội dung tin nhắn cuối cùng...",
        "sender_name": "Tên người gửi",
        "created_at": "2024-07-05T15:30:00Z"
      },
      "is_active": true
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20,
  "has_more": false
}
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

```json
{
  "detail": "Not enough permissions"
}
```

---

## Ví dụ sử dụng

### 1. Lấy tất cả group chat (trang đầu tiên)

```bash
curl -X GET "http://localhost:8000/api/v1/group-chat/all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Phân trang

```bash
# Trang 2 (bỏ qua 20 group đầu tiên, lấy 10 group tiếp theo)
curl -X GET "http://localhost:8000/api/v1/group-chat/all?skip=20&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Tìm kiếm

```bash
# Tìm kiếm group có tên hoặc mô tả chứa từ "chat"
curl -X GET "http://localhost:8000/api/v1/group-chat/all?search=chat" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Lọc theo topic

```bash
# Chỉ lấy group chat của topic cụ thể
curl -X GET "http://localhost:8000/api/v1/group-chat/all?topic_id=uuid-topic" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Kết hợp nhiều filter

```bash
# Tìm kiếm + phân trang + lọc topic
curl -X GET "http://localhost:8000/api/v1/group-chat/all?search=group&skip=0&limit=5&topic_id=uuid-topic" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Thông tin chi tiết

### Group Chat Info

| Field               | Type       | Description                        |
| ------------------- | ---------- | ---------------------------------- |
| `group_id`          | `UUID`     | ID duy nhất của group              |
| `group_name`        | `string`   | Tên group chat                     |
| `group_description` | `string`   | Mô tả group (có thể null)          |
| `topic_id`          | `UUID`     | ID của topic liên quan             |
| `topic_name`        | `string`   | Tên topic                          |
| `topic_status`      | `string`   | Trạng thái topic (active/inactive) |
| `member_count`      | `int`      | Số thành viên hiện tại             |
| `max_members`       | `int`      | Số thành viên tối đa               |
| `message_count`     | `int`      | Tổng số tin nhắn trong group       |
| `group_leader`      | `UUID`     | ID của leader                      |
| `leader_name`       | `string`   | Tên đầy đủ của leader              |
| `leader_username`   | `string`   | Username của leader                |
| `created_by`        | `UUID`     | ID người tạo group                 |
| `created_at`        | `datetime` | Thời gian tạo                      |
| `updated_at`        | `datetime` | Thời gian cập nhật cuối            |
| `latest_message`    | `object`   | Thông tin tin nhắn cuối cùng       |
| `is_active`         | `boolean`  | Trạng thái hoạt động (luôn true)   |

### Latest Message Info

| Field         | Type       | Description       |
| ------------- | ---------- | ----------------- |
| `content`     | `string`   | Nội dung tin nhắn |
| `sender_name` | `string`   | Tên người gửi     |
| `created_at`  | `datetime` | Thời gian gửi     |

### Pagination Info

| Field      | Type      | Description               |
| ---------- | --------- | ------------------------- |
| `total`    | `int`     | Tổng số group chat        |
| `skip`     | `int`     | Số group đã bỏ qua        |
| `limit`    | `int`     | Số group trả về           |
| `has_more` | `boolean` | Còn group tiếp theo không |

---

## API liên quan

### Xem detail group chat cụ thể

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
  "max_members": 50,
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

---

## Lưu ý quan trọng

1. **Quyền truy cập**: Chỉ moderator và admin mới có thể sử dụng API này
2. **Phân trang**: Mặc định 20 group/trang, tối đa 100 group/trang
3. **Tìm kiếm**: Tìm kiếm trong cả tên group và mô tả group
4. **Sắp xếp**: Kết quả được sắp xếp theo thời gian tạo (mới nhất trước)
5. **Performance**: API được tối ưu với eager loading để tránh N+1 query

---

## So sánh với API khác

| API                              | Quyền           | Mục đích                | Dữ liệu                       |
| -------------------------------- | --------------- | ----------------------- | ----------------------------- |
| `/group-chat/all`                | Moderator/Admin | Quản lý toàn bộ group   | Đầy đủ thông tin + phân trang |
| `/group-chat/{group_id}`         | Tất cả user     | Xem detail group cụ thể | Thông tin cơ bản              |
| `/group-chat/my-groups`          | Tất cả user     | Xem group của mình      | Thông tin cơ bản              |
| `/group-chat/topics/with-groups` | Tất cả user     | Xem topic có group      | Thông tin topic + group       |

---

## Test

Chạy test để kiểm tra API:

```bash
python tests/test_all_group_chats.py
```

Test sẽ kiểm tra:

- ✅ Authentication và authorization
- ✅ Phân trang
- ✅ Tìm kiếm
- ✅ Lọc theo topic
- ✅ Response format
- ✅ Group detail API
