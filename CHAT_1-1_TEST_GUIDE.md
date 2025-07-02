# Hướng Dẫn Test Tính Năng Chat 1-1 (Friend Chat) cho FE

## 1. Đăng ký & Đăng nhập tài khoản

### Đăng ký tài khoản

- **Endpoint:** `POST /api/v1/accounts/`
- **Body:**
  ```json
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "YourPassword@123",
    "full_name": "User One"
  }
  ```
- **Lưu ý:** FE nên đăng ký ít nhất 2 tài khoản để test chat 1-1.

### Đăng nhập lấy access token

- **Endpoint:** `POST /api/v1/auth/access-token`
- **Body (form-data):**

  - `username`: user1
  - `password`: YourPassword@123

- **Response:**
  ```json
  {
    "access_token": "JWT_TOKEN",
    "refresh_token": "...",
    "token_type": "bearer"
  }
  ```
- **Lưu ý:** FE cần lưu lại `access_token` để sử dụng cho các API và WebSocket.

---

## 2. Kết bạn (Friend)

### Gửi lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/request`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:**
  ```json
  {
    "receiver_id": "<UUID của user2>"
  }
  ```

### Chấp nhận lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/accept/{sender_id}`
- **Headers:** `Authorization: Bearer <access_token của user2>`

- Sau khi cả hai đã là bạn, có thể chat 1-1.

---

## 3. Kết nối WebSocket để chat real-time

### Kết nối WebSocket

- **URL:** `ws://<backend-host>:<port>/api/v1/chat/ws/chat?token=<access_token>`
  - Ví dụ: `ws://localhost:8000/api/v1/chat/ws/chat?token=JWT_TOKEN`
- **Lưu ý:** Tham số `token` là access_token lấy từ bước đăng nhập.

### Sự kiện khi kết nối thành công

- FE sẽ nhận được:
  ```json
  {
    "type": "connection_established",
    "user_id": "<your_user_id>",
    "message": "Connected to chat server"
  }
  ```
- Và danh sách bạn bè đang online:
  ```json
  {
    "type": "online_friends",
    "friends": ["<friend_id_1>", "<friend_id_2>", ...]
  }
  ```

---

## 4. Gửi & Nhận tin nhắn qua WebSocket

### Gửi tin nhắn

- **Gửi qua WebSocket:**
  ```json
  {
    "type": "send_message",
    "receiver_id": "<UUID của bạn bè>",
    "content": "Nội dung tin nhắn"
  }
  ```
- **Kết quả trả về cho người gửi:**
  ```json
  {
    "type": "message_sent",
    "message_id": "<id>",
    "status": "sent"
  }
  ```
- **Người nhận sẽ nhận được:**
  ```json
  {
    "type": "new_message",
    "message": {
      "message_id": "<id>",
      "sender_id": "<UUID>",
      "receiver_id": "<UUID>",
      "content": "Nội dung tin nhắn",
      "status": "delivered",
      "created_at": "ISO8601",
      "sender": {
        "account_id": "<UUID>",
        "username": "user1",
        "full_name": "User One",
        "avatar": null
      }
    }
  }
  ```

### Đánh dấu đã đọc tin nhắn

- **Gửi qua WebSocket:**
  ```json
  {
    "type": "mark_read",
    "message_id": "<id>"
  }
  ```
- **Người gửi sẽ nhận được:**
  ```json
  {
    "type": "message_read",
    "message_id": "<id>",
    "read_by": "<user_id>"
  }
  ```

### Gửi trạng thái đang nhập (typing)

- **Gửi qua WebSocket:**
  ```json
  {
    "type": "typing",
    "receiver_id": "<UUID của bạn bè>",
    "is_typing": true
  }
  ```
- **Người nhận sẽ nhận được:**
  ```json
  {
    "type": "typing_indicator",
    "user_id": "<user_id>",
    "is_typing": true
  }
  ```

---

## 5. Lấy lịch sử chat & các API REST hỗ trợ

### Lấy lịch sử chat với bạn bè

- **Endpoint:** `GET /api/v1/chat/messages/history/{friend_id}?skip=0&limit=50`
- **Headers:** `Authorization: Bearer <access_token>`

### Đánh dấu tin nhắn đã đọc (REST)

- **Endpoint:** `PUT /api/v1/chat/messages/{message_id}/read`
- **Headers:** `Authorization: Bearer <access_token>`

### Xóa tin nhắn (chỉ người gửi)

- **Endpoint:** `DELETE /api/v1/chat/messages/{message_id}`
- **Headers:** `Authorization: Bearer <access_token>`

### Đếm số tin nhắn chưa đọc

- **Endpoint:** `GET /api/v1/chat/messages/unread-count`
- **Headers:** `Authorization: Bearer <access_token>`

### Lấy danh sách bạn bè online

- **Endpoint:** `GET /api/v1/chat/friends/online`
- **Headers:** `Authorization: Bearer <access_token>`

---

## 6. Lưu ý khi test

- **Chỉ có thể chat với bạn bè đã được chấp nhận (friend status = accepted).**
- **WebSocket cần truyền access_token qua query param `token`.**
- **FE nên test trên 2 trình duyệt/2 tài khoản để kiểm tra realtime.**
- **Nếu mất kết nối WebSocket, FE nên tự động reconnect.**
- **Kiểm tra các trường hợp lỗi: gửi tin nhắn cho người không phải bạn, gửi tin nhắn rỗng, v.v.**

---

## 7. Ví dụ luồng test nhanh

1. Đăng ký 2 tài khoản, đăng nhập lấy access_token.
2. User1 gửi lời mời kết bạn cho User2, User2 chấp nhận.
3. Cả 2 user mở WebSocket (mỗi user 1 tab/trình duyệt).
4. User1 gửi tin nhắn cho User2, User2 nhận được realtime.
5. User2 gửi lại, User1 nhận được.
6. Test các tính năng: đánh dấu đã đọc, typing, lấy lịch sử chat, xóa tin nhắn, đếm tin chưa đọc.

---

Nếu cần ví dụ cụ thể về request/response hoặc muốn hướng dẫn bằng tiếng Anh, hãy báo lại nhé!
