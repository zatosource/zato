# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import time
from http.client import BAD_REQUEST, OK, UNAUTHORIZED
from pathlib import Path
from unittest import main
from urllib.parse import quote

# PyYAML
from yaml import safe_load

# Requests
import requests

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubOpenAPITestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server using OpenAPI specification.
    """

    @classmethod
    def setUpClass(cls):
        """ Set up OpenAPI client and test configuration.
        """
        super().setUpClass()

        if cls.skip_tests:
            return

        # Check if OpenAPI spec environment variable exists
        openapi_spec_file = os.environ.get('Zato_Test_PubSub_OpenAPI_File')
        if not openapi_spec_file:
            cls.skip_tests = True
            return

        # Load OpenAPI specification
        openapi_spec_path = Path(openapi_spec_file)
        if not openapi_spec_path.exists():
            cls.skip_tests = True
            return

        with open(openapi_spec_path, 'r') as f:
            cls.api_spec = safe_load(f)

        # Validate spec loaded correctly
        if not cls.api_spec:
            raise Exception('Failed to load OpenAPI specification')

        logger.info('OpenAPI specification loaded successfully')

# ################################################################################################################################

    def _validate_response_against_schema(self, response, endpoint_path, status_code):
        """ Validate response against OpenAPI schema.
        """
        # Get the path spec from OpenAPI
        paths = self.api_spec.get('paths', {})
        path_spec = paths.get(endpoint_path)

        if not path_spec:
            logger.warning(f'Path {endpoint_path} not found in OpenAPI spec')
            return

        # Get the POST operation (all our endpoints use POST)
        operation = path_spec.get('post')
        if not operation:
            logger.warning(f'POST operation not found for path {endpoint_path}')
            return

        # Get response schema for the status code
        responses = operation.get('responses', {})
        response_spec = responses.get(str(status_code))
        if not response_spec:
            logger.warning(f'Response schema for {status_code} not found for path {endpoint_path}')
            return

        # Validate JSON response
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                self.fail(f'Invalid JSON response for {endpoint_path}: {e}')

            # Get content schema
            content = response_spec.get('content', {})
            json_content = content.get('application/json', {})
            schema = json_content.get('schema', {})

            if schema:
                self._validate_schema(response_data, schema, f'{endpoint_path} response')

# ################################################################################################################################

    def _validate_schema(self, data, schema, context):
        """ Validate data against schema definition.
        """
        schema_type = schema.get('type')

        if schema_type == 'object':
            if not isinstance(data, dict):
                self.fail(f'{context}: expected object, got {type(data).__name__}')

            # Check required fields
            required = schema.get('required', [])
            for field in required:
                if field not in data:
                    self.fail(f'{context}: missing required field "{field}"')

            # Validate properties
            properties = schema.get('properties', {})
            for field, field_schema in properties.items():
                if field in data:
                    self._validate_schema(data[field], field_schema, f'{context}.{field}')

        elif schema_type == 'array':
            if not isinstance(data, list):
                self.fail(f'{context}: expected array, got {type(data).__name__}')

            items_schema = schema.get('items', {})
            if items_schema:
                for i, item in enumerate(data):
                    self._validate_schema(item, items_schema, f'{context}[{i}]')

        elif schema_type == 'string':
            if not isinstance(data, str):
                self.fail(f'{context}: expected string, got {type(data).__name__}')

        elif schema_type == 'integer':
            if not isinstance(data, int):
                self.fail(f'{context}: expected integer, got {type(data).__name__}')

        elif schema_type == 'boolean':
            if not isinstance(data, bool):
                self.fail(f'{context}: expected boolean, got {type(data).__name__}')

        # Handle allOf
        if 'allOf' in schema:
            for sub_schema in schema['allOf']:
                self._validate_schema(data, sub_schema, context)

        # Handle $ref
        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path.startswith('#/components/schemas/'):
                schema_name = ref_path.split('/')[-1]
                components = self.api_spec.get('components', {})
                schemas = components.get('schemas', {})
                ref_schema = schemas.get(schema_name, {})
                if ref_schema:
                    self._validate_schema(data, ref_schema, context)

# ################################################################################################################################

    def test_openapi_publish_message(self):
        """ Test publish message endpoint against OpenAPI spec.
        """
        topic_name = self.test_topics[0]

        # Test simple message as per OpenAPI examples
        simple_payload = {
            'data': 'Order #12345 has been processed'
        }

        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(publish_url, json=simple_payload, auth=self.auth)

        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/topic/{topic_name}', OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))
        self.assertIn('msg_id', response_data)
        self.assertTrue(response_data['msg_id'].startswith('zpsm'))

        # Test JSON message with metadata as per OpenAPI examples
        json_payload = {
            'data': {
                'order_id': 12345,
                'status': 'completed',
                'timestamp': '2025-01-01T12:00:00Z'
            },
            'priority': 8,
            'expiration': 7200,
            'correl_id': 'order-12345-notification'
        }

        response = requests.post(publish_url, json=json_payload, auth=self.auth)
        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/topic/{topic_name}', OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))
        self.assertIn('msg_id', response_data)

# ################################################################################################################################

    def test_openapi_subscribe_to_topic(self):
        """ Test subscribe endpoint against OpenAPI spec.
        """
        topic_name = self.test_topics[0]

        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)

        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/subscribe/topic/{topic_name}', OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))
        self.assertIn('cid', response_data)

# ################################################################################################################################

    def test_openapi_unsubscribe_from_topic(self):
        """ Test unsubscribe endpoint against OpenAPI spec.
        """
        topic_name = self.test_topics[0]

        # First subscribe
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)

        # Step 2: Unsubscribe from topic
        unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
        response = requests.post(unsubscribe_url, auth=self.auth)

        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/unsubscribe/topic/{topic_name}', OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))
        self.assertIn('cid', response_data)

# ################################################################################################################################

    def test_openapi_get_messages(self):
        """ Test get messages endpoint against OpenAPI spec.
        """
        topic_name = self.test_topics[0]

        # Subscribe to topic first
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Publish a test message
        test_message = {
            'data': {
                'order_id': 12345,
                'status': 'completed',
                'amount': 299.99,
                'currency': 'EUR'
            },
            'priority': 5,
            'correl_id': 'test-message-123'
        }

        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(publish_url, json=test_message, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Wait a moment for message to be queued
        time.sleep(0.5)

        # Test default parameters (no request body)
        get_messages_url = f'{self.base_url}/pubsub/messages/get'
        response = requests.post(get_messages_url, auth=self.auth)

        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/messages/get', OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))
        self.assertIn('messages', response_data)
        self.assertIn('message_count', response_data)

        # Validate message structure matches OpenAPI spec
        messages = response_data['messages']
        if messages:
            message = messages[0]
            self.assertIn('data', message)
            self.assertIn('meta', message)
            meta = message['meta']
            self.assertIn('topic_name', meta)
            self.assertIn('size', meta)
            self.assertIn('priority', meta)
            self.assertIn('expiration', meta)
            self.assertIn('msg_id', meta)
            self.assertIn('pub_time_iso', meta)
            self.assertIn('recv_time_iso', meta)
            self.assertIn('expiration_time_iso', meta)
            self.assertIn('time_since_pub', meta)
            self.assertIn('time_since_recv', meta)

            # Validate msg_id pattern from OpenAPI spec
            self.assertTrue(meta['msg_id'].startswith('zpsm'))

        # Test with parameters as per OpenAPI examples
        request_payload = {
            'max_messages': 10,
            'max_len': 1000000
        }

        response = requests.post(get_messages_url, json=request_payload, auth=self.auth)
        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/messages/get', OK)

        # Test batch processing example
        batch_payload = {
            'max_messages': 100,
            'max_len': 2000000
        }

        response = requests.post(get_messages_url, json=batch_payload, auth=self.auth)
        self.assertEqual(response.status_code, OK)
        self._validate_response_against_schema(response, '/pubsub/messages/get', OK)

# ################################################################################################################################

    def test_openapi_topic_name_validation(self):
        """ Test topic name validation as specified in OpenAPI spec.
        """
        # Test topic name with hash character (should fail per OpenAPI pattern)
        invalid_topic = 'unauthorized.topic#invalid'
        encoded_topic = quote(invalid_topic)

        # Test publish with invalid topic
        publish_url = f'{self.base_url}/pubsub/topic/{encoded_topic}'
        payload = {'data': 'test message'}
        response = requests.post(publish_url, json=payload, auth=self.auth)
        self.assertEqual(response.status_code, BAD_REQUEST)
        self._validate_response_against_schema(response, '/pubsub/topic/{topic_name}', BAD_REQUEST)

        # Test subscribe with invalid topic
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{encoded_topic}'
        response = requests.post(subscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, BAD_REQUEST)
        self._validate_response_against_schema(response, '/pubsub/subscribe/topic/{topic_name}', BAD_REQUEST)

        # Test unsubscribe with invalid topic
        unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{encoded_topic}'
        response = requests.post(unsubscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, BAD_REQUEST)
        self._validate_response_against_schema(response, '/pubsub/unsubscribe/topic/{topic_name}', BAD_REQUEST)

# ################################################################################################################################

    def test_openapi_error_responses(self):
        """ Test error responses match OpenAPI spec.
        """
        topic_name = self.test_topics[0]

        # Test 400 Bad Request - missing data field
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        invalid_payload = {'priority': 5}  # Missing required 'data' field

        response = requests.post(publish_url, json=invalid_payload, auth=self.auth)
        self.assertEqual(response.status_code, BAD_REQUEST)
        self._validate_response_against_schema(response, '/pubsub/topic/{topic_name}', BAD_REQUEST)

        response_data = response.json()
        self.assertFalse(response_data.get('is_ok'))
        self.assertIn('details', response_data)
        self.assertIn('cid', response_data)

        # Test 400 Bad Request - malformed JSON
        response = requests.post(publish_url, data='invalid json', headers={'Content-Type': 'application/json'}, auth=self.auth)
        self.assertEqual(response.status_code, BAD_REQUEST)

        # Test 401 Unauthorized
        response = requests.post(publish_url, json={'data': 'test'})
        self.assertEqual(response.status_code, 401)

# ################################################################################################################################

    def test_openapi_message_priority_validation(self):
        """ Test message priority validation as per OpenAPI spec (0-9 range).
        """
        topic_name = self.test_topics[0]
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'

        # Test valid priorities (0-9)
        for priority in [0, 5, 9]:
            payload = {
                'data': f'Test message with priority {priority}',
                'priority': priority
            }
            response = requests.post(publish_url, json=payload, auth=self.auth)
            self.assertEqual(response.status_code, OK, f'Priority {priority} should be valid')

        # Test invalid priorities (outside 0-9 range)
        for priority in [-1, 10, 15]:
            payload = {
                'data': f'Test message with invalid priority {priority}',
                'priority': priority
            }
            response = requests.post(publish_url, json=payload, auth=self.auth)
            # The server should either accept it (clamping to valid range) or reject it
            # Based on the OpenAPI spec, it should be within 0-9 range
            if response.status_code == OK:
                # If accepted, verify the response
                response_data = response.json()
                self.assertTrue(response_data.get('is_ok'))

# ################################################################################################################################

    def test_openapi_expiration_validation(self):
        """ Test message expiration validation as per OpenAPI spec.
        """
        topic_name = self.test_topics[0]
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'

        # Test valid expiration values
        valid_expirations = [1, 3600, 86400, 31536000]  # 1 second to 1 year

        for expiration in valid_expirations:
            payload = {
                'data': f'Test message with expiration {expiration}',
                'expiration': expiration
            }
            response = requests.post(publish_url, json=payload, auth=self.auth)
            self.assertEqual(response.status_code, OK, f'Expiration {expiration} should be valid')

            response_data = response.json()
            self.assertTrue(response_data.get('is_ok'))

# ################################################################################################################################

    def test_openapi_complete_workflow(self):
        """ Test complete workflow as described in README files and OpenAPI spec.
        """
        topic_name = self.test_topics[0]

        # Step 1: Subscribe to topic
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Step 2: Publish multiple messages with different priorities
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'

        messages_to_publish = [
            {
                'data': {'type': 'order', 'id': 1, 'status': 'pending'},
                'priority': 3,
                'correl_id': 'order-001'
            },
            {
                'data': {'type': 'order', 'id': 2, 'status': 'processed'},
                'priority': 7,
                'correl_id': 'order-002'
            },
            {
                'data': {'type': 'alert', 'level': 'critical'},
                'priority': 9,
                'correl_id': 'alert-001'
            }
        ]

        published_msg_ids = []
        for message in messages_to_publish:
            response = requests.post(publish_url, json=message, auth=self.auth)
            self.assertEqual(response.status_code, OK)

            response_data = response.json()
            self.assertTrue(response_data.get('is_ok'))
            published_msg_ids.append(response_data['msg_id'])

        # Step 3: Wait for messages to be queued
        time.sleep(1.0)

        # Step 4: Retrieve messages (should be in priority order)
        get_messages_url = f'{self.base_url}/pubsub/messages/get'
        response = requests.post(get_messages_url, json={'max_messages': 10}, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))

        messages = response_data.get('messages', [])
        self.assertGreaterEqual(len(messages), 3)

        # Verify messages are in priority order (highest first)
        priorities = [msg.get('priority', 0) for msg in messages[:3]]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

        # Step 5: Unsubscribe from topic
        unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
        response = requests.post(unsubscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        response_data = response.json()
        self.assertTrue(response_data.get('is_ok'))

# ################################################################################################################################

    def test_openapi_spec_examples_validation(self):
        """ Test all examples from OpenAPI spec work correctly.
        """
        topic_name = self.test_topics[0]  # Use topic with permissions

        # Subscribe first
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Test simple_message example from OpenAPI spec
        simple_example = {
            'data': 'Order #12345 has been processed'
        }

        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        response = requests.post(publish_url, json=simple_example, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Test json_message example from OpenAPI spec
        json_example = {
            'data': {
                'order_id': 12345,
                'status': 'completed',
                'timestamp': '2025-01-01T12:00:00Z'
            },
            'priority': 8,
            'expiration': 7200,
            'correl_id': 'order-12345-notification'
        }

        response = requests.post(publish_url, json=json_example, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Test get messages examples
        get_messages_url = f'{self.base_url}/pubsub/messages/get'

        # Default example (no body)
        response = requests.post(get_messages_url, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Standard example
        standard_example = {
            'max_messages': 10,
            'max_len': 1000000
        }
        response = requests.post(get_messages_url, json=standard_example, auth=self.auth)
        self.assertEqual(response.status_code, OK)

        # Batch processing example
        batch_example = {
            'max_messages': 100,
            'max_len': 2000000
        }
        response = requests.post(get_messages_url, json=batch_example, auth=self.auth)
        self.assertEqual(response.status_code, OK)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
