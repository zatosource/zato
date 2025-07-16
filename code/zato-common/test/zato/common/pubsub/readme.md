# PubSub Test Framework Specification

## Overview
Test server for PubSub message collection and reporting. Runs as standalone service, receives messages
via REST API, generates HTML report when expected message count is reached.

## Server Configuration

### Command Line Execution
```
python pubsub_test_server.py --config /path/to/config.yaml
```

### YAML Configuration File
```yaml
server:
  host: 127.0.0.1
  port: 10055

collection:
  expected_message_count: 1000
  log_interval: 100  # Log progress every 100 messages
  timeout_seconds: 300  # Auto-complete if inactive for this duration

report:
  url_path: "/report"  # Access at http://server:port/report
```

## REST API Endpoints

### Message Collection Endpoint
- **URL**: `/messages`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body Example**:
  ```json
  {
    "message_id": "pub-123456789",
    "publication_time": "2025-07-16T09:40:14+02:00",
    "publisher_name": "service_x",
    "topic_name": "example_topic",
    "queue_name": "sub_key_12345",
    "priority": 5,
    "expiration": 3600,
    "content": "Message payload here"
  }
  ```
- **Response**: `200 OK` with counter information

### Report Access
- **URL**: `/report`
- **Method**: `GET`
- **Response**: HTML report of collected messages

## Data Model

### Message
```python
class Message:
    message_id: str
    publication_time: datetime
    publisher_name: str
    topic_name: str
    queue_name: str
    priority: int
    expiration: int
    content: Any
    received_time: datetime  # Timestamp when test server received message
    sequence_number: int     # Assigned by test server in order of arrival
```

### TestCollector
```python
class TestCollector:
    messages: List[Message]
    start_time: datetime
    end_time: datetime
    expected_count: int
    received_count: int
    duplicate_count: int
    malformed_count: int
```

## Server Behavior
1. Starts HTTP server on configured host:port
2. Waits for messages on `/messages` endpoint
3. Processes each message:
   - Validates required fields
   - Assigns sequence number
   - Records received timestamp
   - Stores message data in-memory
4. Logs progress at configured intervals:
   - `Received 100/1000 messages (10%) - Current rate: 45 msgs/sec`
5. When expected message count is reached:
   - Records end time
   - Generates HTML report
   - Makes report available at `/report`
   - Logs completion message
6. Handles timeout:
   - If no messages received for `timeout_seconds` duration
   - Marks test as incomplete
   - Generates partial report with warning

## HTML Report

### Summary Section
- Total messages collected vs expected
- Test duration
- Overall message rate (msgs/sec)
- Test status (complete/incomplete)
- Start and end times
- Per-queue statistics:
  - Messages received per queue
  - Average processing time per queue
  - Success/error rates per queue
  - Min/max/avg message rate per queue

### Message Timeline
- Chart showing message arrival rate over time

### Distribution Charts
- Messages by topic
- Messages by queue
- Messages by publisher

### Message Statistics
- Min/max/avg message size
- Min/max/avg priority
- Min/max/avg expiration
- Distribution of messages over time

### Error Summary
- Count of duplicate messages
- Count of malformed messages
- Any identified errors in message sequence
