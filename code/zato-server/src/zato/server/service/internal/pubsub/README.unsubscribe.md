# Zato Pub/Sub Unsubscribe API

## Overview

The Zato Pub/Sub REST API allows external clients to unsubscribe from topics. This document explains how to remove subscriptions and clean up resources.

## Authentication

All requests require HTTP Basic Authentication using your Zato security credentials.

## Unsubscribe from a Topic

Remove subscription from a specific topic.

### Endpoint
```
POST /topic/{topic_name}/unsubscribe
```

### Parameters
- `topic_name` - The name of the topic to unsubscribe from

### Topic Name Restrictions
Topic names must adhere to the following rules:
- Maximum length: 200 characters
- The "#" character is not allowed in topic names
- Only ASCII characters are permitted



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
  "cid": "correlation-id",
  "details": "Authentication failed",
  "status": "401 Unauthorized"
}
```

#### Error (400 Bad Request)
```json
{
  "is_ok": false,
  "cid": "correlation-id",
  "details": "Topic name validation error",
  "status": "400 Bad Request"
}
```

### Examples

#### Unsubscribe from Order Events
```bash
curl -X POST \
  -u username:password \
  http://localhost:17010/topic/orders.processed/unsubscribe
```

#### Unsubscribe from Alert Topic
```bash
curl -X POST \
  -u username:password \
  http://localhost:17010/topic/alerts.critical.system/unsubscribe
```

## Unsubscribe Behavior

### Safe Operation
- Unsubscribing from a topic you're not subscribed to is safe and returns success
- The system recognizes non-existing subscriptions and handles them gracefully
- No error is returned if you're already unsubscribed

### Message Queue Impact
- Your personal message queue remains active for other subscriptions (if any)
- Only messages from the unsubscribed topic stop being delivered
- Existing messages in your queue from that topic remain until retrieved

## Topic Permissions

Your user account must have subscription permissions for the topics you want to unsubscribe from. The same permissions required for subscribing are needed for unsubscribing.

### Permission Examples
```
sub=orders.*           # Can unsubscribe from orders.processed, orders.cancelled, etc.
sub=alerts.**          # Can unsubscribe from any alerts topic at any depth
sub=notifications.user.email  # Can only unsubscribe from this exact topic
```

## Error Handling

Common error scenarios:

### Authentication Errors
- **401 Unauthorized** - Invalid credentials provided in HTTP Basic Auth

### Topic Validation Errors
- **400 Bad Request** - Topic name violates restrictions (length, characters, etc.)

### Server Errors
- **500 Internal Server Error** - Unexpected server-side error during unsubscribe

## Related Operations

After unsubscribing:

1. **Subscribe Again** - Use `POST /topic/{topic_name}/subscribe` to re-subscribe
2. **Check Messages** - Use `POST /messages/get` to retrieve any remaining messages
3. **Publish Messages** - Use `POST /topic/{topic_name}/publish` to send messages

## Best Practices

1. **Handle errors** - Always check the `is_ok` field in responses
2. **Clean unsubscribe** - Unsubscribe from topics when no longer needed to free resources
3. **Check permissions** - Ensure your user has subscribe permissions for the topics
4. **Monitor subscriptions** - Keep track of active subscriptions to avoid unnecessary unsubscribes
5. **Retrieve remaining messages** - Call `/messages/get` after unsubscribing to get any pending messages
