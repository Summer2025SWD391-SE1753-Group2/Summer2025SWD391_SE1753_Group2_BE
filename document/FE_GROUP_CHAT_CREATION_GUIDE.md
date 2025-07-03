# FRONTEND GROUP CHAT CREATION GUIDE

## 1. Tổng quan Flow Tạo Group Chat

Flow tạo group chat mới gồm 4 bước chính:

1. **Chọn topic** từ danh sách active chưa có group
2. **Nhập thông tin** group chat
3. **Thêm thành viên**
4. **Xác nhận và tạo**

---

## 2. Bước 1: Chọn Topic

### UI/UX Design

```jsx
// Modal/Dialog component
const CreateGroupChatModal = () => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load available topics
  const loadAvailableTopics = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/group-chat/topics/available", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      setTopics(data);
    } catch (error) {
      console.error("Error loading topics:", error);
      // Show error message
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal">
      <h2>Tạo Group Chat</h2>

      {loading ? (
        <div>Đang tải danh sách topic...</div>
      ) : (
        <div className="topic-list">
          <h3>Chọn Topic</h3>
          {topics.map((topic) => (
            <div
              key={topic.topic_id}
              className={`topic-item ${
                selectedTopic?.topic_id === topic.topic_id ? "selected" : ""
              }`}
              onClick={() => setSelectedTopic(topic)}
            >
              <h4>{topic.topic_name}</h4>
              <span className="status">{topic.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### API Call

```javascript
// GET /api/v1/group-chat/topics/available
const getAvailableTopics = async () => {
  const response = await fetch("/api/v1/group-chat/topics/available", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to load topics");
  }

  return response.json();
};
```

---

## 3. Bước 2: Nhập Thông Tin Group

### UI/UX Design

```jsx
const GroupInfoForm = ({ selectedTopic, onNext }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = "Tên group chat là bắt buộc";
    } else if (formData.name.length > 100) {
      newErrors.name = "Tên không được quá 100 ký tự";
    }
    if (formData.description && formData.description.length > 500) {
      newErrors.description = "Mô tả không được quá 500 ký tự";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateForm()) {
      onNext(formData);
    }
  };

  return (
    <div className="group-info-form">
      <h3>Thông tin Group Chat</h3>
      <p>Topic: {selectedTopic?.topic_name}</p>

      <div className="form-group">
        <label>Tên Group Chat *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          maxLength={100}
          placeholder="Nhập tên group chat"
        />
        {errors.name && <span className="error">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label>Mô tả (tùy chọn)</label>
        <textarea
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          maxLength={500}
          placeholder="Mô tả group chat"
          rows={3}
        />
        {errors.description && (
          <span className="error">{errors.description}</span>
        )}
      </div>

      <button onClick={handleNext} disabled={!formData.name.trim()}>
        Tiếp theo
      </button>
    </div>
  );
};
```

---

## 4. Bước 3: Thêm Thành Viên

### UI/UX Design

```jsx
const AddMembersForm = ({ groupInfo, onNext }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [loading, setLoading] = useState(false);

  // Search users
  const searchUsers = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `/api/v1/accounts/search/?name=${encodeURIComponent(query)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error("Error searching users:", error);
    } finally {
      setLoading(false);
    }
  };

  const addMember = (user) => {
    if (selectedMembers.length >= 49) {
      alert("Đã đạt giới hạn 50 thành viên");
      return;
    }
    if (!selectedMembers.find((m) => m.account_id === user.account_id)) {
      setSelectedMembers([...selectedMembers, user]);
    }
  };

  const removeMember = (userId) => {
    setSelectedMembers(selectedMembers.filter((m) => m.account_id !== userId));
  };

  const handleNext = () => {
    if (selectedMembers.length < 2) {
      alert("Phải thêm ít nhất 2 thành viên");
      return;
    }
    onNext(selectedMembers);
  };

  return (
    <div className="add-members-form">
      <h3>Thêm Thành Viên</h3>
      <p>Đã chọn: {selectedMembers.length}/49 thành viên</p>

      <div className="search-section">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            searchUsers(e.target.value);
          }}
          placeholder="Tìm kiếm user..."
        />

        {loading && <div>Đang tìm kiếm...</div>}

        <div className="search-results">
          {searchResults.map((user) => (
            <div
              key={user.account_id}
              className="user-item"
              onClick={() => addMember(user)}
            >
              <img src={user.avatar} alt={user.username} />
              <div>
                <div>{user.full_name}</div>
                <div>@{user.username}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="selected-members">
        <h4>Thành viên đã chọn:</h4>
        {selectedMembers.map((member) => (
          <div key={member.account_id} className="selected-member">
            <img src={member.avatar} alt={member.username} />
            <span>{member.full_name}</span>
            <button onClick={() => removeMember(member.account_id)}>Xóa</button>
          </div>
        ))}
      </div>

      <button onClick={handleNext} disabled={selectedMembers.length < 2}>
        Tiếp theo
      </button>
    </div>
  );
};
```

---

## 5. Bước 4: Xác Nhận và Tạo

### UI/UX Design

```jsx
const ConfirmationStep = ({
  selectedTopic,
  groupInfo,
  selectedMembers,
  onCreate,
}) => {
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const response = await fetch("/api/v1/group-chat/create-transaction", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic_id: selectedTopic.topic_id,
          name: groupInfo.name,
          description: groupInfo.description,
          member_ids: selectedMembers.map((m) => m.account_id),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Tạo group chat thất bại");
      }

      const result = await response.json();
      onCreate(result);
    } catch (error) {
      console.error("Error creating group:", error);
      alert(error.message);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="confirmation-step">
      <h3>Xác nhận thông tin</h3>

      <div className="confirmation-details">
        <div>
          <strong>Topic:</strong> {selectedTopic.topic_name}
        </div>
        <div>
          <strong>Tên Group:</strong> {groupInfo.name}
        </div>
        <div>
          <strong>Mô tả:</strong> {groupInfo.description || "Không có"}
        </div>
        <div>
          <strong>Thành viên:</strong> {selectedMembers.length + 1} người
          <ul>
            <li>Bạn (Leader)</li>
            {selectedMembers.map((member) => (
              <li key={member.account_id}>{member.full_name}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="actions">
        <button onClick={handleCreate} disabled={creating}>
          {creating ? "Đang tạo..." : "Tạo Group Chat"}
        </button>
      </div>
    </div>
  );
};
```

---

## 6. Component Chính

### Main Component

```jsx
const CreateGroupChat = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [groupInfo, setGroupInfo] = useState(null);
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  const handleStep1Complete = (topic) => {
    setSelectedTopic(topic);
    setCurrentStep(2);
  };

  const handleStep2Complete = (info) => {
    setGroupInfo(info);
    setCurrentStep(3);
  };

  const handleStep3Complete = (members) => {
    setSelectedMembers(members);
    setCurrentStep(4);
  };

  const handleCreateComplete = (result) => {
    // Handle success
    alert("Tạo group chat thành công!");
    setIsOpen(false);
    // Reset state
    setCurrentStep(1);
    setSelectedTopic(null);
    setGroupInfo(null);
    setSelectedMembers([]);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Tạo Group Chat</button>

      {isOpen && (
        <Modal onClose={() => setIsOpen(false)}>
          {currentStep === 1 && (
            <TopicSelection onComplete={handleStep1Complete} />
          )}
          {currentStep === 2 && (
            <GroupInfoForm
              selectedTopic={selectedTopic}
              onNext={handleStep2Complete}
            />
          )}
          {currentStep === 3 && (
            <AddMembersForm
              groupInfo={groupInfo}
              onNext={handleStep3Complete}
            />
          )}
          {currentStep === 4 && (
            <ConfirmationStep
              selectedTopic={selectedTopic}
              groupInfo={groupInfo}
              selectedMembers={selectedMembers}
              onCreate={handleCreateComplete}
            />
          )}
        </Modal>
      )}
    </>
  );
};
```

---

## 7. Error Handling

### Common Errors

```javascript
const handleApiError = (error) => {
  switch (error.status) {
    case 400:
      if (error.detail.includes("already has a chat group")) {
        alert("Topic này đã có group chat");
      } else if (error.detail.includes("inactive topic")) {
        alert("Không thể tạo group chat cho topic không active");
      }
      break;
    case 403:
      alert("Bạn không có quyền tạo group chat");
      break;
    case 422:
      alert("Dữ liệu không hợp lệ: " + error.detail);
      break;
    default:
      alert("Có lỗi xảy ra, vui lòng thử lại");
  }
};
```

---

## 8. CSS Styling (Gợi ý)

```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.topic-item {
  padding: 10px;
  border: 1px solid #ddd;
  margin: 5px 0;
  cursor: pointer;
  border-radius: 4px;
}

.topic-item.selected {
  background: #e3f2fd;
  border-color: #2196f3;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.user-item:hover {
  background: #f5f5f5;
}

.selected-member {
  display: flex;
  align-items: center;
  padding: 5px;
  background: #e8f5e8;
  margin: 2px 0;
  border-radius: 4px;
}

.error {
  color: #f44336;
  font-size: 12px;
  margin-top: 4px;
}
```

---

## 9. Testing Checklist

- [ ] Load danh sách topic thành công
- [ ] Chọn topic hoạt động
- [ ] Validation form thông tin group
- [ ] Search user hoạt động
- [ ] Thêm/xóa thành viên
- [ ] Validation số lượng thành viên
- [ ] Tạo group chat thành công
- [ ] Error handling các trường hợp
- [ ] UI responsive trên mobile
- [ ] Loading states hiển thị đúng

---

Nếu cần hỗ trợ thêm, liên hệ backend team.
