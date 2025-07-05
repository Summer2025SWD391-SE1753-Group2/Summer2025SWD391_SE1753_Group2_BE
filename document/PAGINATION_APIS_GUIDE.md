# API Phân Trang - Hướng Dẫn Sử Dụng

## Tổng quan

Tài liệu này mô tả các API phân trang cho các entity chính trong hệ thống: **Tags**, **Topics**, **Units**, và **Materials**.

Tất cả các API phân trang đều trả về response format chuẩn với thông tin phân trang đầy đủ.

---

## Format Response Chuẩn

Tất cả các API phân trang đều trả về response với format sau:

```json
{
  "items": [...],        // Danh sách items (tên field thay đổi theo entity)
  "total": 100,          // Tổng số items
  "skip": 0,             // Số items đã bỏ qua
  "limit": 20,           // Số items trả về
  "has_more": true       // Còn items để load không
}
```

---

## 1. Tags API

### Endpoint

```
GET /api/v1/tags/
```

### Parameters

| Parameter | Type  | Required | Default | Description                 |
| --------- | ----- | -------- | ------- | --------------------------- |
| `skip`    | `int` | ❌       | `0`     | Số tags bỏ qua              |
| `limit`   | `int` | ❌       | `100`   | Số tags trả về (tối đa 100) |

### Response

```json
{
  "tags": [
    {
      "tag_id": "uuid",
      "name": "Tên tag",
      "status": "active",
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z",
      "created_by": "uuid",
      "updated_by": "uuid"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

### Ví dụ sử dụng

```bash
# Lấy 10 tags đầu tiên
GET /api/v1/tags/?skip=0&limit=10

# Lấy 10 tags tiếp theo
GET /api/v1/tags/?skip=10&limit=10
```

---

## 2. Topics API

### Endpoint

```
GET /api/v1/topics/
```

### Parameters

| Parameter | Type  | Required | Default | Description                   |
| --------- | ----- | -------- | ------- | ----------------------------- |
| `skip`    | `int` | ❌       | `0`     | Số topics bỏ qua              |
| `limit`   | `int` | ❌       | `100`   | Số topics trả về (tối đa 100) |

### Response

```json
{
  "topics": [
    {
      "topic_id": "uuid",
      "name": "Tên topic",
      "status": "active",
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z"
    }
  ],
  "total": 30,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

### Ví dụ sử dụng

```bash
# Lấy 5 topics đầu tiên
GET /api/v1/topics/?skip=0&limit=5

# Lấy 5 topics tiếp theo
GET /api/v1/topics/?skip=5&limit=5
```

---

## 3. Units API

### Endpoint

```
GET /api/v1/units/
```

### Parameters

| Parameter | Type  | Required | Default | Description                  |
| --------- | ----- | -------- | ------- | ---------------------------- |
| `skip`    | `int` | ❌       | `0`     | Số units bỏ qua              |
| `limit`   | `int` | ❌       | `100`   | Số units trả về (tối đa 100) |

### Response

```json
{
  "units": [
    {
      "unit_id": "uuid",
      "name": "Tên unit",
      "description": "Mô tả unit",
      "status": "active",
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z",
      "created_by": "uuid",
      "updated_by": "uuid"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 20,
  "has_more": false
}
```

### Ví dụ sử dụng

```bash
# Lấy tất cả units
GET /api/v1/units/?skip=0&limit=100
```

---

## 4. Materials API

### Endpoint

```
GET /api/v1/materials/
```

### Parameters

| Parameter | Type  | Required | Default | Description                      |
| --------- | ----- | -------- | ------- | -------------------------------- |
| `skip`    | `int` | ❌       | `0`     | Số materials bỏ qua              |
| `limit`   | `int` | ❌       | `100`   | Số materials trả về (tối đa 100) |

### Response

```json
{
  "materials": [
    {
      "material_id": "uuid",
      "name": "Tên material",
      "status": "active",
      "image_url": "https://example.com/image.jpg",
      "unit_id": "uuid",
      "unit_name": "Tên unit",
      "created_at": "2024-07-05T12:00:00Z",
      "updated_at": "2024-07-05T12:00:00Z",
      "created_by": "uuid",
      "updated_by": "uuid"
    }
  ],
  "total": 200,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

### Ví dụ sử dụng

```bash
# Lấy 20 materials đầu tiên
GET /api/v1/materials/?skip=0&limit=20

# Lấy 20 materials tiếp theo
GET /api/v1/materials/?skip=20&limit=20
```

---

## 5. Các API Phân Trang Khác

### Posts API

```
GET /api/v1/posts/?skip=0&limit=10
GET /api/v1/posts/approved/?skip=0&limit=10
```

### Groups API

```
GET /api/v1/groups/?skip=0&limit=10
GET /api/v1/groups/search/?skip=0&limit=10
```

### Group Chat API

```
GET /api/v1/group-chat/all?skip=0&limit=20
```

### Favourites API

```
GET /api/v1/favourites/?skip=0&limit=10
```

---

## 6. Best Practices

### 1. Chọn Limit Phù Hợp

- **Small datasets**: `limit=10-20`
- **Medium datasets**: `limit=20-50`
- **Large datasets**: `limit=50-100`

### 2. Xử Lý Pagination ở Frontend

```javascript
// Ví dụ JavaScript
async function loadItems(page = 0, limit = 20) {
  const skip = page * limit;
  const response = await fetch(`/api/v1/items/?skip=${skip}&limit=${limit}`);
  const data = await response.json();

  return {
    items: data.items,
    hasMore: data.has_more,
    total: data.total,
  };
}
```

### 3. Error Handling

```javascript
try {
  const data = await loadItems();
  // Process data
} catch (error) {
  console.error("Failed to load items:", error);
  // Handle error appropriately
}
```

### 4. Loading States

```javascript
const [loading, setLoading] = useState(false);
const [items, setItems] = useState([]);
const [hasMore, setHasMore] = useState(true);

async function loadMore() {
  if (loading || !hasMore) return;

  setLoading(true);
  try {
    const newData = await loadItems(items.length / 20);
    setItems([...items, ...newData.items]);
    setHasMore(newData.hasMore);
  } finally {
    setLoading(false);
  }
}
```

---

## 7. Testing

Sử dụng file test để kiểm tra các API phân trang:

```bash
python tests/test_pagination_apis.py
```

File test sẽ kiểm tra:

- Pagination cho tất cả entities
- Response format đúng
- Thông tin phân trang chính xác
- Multiple pages loading

---

## 8. Lưu Ý

1. **Authentication**: Một số API yêu cầu authentication
2. **Rate Limiting**: Có thể có giới hạn số request
3. **Caching**: Nên cache kết quả để tăng performance
4. **Error Codes**: Xử lý các HTTP status codes phù hợp
5. **Validation**: Validate parameters trước khi gửi request

---

## 9. Changelog

### Version 1.0.0 (2024-07-05)

- ✅ Thêm phân trang cho Tags API
- ✅ Thêm phân trang cho Topics API
- ✅ Thêm phân trang cho Units API
- ✅ Thêm phân trang cho Materials API
- ✅ Chuẩn hóa response format
- ✅ Thêm documentation đầy đủ
- ✅ Thêm test cases
