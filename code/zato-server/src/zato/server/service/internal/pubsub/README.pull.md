# Zato Pub/Sub Message Retrieval API

## Overview

The Zato Pub/Sub REST API allows external clients to retrieve messages from their subscribed topics. This document explains how to pull messages from your message queues.

## Authentication

All requests require HTTP Basic Authentication using your Zato security credentials.

## Retrieve Messages

Get messages from your subscribed topics.

### Endpoint
```
POST /messages/get
```

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "max_messages": 10,
  "max_len": 1000000
}
```

#### Parameters
- `max_messages` (optional) - Maximum number of messages to retrieve (default: 1, max: 1000)
- `max_len` (optional) - Maximum total length of message data (default: 5000000 bytes)

### Response

#### Success (200 OK)
```json
{
  "is_ok": true,
  "cid": "correlation-id",
  "data": [
    {
      "data": "message content",
      "msg_id": "unique-message-id",
      "topic_name": "orders.processed",
      "pub_time_iso": "2025-01-01T12:00:00",
      "recv_time_iso": "2025-01-01T12:00:01",
      "priority": 5,
      "size": 123,
      "correl_id": "order-12345",
      "expiration": 3600,
      "mime_type": "application/json"
    }
  ]
}
```

#### Error (401 Unauthorized)
```json
{
  "is_ok": false,
  "details": "Permission denied"
}
```

#### Error (400 Bad Request)
```json
{
  "is_ok": false,
  "details": "No subscription found for user"
}
```

### Examples

#### Get Single Message
```bash
curl -X POST \
  http://localhost:17010/messages/get \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Get Multiple Messages
```bash
curl -X POST \
  http://localhost:17010/messages/get \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"max_messages": 5, "max_len": 100000}'
```

#### Get Many Messages for Batch Processing
```bash
curl -X POST \
  http://localhost:17010/messages/get \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"max_messages": 100, "max_len": 2000000}'
```

## Message Format

Retrieved messages contain:
- `data` - The actual message content (string or JSON object)
- `msg_id` - Unique message identifier
- `topic_name` - Topic the message was published to
- `pub_time_iso` - When the message was published (ISO format)
- `recv_time_iso` - When the message was received by the system (ISO format)
- `priority` - Message priority (1-9, higher is more important)
- `size` - Message size in bytes
- `correl_id` - Correlation ID for message tracking
- `expiration` - Message expiration time in seconds
- `mime_type` - Content type of the message

## Message Processing

### Acknowledgment
Messages are automatically acknowledged when retrieved. Once you pull a message, it is removed from your queue and cannot be retrieved again.

### Order
Messages are delivered in priority order (highest priority first), then by publish time (oldest first) within the same priority level.

### Filtering
You receive messages from all topics you are subscribed to. The `topic_name` field identifies which topic each message came from.

## Error Handling

Common error scenarios:
- **401 Unauthorized** - Invalid credentials
- **400 Bad Request** - No active subscriptions for your user
- **404 Not Found** - No messages available
- **500 Internal Server Error** - Server-side error

## Best Practices

1. **Regular polling** - Call the endpoint regularly to retrieve new messages
2. **Batch processing** - Use `max_messages` to retrieve multiple messages at once for efficiency
3. **Handle empty responses** - No error is returned when no messages are available
4. **Process promptly** - Retrieved messages are removed from the queue immediately
5. **Monitor message size** - Use `max_len` to control total data volume per request
6. **Check all fields** - Use `topic_name` to route messages to appropriate handlers
7. **Use correlation IDs** - Track message flows using `correl_id` fields

## Subscription Requirements

You must have active subscriptions to receive messages:
1. Subscribe to topics using the subscribe endpoint
2. Ensure your user has subscription permissions for the topics
3. Messages are only delivered to your personal queue

## Health Check

Check if the pub/sub service is running:

```
GET /health
```

Returns `200 OK` with `{"status": "ok"}` if the service is healthy.
