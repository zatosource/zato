# PubSub Test Framework Specification

## Overview
Test framework for PubSub message generation and collection. Consists of two main components:

1. **Message Sender** - Generates and publishes messages via REST API
2. **Collection Server** - Receives messages, tracks statistics, and generates reports

Both components utilize the users.yaml configuration to dynamically calculate message counts and distribution.

## Implementation

The framework is implemented using:
- gevent for asynchronous processing and concurrency
- werkzeug for HTTP request handling in the server component
- requests library for sending messages in the client component
- gunicorn for production deployment of the server (optional)

### File Structure
- `models.py` - Data structures for messages and statistics
- `config.py` - Configuration loading and management
- `server.py` - Main server implementation with request handling
- `report.py` - HTML report generation
- `pubsub_test_server.py` - Server entry point and runner
- `users_yaml.py` - Parser and calculator for dynamic message count
- `message_sender.py` - Client for generating and sending messages
- `pubsub_test_client.py` - Client entry point and runner

## Server Configuration

### Command Line Execution
```
python pubsub_test_server.py --config /path/to/config.yaml
```

### Command Line Options
- `--config` - Path to YAML configuration file (required)
- `--log-level` - Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--workers` - Number of Gunicorn worker processes (default: 1)
- `--timeout` - Gunicorn worker timeout in seconds (default: 30)
- `--use-gunicorn` - Use Gunicorn server instead of gevent WSGI server

### YAML Configuration File
```yaml
server:
  host: 127.0.0.1
  port: 10055

collection:
  users_yaml_path: "/path/to/zato/common/pubsub/users.yaml"  # Path to users.yaml
  messages_per_topic_per_user: 10  # Each user sends 10 messages to each topic
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

### Status Endpoint
- **URL**: `/status`
- **Method**: `GET`
- **Response**: JSON with current test status

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
    topics_count: dict  # Count by topic_name
    subscriptions_count: dict  # Count by sub_key/queue_name
    publisher_count: dict  # Count by publisher
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
- Total topics, subscriptions, and publishers
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

## Dynamic Message Count Calculation

The expected message count is calculated dynamically based on the users.yaml configuration:

1. The system parses the users.yaml file which contains all users, topics, and subscriptions
2. For each topic, it identifies all publishers and subscribers
3. The calculation formula is:
   ```
   expected_count = sum(
       messages_per_topic_per_user *
       number_of_publishers_for_topic *
       number_of_subscriptions_for_topic
   )
   ```
4. Each message generated by a publisher is counted once per subscription that receives it
5. The `users_yaml.py` module provides two main functions:
   - `calculate_expected_messages()`: Computes the total expected message count
   - `calculate_message_distribution()`: Provides detailed statistics on message distribution

## Client Configuration

### Command Line Execution
```
python pubsub_test_client.py --config /path/to/client_config.yaml
```

### Command Line Options
- `--config` - Path to YAML configuration file (required)
- `--log-level` - Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--concurrency` - Maximum number of concurrent greenlets (default: 100)
- `--dry-run` - Validate configuration without sending messages

### YAML Configuration File
```yaml
client:
  server_url: "http://127.0.0.1:10055/messages"  # URL of test server
  request_timeout: 30  # HTTP request timeout in seconds
  retry_count: 3  # Number of retries for failed requests

messaging:
  users_yaml_path: "/path/to/zato/common/pubsub/users.yaml"  # Path to users.yaml
  messages_per_topic_per_user: 10  # Each publisher sends this many messages to each topic
  max_concurrent_publishers: 50  # Maximum number of concurrent publisher greenlets
  max_send_rate: 1000  # Maximum messages per second overall
  send_interval: 0.01  # Interval between sends (seconds) per publisher

content:
  template_path: "/path/to/templates/"  # Path to message templates (optional)
  min_size: 1024  # Minimum message size in bytes
  max_size: 4096  # Maximum message size in bytes
  complexity: "medium"  # simple, medium, complex (affects structure of generated messages)
```

## Message Sender Capabilities

### Core Features
- Sends messages to the test server via REST API
- Tracks metrics about sent messages
- Handles retry logic for failed requests
- Maintains publisher-specific sending statistics

### Message Generation
- Template-based message content with variable substitution
- Configurable message size and complexity
- Deterministic message ID generation for verification
- Support for custom message templates

## Concurrency Model

### Publisher Greenlets
- One greenlet per publisher-topic pair from users.yaml
- Each greenlet responsible for sending its quota of messages
- Configurable sending rate and intervals

### Rate Limiting
- Global rate limiting across all publishers
- Per-publisher rate limiting based on configuration
- Adaptive rate control based on server response times

## Client Statistics and Reporting

### Metrics Tracked
- Messages sent successfully vs. failed
- Average sending rate (msgs/sec)
- Response time statistics (min/max/avg)
- Error counts by type
- Message size statistics

### Output Formats
- Console output for real-time monitoring
- JSON statistics file for further analysis
- Option to upload statistics to collection server

### Statistics Captured
- Summary metrics (total sent, success rate, throughput)
- Publisher-specific statistics
- Topic distribution metrics
- Detailed error logs with timestamps
- Performance metrics over time
