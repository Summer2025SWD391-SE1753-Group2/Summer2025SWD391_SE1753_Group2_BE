# Hướng Dẫn Test Tính Năng Chat 1-1 (Friend Chat) cho FE

## 1. Đăng ký & Đăng nhập tài khoản

### Đăng ký tài khoản

- **Endpoint:** `POST /api/v1/accounts/`
- **Body:**
  ```json
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "YourPassword@123",
    "full_name": "User One"
  }
  ```
- **Lưu ý:** FE nên đăng ký ít nhất 2 tài khoản để test chat 1-1.

### Đăng nhập lấy access token

- **Endpoint:** `POST /api/v1/auth/access-token`
- **Body (form-data):**

  - `username`: user1
  - `password`: YourPassword@123

- **Response:**
  ```json
  {
    "access_token": "JWT_TOKEN",
    "refresh_token": "...",
    "token_type": "bearer"
  }
  ```
- **Lưu ý:** FE cần lưu lại `access_token` để sử dụng cho các API và WebSocket.

---

## 2. Kết bạn (Friend)

### Gửi lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/request`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:**
  ```json
  {
    "receiver_id": "<UUID của user2>"
  }
  ```

### Chấp nhận lời mời kết bạn

- **Endpoint:** `POST /api/v1/friends/accept/{sender_id}`
- **Headers:** `Authorization: Bearer <access_token của user2>`

- Sau khi cả hai đã là bạn, có thể chat 1-1.

---

## 3. Kết nối WebSocket để chat real-time

### Kết nối WebSocket

- **URL:** `ws://<backend-host>:<port>/api/v1/chat/ws/chat?token=<access_token>`
  - Ví dụ: `ws://localhost:8000/api/v1/chat/ws/chat?token=JWT_TOKEN`
- **Lưu ý:** Tham số `token` là access_token lấy từ bước đăng nhập.

### Sự kiện khi kết nối thành công

- FE sẽ nhận được:
  ```json
  {
    "type": "connection_established",
    "user_id": "<your_user_id>",
    "message": "Connected to chat server"
  }
  ```
- Và danh sách bạn bè đang online:
  ```json
  {
    "type": "online_friends",
    "friends": ["<friend_id_1>", "<friend_id_2>", ...]
  }
  ```

---

## 4. Gửi & Nhận tin nhắn qua WebSocket

### Gửi tin nhắn

- **Gửi qua WebSocket:**
  ```json
  {
    "type": "send_message",
    "receiver_id": "<UUID của bạn bè>",
    "content": "Nội dung tin nhắn"
  }
  ```
- **Kết quả trả về cho người gửi:**
  ```json
  {
    "type": "message_sent",
    "message_id": "<id>",
    "status": "sent"
  }
  ```
- **Người nhận sẽ nhận được:**
  ```json
  {
    "type": "new_message",
    "message": {
      "message_id": "<id>",
      "sender_id": "<UUID>",
      "receiver_id": "<UUID>",
      "content": "Nội dung tin nhắn",
      "status": "delivered",
      "created_at": "ISO8601",
      "sender": {
        "account_id": "<UUID>",
        "username": "user1",
        "full_name": "User One",
        "avatar": null
      }
    }
  }
  ```

### Đánh dấu đã đọc tin nhắn

- **Gửi qua WebSocket:**
  ```json
  {
    "type": "mark_read",
    "message_id": "<id>"
  }
  ```
- **Người gửi sẽ nhận được:**
  ```json
  {
    "type": "message_read",
    "message_id": "<id>",
    "read_by": "<user_id>"
  }
  ```

### Gửi trạng thái đang nhập (typing)

- **Gửi qua WebSocket:**
  ```json
  {
    "type": "typing",
    "receiver_id": "<UUID của bạn bè>",
    "is_typing": true
  }
  ```
- **Người nhận sẽ nhận được:**
  ```json
  {
    "type": "typing_indicator",
    "user_id": "<user_id>",
    "is_typing": true
  }
  ```

---

## 5. Lấy lịch sử chat & các API REST hỗ trợ

### Lấy lịch sử chat với bạn bè

- **Endpoint:** `GET /api/v1/chat/messages/history/{friend_id}?skip=0&limit=50`
- **Headers:** `Authorization: Bearer <access_token>`

