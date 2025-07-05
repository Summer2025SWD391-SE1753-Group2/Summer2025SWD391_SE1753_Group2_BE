# API Summary - Tổng Quan Hệ Thống

## Tổng quan

Tài liệu này cung cấp tổng quan về tất cả các API trong hệ thống, bao gồm các endpoint chính và tính năng phân trang.

---

## 1. Authentication & Authorization

### Auth APIs
- `POST /api/v1/auth/login` - Đăng nhập
- `POST /api/v1/auth/register` - Đăng ký
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Đăng xuất

### Google OAuth
- `GET /api/v1/auth/google/login` - Google OAuth login
- `GET /api/v1/auth/google/callback` - Google OAuth callback

---

## 2. User Management

### Account APIs
- `GET /api/v1/accounts/me` - Lấy thông tin user hiện tại
- `GET /api/v1/accounts/all` - Lấy tất cả accounts (Admin only)
- `PUT /api/v1/accounts/me` - Cập nhật thông tin cá nhân
- `PUT /api/v1/accounts/{account_id}` - Cập nhật account (Admin/Moderator)

### Role Management
- `GET /api/v1/roles/` - Lấy danh sách roles
- `POST /api/v1/roles/` - Tạo role mới (Admin only)
- `PUT /api/v1/roles/{role_id}` - Cập nhật role (Admin only)

---

## 3. Content Management

### Posts APIs
- `GET /api/v1/posts/` - Lấy danh sách posts (có phân trang)
- `GET /api/v1/posts/approved/` - Lấy posts đã approved (có phân trang)
- `GET /api/v1/posts/{post_id}` - Lấy chi tiết post
- `POST /api/v1/posts/` - Tạo post mới
- `PUT /api/v1/posts/{post_id}` - Cập nhật post
- `DELETE /api/v1/posts/{post_id}` - Xóa post
- `GET /api/v1/posts/search/` - Tìm kiếm posts
- `GET /api/v1/posts/search/by-tag/` - Tìm posts theo tag
- `GET /api/v1/posts/search/by-topic/` - Tìm posts theo topic

### Comments APIs
- `GET /api/v1/comments/{post_id}` - Lấy comments của post
- `POST /api/v1/comments/` - Tạo comment mới
- `PUT /api/v1/comments/{comment_id}` - Cập nhật comment
- `DELETE /api/v1/comments/{comment_id}` - Xóa comment

---

## 4. Tag Management

### Tags APIs (Có Phân Trang)
- `GET /api/v1/tags/` - Lấy danh sách tags với phân trang
- `GET /api/v1/tags/{tag_id}` - Lấy chi tiết tag
- `POST /api/v1/tags/` - Tạo tag mới
- `PUT /api/v1/tags/{tag_id}` - Cập nhật tag
- `DELETE /api/v1/tags/{tag_id}` - Xóa tag

