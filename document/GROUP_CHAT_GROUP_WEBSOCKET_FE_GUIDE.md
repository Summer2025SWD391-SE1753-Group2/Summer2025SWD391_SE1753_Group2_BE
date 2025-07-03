# HƯỚNG DẪN TÍCH HỢP GROUP CHAT WEBSOCKET CHO FRONTEND

## 1. Đăng nhập & Lấy Access Token

FE cần lấy access token để gọi API và connect WebSocket:

```
POST /api/v1/auth/access-token
Content-Type: application/x-www-form-urlencoded

username=<tên đăng nhập>&password=<mật khẩu>
```

**Response:**

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

---

## 2. Lấy lịch sử chat group khi vào phòng

Khi user vào màn hình chat group, FE cần gọi API để lấy lịch sử tin nhắn:

```
GET /api/v1/group-chat/{group_id}/messages?skip=0&limit=50
Authorization: Bearer <access_token>
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
    // ...
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

- FE nên gọi API này mỗi lần vào group hoặc refresh để đồng bộ tin nhắn.
- Hỗ trợ phân trang (infinite scroll).

---

## 3. Kết nối WebSocket group chat

**Endpoint:**

```
ws://<host>:8000/api/v1/group-chat/ws/group/{group_id}?token=<access_token>
```

- FE dùng access_token làm query param `token`.
- Kết nối xong sẽ nhận được các message hệ thống:
  - `connection_established`
  - `online_members`

**Ví dụ:**

```js
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/group-chat/ws/group/${groupId}?token=${token}`
);
```

---

## 4. Gửi và nhận tin nhắn qua WebSocket

### a. Gửi tin nhắn

```json
{
  "type": "send_message",
  "content": "Nội dung tin nhắn"
}
```

### b. Nhận tin nhắn mới

```json
{
  "type": "group_message",
  "data": {
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
}
```

### c. Xác nhận gửi thành công (cho sender)

```json
{
  "type": "message_sent",
  "message_id": "uuid",
  "group_id": "uuid",
  "status": "sent"
}
```

---

## 5. Typing indicator (đang nhập)

### a. Gửi typing

```json
{
  "type": "typing",
  "is_typing": true
}
```

### b. Nhận typing indicator

```json
{
  "type": "typing_indicator",
  "group_id": "uuid",
  "user_id": "uuid",
  "is_typing": true
}
```

---

## 6. Online members

Khi connect, FE sẽ nhận được:

```json
{
  "type": "online_members",
  "group_id": "uuid",
  "members": ["user_id1", "user_id2", ...]
}
```

- FE nên highlight các user đang online trong group.

---

## 7. Đồng bộ tin nhắn khi refresh

- Khi user refresh hoặc vào lại group, FE gọi lại API lịch sử chat để lấy toàn bộ tin nhắn.
- Sau đó connect lại WebSocket để nhận tin nhắn mới realtime.
- FE nên merge tin nhắn từ API và WebSocket để tránh trùng lặp.

---

## 8. Lưu ý bảo mật

- Luôn dùng access_token hợp lệ cho cả API và WebSocket.
- Không lộ token ra ngoài FE/public.
- Chỉ thành viên group mới xem/gửi được tin nhắn.

---

## 9. Gợi ý UI/UX

- Hiển thị avatar, tên, thời gian gửi cho mỗi tin nhắn.
- Hiển thị trạng thái online/typing của thành viên.
- Hỗ trợ scroll để load thêm lịch sử (infinite scroll).
- Hiển thị rõ ràng lỗi khi mất kết nối WebSocket hoặc token hết hạn.

---

## 10. Tổng kết flow FE:

1. Lấy access_token
2. Gọi API lấy lịch sử chat group
3. Connect WebSocket group chat
4. Lắng nghe và render các message realtime
5. Gửi message/typing qua WebSocket
6. Khi refresh, lặp lại bước 2-5

---

## 11. Quản lý thành viên group

### a. Đổi tên nhóm

```
PUT /api/v1/group-chat/{group_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Tên nhóm mới"
}
```

**Quyền:** Leader hoặc moderator của group

### b. Lấy danh sách thành viên

```
GET /api/v1/group-chat/{group_id}/members
Authorization: Bearer <access_token>
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
    "avatar": "avatar_url",
    "email": "user@example.com"
  }
]
```

### c. Tìm kiếm user để thêm vào nhóm

```
GET /api/v1/accounts/search/?name={keyword}&skip=0&limit=100
Authorization: Bearer <access_token>
```

**Lưu ý:** FE cần filter loại bỏ users đã trong nhóm

### d. Thêm user vào nhóm

```
POST /api/v1/group-chat/{group_id}/members
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "account_id": "uuid",
  "role": "member"
}
```

### e. Xóa thành viên khỏi nhóm

```
DELETE /api/v1/group-chat/{group_id}/members/{account_id}
Authorization: Bearer <access_token>
```

### f. Giới hạn thành viên

- **Tối thiểu:** 2 thành viên
- **Tối đa:** 50 thành viên

---

## 12. Tham khảo thêm

- API chi tiết: `document/GROUP_CHAT_API_GUIDE.md`, `document/GROUP_CHAT_API_SUMMARY.md`
- Nếu cần ví dụ code cụ thể (React, Vue, ...), liên hệ backend!
