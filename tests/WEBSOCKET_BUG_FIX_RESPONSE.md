# 🐛 WebSocket Group Chat Bug Fix Response

## 📋 Vấn đề đã được xác định và sửa

### 1. **Vấn đề chính: Logic join group bị conflict**

**Nguyên nhân:**

- WebSocket endpoint gọi `join_group()` trước khi `update_user_groups_in_manager()`
- Function `update_user_groups_in_manager()` xóa user khỏi tất cả groups cũ trước khi thêm vào groups mới
- Điều này gây ra việc user bị remove khỏi group hiện tại

**Đã sửa:**

```python
# Trước (có lỗi):
await manager.connect(websocket, current_user.account_id)
manager.join_group(current_user.account_id, group_id)  # ❌ Join trước
update_user_groups_in_manager(db, current_user.account_id)  # ❌ Sau đó xóa hết

# Sau (đã sửa):
await manager.connect(websocket, current_user.account_id)
update_user_groups_in_manager(db, current_user.account_id)  # ✅ Update trước
if not manager.is_group_member(current_user.account_id, group_id):
    manager.join_group(current_user.account_id, group_id)  # ✅ Join nếu chưa có
```

### 2. **Vấn đề: Function update_user_groups_in_manager xóa user khỏi groups**

**Đã sửa:**

```python
# Trước (có lỗi):
manager.update_user_groups(user_id, group_ids)  # ❌ Xóa hết groups cũ

# Sau (đã sửa):
for group_id in group_ids:
    if not manager.is_group_member(user_id, group_id):
        manager.join_group(user_id, group_id)  # ✅ Chỉ thêm, không xóa
```

### 3. **Thêm logging để debug**

**Đã thêm:**

```python
# Log khi user connect
logger.info(f"User {current_user.account_id} connected to group {group_id}. Online members: {online_members}")

# Log khi broadcast message
logger.info(f"Broadcasting message to group {group_id} from user {sender_id}")
```

## 🔧 Files đã được sửa

1. **`app/apis/v1/endpoints/group_chat.py`**

   - Sửa logic join group
   - Thêm logging
   - Cải thiện error handling

2. **`app/services/group_chat_service.py`**

   - Sửa function `update_user_groups_in_manager()`
   - Không xóa user khỏi groups hiện tại

3. **`app/core/websocket_manager.py`**
   - Đã có sẵn, không cần sửa
   - Hỗ trợ đầy đủ group connections

## 🧪 Testing Scripts đã tạo

### 1. **Diagnosis Script**

```bash
python fix_websocket_issues.py
```

- Kiểm tra server status
- Test login
- Test group membership
- Test WebSocket connection

### 2. **Simple Test Script**

```bash
python test_websocket_simple.py
```

- Test với credentials thực tế
- Test multiple users
- Test message sending/receiving

### 3. **Create Test Data**

```bash
python create_test_data.py
```

- Tạo test users
- Tạo test group
- Setup test environment

## 🔍 Cách kiểm tra BE logs

### 1. **Start server với debug logging:**

```bash
uvicorn app.main:app --reload --log-level debug
```

### 2. **Watch logs khi FE connect:**

```
INFO: User {user_id} connected to WebSocket
INFO: User {user_id} joined group {group_id}
INFO: Updated groups for user {user_id}: [group_ids]
INFO: User {user_id} connected to group {group_id}. Online members: [member_ids]
```

### 3. **Watch logs khi gửi message:**

```
INFO: Broadcasting message to group {group_id} from user {sender_id}
INFO: Broadcasted message to group {group_id} to {count} members
```

## 🚀 Cách test với FE

### 1. **Restart BE server:**

```bash
# Stop server hiện tại
# Start lại với debug logging
uvicorn app.main:app --reload --log-level debug
```

### 2. **Test WebSocket connection:**

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/group-chat/ws/group/${groupId}?token=${token}`
);

ws.onopen = () => {
  console.log("Connected to group chat");
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log("Received:", msg);

  if (msg.type === "connection_established") {
    console.log("✅ Connection established");
  } else if (msg.type === "online_members") {
    console.log("👥 Online members:", msg.members.length);
  } else if (msg.type === "group_message") {
    console.log("💬 New message:", msg.data.content);
  }
};
```

### 3. **Test gửi message:**

```javascript
ws.send(
  JSON.stringify({
    type: "send_message",
    content: "Test message",
  })
);
```

## 📊 Expected Behavior sau khi sửa

### 1. **Khi user connect:**

- ✅ Nhận được `connection_established`
- ✅ Nhận được `online_members` với đúng số lượng
- ✅ User được thêm vào group connections

### 2. **Khi gửi message:**

- ✅ Message được lưu vào DB
- ✅ Tất cả thành viên online nhận được `group_message`
- ✅ Sender nhận được `message_sent` confirmation

### 3. **Khi user disconnect:**

- ✅ User được remove khỏi group connections
- ✅ Online members count được update

## 🔒 Security Features

- ✅ JWT authentication required
- ✅ Member-only access (4003 error cho non-members)
- ✅ Message validation
- ✅ Auto-disconnect khi bị xóa khỏi group

## 📝 Next Steps

1. **FE Team:**

   - Restart BE server
   - Test lại WebSocket connection
   - Kiểm tra logs BE
   - Report kết quả

2. **BE Team:**
   - Monitor logs khi FE test
   - Verify fixes hoạt động
   - Deploy to production nếu cần

## 🆘 Nếu vẫn có vấn đề

### 1. **Check BE logs:**

```bash
# Look for these log messages:
grep "User.*connected to group" logs
grep "Broadcasting message" logs
grep "Online members" logs
```

### 2. **Test với diagnosis script:**

```bash
python fix_websocket_issues.py
```

### 3. **Verify group membership:**

```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/group-chat/{group_id}/members
```

---

## 🎯 Kết luận

**Các vấn đề chính đã được sửa:**

1. ✅ Logic join group conflict
2. ✅ Function update_user_groups_in_manager
3. ✅ Thêm comprehensive logging
4. ✅ Cải thiện error handling

**WebSocket Group Chat giờ đây sẽ hoạt động đúng như Chat 1-1!**

**Hãy test lại và report kết quả cho BE team.**
