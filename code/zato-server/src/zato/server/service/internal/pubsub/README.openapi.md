# Zato Pub/Sub REST API - OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: Zato Pub/Sub REST API
  description: |
    REST API for Zato's publish/subscribe messaging system.

    This API allows clients to:
    - Publish messages to topics
    - Subscribe to topics to receive messages
    - Retrieve messages from subscribed topics
    - Unsubscribe from topics

    All operations require HTTP Basic Authentication.
  version: 3.3.0
  contact:
    name: Zato Source
    url: https://zato.io

servers:
  - url: http://localhost:44556

security:
  - basicAuth: []

paths:
  /topic/{topic_name}/publish:
    post:
      summary: Publish a message to a topic
      description: |
        Publish a message to the specified topic. The user must have publish permissions for the topic.
        Topic names are validated and must meet specific requirements.
      parameters:
        - name: topic_name
          in: path
          required: true
          description: Name of the topic to publish to
          schema:
            type: string
            maxLength: 200
            pattern: '^[^\#]*$'
            example: orders.processed
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - data
              properties:
                data:
                  description: The message content
                  oneOf:
                    - type: string
                    - type: object
                  example: "Order #12345 has been processed"
                priority:
                  type: integer
                  minimum: 0
                  maximum: 9
                  default: 5
                  description: Message priority (0=lowest, 9=highest)
                expiration:
                  type: integer
                  minimum: 0
                  default: 31536000
                  description: Message expiration time in seconds
                correl_id:
                  type: string
                  description: Correlation ID for message tracking
                  example: order-12345-notification
                in_reply_to:
                  type: string
                  description: ID of message this is replying to
                ext_client_id:
                  type: string
                  description: External client identifier
            examples:
              simple_message:
                summary: Simple text message
                value:
                  data: "Order #12345 has been processed"
              json_message:
                summary: JSON message with metadata
                value:
                  data:
                    order_id: 12345
                    status: completed
                    timestamp: "2025-01-01T12:00:00Z"
                  priority: 8
                  expiration: 7200
                  correl_id: order-12345-notification
      responses:
        '200':
          description: Message published successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PublishResponse'
        '400':
          description: Bad request (invalid topic name, missing data, malformed JSON)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Authentication failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /topic/{topic_name}/subscribe:
    post:
      summary: Subscribe to a topic
      description: |
        Subscribe to receive messages from the specified topic. The user must have subscribe permissions for the topic.
        Topics are automatically created if they don't exist.
      parameters:
        - name: topic_name
          in: path
          required: true
          description: Name of the topic to subscribe to
          schema:
            type: string
            maxLength: 200
            pattern: '^[^\#]*$'
            example: orders.processed
      responses:
        '200':
          description: Successfully subscribed to topic
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SuccessResponse'
        '400':
          description: Bad request (invalid topic name)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Authentication failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /topic/{topic_name}/unsubscribe:
    post:
      summary: Unsubscribe from a topic
      description: |
        Remove subscription from the specified topic. The user must have subscribe permissions for the topic.
        Unsubscribing from a non-subscribed topic is safe and returns success.
      parameters:
        - name: topic_name
          in: path
          required: true
          description: Name of the topic to unsubscribe from
          schema:
            type: string
            maxLength: 200
            pattern: '^[^\#]*$'
            example: orders.processed
      responses:
        '200':
          description: Successfully unsubscribed from topic
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SuccessResponse'
        '400':
          description: Bad request (invalid topic name)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Authentication failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /messages/get:
    post:
      summary: Retrieve messages from subscribed topics
      description: |
        Get messages from all topics the user is subscribed to. Messages are delivered in priority order
        (highest priority first), then by publish time (oldest first) within the same priority level.
        Retrieved messages are automatically acknowledged and removed from the queue.
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                max_messages:
                  type: integer
                  minimum: 0
                  maximum: 1000
                  default: 50
                  description: Maximum number of messages to retrieve
                max_len:
                  type: integer
                  minimum: 0
                  maximum: 5000000
                  default: 5000000
                  description: Maximum total length of message data in bytes
            examples:
              default_params:
                summary: Use default parameters
                value: {}
              custom_params:
                summary: Custom parameters
                value:
                  max_messages: 10
                  max_len: 1000000
              batch_processing:
                summary: Batch processing
                value:
                  max_messages: 100
                  max_len: 2000000
      responses:
        '200':
          description: Messages retrieved successfully
          content:
            application/json:
              schema:
                oneOf:
                  - $ref: '#/components/schemas/MessagesListResponse'
                  - $ref: '#/components/schemas/SingleMessageResponse'
        '400':
          description: Bad request (malformed JSON, no subscription found)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Authentication failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
      description: HTTP Basic Authentication using Zato security credentials

  schemas:
    SuccessResponse:
      type: object
      required:
        - is_ok
        - cid
      properties:
        is_ok:
          type: boolean
          example: true
        cid:
          type: string
          description: Correlation ID for request tracking
          example: correlation-id-123
        status:
          type: string
          example: "200 OK"

    PublishResponse:
      allOf:
        - $ref: '#/components/schemas/SuccessResponse'
        - type: object
          required:
            - msg_id
          properties:
            msg_id:
              type: string
              description: Unique message identifier
              pattern: '^zpsm\.[a-z0-9-]+$'
              example: zpsm.20250829-074432-7264-d47439a9f-abc

    ErrorResponse:
      type: object
      required:
        - is_ok
        - cid
        - details
        - status
      properties:
        is_ok:
          type: boolean
          example: false
        cid:
          type: string
          description: Correlation ID for request tracking
          example: correlation-id-123
        details:
          type: string
          description: Error description
          example: Authentication failed
        status:
          type: string
          description: HTTP status description
          example: "401 Unauthorized"

    MessageMetadata:
      type: object
      required:
        - topic_name
        - size
        - priority
        - expiration
        - msg_id
        - pub_time_iso
        - recv_time_iso
        - time_since_pub
        - time_since_recv
      properties:
        topic_name:
          type: string
          description: Topic the message was published to
          example: orders.processed
        size:
          type: integer
          description: Message size in bytes
          example: 123
        priority:
          type: integer
          minimum: 0
          maximum: 9
          description: Message priority
          example: 5
        expiration:
          type: integer
          description: Message expiration time in seconds
          example: 3600
        msg_id:
          type: string
          description: Unique message identifier
          pattern: '^zpsm\.[a-z0-9-]+$'
          example: zpsm.20250829-074432-7264-d47439a9f-abc
        correl_id:
          type: string
          description: Correlation ID for message tracking
          example: order-12345
        pub_time_iso:
          type: string
          format: date-time
          description: When the message was published (ISO format with timezone)
          example: "2025-01-01T12:00:00+00:00"
        recv_time_iso:
          type: string
          format: date-time
          description: When the message was received by the system (ISO format with timezone)
          example: "2025-01-01T12:00:01+00:00"
        expiration_time_iso:
          type: string
          format: date-time
          description: When the message will expire (ISO format with timezone)
          example: "2025-01-01T13:00:00+00:00"
        time_since_pub:
          type: string
          description: Time elapsed since message was published (duration format)
          example: "0:00:30.123456"
        time_since_recv:
          type: string
          description: Time elapsed since message was received (duration format)
          example: "0:00:30.123456"
        in_reply_to:
          type: string
          description: ID of message this is replying to
        ext_client_id:
          type: string
          description: External client identifier

    Message:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          description: The actual message content
          oneOf:
            - type: string
            - type: object
          example:
            order_id: 12345
            status: completed
            amount: 299.99
            currency: EUR
        meta:
          $ref: '#/components/schemas/MessageMetadata'

    MessagesListResponse:
      allOf:
        - $ref: '#/components/schemas/SuccessResponse'
        - type: object
          required:
            - messages
            - message_count
          properties:
            messages:
              type: array
              items:
                $ref: '#/components/schemas/Message'
              description: Array of retrieved messages
            message_count:
              type: integer
              description: Number of messages returned
              example: 3

    SingleMessageResponse:
      allOf:
        - $ref: '#/components/schemas/SuccessResponse'
        - type: object
          required:
            - data
            - meta
          properties:
            data:
              description: The actual message content
              oneOf:
                - type: string
                - type: object
              example: "Hello World"
            meta:
              allOf:
                - $ref: '#/components/schemas/MessageMetadata'
                - type: object
                  required:
                    - message_count
                  properties:
                    message_count:
                      type: integer
                      description: Number of messages returned (always 1 for single message response)
                      example: 1

tags:
  - name: Publishing
    description: Operations for publishing messages to topics
  - name: Subscription
    description: Operations for managing topic subscriptions
  - name: Messaging
    description: Operations for retrieving messages
  - name: Health
    description: Service health monitoring
```
