# Zato Pub/Sub Publish API

## Overview

The Zato Pub/Sub REST API allows external clients to publish messages to topics. This document explains how to use the publish endpoint.

## Authentication

All requests require HTTP Basic Authentication using your Zato security credentials.

## Publish a Message

Send a message to a specific topic.

### Endpoint
```
POST /topic/{topic_name}/publish
```

### Parameters
- `topic_name` - The name of the topic to publish to

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "data": "message content",
  "priority": 5,
  "expiration": 3600,
  "correl_id": "optional-correlation-id",
  "in_reply_to": "optional-message-id",
  "ext_client_id": "optional-external-client-id"
}
```

#### Required Parameters
- `data` - The message content (string or JSON object)

#### Optional Parameters
- `priority` - Message priority from 1-9 (default: 5, higher is more important)
- `expiration` - Message expiration time in seconds (default: 3600)
- `correl_id` - Correlation ID for message tracking
- `in_reply_to` - ID of message this is replying to
- `ext_client_id` - External client identifier

### Response

#### Success (200 OK)
```json
{
  "is_ok": true,
  "msg_id": "unique-message-id",
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
  "details": "Message data missing"
}
```

### Examples

#### Simple Message
```bash
curl -X POST \
  http://localhost:17010/topic/orders.processed/publish \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"data": "Order #12345 has been processed"}'
```

#### JSON Message with Options
```bash
curl -X POST \
  http://localhost:17010/topic/notifications.urgent/publish \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "order_id": 12345,
      "status": "completed",
      "timestamp": "2025-01-01T12:00:00Z"
    },
    "priority": 8,
    "expiration": 7200,
    "correl_id": "order-12345-notification"
  }'
```

#### High Priority Alert
```bash
curl -X POST \
  http://localhost:17010/topic/alerts.critical/publish \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{
    "data": "System disk usage above 95%",
    "priority": 9,
    "expiration": 300
  }'
```

## Topic Permissions

Your user account must have publish permissions for the topics you want to publish to. Permissions are configured
using pattern matching - see the pattern documentation for details on how topic patterns work.

## Message Properties

### Priority Levels
- **1-3**: Low priority (background tasks, logs)
- **4-6**: Normal priority (regular business messages)
- **7-9**: High priority (alerts, urgent notifications)

### Expiration
- Messages expire after the specified time in seconds
- Expired messages are automatically removed from queues
- Default expiration is 3600 seconds (1 hour)
- Set to 0 for messages that never expire

### Message ID
- Each published message receives a unique ID
- Use this ID for tracking and correlation
- Format: `zato.msg.` followed by a UUID

## Error Handling

Common error scenarios:
- **401 Unauthorized** - Invalid credentials or insufficient permissions
- **400 Bad Request** - Missing data field or invalid request format
- **404 Not Found** - Topic does not exist
- **500 Internal Server Error** - Server-side error

## Best Practices

1. **Check permissions** - Ensure your user has publish access to the topics
2. **Handle errors** - Always check the `is_ok` field in responses
3. **Set appropriate priority** - Use priority levels to ensure important messages are processed first
4. **Use correlation IDs** - Include correlation IDs for message tracking and debugging
5. **Set reasonable expiration** - Don't let messages accumulate indefinitely
6. **Validate data** - Ensure message content is properly formatted
