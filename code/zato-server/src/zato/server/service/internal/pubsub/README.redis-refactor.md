# Zato Pub/Sub: RabbitMQ to Redis Migration Plan

## Overview

Replace RabbitMQ with Redis for pub/sub messaging. Eliminate separate pub/sub REST server processes - handle all pub/sub REST endpoints as standard Zato services within the main Zato server process.

## Architecture Change

### Current (RabbitMQ)
```
HAProxy
   ├── Zato Server (services)
   ├── PubSubRESTServerPublish (separate process, port X)
   └── PubSubRESTServerPull (separate process, port Y)
```

### Target (Redis)
```
HAProxy
   └── Zato Server (services + pub/sub endpoints)
           └── Redis connection pool (shared)
```

**Key change**: No separate pub/sub processes. All pub/sub REST endpoints become regular Zato services.

## REST API Endpoints (unchanged externally)

| Endpoint | Current Handler | New Handler |
|----------|-----------------|-------------|
| `POST /pubsub/topic/{topic_name}` | `PubSubRESTServerPublish.on_publish()` | `pubsub.rest.publish` service |
| `POST /pubsub/messages/get` | `PubSubRESTServerPull.on_messages_get()` | `pubsub.rest.get-messages` service |
| `POST /pubsub/subscribe/topic/{topic_name}` | `BaseRESTServer.on_subscribe()` | `pubsub.rest.subscribe` service |
| `POST /pubsub/unsubscribe/topic/{topic_name}` | `BaseRESTServer.on_unsubscribe()` | `pubsub.rest.unsubscribe` service |

## Why Redis Streams

| Requirement | Redis Streams |
|-------------|---------------|
| Messages persist until pulled | XADD persists, XACK acknowledges |
| Per-user queues (sub_key) | Consumer Groups |
| Multiple topics per user | XREADGROUP from multiple streams |
| Message expiration | XTRIM / MINID |
| Pull-based delivery | XREADGROUP with `>` for new messages |
| Priority | Post-fetch sort (already done in `_transform_messages`) |

## Redis Data Structures

| Key Pattern | Type | Purpose |
|-------------|------|---------|
| `zato:pubsub:stream:{topic_name}` | Stream | Messages for topic |
| `zato:pubsub:subs:{sub_key}` | Set | Topics this sub_key subscribes to |
| `zato:pubsub:topic_subs:{topic_name}` | Set | Sub_keys subscribed to this topic |

## Implementation Plan

### Phase 1: Create Redis Pub/Sub Layer

New file: `zato-common/src/zato/common/pubsub/redis_backend.py`

```python
class RedisPubSubBackend:
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def publish(self, topic_name, message):
        stream_key = f'zato:pubsub:stream:{topic_name}'
        msg_id = self.redis.xadd(stream_key, message, maxlen=...)
        return msg_id
    
    def subscribe(self, sub_key, topic_name):
        # Add topic to subscriber's set
        self.redis.sadd(f'zato:pubsub:subs:{sub_key}', topic_name)
        # Add subscriber to topic's set
        self.redis.sadd(f'zato:pubsub:topic_subs:{topic_name}', sub_key)
        # Create consumer group if not exists
        stream_key = f'zato:pubsub:stream:{topic_name}'
        try:
            self.redis.xgroup_create(stream_key, sub_key, id='0', mkstream=True)
        except ResponseError:
            pass  # Group already exists
    
    def unsubscribe(self, sub_key, topic_name):
        self.redis.srem(f'zato:pubsub:subs:{sub_key}', topic_name)
        self.redis.srem(f'zato:pubsub:topic_subs:{topic_name}', sub_key)
        # Optionally destroy consumer group
    
    def fetch_messages(self, sub_key, max_messages, max_len):
        topics = self.redis.smembers(f'zato:pubsub:subs:{sub_key}')
        if not topics:
            return []
        
        messages = []
        streams = {f'zato:pubsub:stream:{t}': '>' for t in topics}
        
        # Read from all subscribed streams
        result = self.redis.xreadgroup(
            groupname=sub_key,
            consumername=sub_key,
            streams=streams,
            count=max_messages,
            block=0  # Non-blocking
        )
        
        for stream_name, stream_messages in result:
            for msg_id, msg_data in stream_messages:
                messages.append(msg_data)
                # Auto-acknowledge
                self.redis.xack(stream_name, sub_key, msg_id)
        
        # Sort by priority desc, then timestamp asc
        messages.sort(key=lambda m: (-int(m.get('priority', 5)), m.get('pub_time_iso', '')))
        return messages[:max_messages]
```