**Response Format:**
```json
{
  "tags": [...],
  "total": 50,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

---

## 5. Topic Management

### Topics APIs (Có Phân Trang)
- `GET /api/v1/topics/` - Lấy danh sách topics với phân trang
- `GET /api/v1/topics/{topic_id}` - Lấy chi tiết topic
- `POST /api/v1/topics/` - Tạo topic mới
- `PUT /api/v1/topics/{topic_id}` - Cập nhật topic
- `DELETE /api/v1/topics/{topic_id}` - Xóa topic

**Response Format:**
```json
{
  "topics": [...],
  "total": 30,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

---

## 6. Unit Management

### Units APIs (Có Phân Trang)
- `GET /api/v1/units/` - Lấy danh sách units với phân trang
- `GET /api/v1/units/{unit_id}` - Lấy chi tiết unit
- `POST /api/v1/units/` - Tạo unit mới
- `PUT /api/v1/units/{unit_id}` - Cập nhật unit
- `DELETE /api/v1/units/{unit_id}` - Xóa unit
- `GET /api/v1/units/search/` - Tìm kiếm units

**Response Format:**
```json
{
  "units": [...],
  "total": 15,
  "skip": 0,
  "limit": 20,
  "has_more": false
}
```

---

## 7. Material Management

### Materials APIs (Có Phân Trang)
- `GET /api/v1/materials/` - Lấy danh sách materials với phân trang
- `GET /api/v1/materials/{material_id}` - Lấy chi tiết material
- `POST /api/v1/materials/` - Tạo material mới
- `PUT /api/v1/materials/{material_id}` - Cập nhật material
- `DELETE /api/v1/materials/{material_id}` - Xóa material

**Response Format:**
```json
{
  "materials": [...],
  "total": 200,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

---

## 8. Group Management

### Groups APIs
- `GET /api/v1/groups/` - Lấy danh sách groups (có phân trang)
- `GET /api/v1/groups/search/` - Tìm kiếm groups với phân trang
- `GET /api/v1/groups/{group_id}` - Lấy chi tiết group
- `POST /api/v1/groups/` - Tạo group mới
- `PUT /api/v1/groups/{group_id}` - Cập nhật group
- `DELETE /api/v1/groups/{group_id}` - Xóa group

### Group Members APIs
- `GET /api/v1/group-members/{group_id}` - Lấy members của group
- `GET /api/v1/group-members/search/` - Tìm kiếm members với phân trang
- `POST /api/v1/group-members/` - Thêm member vào group
- `DELETE /api/v1/group-members/{member_id}` - Xóa member khỏi group

---

## 9. Group Chat System

### Group Chat APIs
- `GET /api/v1/group-chat/my-groups` - Lấy groups của user
- `GET /api/v1/group-chat/all` - Lấy tất cả group chats (Moderator/Admin)
- `POST /api/v1/group-chat/create` - Tạo group chat mới
- `PUT /api/v1/group-chat/{group_id}` - Cập nhật group chat
- `DELETE /api/v1/group-chat/{group_id}` - Xóa group chat

### Topic Management for Chat Groups
- `GET /api/v1/group-chat/topics/available` - Topics có thể tạo chat group
- `GET /api/v1/group-chat/topics/with-groups` - Topics đã có chat group
- `GET /api/v1/group-chat/topics/with-or-without-group` - Tất cả topics với thông tin group

### Group Chat Messages
- `GET /api/v1/group-chat/{group_id}/messages` - Lấy tin nhắn của group
- `POST /api/v1/group-chat/{group_id}/messages` - Gửi tin nhắn
- `DELETE /api/v1/group-chat/messages/{message_id}` - Xóa tin nhắn

### Group Members Management
- `GET /api/v1/group-chat/{group_id}/members/search` - Tìm kiếm members với phân trang
- `POST /api/v1/group-chat/{group_id}/members` - Thêm member
- `DELETE /api/v1/group-chat/{group_id}/members/{account_id}` - Xóa member

---

## 10. Favourites System

### Favourites APIs (Có Phân Trang)
- `GET /api/v1/favourites/` - Lấy danh sách favourites với phân trang
- `POST /api/v1/favourites/` - Tạo favourite mới
- `PUT /api/v1/favourites/{favourite_id}` - Cập nhật favourite
- `DELETE /api/v1/favourites/{favourite_id}` - Xóa favourite
- `GET /api/v1/favourites/{favourite_id}/posts` - Lấy posts trong favourite
- `GET /api/v1/favourites/name/{favourite_name}/posts` - Lấy posts theo tên favourite

---

## 11. WebSocket APIs

### Real-time Communication
- `WS /ws/{user_id}` - WebSocket connection cho real-time chat
- `WS /ws/group/{group_id}` - WebSocket connection cho group chat

---

## 12. Pagination Standards

### Common Parameters
Tất cả các API có phân trang đều sử dụng:
- `skip`: Số items bỏ qua (default: 0)
- `limit`: Số items trả về (default: 10-100, tùy API)

### Response Format
```json
{
  "items": [...],        // Tên field thay đổi theo entity
  "total": 100,          // Tổng số items
  "skip": 0,             // Số items đã bỏ qua
  "limit": 20,           // Số items trả về
  "has_more": true       // Còn items để load không
}
```

### APIs với Phân Trang
✅ **Posts**: `/api/v1/posts/`, `/api/v1/posts/approved/`
✅ **Tags**: `/api/v1/tags/`
✅ **Topics**: `/api/v1/topics/`
✅ **Units**: `/api/v1/units/`
✅ **Materials**: `/api/v1/materials/`
✅ **Groups**: `/api/v1/groups/`, `/api/v1/groups/search/`
✅ **Group Members**: `/api/v1/group-members/search/`
✅ **Group Chat**: `/api/v1/group-chat/all`
✅ **Favourites**: `/api/v1/favourites/`

---

## 13. Authentication & Authorization

### Role-based Access Control
- **User**: Truy cập cơ bản, tạo/sửa content của mình
- **Moderator**: Quản lý content, groups, có quyền moderate
- **Admin**: Toàn quyền hệ thống

### Protected Endpoints
- Hầu hết endpoints yêu cầu authentication
- Một số endpoints yêu cầu role cụ thể
- Admin-only endpoints được đánh dấu rõ ràng

---

## 14. Error Handling

### Common HTTP Status Codes
- `200 OK` - Thành công
- `201 Created` - Tạo mới thành công
- `400 Bad Request` - Dữ liệu không hợp lệ
- `401 Unauthorized` - Chưa đăng nhập
- `403 Forbidden` - Không có quyền
- `404 Not Found` - Không tìm thấy
- `500 Internal Server Error` - Lỗi server

### Error Response Format
```json
{
  "detail": "Error message"
}
```

---

## 15. Testing

### Test Files
- `tests/test_pagination_apis.py` - Test phân trang
- `tests/test_all_group_chats.py` - Test group chat APIs
- `tests/test_auth.py` - Test authentication

### Running Tests
```bash
python tests/test_pagination_apis.py
```

---

## 16. Documentation

### API Guides
- `document/PAGINATION_APIS_GUIDE.md` - Hướng dẫn phân trang
- `document/ALL_GROUP_CHATS_API_GUIDE.md` - Group chat APIs
- `document/TOPIC_API_GUIDE.md` - Topic management
- `document/GROUP_CHAT_API_SUMMARY.md` - Group chat summary

---

## 17. Changelog

### Version 1.0.0 (2024-07-05)
- ✅ Thêm phân trang cho tất cả list APIs
- ✅ Chuẩn hóa response format
- ✅ Cập nhật documentation
- ✅ Thêm test cases
- ✅ Cải thiện error handling
- ✅ Thêm role-based access control 