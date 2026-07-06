# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import PubSub
from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManagerStub:
    """ Runs the real bridge delivery code of ConfigManager with everything around it mocked out.
    """

    # The real methods under test, bound to this stub
    get_pubsub_topic_by_amqp_channel = ConfigManager.get_pubsub_topic_by_amqp_channel
    pubsub_deliver_amqp_message = ConfigManager.pubsub_deliver_amqp_message

    def __init__(self) -> 'None':
        self.server = MagicMock()
        self._push_subs = {}
        self._topic_backends = {}

# ################################################################################################################################
# ################################################################################################################################

class TestBridgeChannelToTopicMapping(unittest.TestCase):

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        self.stub._topic_backends['topic.amqp'] = {
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': 'my.outconn',
            'amqp_exchange': 'my.exchange',
            'amqp_routing_key': 'topic.amqp',
            'amqp_channel_name': 'channel.1',
            'original_service_name': 'original.service',
        }

# ################################################################################################################################

    def test_channel_resolves_to_topic(self) -> 'None':
        out = self.stub.get_pubsub_topic_by_amqp_channel('channel.1')
        self.assertEqual(out, 'topic.amqp')

# ################################################################################################################################

    def test_unknown_channel_raises(self) -> 'None':
        with self.assertRaises(Exception) as ctx:
            _ = self.stub.get_pubsub_topic_by_amqp_channel('channel.unknown')

        self.assertIn('channel.unknown', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class TestBridgeDelivery(unittest.TestCase):

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        # One service push subscriber and one REST push subscriber of the same topic,
        # plus a service push subscriber of an unrelated topic.
        self.stub._push_subs = {
            'sk.service.1': [{
                'sub_key': 'sk.service.1',
                'topic_name': 'topic.amqp',
                'push_type': PubSub.Push_Type.Service,
                'push_service_name': 'my.push.service',
                'rest_push_endpoint_id': None,
            }],
            'sk.rest.1': [{
                'sub_key': 'sk.rest.1',
                'topic_name': 'topic.amqp',
                'push_type': PubSub.Push_Type.REST,
                'push_service_name': None,
                'rest_push_endpoint_id': 123,
                'rest_push_url': 'http://localhost:12345/push',
            }],
            'sk.other.topic': [{
                'sub_key': 'sk.other.topic',
                'topic_name': 'topic.other',
                'push_type': PubSub.Push_Type.Service,
                'push_service_name': 'other.push.service',
                'rest_push_endpoint_id': None,
            }],
        }

# ################################################################################################################################

    def test_delivers_to_service_push_subscribers(self) -> 'None':

        with patch('requests.post') as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            self.stub.pubsub_deliver_amqp_message('topic.amqp', 'message body', 'test-cid-001')

        # The push service got the body as-is ..
        self.stub.server.invoke.assert_called_once_with('my.push.service', 'message body')

        # .. and the unrelated topic's subscriber was not invoked.
        for call in self.stub.server.invoke.call_args_list:
            self.assertNotEqual(call[0][0], 'other.push.service')

# ################################################################################################################################

    def test_delivers_to_rest_push_subscribers(self) -> 'None':

        with patch('requests.post') as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            self.stub.pubsub_deliver_amqp_message('topic.amqp', 'message body', 'test-cid-001')

        mock_post.assert_called_once()

        call_args = mock_post.call_args

        self.assertEqual(call_args[0][0], 'http://localhost:12345/push')
        self.assertEqual(call_args[1]['data'], 'message body')

# ################################################################################################################################

    def test_dict_body_is_serialized_for_rest_push(self) -> 'None':

        body = {'order_id': 123, 'status': 'new'}

        with patch('requests.post') as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            self.stub.pubsub_deliver_amqp_message('topic.amqp', body, 'test-cid-001')

        call_args = mock_post.call_args

        self.assertEqual(call_args[1]['data'], '{"order_id": 123, "status": "new"}')

# ################################################################################################################################

    def test_rest_delivery_failure_propagates(self) -> 'None':
        """ A failed POST raises so the AMQP message is not acked and the broker redelivers it.
        """
        with patch('requests.post') as mock_post:
            mock_post.return_value.raise_for_status.side_effect = Exception('HTTP 500')

            with self.assertRaises(Exception):
                self.stub.pubsub_deliver_amqp_message('topic.amqp', 'message body', 'test-cid-001')

# ################################################################################################################################
# ################################################################################################################################

class TestBridgeService(unittest.TestCase):
    """ The OnAMQPMessage service resolves the topic from the channel name
    and hands the body over for delivery.
    """

    def test_handle_maps_channel_and_delivers(self) -> 'None':

        from zato.server.service.internal.pubsub.topic import OnAMQPMessage

        service = MagicMock()
        service.channel.name = 'channel.1'
        service.cid = 'test-cid-001'
        service.request.raw_request = 'inbound body'
        service.server.config_manager.get_pubsub_topic_by_amqp_channel.return_value = 'topic.amqp'

        OnAMQPMessage.handle(service)

        service.server.config_manager.get_pubsub_topic_by_amqp_channel.assert_called_once_with('channel.1')
        service.server.config_manager.pubsub_deliver_amqp_message.assert_called_once_with(
            'topic.amqp', 'inbound body', 'test-cid-001')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
