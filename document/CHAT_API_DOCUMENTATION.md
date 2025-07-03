# Real-Time Chat API Documentation

## Overview

The real-time chat feature allows users to send messages to their friends in real-time using WebSocket connections. Only friends can message each other, ensuring privacy and security.

## Features

- ✅ Real-time messaging via WebSocket
- ✅ Friend-only messaging (security)
- ✅ Message status tracking (sent, delivered, read)
- ✅ Typing indicators
- ✅ Chat history retrieval
- ✅ Message deletion (soft delete)
- ✅ Unread message count
- ✅ Online friends tracking
- ✅ JWT authentication for WebSocket connections

## Database Models

### Message Model

```python
class Message(Base):
    __tablename__ = "message"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    content = Column(Text, nullable=False)
    status = Column(Enum(MessageStatusEnum), default=MessageStatusEnum.sent)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True), nullable=True)
```

### Message Status Enum

- `sent`: Message has been sent
- `delivered`: Message has been delivered to recipient
- `read`: Message has been read by recipient

## WebSocket API

### Connection

**Endpoint:** `ws://localhost:8000/api/v1/chat/ws/chat?token={jwt_token}`

**Authentication:** JWT token required as query parameter

**Connection Flow:**

1. Connect with valid JWT token
2. Receive connection confirmation
3. Receive list of online friends
4. Start sending/receiving messages

### Message Types

#### 1. Send Message

```json
{
  "type": "send_message",
  "receiver_id": "uuid-of-receiver",
  "content": "Message content"
}
```

#### 2. Mark Message as Read

```json
{
  "type": "mark_read",
  "message_id": "uuid-of-message"
}
```

#### 3. Typing Indicator

```json
{
  "type": "typing",
  "receiver_id": "uuid-of-receiver",
  "is_typing": true
}
```

### Received Message Types

#### 1. Connection Established

```json
{
  "type": "connection_established",
  "user_id": "uuid-of-user",
  "message": "Connected to chat server"
}
```

#### 2. Online Friends

```json
{
  "type": "online_friends",
  "friends": ["uuid1", "uuid2", "uuid3"]
}
```

#### 3. New Message

```json
{
  "type": "new_message",
  "message": {
    "message_id": "uuid",
    "sender_id": "uuid",
    "receiver_id": "uuid",
    "content": "Message content",
    "status": "delivered",
    "created_at": "2024-01-01T12:00:00Z",
    "sender": {
      "account_id": "uuid",
      "username": "sender_username",
      "full_name": "Sender Name",
      "avatar": "avatar_url"
    }
  }
}
```

#### 4. Message Sent Confirmation

```json
{
  "type": "message_sent",
  "message_id": "uuid",
  "status": "sent"
}
```

#### 5. Message Read Notification

```json
{
  "type": "message_read",
  "message_id": "uuid",
  "read_by": "uuid-of-reader"
}
```

#### 6. Typing Indicator

```json
{
  "type": "typing_indicator",
  "user_id": "uuid",
  "is_typing": true
}
```

## REST API Endpoints

### 1. Send Message

**POST** `/api/v1/chat/messages/`

**Request Body:**

```json
{
  "receiver_id": "uuid-of-receiver",
  "content": "Message content"
}
```

**Response:**

```json
{
  "message_id": "uuid",
  "sender_id": "uuid",
  "receiver_id": "uuid",
  "content": "Message content",
  "status": "sent",
  "is_deleted": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "read_at": null,
  "sender": {
    "account_id": "uuid",
    "username": "sender_username",
    "full_name": "Sender Name",
    "avatar": "avatar_url"
  },
  "receiver": {
    "account_id": "uuid",
    "username": "receiver_username",
    "full_name": "Receiver Name",
    "avatar": "avatar_url"
  }
}
```

### 2. Get Chat History

**GET** `/api/v1/chat/messages/history/{friend_id}?skip=0&limit=50`

**Query Parameters:**

- `skip`: Number of messages to skip (default: 0)
- `limit`: Number of messages to return (default: 50, max: 100)

**Response:**