### Phase 2: Create Pub/Sub REST Services

New file: `zato-server/src/zato/server/service/internal/pubsub/rest.py`

```python
class Publish(Service):
    name = 'pubsub.rest.publish'
    
    class SimpleIO:
        input_required = 'topic_name'
        input_optional = 'data', 'priority', 'expiration', 'correl_id'
        output_optional = 'msg_id', 'is_ok', 'cid'
    
    def handle(self):
        # Validate topic name
        # Check permissions via pattern matcher
        # Publish to Redis stream
        msg_id = self.server.pubsub_redis.publish(
            self.request.input.topic_name,
            self.request.input.data,
            ...
        )
        self.response.payload.msg_id = msg_id
        self.response.payload.is_ok = True


class GetMessages(Service):
    name = 'pubsub.rest.get-messages'
    
    class SimpleIO:
        input_optional = 'max_messages', 'max_len'
        output_optional = 'messages', 'message_count', 'is_ok', 'cid'
    
    def handle(self):
        # Get sub_key for authenticated user
        sub_key = self._get_user_sub_key()
        
        # Fetch from Redis
        messages = self.server.pubsub_redis.fetch_messages(
            sub_key,
            self.request.input.max_messages or 50,
            self.request.input.max_len or 5_000_000
        )
        
        self.response.payload.messages = messages
        self.response.payload.message_count = len(messages)
        self.response.payload.is_ok = True


class Subscribe(Service):
    name = 'pubsub.rest.subscribe'
    
    class SimpleIO:
        input_required = 'topic_name'
        output_optional = 'is_ok', 'cid'
    
    def handle(self):
        # Validate topic, check permissions
        # Create subscription in ODB
        # Register in Redis
        self.server.pubsub_redis.subscribe(sub_key, topic_name)


class Unsubscribe(Service):
    name = 'pubsub.rest.unsubscribe'
    
    class SimpleIO:
        input_required = 'topic_name'
        output_optional = 'is_ok', 'cid'
    
    def handle(self):
        # Remove from Redis
        self.server.pubsub_redis.unsubscribe(sub_key, topic_name)
        # Update ODB
```

### Phase 3: Register REST Channels

Create REST channels in Zato for the pub/sub endpoints:

| URL Pattern | Service | Method |
|-------------|---------|--------|
| `/pubsub/topic/{topic_name}` | `pubsub.rest.publish` | POST |
| `/pubsub/messages/get` | `pubsub.rest.get-messages` | POST |
| `/pubsub/subscribe/topic/{topic_name}` | `pubsub.rest.subscribe` | POST |
| `/pubsub/unsubscribe/topic/{topic_name}` | `pubsub.rest.unsubscribe` | POST |

### Phase 4: Initialize Redis in Zato Server

Modify: `zato-server/src/zato/server/base/parallel.py`

```python
class ParallelServer:
    def __init__(self, ...):
        ...
        # Initialize Redis pub/sub backend
        self.pubsub_redis = RedisPubSubBackend(self.kvdb.conn)  # Reuse existing Redis connection
```

### Phase 5: HAProxy Configuration

Simplify HAProxy - all traffic goes to Zato servers:

```
frontend http_front
    bind *:80
    default_backend zato_servers

backend zato_servers
    balance roundrobin
    server zato1 127.0.0.1:17010 check
    server zato2 127.0.0.1:17011 check
```

No special routing for pub/sub endpoints needed.

## Files to Create

| File | Purpose |
|------|---------|
| `zato-common/src/zato/common/pubsub/redis_backend.py` | Redis pub/sub operations |
| `zato-server/src/zato/server/service/internal/pubsub/rest.py` | REST endpoint services |

## Files to Modify

| File | Changes |
|------|---------|
| `zato-server/src/zato/server/base/parallel.py` | Initialize `pubsub_redis` |
| `zato-server/src/zato/server/base/worker.py` | Load pub/sub permissions into pattern matcher |

## Files to Delete (after migration)

