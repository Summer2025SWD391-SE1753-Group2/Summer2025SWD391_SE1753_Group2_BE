# Feedback API Documentation

## Overview

Hệ thống Feedback cho phép user tạo feedback/report và admin/moderator xem và phản hồi.

## Role-based Access Control

### User Role

- ✅ **Create feedback** - Tạo feedback mới
- ✅ **View own feedbacks** - Xem feedback của mình
- ❌ **View all feedbacks** - Không thể xem feedback của người khác
- ❌ **Resolve feedback** - Không thể phản hồi feedback

### Moderator/Admin Role

- ❌ **Create feedback** - Không thể tạo feedback
- ✅ **View all feedbacks** - Xem tất cả feedback
- ✅ **Resolve feedback** - Phản hồi và giải quyết feedback
- ✅ **View statistics** - Xem thống kê feedback

## API Endpoints

### 1. Create Feedback (User Only)

```http
POST /api/v1/feedback/
```

**Request Body:**

```json
{
  "title": "Bug Report Title",
  "description": "Detailed description of the issue",
  "feedback_type": "bug_report",
  "priority": "medium",
  "screenshot_url": "https://example.com/screenshot.png",
  "browser_info": "Chrome 120.0.0.0",
  "device_info": "Windows 10"
}
```

**Response (201):**

```json
{
  "feedback_id": "uuid",
  "title": "Bug Report Title",
  "description": "Detailed description of the issue",
  "feedback_type": "bug_report",
  "priority": "medium",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "creator": {
    "account_id": "uuid",
    "username": "user123",
    "full_name": "User Name",
    "avatar": "https://example.com/avatar.jpg"
  }
}
```

### 2. Get My Feedbacks (User Only)

```http
GET /api/v1/feedback/my-feedbacks/?skip=0&limit=10
```

**Response (200):**

```json
{
  "feedbacks": [
    {
      "feedback_id": "uuid",
      "title": "Bug Report Title",
      "description": "Description",
      "feedback_type": "bug_report",
      "priority": "medium",
      "status": "pending",
      "created_at": "2024-01-01T00:00:00Z",
      "creator": {...}
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### 3. Get My Specific Feedback (User Only)

```http
GET /api/v1/feedback/my-feedbacks/{feedback_id}
```

### 4. Get All Feedbacks (Moderator/Admin Only)

```http
GET /api/v1/feedback/all/?skip=0&limit=10&status_filter=pending&type_filter=bug_report&priority_filter=high
```

**Query Parameters:**

- `skip`: Number of feedbacks to skip (pagination)
- `limit`: Number of feedbacks to return (max 100)
- `status_filter`: Filter by status (pending, in_progress, resolved, rejected)
- `type_filter`: Filter by type (bug_report, feature_request, content_report, user_report, general_feedback, other)
- `priority_filter`: Filter by priority (low, medium, high, urgent)

### 5. Get Specific Feedback (Moderator/Admin Only)

```http
GET /api/v1/feedback/all/{feedback_id}
```

### 6. Resolve Feedback (Moderator/Admin Only)

```http
PUT /api/v1/feedback/all/{feedback_id}/resolve
```

**Request Body:**

```json
{
  "status": "resolved",
  "resolution_note": "This issue has been fixed in version 2.0"
}
```

**Response (200):**

```json
{
  "feedback_id": "uuid",
  "title": "Bug Report Title",
  "description": "Description",
  "feedback_type": "bug_report",
  "priority": "medium",
  "status": "resolved",
  "resolution_note": "This issue has been fixed in version 2.0",
  "resolved_at": "2024-01-01T00:00:00Z",
  "resolver": {
    "account_id": "uuid",
    "username": "admin123",
    "full_name": "Admin Name"
  }
}
```

### 7. Delete Feedback (Admin Only)

```http
DELETE /api/v1/feedback/all/{feedback_id}
```

### 8. Get Feedback Statistics (Moderator/Admin Only)

```http
GET /api/v1/feedback/stats/
```

**Response (200):**

```json
{
  "total": 50,
  "pending": 15,
  "in_progress": 10,
  "resolved": 20,
  "rejected": 5,
  "by_type": {
    "bug_report": 20,
    "feature_request": 15,
    "content_report": 10,
    "user_report": 3,
    "general_feedback": 2
  },
  "by_priority": {
    "low": 10,
    "medium": 25,
    "high": 12,
    "urgent": 3
  }
}
```

## Feedback Types

| Type               | Description                    |
| ------------------ | ------------------------------ |
| `bug_report`       | Báo cáo lỗi/bug                |
| `feature_request`  | Yêu cầu tính năng mới          |
| `content_report`   | Báo cáo nội dung không phù hợp |
| `user_report`      | Báo cáo user vi phạm           |
| `general_feedback` | Feedback chung                 |
| `other`            | Khác                           |

## Feedback Status

| Status        | Description   |
| ------------- | ------------- |
| `pending`     | Chờ xử lý     |
| `in_progress` | Đang xử lý    |
| `resolved`    | Đã giải quyết |
| `rejected`    | Từ chối       |

## Feedback Priority

| Priority | Description |
| -------- | ----------- |
| `low`    | Thấp        |
| `medium` | Trung bình  |
| `high`   | Cao         |
| `urgent` | Khẩn cấp    |

## Error Responses

### 403 Forbidden

```json
{
  "detail": "Permission denied for this action"
}
```

### 404 Not Found

```json
{
  "detail": "Feedback not found"
}
```

### 400 Bad Request

```json
{
  "detail": "Only pending feedbacks can be updated"
}
```

## Frontend Integration Examples

### Create Feedback (React/TypeScript)

```typescript
const createFeedback = async (feedbackData: FeedbackCreate) => {
  const response = await fetch("/api/v1/feedback/", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(feedbackData),
  });

  if (response.ok) {
    const feedback = await response.json();
    console.log("Feedback created:", feedback);
  }
};
```

### Get User Feedbacks (React/TypeScript)

```typescript
const getUserFeedbacks = async (skip = 0, limit = 10) => {
  const response = await fetch(
    `/api/v1/feedback/my-feedbacks/?skip=${skip}&limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.ok) {
    const data = await response.json();
    return data.feedbacks;
  }
};
```

### Resolve Feedback (Admin/Moderator)

```typescript
const resolveFeedback = async (
  feedbackId: string,
  resolution: FeedbackResolution
) => {
  const response = await fetch(`/api/v1/feedback/all/${feedbackId}/resolve`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(resolution),
  });

  if (response.ok) {
    const feedback = await response.json();
    console.log("Feedback resolved:", feedback);
  }
};
```
