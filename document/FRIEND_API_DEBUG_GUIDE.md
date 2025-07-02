# Hướng dẫn Debug API Bạn Bè

## 1. Các lỗi thường gặp

### a. Lỗi "Lỗi khi tải lời mời kết bạn: AxiosError"

**Nguyên nhân có thể:**

- Moderator chưa có lời mời kết bạn nào (BE trả về mảng rỗng)
- Token không hợp lệ hoặc hết hạn
- User không có quyền truy cập API

### b. Lỗi 500 Internal Server Error

**Nguyên nhân có thể:**

- Lỗi trong logic xử lý dữ liệu
- Database connection issue
- Schema validation error

## 2. Cách Debug

### a. Test quyền truy cập

```
GET /api/v1/friends/test-access
```

**Response thành công:**

```json
{
  "user_id": "uuid",
  "username": "moderator123",
  "role": "moderator",
  "status": "active",
  "message": "User can access friend APIs"
}
```

### b. Kiểm tra pending requests

```
GET /api/v1/friends/pending
```

**Response khi không có lời mời:**

```json
[]
```

**Response khi có lời mời:**

```json
[
  {
    "sender_id": "uuid",
    "receiver_id": "uuid",
    "status": "pending",
    "created_at": "2024-07-05T12:00:00Z",
    "updated_at": "2024-07-05T12:00:00Z",
    "sender": {
      "account_id": "uuid",
      "username": "user123",
      "full_name": "Tên đầy đủ",
      "avatar": "avatar_url"
    }
  }
]
```

## 3. Hướng dẫn FE xử lý

### a. Xử lý mảng rỗng

```js
// Khi gọi API pending requests
try {
  const response = await api.get("/friends/pending");
  if (response.data.length === 0) {
    // Hiển thị thông báo "Không có lời mời kết bạn nào"
    setPendingRequests([]);
    setMessage("Không có lời mời kết bạn nào");
  } else {
    setPendingRequests(response.data);
  }
} catch (error) {
  if (error.response?.status === 500) {
    // Lỗi server, hiển thị thông báo lỗi
    setError("Lỗi server, vui lòng thử lại sau");
  } else {
    // Lỗi khác
    setError("Có lỗi xảy ra, vui lòng thử lại");
  }
}
```

### b. Kiểm tra quyền truy cập trước

```js
// Kiểm tra quyền truy cập trước khi gọi API
try {
  const accessTest = await api.get("/friends/test-access");
  console.log("User can access friend APIs:", accessTest.data);

  // Nếu có quyền, gọi API pending requests
  const pendingResponse = await api.get("/friends/pending");
  // Xử lý response...
} catch (error) {
  console.error("Access test failed:", error);
  setError("Không có quyền truy cập tính năng bạn bè");
}
```

## 4. Log Debug từ Backend

Backend sẽ log các thông tin sau khi gọi API `/pending`:

```
Debug: Found X pending requests for user uuid
Debug: Returning X pending requests
```

Nếu có lỗi:

```
Error in list_pending_requests: error_message
```

## 5. Kiểm tra Database

Nếu vẫn có vấn đề, kiểm tra:

1. **Bảng `friend`**: Có lời mời pending nào không
2. **Bảng `account`**: User có tồn tại và active không
3. **Bảng `role`**: User có role đúng không

## 6. Lưu ý

- **Moderator có thể sử dụng tất cả tính năng bạn bè** như user thường
- **API trả về mảng rỗng `[]`** khi không có lời mời kết bạn
- **Không phải lỗi** khi trả về mảng rỗng, đây là trạng thái bình thường

---

Nếu vẫn gặp vấn đề, hãy cung cấp:

1. Response từ `/friends/test-access`
2. Response từ `/friends/pending`
3. Log lỗi chi tiết từ console
