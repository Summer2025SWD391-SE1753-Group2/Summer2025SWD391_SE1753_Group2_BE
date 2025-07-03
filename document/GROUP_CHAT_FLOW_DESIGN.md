# Thiết kế luồng tạo Group Chat (Moderator/Admin)

## 1. Tổng quan

- Chỉ **moderator** hoặc **admin** mới có quyền tạo group chat.
- Mỗi topic chỉ được phép có **1 group chat**.
- Group chat tối đa **50 thành viên**.
- Thành viên được thêm vào group chat có thể rời khỏi group nếu muốn.
- Có thể tạo group chat từ 2 luồng:
  - Từ trang topic (nếu topic chưa có group chat và đang active)
  - Từ trang group chat (chọn topic chưa có group chat)

---

## 2. Luồng tạo group chat

### Cách 1: Tạo từ topic

- Ở trang chi tiết topic, nếu topic **active** và **chưa có group chat**:
  - Hiển thị nút **"Tạo Group Chat"**
  - Khi bấm, chuyển sang flow nhập thông tin group chat

### Cách 2: Tạo từ trang group chat

- Ở trang group chat, bấm **"+ Thêm Group Chat"**
- Hiển thị danh sách tất cả topic **active** chưa có group chat
- Chọn 1 topic, chuyển sang flow nhập thông tin group chat

---

## 3. Các bước tạo group chat (transaction)

### Bước 1: Nhập tên group chat

- Bắt buộc, tối đa 100 ký tự
- Có thể nhập mô tả (tùy chọn, tối đa 500 ký tự)

### Bước 2: Thêm thành viên

- Chọn từ danh sách user (có thể search/filter)
- **Phải thêm ít nhất 2 thành viên** (không tính moderator/admin tạo group)
- Tổng số thành viên (bao gồm người tạo) tối đa 50
- Thành viên được thêm sẽ **auto join** group chat khi tạo thành công
- Thành viên có thể tự rời khỏi group sau này

### Bước 3: Xác nhận & tạo group chat

- Kiểm tra lại thông tin (tên, mô tả, danh sách thành viên)
- Bấm **"Tạo"** để hoàn tất
- Nếu thành công, chuyển sang màn hình chat group mới

---

## 4. Quản lý group chat

### a. Quyền trong group chat

- **Leader**: Người tạo group (moderator/admin), không thể bị xóa khỏi group, không thể bị hạ quyền trừ khi là admin
- **Moderator**: Có thể nâng/hạ quyền member, xóa member (chỉ member có role thấp hơn)
- **Member**: Thành viên thường, có thể rời group bất cứ lúc nào

### b. Nâng/hạ quyền

- Chỉ **admin** hoặc **moderator** mới có thể nâng member lên moderator
- Không thể nâng ai lên leader, chỉ có 1 leader duy nhất (người tạo group)
- Không thể tự nâng quyền cho bản thân lên leader

### c. Xóa thành viên

- Chỉ xóa được member có role thấp hơn mình
- Không thể xóa leader khỏi group

### d. Xóa group chat

- Chỉ **admin** hoặc **leader** mới có quyền xóa group chat
- Khi xóa cần xác nhận (popup confirm)
- Khi xóa group, tất cả thành viên sẽ bị remove khỏi group, lịch sử chat có thể bị xóa hoặc ẩn (tùy chính sách)

---

## 5. Ràng buộc & lưu ý

- Không thể tạo group chat nếu topic **inactive** hoặc đã có group chat
- Không thể tạo group chat nếu không đủ thành viên (ít nhất 3 người: 1 leader + 2 member)
- Khi tạo group, người tạo **auto là leader** và được add vào group
- Thành viên được add vào group sẽ nhận thông báo (nếu có)
- Nếu có lỗi ở bất kỳ bước nào, transaction phải rollback (không tạo group, không add member)

---

## 6. Checklist cho FE/BE

- [ ] Luồng chọn topic hợp lệ (active, chưa có group chat)
- [ ] Form nhập tên group, mô tả, validate đủ
- [ ] Chọn đủ thành viên (>=2, tổng <=50)
- [ ] Transaction tạo group + add member phải đảm bảo toàn vẹn
- [ ] Xử lý rollback nếu lỗi
- [ ] Quản lý quyền trong group chat đúng logic
- [ ] Xóa group chat cần xác nhận

---

## 7. API gợi ý (tham khảo)

- `POST /api/v1/group-chat/create-transaction` (body gồm: topic_id, name, description, member_ids[])
- `POST /api/v1/group-chat/{group_id}/members` (thêm thành viên sau khi tạo)
- `POST /api/v1/group-chat/{group_id}/role` (nâng/hạ quyền)
- `DELETE /api/v1/group-chat/{group_id}` (xóa group chat)

---

Nếu cần bổ sung chi tiết UI/UX hoặc flow, liên hệ backend để thống nhất trước khi code!
