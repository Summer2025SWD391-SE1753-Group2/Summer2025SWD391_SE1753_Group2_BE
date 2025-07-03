# GROUP CHAT API SUMMARY

## Tổng quan

Tài liệu tóm tắt tất cả các API liên quan đến Group Chat, bao gồm 4 chức năng chính: **Xem**, **Sửa**, **Xóa**, và **Tạo** group chat.

---

## 1. API XEM (READ)

### 1.1 Lấy thông tin group chat

```
GET /api/v1/group-chat/{group_id}
```

- **Quyền**: Tất cả user đã đăng nhập
- **Mô tả**: Lấy thông tin chi tiết của group chat
- **Response**: GroupOut với topic_name, leader_name, member_count

### 1.2 Lấy danh sách thành viên

```
GET /api/v1/group-chat/{group_id}/members
```

- **Quyền**: Thành viên của group
- **Mô tả**: Lấy danh sách tất cả thành viên trong group
- **Response**: List[GroupMemberOut]

### 1.3 Lấy lịch sử chat

```
GET /api/v1/group-chat/{group_id}/messages?skip=0&limit=50
```

- **Quyền**: Thành viên của group
- **Mô tả**: Lấy lịch sử tin nhắn trong group
- **Response**: GroupMessageList

### 1.4 Lấy group chat của user

```
GET /api/v1/group-chat/my-groups
```

- **Quyền**: User đã đăng nhập
- **Mô tả**: Lấy danh sách group chat mà user tham gia
- **Response**: List[dict] với thông tin group và role của user

---

## 2. API SỬA (UPDATE)

### 2.1 Cập nhật thông tin group

```
PUT /api/v1/group-chat/{group_id}
```

- **Quyền**: Leader hoặc moderator của group
- **Mô tả**: Cập nhật tên và mô tả group chat
- **Request**: GroupUpdate (name, description)
- **Response**: GroupOut đã cập nhật

### 2.2 Thêm thành viên vào group

```
POST /api/v1/group-chat/{group_id}/members
```

- **Quyền**: Leader hoặc moderator của group
- **Mô tả**: Thêm thành viên mới vào group
- **Request**: GroupMemberCreate (account_id, role)
- **Response**: GroupMemberOut

---

## 3. API XÓA (DELETE)

### 3.1 Xóa group chat

```
DELETE /api/v1/group-chat/{group_id}
```

- **Quyền**: Chỉ admin
- **Mô tả**: Xóa hoàn toàn group chat (bao gồm members, messages)
- **Response**: 204 No Content
- **Lưu ý**: Cần xác nhận trước khi xóa

---

## 4. API TẠO (CREATE)

### 4.1 Lấy danh sách topic có thể tạo group

```
GET /api/v1/group-chat/topics/available
```

- **Quyền**: Moderator/Admin
- **Mô tả**: Lấy danh sách topic active chưa có group chat
- **Response**: List[dict] với topic_id, topic_name, status

### 4.2 Tạo group chat (transaction)

```
POST /api/v1/group-chat/create-transaction
```

- **Quyền**: Moderator/Admin
- **Mô tả**: Tạo group chat mới với transaction safety
- **Request**: GroupChatCreateTransaction
- **Response**: GroupChatTransactionOut
- **Điều kiện**:
  - Topic active và chưa có group chat
  - Ít nhất 2 thành viên
  - Tối đa 50 thành viên

### 4.3 Tạo group chat (legacy)

```
POST /api/v1/group-chat/create
```

- **Quyền**: Moderator/Admin
- **Mô tả**: Tạo group chat theo cách cũ
- **Request**: GroupCreate
- **Response**: GroupOut

---

## 5. API HỖ TRỢ

### 5.1 Gửi tin nhắn

```
POST /api/v1/group-chat/{group_id}/messages
```

- **Quyền**: Thành viên của group
- **Mô tả**: Gửi tin nhắn vào group chat
- **Request**: GroupMessageCreate
- **Response**: GroupMessageOut

### 5.2 Kiểm tra topic có thể tạo group

```
GET /api/v1/group-chat/topics/{topic_id}/check
```

- **Quyền**: Moderator/Admin
- **Mô tả**: Kiểm tra topic có thể tạo group chat không
- **Response**: dict với can_create, reason

### 5.3 Lấy tất cả topic với group chat

```
GET /api/v1/group-chat/topics/with-or-without-group
```

- **Quyền**: Tất cả user
- **Mô tả**: Lấy tất cả topic và thông tin group chat (nếu có)
- **Response**: List[dict] với topic và group_chat info

---

## 6. QUYỀN HẠN CHI TIẾT

| Chức năng    | User | Member | Leader | Moderator | Admin |
| ------------ | ---- | ------ | ------ | --------- | ----- |
| Xem group    | ✅   | ✅     | ✅     | ✅        | ✅    |
| Xem members  | ❌   | ✅     | ✅     | ✅        | ✅    |
| Xem messages | ❌   | ✅     | ✅     | ✅        | ✅    |
| Sửa group    | ❌   | ❌     | ✅     | ✅        | ✅    |
| Thêm member  | ❌   | ❌     | ✅     | ✅        | ✅    |
| Tạo group    | ❌   | ❌     | ❌     | ✅        | ✅    |
| Xóa group    | ❌   | ❌     | ❌     | ❌        | ✅    |

---

## 7. FLOW TẠO GROUP CHAT MỚI

### Bước 1: Chọn topic

```
GET /api/v1/group-chat/topics/available
```

### Bước 2: Nhập thông tin

- Tên group: 1-100 ký tự
- Mô tả: tối đa 500 ký tự (tùy chọn)

### Bước 3: Thêm thành viên

```
GET /api/v1/accounts/search/?name={query}
```

- Ít nhất 2 thành viên
- Tối đa 50 thành viên (bao gồm creator)

### Bước 4: Tạo group

```
POST /api/v1/group-chat/create-transaction
```

---

## 8. ERROR CODES

| Code | Mô tả                                       |
| ---- | ------------------------------------------- |
| 400  | Topic đã có group chat / Topic không active |
| 403  | Không có quyền thực hiện                    |
| 404  | Group/Topic không tồn tại                   |
| 422  | Validation error (tên, số lượng member)     |
| 500  | Server error                                |

---

## 9. SCHEMAS CHÍNH

### GroupOut

```json
{
  "group_id": "uuid",
  "topic_id": "uuid",
  "name": "string",
  "description": "string",
  "group_leader": "uuid",
  "created_by": "uuid",
  "is_chat_group": true,
  "created_at": "datetime",
  "updated_at": "datetime",
  "topic_name": "string",
  "leader_name": "string",
  "member_count": 5
}
```

### GroupChatCreateTransaction

```json
{
  "topic_id": "uuid",
  "name": "string",
  "description": "string",
  "member_ids": ["uuid1", "uuid2"]
}
```

---

## 10. TESTING CHECKLIST

### API Testing

- [ ] Tạo group chat thành công
- [ ] Validation các trường bắt buộc
- [ ] Kiểm tra quyền hạn
- [ ] Error handling
- [ ] Transaction rollback khi lỗi

### Integration Testing

- [ ] Flow tạo group chat hoàn chỉnh
- [ ] Gửi tin nhắn trong group
- [ ] Thêm/xóa thành viên
- [ ] Cập nhật thông tin group
- [ ] Xóa group chat

---

**Lưu ý**: Tất cả API đều yêu cầu authentication token trong header `Authorization: Bearer {token}`.