### Đánh dấu tin nhắn đã đọc (REST)

- **Endpoint:** `PUT /api/v1/chat/messages/{message_id}/read`
- **Headers:** `Authorization: Bearer <access_token>`

### Xóa tin nhắn (chỉ người gửi)

- **Endpoint:** `DELETE /api/v1/chat/messages/{message_id}`
- **Headers:** `Authorization: Bearer <access_token>`

### Đếm số tin nhắn chưa đọc

- **Endpoint:** `GET /api/v1/chat/messages/unread-count`
- **Headers:** `Authorization: Bearer <access_token>`

### Lấy danh sách bạn bè online

- **Endpoint:** `GET /api/v1/chat/friends/online`
- **Headers:** `Authorization: Bearer <access_token>`

---

## 6. Lưu ý khi test

- **Chỉ có thể chat với bạn bè đã được chấp nhận (friend status = accepted).**
- **WebSocket cần truyền access_token qua query param `token`.**
- **FE nên test trên 2 trình duyệt/2 tài khoản để kiểm tra realtime.**
- **Nếu mất kết nối WebSocket, FE nên tự động reconnect.**
- **Kiểm tra các trường hợp lỗi: gửi tin nhắn cho người không phải bạn, gửi tin nhắn rỗng, v.v.**

---

## 7. Ví dụ luồng test nhanh

1. Đăng ký 2 tài khoản, đăng nhập lấy access_token.
2. User1 gửi lời mời kết bạn cho User2, User2 chấp nhận.
3. Cả 2 user mở WebSocket (mỗi user 1 tab/trình duyệt).
4. User1 gửi tin nhắn cho User2, User2 nhận được realtime.
5. User2 gửi lại, User1 nhận được.
6. Test các tính năng: đánh dấu đã đọc, typing, lấy lịch sử chat, xóa tin nhắn, đếm tin chưa đọc.

---

Nếu cần ví dụ cụ thể về request/response hoặc muốn hướng dẫn bằng tiếng Anh, hãy báo lại nhé!

## 8. Lấy và hiển thị nhiều tin nhắn cũ hơn (phân trang/lazy load)

### API lấy lịch sử chat hỗ trợ phân trang

- **Endpoint:** `GET /api/v1/chat/messages/history/{friend_id}?skip=0&limit=50`
- **Headers:** `Authorization: Bearer <access_token>`
- **Giải thích:**
  - `skip`: Số lượng tin nhắn bỏ qua (dùng cho phân trang/lazy load khi scroll lên trên).
  - `limit`: Số lượng tin nhắn muốn lấy mỗi lần (ví dụ: 20, 50, 100).
- **Response mẫu:**
  ```json
  {
    "messages": [
      // ... danh sách tin nhắn (mới nhất trước)
    ],
    "total": 123,
    "skip": 0,
    "limit": 50
  }
  ```

### FE cần làm gì?

- Khi user scroll lên đầu khung chat, FE gọi lại API với `skip = số tin nhắn đã có`, `limit = số muốn lấy thêm`.
- FE nối thêm các tin nhắn cũ vào đầu danh sách hiện tại.
- Nên có scroll bar cho khung chat để user xem lại lịch sử cũ.
- Khi chuyển sang bạn bè khác, FE gọi API với `friend_id` tương ứng để lấy lịch sử chat riêng từng người.
- Mỗi bạn bè sẽ có lịch sử chat riêng biệt, không lẫn lộn.

### Gợi ý UI/UX:

- Khung chat nên có scroll bar dọc.
- Khi kéo lên trên cùng, tự động load thêm tin nhắn cũ (nếu còn).
- Hiển thị tổng số tin nhắn hoặc thông báo "Đã hết lịch sử" nếu không còn tin nhắn cũ.
- Khi chuyển bạn chat, clear khung chat cũ và load lịch sử mới theo `friend_id`.

---

## 9. Giữ nguyên đoạn chat khi reload trang (không bị nhảy ra ngoài)

### 1. Sử dụng URL động cho từng đoạn chat

- Khi user chọn bạn bè để chat, FE điều hướng tới URL dạng:
  ```
  /chat/{friend_id}
  ```
- Ví dụ:
  - Chat với bạn A: `/chat/123e4567-e89b-12d3-a456-426614174000`
  - Chat với bạn B: `/chat/987e6543-e21b-12d3-a456-426614174999`
