# GROUP MEMBERS SEARCH API GUIDE

## 1. Tổng quan

Hướng dẫn sử dụng API để liệt kê và tìm kiếm thành viên trong group chat với tính năng search và phân trang.

---

## 2. API Endpoints

### 2.1 Lấy tất cả thành viên (không search)

```
GET /api/v1/group-chat/{group_id}/members
```

**Quyền**: Thành viên của group
**Response**: List[GroupMemberOut]

```json
[
  {
    "group_member_id": "uuid",
    "account_id": "uuid",
    "group_id": "uuid",
    "role": "leader",
    "joined_at": "2024-07-05T12:00:00Z",
    "username": "john_doe",
    "full_name": "John Doe",
    "avatar": "https://example.com/avatar.jpg",
    "email": "john@example.com"
  }
]
```

### 2.2 Lấy thành viên với search và phân trang

```
GET /api/v1/group-chat/{group_id}/members/search?skip=0&limit=20&search=john
```

**Quyền**: Thành viên của group
**Parameters**:

- `skip` (int, optional): Số thành viên bỏ qua (default: 0)
- `limit` (int, optional): Số thành viên trả về (default: 20, max: 100)
- `search` (string, optional): Từ khóa tìm kiếm (username, full_name, email)

**Response**: GroupMembersSearchOut

```json
{
  "members": [
    {
      "group_member_id": "uuid",
      "account_id": "uuid",
      "group_id": "uuid",
      "role": "leader",
      "joined_at": "2024-07-05T12:00:00Z",
      "username": "john_doe",
      "full_name": "John Doe",
      "avatar": "https://example.com/avatar.jpg",
      "email": "john@example.com"
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

---

## 3. Tính năng Search

### 3.1 Cách search hoạt động

- **Search fields**: username, full_name, email
- **Search type**: Case-insensitive partial match (LIKE %term%)
- **Ví dụ**: search="john" sẽ tìm được:
  - username: "john_doe"
  - full_name: "John Doe"
  - email: "john@example.com"

### 3.2 Search examples

```javascript
// Tìm theo username
GET /api/v1/group-chat/{group_id}/members/search?search=john

// Tìm theo tên
GET /api/v1/group-chat/{group_id}/members/search?search=doe

// Tìm theo email
GET /api/v1/group-chat/{group_id}/members/search?search=@gmail

