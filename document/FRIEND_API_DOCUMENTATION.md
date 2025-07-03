# Friend API Documentation

## 1. Gửi lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/request`
- **Headers:** `Authorization: Bearer <access_token>`
- **Request Body:**
  ```json
  {
    "receiver_id": "<UUID của người muốn kết bạn>"
  }
  ```
- **Response:**
  ```json
  {
    "sender_id": "<UUID của bạn>",
    "receiver_id": "<UUID của người nhận>",
    "status": "pending",
    "created_at": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
  ```
- **Chức năng:** Gửi lời mời kết bạn tới user khác.

---

## 2. Chấp nhận lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/accept/{sender_id}`
- **Headers:** `Authorization: Bearer <access_token>`
- **Path Param:**
  - `sender_id`: UUID của người đã gửi lời mời kết bạn cho bạn
- **Response:**
  ```json
  {
    "sender_id": "<UUID của người gửi>",
    "receiver_id": "<UUID của bạn>",
    "status": "accepted",
    "created_at": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:05:00Z"
  }
  ```
- **Chức năng:** Chấp nhận lời mời kết bạn từ user khác.

---

## 3. Từ chối lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/reject/{sender_id}`
- **Headers:** `Authorization: Bearer <access_token>`
- **Path Param:**
  - `sender_id`: UUID của người đã gửi lời mời kết bạn cho bạn
- **Response:**
  ```json
  {
    "sender_id": "<UUID của người gửi>",
    "receiver_id": "<UUID của bạn>",
    "status": "rejected",
    "created_at": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:05:00Z"
  }
  ```
- **Chức năng:** Từ chối lời mời kết bạn từ user khác.

---

## 4. Lấy danh sách bạn bè

- **Endpoint:** `GET /api/v1/friends/list`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  [
    {
      "account_id": "<UUID>",
      "username": "user1",
      "email": "user1@example.com",
      "full_name": "User One",
      "avatar": null,
      "status": "active",
      "role": {
        "role_id": 1,
        "role_name": "user",
        "status": "active"
      },
      "email_verified": true,
      "phone_verified": false,
      "phone_number": null,
      "date_of_birth": null,
      "created_at": "2024-06-01T12:00:00Z",
      "updated_at": "2024-06-01T12:00:00Z",
      "created_by": null,
      "updated_by": null,
      "friend_count": 5,
      "is_friend": true
    },
    ...
  ]
  ```
- **Chức năng:** Lấy danh sách tất cả bạn bè đã kết bạn.

---

## 5. Lấy danh sách lời mời kết bạn đang chờ xử lý

- **Endpoint:** `GET /api/v1/friends/pending`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  [
    {
      "sender_id": "<UUID của người gửi>",
      "receiver_id": "<UUID của bạn>",
      "status": "pending",
      "created_at": "2024-06-01T12:00:00Z",
      "updated_at": "2024-06-01T12:00:00Z"
    },
    ...
  ]
  ```
- **Chức năng:** Lấy danh sách các lời mời kết bạn bạn nhận được mà chưa xử lý.

---

## 6. Xóa bạn

- **Endpoint:** `DELETE /api/v1/friends/{friend_id}`
- **Headers:** `Authorization: Bearer <access_token>`
- **Path Param:**
  - `friend_id`: UUID của bạn muốn xóa
- **Response:**
  ```json
  {
    "message": "Friend removed successfully"
  }
  ```
- **Chức năng:** Xóa một người khỏi danh sách bạn bè.

---

## 7. Kiểm tra trạng thái bạn bè

- **Endpoint:** `GET /api/v1/friends/status/{friend_id}`
- **Headers:** `Authorization: Bearer <access_token>`
- **Path Param:**
  - `friend_id`: UUID của user muốn kiểm tra trạng thái quan hệ bạn bè
- **Response:**
  ```json
  { "status": "friends" }           // Đã là bạn bè
  { "status": "request_sent" }      // Bạn đã gửi lời mời kết bạn cho người này
  { "status": "request_received" }  // Người này đã gửi lời mời kết bạn cho bạn
  { "status": "none" }              // Không có quan hệ bạn bè/lời mời nào
  ```
- **Chức năng:** FE dùng API này để xác định trạng thái bạn bè, hiển thị đúng nút "Thêm bạn", "Đã gửi lời mời", "Đã nhận lời mời" hoặc "Bạn bè".

---

## Lưu ý khi tìm kiếm và gửi lời mời kết bạn

- Khi user đã gửi lời mời kết bạn cho một người, nếu tiếp tục gửi nữa, backend sẽ trả về lỗi:
  ```json
  {
    "detail": "Friend request already exists"
  }
  ```
- FE cần kiểm tra response của API gửi lời mời kết bạn (`POST /api/v1/friends/request`). Nếu nhận được lỗi này, nên hiển thị thông báo cho user biết: "Bạn đã gửi lời mời kết bạn trước đó, vui lòng chờ xác nhận."
- Ngoài ra, nếu đã là bạn bè hoặc đã có lời mời chờ xử lý, backend cũng sẽ trả về lỗi tương tự. FE nên disable nút gửi lời mời hoặc hiển thị trạng thái phù hợp trong danh sách tìm kiếm bạn bè.

---