- Khi reload, FE đọc được `friend_id` từ URL và tự động load lại đúng đoạn chat.

### 2. FE tự động load lại lịch sử chat khi reload

- Khi component chat mount (hoặc khi URL `friend_id` thay đổi):
  1. Lấy `friend_id` từ URL.
  2. Gọi API lấy lịch sử chat với friend đó.
  3. Kết nối lại WebSocket nếu cần.

**Ví dụ React:**

```jsx
import { useParams } from "react-router-dom";

function ChatScreen() {
  const { friendId } = useParams();

  useEffect(() => {
    if (friendId) {
      // Gọi API lấy lịch sử chat với friendId
      // Kết nối lại WebSocket nếu cần
    }
  }, [friendId]);
}
```

### 3. Giữ trạng thái UI khi reload

- Nếu có sidebar/danh sách bạn bè, khi reload nên tự động highlight bạn bè đang chat dựa vào `friend_id` trên URL.
- Nếu dùng Redux/Context, có thể sync lại state từ URL.

### 4. (Tùy chọn) Lưu trạng thái vào localStorage/sessionStorage

- Nếu muốn giữ thêm các trạng thái UI khác (ví dụ: vị trí scroll, draft message...), có thể lưu vào localStorage.
- Khi reload, đọc lại và khôi phục.

### 5. Tóm tắt luồng chuẩn

1. User chọn bạn bè để chat → FE điều hướng tới `/chat/{friend_id}`.
2. FE đọc URL, lấy `friend_id`, gọi API lấy lịch sử chat, kết nối WebSocket.
3. User reload trang → FE vẫn ở `/chat/{friend_id}`, tự động load lại đúng đoạn chat.
4. Chuyển bạn chat → FE đổi URL, load lại lịch sử chat mới.

### 6. Gợi ý cho BE

- Không cần thay đổi gì, chỉ cần API `/api/v1/chat/messages/history/{friend_id}` hoạt động đúng.

### 7. Gợi ý cho FE

- Nếu chưa có router động, hãy bổ sung.
- Nếu đã có, chỉ cần đảm bảo khi reload, FE đọc đúng `friend_id` từ URL và load lại chat.

---

## 10. Vấn đề mất tin nhắn khi chat nhiều và cách tối ưu

### Hiện tượng

- Khi số lượng tin nhắn nhiều, mỗi lần gửi hoặc reload, lịch sử chat với từng bạn bè bị mất/bị thiếu tin nhắn cũ.

### Nguyên nhân thường gặp

1. **FE chỉ giữ một phần tin nhắn (ví dụ: 50 tin mới nhất), khi gửi tin mới thì replace toàn bộ list, làm mất các tin cũ đã load trước đó.**
2. **Khi load thêm tin nhắn cũ (scroll lên), FE không nối (prepend) đúng vào đầu danh sách, hoặc bị ghi đè.**
3. **Khi chuyển bạn chat, state không clear đúng, hoặc không lưu riêng biệt lịch sử từng bạn.**
4. **API trả về tin nhắn không đúng thứ tự, hoặc không phân trang chuẩn (ví dụ: luôn trả về 50 tin mới nhất, không trả về các tin cũ hơn khi skip tăng lên).**

### Cách tối ưu & khắc phục

#### 1. FE phải lưu lịch sử chat riêng cho từng bạn bè

- Sử dụng object/map:
  ```js
  {
    friendId1: [msg1, msg2, ...],
    friendId2: [msgA, msgB, ...],
    ...
  }
  ```
- Khi chuyển bạn chat, chỉ hiển thị list của friendId tương ứng.

#### 2. Khi gửi tin nhắn mới

- **Không replace toàn bộ list!**
- Thêm tin nhắn mới vào cuối mảng (append), giữ nguyên các tin cũ đã load.

#### 3. Khi load thêm tin nhắn cũ (scroll lên)

- **Prepend** (nối vào đầu) các tin nhắn cũ vào mảng hiện tại, không replace.
- Đảm bảo không bị trùng tin nhắn (check message_id).

#### 4. API backend phải hỗ trợ phân trang chuẩn

