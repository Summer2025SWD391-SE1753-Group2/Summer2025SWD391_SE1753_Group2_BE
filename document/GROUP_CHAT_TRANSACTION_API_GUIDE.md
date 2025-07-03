# GROUP CHAT TRANSACTION API GUIDE

## 1. Tổng quan

- Chỉ moderator/admin mới có quyền tạo group chat.
- Mỗi topic chỉ có 1 group chat.
- Group chat tối đa 50 thành viên.
- Tạo group chat là 1 transaction: tạo group, add leader, add nhiều member cùng lúc, rollback nếu lỗi.

---

## 2. Luồng tạo group chat (UI/UX)

### Bước 1: Chọn topic hợp lệ

- Chỉ hiển thị topic **active** và **chưa có group chat**.
- Có thể chọn từ trang topic hoặc trang group chat (list topic chưa có group chat).

### Bước 2: Nhập thông tin group chat

- Nhập tên group chat (bắt buộc, tối đa 100 ký tự).
- Nhập mô tả (tùy chọn, tối đa 500 ký tự).

### Bước 3: Thêm thành viên

- Chọn từ danh sách user (có thể search/filter).
- **Phải chọn ít nhất 2 thành viên** (không tính người tạo).
- Tổng thành viên (bao gồm creator) tối đa 50.

### Bước 4: Xác nhận & tạo group chat

- Hiển thị lại thông tin, danh sách thành viên.
- Bấm "Tạo" để gửi request lên backend.

---

## 3. API tạo group chat (transaction)

### Endpoint

```
POST /api/v1/group-chat/create-transaction
```

### Request Body

```json
{
  "topic_id": "uuid-topic",
  "name": "Tên group chat",
  "description": "Mô tả group chat (tùy chọn)",
  "member_ids": ["uuid-user-1", "uuid-user-2"]
}
```

- `member_ids`: danh sách account_id của các thành viên (không bao gồm creator).
- Phải có ít nhất 2 member_ids, tối đa 49 (tổng với creator là 50).

### Response thành công

```json
{
  "group": {
    "group_id": "uuid-group",
    "topic_id": "uuid-topic",
    "name": "Tên group chat",
    "description": "Mô tả group chat",
    "group_leader": "uuid-creator",
    "created_by": "uuid-creator",
    "is_chat_group": true,
    "created_at": "2024-07-05T12:00:00Z",
    "updated_at": "2024-07-05T12:00:00Z",
    "topic_name": "Tên topic",
    "leader_name": "Tên leader",
    "member_count": 3
  },
  "members": [
    {
      "group_member_id": "uuid",
      "account_id": "uuid-creator",
      "group_id": "uuid-group",
      "role": "leader",
      "joined_at": "2024-07-05T12:00:00Z",
      "username": "creator",
      "full_name": "Tên creator",
      "avatar": "avatar_url"
    },
    {
      "group_member_id": "uuid",
      "account_id": "uuid-user-1",
      "group_id": "uuid-group",
      "role": "member",
      "joined_at": "2024-07-05T12:00:00Z",
      "username": "user1",
      "full_name": "Tên user 1",
      "avatar": "avatar_url"
    }
    // ...
  ]
}
```

---

## 4. Ràng buộc & lưu ý

- Topic phải **active** và **chưa có group chat**.
- Không thể tạo group chat nếu thiếu member hoặc member không hợp lệ.
- Nếu có lỗi ở bất kỳ bước nào, group chat sẽ không được tạo (transaction rollback).
- Thành viên được add vào group sẽ auto join và có thể rời group sau này.
- Người tạo luôn là leader, không thể bị xóa khỏi group.

---

## 5. Lỗi thường gặp

### a. Topic đã có group chat

```json
{
  "detail": "Topic already has a chat group"
}
```

### b. Topic inactive

```json
{
  "detail": "Cannot create group chat for inactive topic"
}
```

### c. Thiếu member

```json
{
  "detail": "Must add at least 2 members"
}
```

### d. Member không hợp lệ

```json
{
  "detail": "Some member accounts not found"
}
```

### e. Lỗi khác (rollback)

```json
{
  "detail": "Failed to create group chat: ..."
}
```

---

## 6. Gợi ý UI/UX

- Chỉ hiển thị nút tạo group chat với topic hợp lệ.
- Validate đủ member, tên group, mô tả trước khi gửi request.
- Hiển thị rõ lỗi trả về từ backend.
- Sau khi tạo thành công, chuyển user sang màn hình chat group mới.
- Thành viên có thể rời group bất cứ lúc nào.

---

## 7. Chọn thành viên bằng search username

### API tìm kiếm user

```
GET /api/v1/accounts/search/?name={query}
```

- `name`: chuỗi cần tìm (username hoặc full name, tìm kiếm partial, không phân biệt hoa thường)
- Trả về: danh sách user phù hợp

**Ví dụ gọi:**

```
GET /api/v1/accounts/search/?name=nguyen
```

**Response:**

```json
[
  {
    "account_id": "uuid",
    "username": "nguyenvanabc",
    "full_name": "Nguyễn Văn A",
    "email": "abc@gmail.com",
    "avatar": "avatar_url"
    // ...
  }
]
```

### Gợi ý UI/UX

- Khi FE nhập username, gọi API này để suggest user (autocomplete).
- Chọn user từ danh sách trả về để add vào member_ids khi tạo group chat.
- Nên loại bỏ user đã trong group khỏi danh sách suggest (nếu cần).

---

## 8. Kiểm tra user đã trong group chat

### API lấy danh sách thành viên group chat

```
GET /api/v1/group-chat/{group_id}/members
```

- Trả về: danh sách các thành viên hiện tại của group chat (bao gồm leader, moderator, member)
- Response là list các object GroupMemberOut (có account_id, username, role, ...)

**Cách sử dụng:**

- Khi FE search user để thêm vào group chat, gọi API này để lấy danh sách account_id các thành viên hiện tại.
- Nếu user đã có trong group chat thì disable nút "Thêm" hoặc ẩn khỏi danh sách suggest.

---

## 10. Lấy lịch sử chat group (group chat history)

### API lấy tin nhắn group chat

```
GET /api/v1/group-chat/{group_id}/messages?skip=0&limit=50
```

- `group_id`: ID của group chat muốn lấy lịch sử
- `skip`, `limit`: phân trang tin nhắn (mặc định skip=0, limit=50)
- Yêu cầu user phải là thành viên của group

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
    // ...
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

**Gợi ý sử dụng:**

- FE gọi API này để lấy lịch sử chat của group chat (tương tự như chat bạn bè với `/chat/{friend_id}`)
- Dùng để render màn hình chat group, phân trang tin nhắn
- Chỉ thành viên group mới xem được lịch sử chat

---

## 11. Xóa group chat

### API xóa group chat

```
DELETE /api/v1/group-chat/{group_id}
```

- `group_id`: ID của group chat muốn xóa
- **Chỉ admin mới có quyền xóa group chat**
- Response: 204 No Content (xóa thành công)

**Lưu ý:**

- Khi xóa group chat, tất cả thành viên sẽ bị remove khỏi group
- Tất cả tin nhắn trong group sẽ bị xóa
- Group chat sẽ bị xóa hoàn toàn khỏi hệ thống
- Cần xác nhận (confirm) trước khi xóa

**Lỗi thường gặp:**

```json
{
  "detail": "Only admin can delete group chat"
}
```

---

Nếu cần thêm ví dụ hoặc hướng dẫn chi tiết, liên hệ backend.
