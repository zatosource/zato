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

### Topic Name Restrictions
Topic names must adhere to the following rules:
- Maximum length: 200 characters
- The "#" character is not allowed in topic names
- Only ASCII characters are permitted

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
  "cid": "correlation-id",
  "status": "200 OK",
  "msg_id": "zpsm3e2d9618450f4505b1796428dc2b0aea"
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

#### High Priority Business Event
```bash
curl -X POST \
  http://localhost:17010/topic/payments.failed/publish \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "payment_id": "pay_67890",
      "customer_id": "cust_12345",
      "amount": 299.99,
      "reason": "insufficient_funds"
    },
    "priority": 9,
    "expiration": 300
  }'
```

## Topic Permissions

Your user account must have publish permissions for the topics you want to publish to. Permissions are configured
using pattern matching - see the pattern documentation for details on how topic patterns work.

## Message Properties

### Priority Levels
- **1-3**: Low priority (background processing, audit logs)
- **4-6**: Normal priority (regular business transactions)
- **7-9**: High priority (urgent business events, payment failures)

### Expiration
- Messages expire after the specified time in seconds
- Expired messages are automatically removed from queues
- Default expiration is 1 year
- Set to 0 for messages that never expire

### Message ID
- Each published message receives a unique message ID in the response
- Format: `zpsm` followed by a randomly generated string
- Example: `zpsm3e2d9618450f4505b1796428dc2b0aea`

## Error Handling

Common error scenarios:

### Authentication Errors
- **401 Unauthorized** - Invalid credentials provided in HTTP Basic Auth
- **401 Permission Denied** - Valid credentials but no publish permission for the topic

### Request Format Errors
- **400 Input data missing** - No JSON body provided in the request
- **400 Message data missing** - JSON body exists but missing required `data` field
- **400 Invalid JSON** - Malformed JSON in request body

### Topic Validation Errors
- **400 Topic name validation** - Topic name violates restrictions (length, characters, etc.)

### Server Errors
- **500 Internal Server Error** - Unexpected server-side error during processing

## Best Practices

1. **Check permissions** - Ensure your user has publish access to the topics
2. **Handle errors** - Always check the `is_ok` field in responses
3. **Set appropriate priority** - Use priority levels to ensure important messages are processed first
4. **Use correlation IDs** - Include correlation IDs for message tracking and debugging
5. **Set reasonable expiration** - Don't let messages accumulate indefinitely
6. **Validate data** - Ensure message content is properly formatted
