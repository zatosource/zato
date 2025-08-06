# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import warnings
from unittest import main, TestCase

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.server.rest import PubSubRESTServer

# ################################################################################################################################
# ################################################################################################################################

class TestBrokerClient:
    """ Test broker client that captures publish calls without mocking.
    """

    def __init__(self):
        self.published_messages = []
        self.published_exchanges = []
        self.published_routing_keys = []

    def publish(self, message, exchange, routing_key):
        """ Capture publish parameters for verification.
        """
        self.published_messages.append(message)
        self.published_exchanges.append(exchange)
        self.published_routing_keys.append(routing_key)

# ################################################################################################################################
# ################################################################################################################################

class RESTTransformMessagesTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = TestBrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

# ################################################################################################################################

    def test_transform_messages_converts_rabbitmq_format(self):
        """ _transform_messages converts RabbitMQ message format to Zato format.
        """
        rabbitmq_messages = [
            {
                'payload': 'test message data',
                'properties': {
                    'message_id': 'msg_123',
                    'correlation_id': 'corr_456',
                    'priority': 5,
                    'content_type': 'text/plain',
                    'timestamp': '2025-01-01T12:00:00Z',
                    'expiration': '3600',
                    'headers': {
                        'topic_name': 'test.topic',
                        'ext_client_id': 'client_789',
                        'ext_pub_time_iso': '2025-01-01T11:59:00Z'
                    }
                }
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 1)
        message = result[0]

        self.assertEqual(message['data'], 'test message data')
        self.assertEqual(message['msg_id'], 'msg_123')
        self.assertEqual(message['correl_id'], 'corr_456')
        self.assertEqual(message['priority'], 5)
        self.assertEqual(message['mime_type'], 'text/plain')
        self.assertEqual(message['pub_time_iso'], '2025-01-01T12:00:00Z')
        self.assertEqual(message['recv_time_iso'], '2025-01-01T12:00:00Z')
        self.assertEqual(message['expiration'], '3600')
        self.assertEqual(message['topic_name'], 'test.topic')
        self.assertEqual(message['ext_client_id'], 'client_789')
        self.assertEqual(message['ext_pub_time_iso'], '2025-01-01T11:59:00Z')
        self.assertEqual(message['in_reply_to'], '')
        self.assertEqual(message['expiration_time_iso'], '')
        self.assertEqual(message['size'], len('test message data'.encode('utf-8')))

# ################################################################################################################################

    def test_transform_messages_handles_missing_properties(self):
        """ _transform_messages handles messages with missing properties gracefully.
        """
        rabbitmq_messages = [
            {
                'payload': 'minimal message',
                'properties': {}
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 1)
        message = result[0]

        self.assertEqual(message['data'], 'minimal message')
        self.assertEqual(message['msg_id'], '')
        self.assertEqual(message['correl_id'], '')
        self.assertEqual(message['priority'], PubSub.Message.Default_Priority)
        self.assertEqual(message['mime_type'], 'application/json')
        self.assertEqual(message['expiration'], PubSub.Message.Default_Expiration)

# ################################################################################################################################

    def test_transform_messages_handles_missing_headers(self):
        """ _transform_messages handles messages with missing headers gracefully.
        """
        rabbitmq_messages = [
            {
                'payload': 'message without headers',
                'properties': {
                    'message_id': 'msg_456'
                }
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 1)
        message = result[0]

        self.assertEqual(message['data'], 'message without headers')
        self.assertEqual(message['msg_id'], 'msg_456')
        self.assertEqual(message['topic_name'], '')
        self.assertEqual(message['ext_client_id'], '')
        self.assertEqual(message['ext_pub_time_iso'], '')

# ################################################################################################################################

    def test_transform_messages_calculates_size_for_string(self):
        """ _transform_messages calculates correct size for string payloads.
        """
        test_payload = 'test string message'
        rabbitmq_messages = [
            {
                'payload': test_payload,
                'properties': {}
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 1)
        message = result[0]

        self.assertEqual(message['data'], test_payload)
        self.assertEqual(message['size'], len(test_payload.encode('utf-8')))

# ################################################################################################################################

    def test_transform_messages_calculates_size_for_bytes(self):
        """ _transform_messages calculates correct size for byte payloads.
        """
        byte_payload = b'binary data'
        rabbitmq_messages = [
            {
                'payload': byte_payload,
                'properties': {}
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 1)
        message = result[0]

        self.assertEqual(message['data'], byte_payload)
        self.assertEqual(message['size'], len(byte_payload))

# ################################################################################################################################

    def test_transform_messages_handles_unicode_strings(self):
        """ _transform_messages handles unicode strings correctly.
        """
        unicode_payload = 'test message with unicode: 🚀 ñáéíóú'
        rabbitmq_messages = [
            {
                'payload': unicode_payload,
                'properties': {}
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 1)
        message = result[0]

        self.assertEqual(message['data'], unicode_payload)
        self.assertEqual(message['size'], len(unicode_payload.encode('utf-8')))

# ################################################################################################################################

    def test_transform_messages_handles_multiple_messages(self):
        """ _transform_messages handles multiple messages correctly.
        """
        rabbitmq_messages = [
            {
                'payload': 'first message',
                'properties': {'message_id': 'msg_1'}
            },
            {
                'payload': 'second message',
                'properties': {'message_id': 'msg_2'}
            },
            {
                'payload': 'third message',
                'properties': {'message_id': 'msg_3'}
            }
        ]

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]['data'], 'first message')
        self.assertEqual(result[0]['msg_id'], 'msg_1')

        self.assertEqual(result[1]['data'], 'second message')
        self.assertEqual(result[1]['msg_id'], 'msg_2')

        self.assertEqual(result[2]['data'], 'third message')
        self.assertEqual(result[2]['msg_id'], 'msg_3')

# ################################################################################################################################

    def test_transform_messages_handles_empty_list(self):
        """ _transform_messages handles empty message list.
        """
        rabbitmq_messages = []

        result = self.rest_server._transform_messages(rabbitmq_messages)

        self.assertEqual(result, [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
