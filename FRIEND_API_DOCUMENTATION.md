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