| File | Reason |
|------|--------|
| `zato-common/src/zato/common/pubsub/server/rest_pull.py` | Replaced by service |
| `zato-common/src/zato/common/pubsub/server/rest_publish.py` | Replaced by service |
| `zato-common/src/zato/common/pubsub/server/rest_base.py` | No longer needed |
| `zato-common/src/zato/common/pubsub/server/base.py` | No longer needed |
| `zato-common/src/zato/common/pubsub/server/haproxy.cfg` | Simplified |

## Files Unchanged

| File | Reason |
|------|--------|
| `subscription.py`, `topic.py`, `client.py` | ODB operations remain |
| `openapi.yaml` | External API unchanged |
| `matcher.py` | Pattern matching logic reused |

## Implementation Steps

### Step 1: Implement + Test (single commit)

**Files created:**
- `zato-common/src/zato/common/pubsub/redis_backend.py` - Redis pub/sub operations
- `zato-common/src/zato/common/pubsub/subscriptions_store.py` - In-memory subscription mappings
- `zato-common/test/zato/common/pubsub/test_redis_backend.py` - Backend tests
- `zato-server/src/zato/server/service/internal/pubsub/rest.py` - REST services
- `zato-server/test/zato/server/service/internal/pubsub/test_rest_services.py` - Service tests

**Files modified:**
- `zato-server/src/zato/server/base/parallel/__init__.py` - Initialize Redis backend, pattern matcher, subscriptions store

**REST channels** (via enmasse YAML or migration):
- `/pubsub/topic/{topic_name}` → `pubsub.rest.publish`
- `/pubsub/messages/get` → `pubsub.rest.get-messages`
- `/pubsub/subscribe/topic/{topic_name}` → `pubsub.rest.subscribe`
- `/pubsub/unsubscribe/topic/{topic_name}` → `pubsub.rest.unsubscribe`

**Tests:**

`test_redis_backend.py`:
```python
class TestRedisPubSubBackend:
    def test_publish_creates_stream_entry(self):
    def test_subscribe_creates_consumer_group(self):
    def test_fetch_returns_messages_in_priority_order(self):
    def test_fetch_acknowledges_messages(self):
    def test_unsubscribe_removes_from_sets(self):
    def test_unsubscribe_last_topic_destroys_consumer_group(self):
    def test_message_expiration_cleanup(self):
```

`test_rest_services.py`:
```python
class TestPublishService:
    def test_publish_returns_msg_id(self):
    def test_publish_validates_topic_name(self):
    def test_publish_checks_permissions(self):
    def test_publish_rejects_missing_data(self):

class TestGetMessagesService:
    def test_get_messages_returns_subscribed_messages(self):
    def test_get_messages_respects_max_messages(self):
    def test_get_messages_respects_max_len(self):
    def test_get_messages_returns_empty_when_no_subscription(self):

class TestSubscribeService:
    def test_subscribe_creates_subscription(self):
    def test_subscribe_idempotent(self):
    def test_subscribe_checks_permissions(self):

class TestUnsubscribeService:
    def test_unsubscribe_removes_subscription(self):
    def test_unsubscribe_idempotent(self):
```

**Run:** `pytest zato-common/test/zato/common/pubsub/test_redis_backend.py zato-server/test/zato/server/service/internal/pubsub/test_rest_services.py`

### Step 2: Deploy + Cleanup
- Update HAProxy config (simplify)
- Remove old pub/sub server processes from deployment
- Delete old pub/sub server code

## Design Decisions

| Decision | Choice |
|----------|--------|
| Message expiration | XTRIM with MINID based on `expiration` field; separate cleanup process connecting to Redis |
| Consumer group cleanup | Destroy group when user unsubscribes from last topic |
| Authentication | Services get username from `self.channel.security.username` |
| URL path parameters | REST channel maps `{topic_name}` to SimpleIO input |
| Internal broker messaging | Also moves to Redis (Redis pub/sub for server-to-server) |
| Existing tests | Adapt to test Redis backend |

## Benefits

- **Single process type** - easier ops
- **Shared Redis pool** - already exists in Zato (`self.kvdb`)
- **Standard deployment** - services like any other
- **Simpler HAProxy** - no special routing
- **Better observability** - standard Zato service metrics
- **No RabbitMQ dependency** - single external dependency (Redis)
