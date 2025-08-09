# Zato Pub/Sub Subscription API

## Overview

The Zato Pub/Sub REST API allows external clients to subscribe to topics and receive messages. This document explains how to use the subscription endpoints.

## Authentication

All requests require HTTP Basic Authentication using your Zato security credentials.

## Subscribe to a Topic

Subscribe to receive messages from a specific topic.

### Endpoint
```
POST /topic/{topic_name}/subscribe
```

### Parameters
- `topic_name` - The name of the topic to subscribe to

### Request Headers
```
Content-Type: application/json

```

### Request Body
No request body required.

### Response

#### Success (200 OK)
```json
{
  "is_ok": true,
  "cid": "correlation-id"
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
  "details": "Error message"
}
```

### Example

```bash
curl -X POST \
  http://localhost:17010/topic/orders.processed/subscribe \
  -u username:password \
  -H "Content-Type: application/json"
```

## Unsubscribe from a Topic

Remove subscription from a specific topic.

### Endpoint
```
POST /topic/{topic_name}/unsubscribe
```

### Parameters
- `topic_name` - The name of the topic to unsubscribe from

### Request Headers
```
Content-Type: application/json

```

### Request Body
No request body required.

### Response

#### Success (200 OK)
```json
{
  "is_ok": true,
  "cid": "correlation-id"
}
```

### Example

```bash
curl -X POST \
  http://localhost:17010/topic/orders.processed/unsubscribe \
  -u username:password \
  -H "Content-Type: application/json"
```

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
      "priority": 5,
      "size": 123
    }
  ]
}
```

#### Error Response
```json
{
  "is_ok": false,
  "details": "Error message"
}
```

### Example

```bash
curl -X POST \
  http://localhost:17010/messages/get \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"max_messages": 5, "max_len": 100000}'
```

## Topic Permissions

Your user account must have subscription permissions for the topics you want to subscribe to. Permissions
are configured using pattern matching - see the pattern documentation for details on how topic patterns work.

## Message Format

Retrieved messages contain:
- `data` - The actual message content
- `msg_id` - Unique message identifier
- `topic_name` - Topic the message was published to
- `pub_time_iso` - When the message was published (ISO format)
- `priority` - Message priority (1-9, higher is more important)
- `size` - Message size in bytes

## Error Handling

Common error scenarios:
- **401 Unauthorized** - Invalid credentials or insufficient permissions
- **400 Bad Request** - Invalid request format or parameters
- **404 Not Found** - Topic does not exist
- **500 Internal Server Error** - Server-side error

## Best Practices

1. **Handle errors** - Always check the `is_ok` field in responses
2. **Limit message retrieval** - Use appropriate `max_messages` and `max_len` values
3. **Regular polling** - Call `/messages/get` regularly to retrieve new messages
4. **Process messages promptly** - Retrieved messages are removed from your queue