- Khi gọi `/api/v1/chat/messages/history/{friend_id}?skip=0&limit=50` trả về 50 tin mới nhất.
- Khi gọi `/api/v1/chat/messages/history/{friend_id}?skip=50&limit=50` trả về 50 tin cũ hơn tiếp theo.
- FE phải nối đúng vào đầu mảng.

#### 5. Khi chuyển bạn chat

- Clear state chat hiện tại, load lại lịch sử đúng của bạn mới.

### Gợi ý code FE (React pseudo-code)

```js
// State lưu lịch sử từng bạn
const [chatHistory, setChatHistory] = useState({}); // { friendId: [msg, ...] }
const [currentFriendId, setCurrentFriendId] = useState(null);

function onSendMessage(newMsg) {
  setChatHistory((prev) => ({
    ...prev,
    [currentFriendId]: [...(prev[currentFriendId] || []), newMsg],
  }));
}

function onLoadMore(oldMsgs) {
  setChatHistory((prev) => ({
    ...prev,
    [currentFriendId]: [...oldMsgs, ...(prev[currentFriendId] || [])],
  }));
}
```

### Checklist tối ưu

- [x] FE lưu lịch sử chat riêng cho từng bạn.
- [x] Khi gửi tin mới, chỉ append vào list, không replace.
- [x] Khi load thêm tin cũ, prepend vào đầu list.
- [x] Khi chuyển bạn chat, load lại đúng lịch sử.
- [x] API backend trả về đúng phân trang, không lặp/tin trùng.

### Nếu vẫn bị mất tin nhắn

- **Kiểm tra lại API:** Đảm bảo skip/limit hoạt động đúng, không trả về trùng hoặc thiếu tin nhắn.
- **Kiểm tra lại logic FE:** Đảm bảo không replace toàn bộ list khi gửi hoặc load thêm.

---

## 11. Tìm kiếm account (search account) và phân trang

### API tìm kiếm account

- **Endpoint:** `GET /api/v1/accounts/search/`
- **Query params:**
  - `name`: Từ khóa tìm kiếm (username hoặc full name, partial match, không phân biệt hoa thường)
  - `skip`: (tùy chọn) Số lượng account bỏ qua (dùng cho phân trang/lazy load)
  - `limit`: (tùy chọn) Số lượng account trả về mỗi lần (mặc định 100, nên chọn 10-20 cho UI)
- **Yêu cầu đăng nhập:** Có (phải truyền token)
- **Response:**
  - Trả về danh sách các account dạng `AccountOut`.

**Ví dụ gọi API:**

```
GET /api/v1/accounts/search/?name=khoi&skip=0&limit=20
Authorization: Bearer <access_token>
```

- Khi user scroll hoặc bấm "Xem thêm", FE tăng `skip` lên bằng số account đã có, giữ nguyên `limit` để lấy thêm account mới.
- FE nên nối thêm vào danh sách hiện tại, không replace toàn bộ list.
- Nếu response trả về ít hơn `limit`, có thể đã hết kết quả.

## 11. Phân trang khi tìm kiếm account (search user)

### API tìm kiếm account hỗ trợ phân trang

- **Endpoint:** `GET /api/v1/accounts/search/?name={keyword}&skip={skip}&limit={limit}`
- **Tham số:**
  - `name`: Từ khóa tìm kiếm (bắt buộc)
  - `skip`: Số lượng account bỏ qua (dùng cho phân trang/lazy load, mặc định 0)
  - `limit`: Số lượng account trả về mỗi lần (ví dụ: 20, 50, 100, mặc định 100)
- **Ví dụ:**
  - Lấy 20 account đầu tiên: `/api/v1/accounts/search/?name=khoi&skip=0&limit=20`
  - Lấy 20 account tiếp theo: `/api/v1/accounts/search/?name=khoi&skip=20&limit=20`

### FE cần làm gì?

- Khi user scroll hoặc bấm "Xem thêm", FE tăng `skip` lên bằng số account đã có, giữ nguyên `limit`.
- FE nối thêm kết quả mới vào danh sách hiện tại, không replace toàn bộ.
- Nếu trả về ít hơn `limit`, có thể đã hết kết quả.

### Gợi ý UI/UX:

- Hiển thị nút "Xem thêm" hoặc tự động load thêm khi scroll tới cuối danh sách.
- Thông báo "Không còn kết quả" nếu đã hết.

---