```json
{
    "messages": [
        {
            "message_id": "uuid",
            "sender_id": "uuid",
            "receiver_id": "uuid",
            "content": "Message content",
            "status": "read",
            "is_deleted": false,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "read_at": "2024-01-01T12:05:00Z",
            "sender": {...},
            "receiver": {...}
        }
    ],
    "total": 150,
    "skip": 0,
    "limit": 50
}
```

### 3. Mark Message as Read

**PUT** `/api/v1/chat/messages/{message_id}/read`

**Response:** Updated message object

### 4. Delete Message

**DELETE** `/api/v1/chat/messages/{message_id}`

**Note:** Only the sender can delete their own messages

### 5. Get Unread Message Count

**GET** `/api/v1/chat/messages/unread-count`

**Response:**

```json
{
  "unread_count": 5
}
```

### 6. Get Online Friends

**GET** `/api/v1/chat/friends/online`

**Response:**

```json
{
  "online_friends": ["uuid1", "uuid2", "uuid3"]
}
```

## Security Features

1. **Friend-only messaging**: Users can only send messages to their accepted friends
2. **JWT authentication**: All WebSocket connections require valid JWT tokens
3. **Message ownership**: Only message senders can delete their messages
4. **Soft delete**: Messages are marked as deleted rather than permanently removed
5. **Input validation**: Message content is validated for length and format

## Error Handling

### WebSocket Errors

- **401 Unauthorized**: Invalid or missing JWT token
- **403 Forbidden**: User not found or inactive
- **500 Internal Server Error**: Server-side errors

### REST API Errors

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Not friends with recipient
- **404 Not Found**: User or message not found
- **422 Validation Error**: Invalid request body

## Usage Examples

### JavaScript WebSocket Client

```javascript
// Connect to WebSocket
const token = "your-jwt-token";
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/chat/ws/chat?token=${token}`
);

ws.onopen = function () {
  console.log("Connected to chat server");
};

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case "new_message":
      console.log(
        `New message from ${data.message.sender.username}: ${data.message.content}`
      );
      break;
    case "typing_indicator":
      console.log(`User ${data.user_id} is typing: ${data.is_typing}`);
      break;
    case "connection_established":
      console.log("Connection established");
      break;
  }
};

// Send a message
function sendMessage(receiverId, content) {
  ws.send(
    JSON.stringify({
      type: "send_message",
      receiver_id: receiverId,
      content: content,
    })
  );
}

// Send typing indicator
function sendTypingIndicator(receiverId, isTyping) {
  ws.send(
    JSON.stringify({
      type: "typing",
      receiver_id: receiverId,
      is_typing: isTyping,
    })
  );
}
```

### Python Client Example

```python
import asyncio
import websockets
import json

async def chat_client():
    token = "your-jwt-token"
    uri = f"ws://localhost:8000/api/v1/chat/ws/chat?token={token}"

    async with websockets.connect(uri) as websocket:
        # Send a message
        message = {
            "type": "send_message",
            "receiver_id": "friend-uuid",
            "content": "Hello from Python!"
        }
        await websocket.send(json.dumps(message))

        # Listen for responses
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data}")

asyncio.run(chat_client())
```

## Database Migration

Run the migration to create the message table:

```bash
# Copy the migration file to alembic/versions/
cp create_message_migration.py alembic/versions/

# Run the migration
alembic upgrade head
```

## Testing

Use the provided test script to test the chat functionality:

```bash
python test_chat_api.py
```

## Performance Considerations

1. **Connection pooling**: WebSocket connections are managed efficiently
2. **Database indexing**: Proper indexes on message table for fast queries
3. **Message pagination**: Chat history supports pagination for large conversations
4. **Memory management**: Inactive connections are cleaned up automatically

## Future Enhancements

1. **Message encryption**: End-to-end encryption for messages
2. **File sharing**: Support for sending images and files
3. **Group chats**: Multi-user chat rooms
4. **Message reactions**: Like, heart, etc. reactions to messages
5. **Message search**: Search functionality for chat history
6. **Push notifications**: Mobile push notifications for offline users
