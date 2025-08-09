# Zato Pub/Sub Unsubscribe API

## Overview

The Zato Pub/Sub REST API allows external clients to unsubscribe from topics. This document explains how to use the unsubscribe endpoint.

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
  http://localhost:17010/topic/orders.processed/unsubscribe \
  -u username:password \
  -H "Content-Type: application/json"
```

## Topic Permissions

Your user account must have subscription permissions for the topics you want to unsubscribe from.
Permissions are configured using pattern matching - see the pattern documentation for details on how topic patterns work.

## Error Handling

Common error scenarios:
- **401 Unauthorized** - Invalid credentials or insufficient permissions
- **400 Bad Request** - Invalid request format or parameters
- **404 Not Found** - Topic does not exist or no active subscription
- **500 Internal Server Error** - Server-side error

## Best Practices

1. **Handle errors** - Always check the `is_ok` field in responses
2. **Clean unsubscribe** - Unsubscribe from topics when no longer needed to free resources

Returns `200 OK` with `{"status": "ok"}` if the service is healthy.
