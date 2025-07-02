# Hướng dẫn FE: Lấy và Hiển thị Nickname Bạn Bè Đúng Cách trong Chat 1-1

## 1. Vấn đề thường gặp

- Sau khi đổi nickname, FE hiển thị đúng nhưng khi reload hoặc quay lại đoạn chat thì nickname bị mất.
- Nguyên nhân: FE không lấy lại nickname từ backend mà chỉ dùng dữ liệu cũ hoặc không lấy gì cả.

## 2. Nguyên tắc quan trọng

- **Nickname là dữ liệu cá nhân hóa, luôn phải lấy từ backend mỗi khi vào đoạn chat.**
- Không lưu nickname lâu dài ở localStorage hoặc cache mà không đồng bộ lại với backend.

## 3. API đã được cập nhật - Backend trả về nickname

### a. API lấy danh sách bạn bè (ĐÃ CẬP NHẬT)

```
GET /friends/list
```

**Response mới:**

```json
[
  {
    "account_id": "...",
    "username": "user123",
    "full_name": "Pham Dang Khoi",
    "email": "user@example.com",
    "avatar": "avatar_url",
    "nickname": "Anh Ba đẹp trai" // ← TRƯỜNG NICKNAME MỚI
  }
]
```

**Lưu ý quan trọng:**

- Trường `nickname` sẽ chứa nickname mà user hiện tại đã đặt cho bạn bè đó.
- Nếu chưa đặt nickname, trường này sẽ là `null`.
- FE nên ưu tiên hiển thị `nickname` nếu có, nếu không thì hiển thị `full_name` hoặc `username`.

### b. API cập nhật nickname

```
PUT /friends/{friend_id}/nickname
Body: { "nickname": "Tên mới" }
```

## 4. Hướng dẫn lấy nickname mới nhất

### a. Sau khi đổi nickname thành công

- Gọi API `PUT /friends/{friend_id}/nickname` để cập nhật nickname.
- Sau khi nhận response thành công, **gọi lại API `GET /friends/list`** để lấy danh sách bạn bè mới nhất.
- Cập nhật UI với nickname mới từ response.

### b. Khi vào đoạn chat (hoặc reload)

- **Luôn gọi API `GET /friends/list`** để lấy danh sách bạn bè với nickname mới nhất.
- Tìm bạn bè cần hiển thị trong response và lấy trường `nickname`.

### c. Khi hiển thị tên trong chat

```js
// Logic hiển thị tên
const displayName = friend.nickname || friend.full_name || friend.username;
```

## 5. Ví dụ luồng FE

1. **User đổi nickname**

   - Gọi `PUT /friends/{friend_id}/nickname`
   - Nhận response thành công.
   - **Gọi lại `GET /friends/list`** để lấy danh sách mới.
   - Cập nhật UI với nickname mới.

2. **User reload hoặc quay lại đoạn chat**
   - Gọi `GET /friends/list` để lấy danh sách bạn bè với nickname.
   - Tìm bạn bè cần hiển thị và lấy trường `nickname`.
   - Hiển thị nickname nếu có.

## 6. Gợi ý code (pseudo-code)

```js
// Khi vào đoạn chat hoặc reload
async function loadChat(friendId) {
  const friends = await api.get("/friends/list");
  const friend = friends.find((f) => f.account_id === friendId);
  const displayName = friend.nickname || friend.full_name || friend.username;
  // Hiển thị displayName trên UI
}

// Sau khi đổi nickname
async function updateNickname(friendId, newNickname) {
  await api.put(`/friends/${friendId}/nickname`, { nickname: newNickname });
  // Gọi lại danh sách bạn bè để lấy nickname mới
  const friends = await api.get("/friends/list");
  // Cập nhật UI với dữ liệu mới
}
```

## 7. Lưu ý

- **Backend đã cập nhật API `/friends/list`** để trả về trường `nickname`.
- Không lưu nickname ở localStorage hoặc cache lâu dài – luôn lấy từ backend.
- Nếu có cache, hãy refresh cache mỗi lần đổi nickname hoặc reload chat.

---

Nếu cần ví dụ cụ thể cho framework FE (React, Vue, v.v.), vui lòng liên hệ backend để được hỗ trợ thêm.
