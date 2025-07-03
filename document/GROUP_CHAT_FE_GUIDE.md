# Group Chat Frontend Guide

## 1. Tổng quan

Group chat cho phép moderator và admin tạo group chat từ topic, với các ràng buộc:

- **1 topic chỉ có 1 group chat** trên toàn bộ hệ thống
- **Chỉ moderator và admin** có thể tạo group chat
- **Tối đa 50 thành viên** mỗi group
- **Creator tự động trở thành leader**

## 2. Luồng tạo Group Chat

### Bước 1: Lấy danh sách topic có thể tạo group

```javascript
// Chỉ moderator/admin mới có quyền
const getAvailableTopics = async () => {
  try {
    const response = await axios.get("/api/v1/group-chat/topics/available", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 403) {
      // User không có quyền
      showError("Bạn không có quyền tạo group chat");
    }
    throw error;
  }
};
```

### Bước 2: Kiểm tra topic trước khi tạo

```javascript
const checkTopicAvailability = async (topicId) => {
  try {
    const response = await axios.get(
      `/api/v1/group-chat/topics/${topicId}/check`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      showError("Topic không tồn tại");
    } else if (error.response?.status === 403) {
      showError("Bạn không có quyền kiểm tra topic");
    }
    throw error;
  }
};
```

### Bước 3: Tạo group chat

```javascript
const createGroupChat = async (groupData) => {
  try {
    const response = await axios.post("/api/v1/group-chat/create", groupData, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    handleCreateGroupError(error);
    throw error;
  }
};
```

## 3. Xử lý lỗi chi tiết

### Lỗi 422 - Unprocessable Content

**Nguyên nhân:** Dữ liệu gửi lên không đúng format hoặc thiếu field bắt buộc.

**Cách xử lý:**

```javascript
const handleCreateGroupError = (error) => {
  if (error.response?.status === 422) {
    const validationErrors = error.response.data.detail;

    // Hiển thị lỗi validation
    if (Array.isArray(validationErrors)) {
      validationErrors.forEach((err) => {
        const field = err.loc[err.loc.length - 1];
        const message = err.msg;

        switch (field) {
          case "topic_id":
            showFieldError("topic_id", "Topic ID không hợp lệ");
            break;
          case "name":
            showFieldError("name", "Tên group không được để trống");
            break;
          case "max_members":
            showFieldError("max_members", "Số thành viên tối đa phải từ 1-50");
            break;
          default:
            showError(`Lỗi: ${message}`);
        }
      });
    } else {
      showError("Dữ liệu không hợp lệ");
    }
  }
};
```

### Lỗi 400 - Bad Request

**Nguyên nhân:** Topic đã có group chat hoặc group đã đầy.

**Cách xử lý:**

```javascript
const handleCreateGroupError = (error) => {
  if (error.response?.status === 400) {
    const message = error.response.data.detail;

    if (message === "Topic already has a chat group") {
      showError("Topic này đã có group chat. Vui lòng chọn topic khác.");
      // Có thể redirect đến group hiện tại
      redirectToExistingGroup();
    } else if (message === "Group is full") {
      showError("Group đã đầy thành viên");
    } else if (message === "Member already exists in group") {
      showError("Thành viên đã có trong group");
    } else {
      showError(message);
    }
  }
};
```

### Lỗi 403 - Forbidden

**Nguyên nhân:** User không có quyền (không phải moderator/admin).

**Cách xử lý:**

```javascript
const handleCreateGroupError = (error) => {
  if (error.response?.status === 403) {
    showError("Chỉ moderator và admin mới có thể tạo group chat");
    // Ẩn nút tạo group
    hideCreateGroupButton();
  }
};
```

### Lỗi 404 - Not Found

**Nguyên nhân:** Topic không tồn tại.

**Cách xử lý:**

```javascript
const handleCreateGroupError = (error) => {
  if (error.response?.status === 404) {
    showError("Topic không tồn tại");
    // Refresh danh sách topic
    refreshTopicList();
  }
};
```

## 4. Form validation

### Validation phía frontend

```javascript
const validateGroupForm = (formData) => {
  const errors = {};

  // Kiểm tra topic_id
  if (!formData.topic_id) {
    errors.topic_id = "Vui lòng chọn topic";
  }

  // Kiểm tra name
  if (!formData.name || formData.name.trim().length === 0) {
    errors.name = "Tên group không được để trống";
  } else if (formData.name.length > 100) {
    errors.name = "Tên group không được quá 100 ký tự";
  }

  // Kiểm tra description
  if (formData.description && formData.description.length > 500) {
    errors.description = "Mô tả không được quá 500 ký tự";
  }

  // Kiểm tra max_members
  if (
    !formData.max_members ||
    formData.max_members < 1 ||
    formData.max_members > 50
  ) {
    errors.max_members = "Số thành viên tối đa phải từ 1-50";
  }

  return errors;
};
```

### Form data structure

```javascript
const groupData = {
  topic_id: "uuid-string", // Bắt buộc
  name: "Tên group", // Bắt buộc, max 100 chars
  description: "Mô tả group", // Tùy chọn, max 500 chars
  max_members: 50, // Bắt buộc, 1-50
};
```

## 5. UI/UX Best Practices

### Loading states

