# Hướng dẫn sử dụng API Đặt Nickname Bạn Bè trong Chat 1-1

## 1. Mô tả tính năng

- Mỗi user có thể đặt nickname riêng cho từng bạn bè của mình.
- Nickname này chỉ hiển thị cho chính user đó trong đoạn chat 1-1.
- Nickname được lưu riêng cho từng phía (A đặt cho B, B đặt cho A).

## 2. API cập nhật nickname

### Endpoint

```
PUT /friends/{friend_id}/nickname
```

### Request Body

```json
{
  "nickname": "Tên bạn muốn đặt"
}
```

- `friend_id`: UUID của bạn bè muốn đặt nickname.
- `nickname`: Nickname mới (tối đa 100 ký tự).

### Ví dụ request

```
PUT /friends/123e4567-e89b-12d3-a456-426614174000/nickname
Content-Type: application/json
{
  "nickname": "Anh Ba đẹp trai"
}
```

### Response thành công

```json
{
  "sender_id": "...",
  "receiver_id": "...",
  "status": "accepted",
  "created_at": "2024-07-05T12:00:00Z",
  "updated_at": "2024-07-05T12:05:00Z",
  "sender_nickname": "Anh Ba đẹp trai",
  "receiver_nickname": null
}
```

- Nếu bạn là sender, trường `sender_nickname` sẽ được cập nhật.
- Nếu bạn là receiver, trường `receiver_nickname` sẽ được cập nhật.

## 3. Lấy nickname khi hiển thị chat

- Khi lấy thông tin bạn bè hoặc lịch sử chat, backend sẽ trả về trường `sender_nickname` và `receiver_nickname`.
- FE nên ưu tiên hiển thị nickname nếu có, nếu không thì hiển thị tên thật.

## 4. Gợi ý UI/UX cho FE

- Cho phép user đổi nickname bạn bè ngay trong giao diện chat (ví dụ: nút "Đổi nickname").
- Khi vào đoạn chat, lấy nickname từ API và hiển thị thay cho tên thật nếu có.
- Nếu nickname rỗng/null, hiển thị tên thật như bình thường.

## 5. Lưu ý

- Nickname là cá nhân hóa, chỉ user đặt mới thấy.
- Đổi nickname không ảnh hưởng đến phía bạn bè.

---

Nếu cần thêm ví dụ hoặc hướng dẫn chi tiết về các API khác, vui lòng liên hệ backend.