// Kết hợp với phân trang
GET /api/v1/group-chat/{group_id}/members/search?search=john&skip=20&limit=10
```

---

## 4. Frontend Implementation

### 4.1 Component chính

```jsx
const GroupMembersList = ({ groupId }) => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0,
    hasMore: false,
  });

  const loadMembers = async (search = "", skip = 0) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: pagination.limit.toString(),
      });

      if (search.trim()) {
        params.append("search", search.trim());
      }

      const response = await fetch(
        `/api/v1/group-chat/${groupId}/members/search?${params}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const data = await response.json();

      if (skip === 0) {
        setMembers(data.members);
      } else {
        setMembers((prev) => [...prev, ...data.members]);
      }

      setPagination({
        skip: data.skip,
        limit: data.limit,
        total: data.total,
        hasMore: data.has_more,
      });
    } catch (error) {
      console.error("Error loading members:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
    setPagination((prev) => ({ ...prev, skip: 0 }));
    loadMembers(term, 0);
  };

  const loadMore = () => {
    if (pagination.hasMore && !loading) {
      loadMembers(searchTerm, pagination.skip + pagination.limit);
    }
  };

  useEffect(() => {
    loadMembers();
  }, [groupId]);

  return (
    <div className="group-members-list">
      <div className="search-section">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Tìm kiếm thành viên..."
          className="search-input"
        />
      </div>

      <div className="members-count">{pagination.total} thành viên</div>

      <div className="members-list">
        {members.map((member) => (
          <MemberCard key={member.group_member_id} member={member} />
        ))}
      </div>

      {loading && <div className="loading">Đang tải...</div>}

      {pagination.hasMore && (
        <button onClick={loadMore} disabled={loading} className="load-more-btn">
          {loading ? "Đang tải..." : "Tải thêm"}
        </button>
      )}
    </div>
  );
};
```

### 4.2 Member Card Component

```jsx
const MemberCard = ({ member }) => {
  const getRoleBadge = (role) => {
    const roleConfig = {
      leader: { label: "Leader", color: "gold" },
      moderator: { label: "Moderator", color: "blue" },
      member: { label: "Member", color: "gray" },
    };

    const config = roleConfig[role] || roleConfig.member;

    return (
      <span className="role-badge" style={{ backgroundColor: config.color }}>
        {config.label}
      </span>
    );
  };

  return (
    <div className="member-card">
      <div className="member-avatar">
        <img
          src={member.avatar || "/default-avatar.png"}
          alt={member.full_name}
        />
      </div>

      <div className="member-info">
        <div className="member-name">{member.full_name}</div>
        <div className="member-username">@{member.username}</div>
        <div className="member-email">{member.email}</div>
      </div>

      <div className="member-role">{getRoleBadge(member.role)}</div>

      <div className="member-joined">
        Tham gia: {new Date(member.joined_at).toLocaleDateString("vi-VN")}
      </div>
    </div>
  );
};
```

### 4.3 Debounced Search

```jsx
import { useDebounce } from "use-debounce";

const GroupMembersList = ({ groupId }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearchTerm] = useDebounce(searchTerm, 300);

  useEffect(() => {
    handleSearch(debouncedSearchTerm);
  }, [debouncedSearchTerm]);

  const handleSearchInput = (value) => {
    setSearchTerm(value);
  };

  return (
    <div className="group-members-list">
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => handleSearchInput(e.target.value)}
        placeholder="Tìm kiếm thành viên..."
      />
      {/* Rest of component */}
    </div>
  );
};
```

---

## 5. UI/UX Best Practices

### 5.1 Search Experience

- **Debounce**: Delay search 300-500ms sau khi user ngừng gõ
- **Loading state**: Hiển thị loading khi đang search
- **Empty state**: Hiển thị thông báo khi không tìm thấy kết quả
- **Search suggestions**: Gợi ý từ khóa tìm kiếm

### 5.2 Pagination Experience

- **Infinite scroll**: Tự động load thêm khi scroll xuống cuối
- **Load more button**: Nút "Tải thêm" cho mobile
- **Loading indicator**: Hiển thị khi đang load thêm
- **End of list**: Thông báo khi đã hết dữ liệu

### 5.3 Member Display

- **Avatar**: Hiển thị avatar với fallback
- **Role badges**: Màu sắc khác nhau cho từng role
- **Join date**: Hiển thị ngày tham gia
- **Contact info**: Email (có thể ẩn/hiện)

---

## 6. CSS Styling

```css
.group-members-list {
  max-width: 800px;
  margin: 0 auto;
}

.search-section {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.members-count {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.member-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  background: white;
  transition: box-shadow 0.2s;
}

.member-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.member-avatar {
  margin-right: 16px;
}

.member-avatar img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.member-username {
  color: #666;
  font-size: 14px;
  margin-bottom: 2px;
}

.member-email {
  color: #999;
  font-size: 12px;
}

.member-role {
  margin-left: 16px;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.load-more-btn {
  width: 100%;
  padding: 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 16px;
}

.load-more-btn:hover {
  background: #e0e0e0;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-state img {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}
```

---

## 7. Error Handling

### 7.1 Common Errors

```javascript
const handleApiError = (error) => {
  switch (error.status) {
    case 403:
      alert("Bạn không có quyền xem danh sách thành viên");
      break;
    case 404:
      alert("Group chat không tồn tại");
      break;
    case 422:
      alert("Tham số không hợp lệ");
      break;
    default:
      alert("Có lỗi xảy ra, vui lòng thử lại");
  }
};
```

### 7.2 Empty State

```jsx
const EmptyState = ({ searchTerm }) => {
  if (searchTerm) {
    return (
      <div className="empty-state">
        <img src="/no-results.svg" alt="No results" />
        <h3>Không tìm thấy thành viên</h3>
        <p>Thử tìm kiếm với từ khóa khác</p>
      </div>
    );
  }

  return (
    <div className="empty-state">
      <img src="/empty-group.svg" alt="Empty group" />
      <h3>Chưa có thành viên</h3>
      <p>Group chat này chưa có thành viên nào</p>
    </div>
  );
};
```

---

## 8. Performance Tips

### 8.1 Optimization

- **Debounce search**: Tránh gọi API quá nhiều
- **Virtual scrolling**: Cho danh sách dài (>1000 items)
- **Caching**: Cache kết quả search
- **Lazy loading**: Load avatar khi cần

### 8.2 Mobile Optimization

- **Touch-friendly**: Button size >= 44px
- **Swipe actions**: Swipe để thực hiện actions
- **Pull to refresh**: Refresh danh sách
- **Offline support**: Cache data offline

---

## 9. Testing Checklist

- [ ] Load danh sách thành viên thành công
- [ ] Search hoạt động với username, full_name, email
- [ ] Pagination hoạt động đúng
- [ ] Loading states hiển thị
- [ ] Error handling các trường hợp
- [ ] Empty state khi không có kết quả
- [ ] Mobile responsive
- [ ] Performance với danh sách dài
- [ ] Accessibility (keyboard navigation, screen reader)

---

Nếu cần hỗ trợ thêm, liên hệ backend team.