```javascript
const [isLoading, setIsLoading] = useState(false);
const [isCheckingTopic, setIsCheckingTopic] = useState(false);

const handleCreateGroup = async (formData) => {
  setIsLoading(true);
  try {
    // Kiểm tra topic trước
    setIsCheckingTopic(true);
    const topicCheck = await checkTopicAvailability(formData.topic_id);

    if (!topicCheck.can_create) {
      showError(topicCheck.reason);
      return;
    }

    // Tạo group
    const group = await createGroupChat(formData);
    showSuccess("Tạo group thành công!");
    navigateToGroup(group.group_id);
  } catch (error) {
    handleCreateGroupError(error);
  } finally {
    setIsLoading(false);
    setIsCheckingTopic(false);
  }
};
```

### Error handling components

```javascript
const ErrorMessage = ({ error, onRetry }) => {
  if (!error) return null;

  return (
    <div className="error-message">
      <p>{error}</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-btn">
          Thử lại
        </button>
      )}
    </div>
  );
};

const FieldError = ({ field, error }) => {
  if (!error) return null;

  return (
    <div className="field-error">
      <span className="error-text">{error}</span>
    </div>
  );
};
```

### Success feedback

```javascript
const showSuccess = (message) => {
  // Hiển thị toast notification
  toast.success(message, {
    position: "top-right",
    autoClose: 3000,
  });
};

const showError = (message) => {
  toast.error(message, {
    position: "top-right",
    autoClose: 5000,
  });
};
```

## 6. Debug Checklist

Khi gặp lỗi 422, kiểm tra:

- [ ] **Topic ID** có đúng format UUID không?
- [ ] **Name** có được điền và không quá 100 ký tự không?
- [ ] **Max members** có từ 1-50 không?
- [ ] **Description** có quá 500 ký tự không?
- [ ] **Token** có hợp lệ và user có quyền moderator/admin không?
- [ ] **Topic** có tồn tại và chưa có group chat không?

## 7. Test Cases

### Test tạo group thành công

```javascript
const testCreateGroupSuccess = async () => {
  const groupData = {
    topic_id: "valid-topic-uuid",
    name: "Test Group",
    description: "Test description",
    max_members: 50,
  };

  const result = await createGroupChat(groupData);
  console.log("Group created:", result);
};
```

### Test lỗi validation

```javascript
const testValidationErrors = async () => {
  const invalidData = {
    topic_id: "", // Thiếu topic_id
    name: "", // Thiếu name
    max_members: 100, // Quá giới hạn
  };

  try {
    await createGroupChat(invalidData);
  } catch (error) {
    console.log("Validation errors:", error.response.data);
  }
};
```

## 8. Common Issues & Solutions

### Issue: "Topic already has a chat group"

**Solution:**

- Gọi API `GET /group-chat/topics/with-groups` để lấy danh sách topic đã có group
- Hiển thị thông báo và link đến group hiện tại

### Issue: "Only moderators and admins can create chat groups"

**Solution:**

- Kiểm tra role của user trước khi hiển thị nút tạo group
- Ẩn/hiện UI dựa trên quyền

### Issue: "Group is full"

**Solution:**

- Kiểm tra số lượng thành viên hiện tại trước khi thêm
- Hiển thị thông báo và disable nút thêm thành viên

## 9. API Response Examples

### Success Response

```json
{
  "group_id": "uuid",
  "name": "Test Group",
  "description": "Test description",
  "topic_id": "topic-uuid",
  "topic_name": "Test Topic",
  "group_leader": "leader-uuid",
  "leader_name": "Leader Name",
  "member_count": 1,
  "max_members": 50,
  "is_chat_group": true,
  "created_at": "2024-07-05T12:00:00Z"
}
```

### Error Response (422)

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "max_members"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### Error Response (400)

```json
{
  "detail": "Topic already has a chat group"
}
```

## 10. Lấy tất cả topic và group chat (nếu có)

### Khi nào nên dùng?

- Khi FE muốn hiển thị tất cả topic và biết topic nào đã có group chat, topic nào chưa có group chat.
- Dùng cho màn hình tổng quan, chọn topic để tạo group chat hoặc join group chat.

### Endpoint

```
GET /api/v1/group-chat/topics/with-or-without-group
```

### Response mẫu

```json
[
  {
    "topic_id": "uuid-topic-1",
    "topic_name": "Cooking",
    "status": "active",
    "group_chat": {
      "group_id": "uuid-group-1",
      "group_name": "Cooking Group",
      "group_description": "All about cooking",
      "member_count": 12,
      "max_members": 50,
      "created_at": "2024-06-01T12:00:00Z"
    }
  },
  {
    "topic_id": "uuid-topic-2",
    "topic_name": "Travel",
    "status": "active",
    "group_chat": null
  }
]
```

- Nếu topic chưa có group chat, trường `group_chat` sẽ là `null`.
- Nếu đã có group chat, trả về đầy đủ thông tin group.

### Gợi ý sử dụng

- FE có thể dùng API này để:
  - Hiển thị tất cả topic và biết topic nào đã có group chat, topic nào chưa.
  - Cho phép tạo group chat mới với các topic chưa có group chat.
  - Hiển thị thông tin group chat cho các topic đã có.
