# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import unittest
from json import loads
from unittest.mock import MagicMock

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.outgoing import delivery_handlers, deliver_envelope, get_outgoing_sub_config, \
    get_outgoing_sub_key, get_outgoing_topic_name, OutgoingPublisher, parse_outgoing_sub_key, register_delivery_handler
from zato.common.pubsub.sql.backend import PublishResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# The connection types these tests register handlers for - names of things that could be published
# to, none of which is a type the product itself registers.
_type_ftp = 'ftp-test'
_type_smb = 'smb-test'

# The connection name most of the assertions use.
_conn_name = 'Order Intake'

# ################################################################################################################################
# ################################################################################################################################

class OutgoingNamingTestCase(unittest.TestCase):
    """ The topic and the sub key one outgoing connection is known by.
    """

    def test_topic_name_is_built_from_type_and_name(self) -> 'None':
        out = get_outgoing_topic_name('rest', 'orders')
        self.assertEqual(out, 'zato.out.to.rest.orders')

# ################################################################################################################################

    def test_topic_name_is_lowercased(self) -> 'None':
        out = get_outgoing_topic_name('rest', _conn_name)
        self.assertEqual(out, 'zato.out.to.rest.order intake')

# ################################################################################################################################

    def test_topic_name_is_under_the_outgoing_prefix(self) -> 'None':
        out = get_outgoing_topic_name('rest', 'orders')
        self.assertTrue(out.startswith(PubSub.Outgoing.Topic_Prefix))

# ################################################################################################################################

    def test_sub_key_preserves_connection_name_case(self) -> 'None':
        out = get_outgoing_sub_key('rest', _conn_name)
        self.assertEqual(out, 'zato.out.rest.Order Intake')

# ################################################################################################################################

    def test_sub_key_round_trips_through_parse(self) -> 'None':
        sub_key = get_outgoing_sub_key('rest', _conn_name)
        conn_type, conn_name = parse_outgoing_sub_key(sub_key)

        self.assertEqual(conn_type, 'rest')
        self.assertEqual(conn_name, _conn_name)

# ################################################################################################################################

    def test_sub_key_round_trips_with_dots_in_the_connection_name(self) -> 'None':
        """ A connection named after a host keeps every one of its dots on the way back.
        """
        conn_name = 'crm.example.com api'
        sub_key = get_outgoing_sub_key('rest', conn_name)

        conn_type, parsed_name = parse_outgoing_sub_key(sub_key)

        self.assertEqual(conn_type, 'rest')
        self.assertEqual(parsed_name, conn_name)

# ################################################################################################################################

    def test_topic_name_too_long_is_rejected(self) -> 'None':
        """ A connection whose name pushes the topic past what a topic name may be is not publishable to.
        """
        conn_name = 'c' * (PubSub.Topic.Name_Max_Len + 1)

        with self.assertRaises(ValueError):
            _ = get_outgoing_topic_name('rest', conn_name)

# ################################################################################################################################

    def test_sub_config_points_at_the_delivery_service(self) -> 'None':
        """ Every outgoing connection is subscribed by the one delivery service, as a push subscription.
        """
        topic_name = get_outgoing_topic_name('rest', _conn_name)
        sub_key = get_outgoing_sub_key('rest', _conn_name)

        out = get_outgoing_sub_config(sub_key, topic_name)

        self.assertEqual(out['sub_key'], sub_key)
        self.assertEqual(out['topic_name'], topic_name)
        self.assertEqual(out['push_type'], PubSub.Push_Type.Service)
        self.assertEqual(out['push_service_name'], PubSub.Outgoing.Delivery_Service)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingRegistryTestCase(unittest.TestCase):
    """ Which handler a published message is given to.
    """

    def setUp(self) -> 'None':
        self.server = MagicMock()
        self.received:'anylist' = []

        for conn_type in (_type_ftp, _type_smb):
            _ = delivery_handlers.pop(conn_type, None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        for conn_type in (_type_ftp, _type_smb):
            _ = delivery_handlers.pop(conn_type, None)

# ################################################################################################################################

    def _register(self, conn_type:'str') -> 'None':

        received = self.received

        def handler(server:'any_', cid:'str', conn_name:'str', data:'str') -> 'None':
            received.append((conn_type, conn_name, data))

        register_delivery_handler(conn_type, handler)

# ################################################################################################################################

    def test_envelope_reaches_the_handler_of_its_type(self) -> 'None':

        self._register(_type_ftp)

        envelope = {'conn_type': _type_ftp, 'conn_name': _conn_name, 'data': 'Order 1234'}
        deliver_envelope(self.server, 'test-cid', envelope)

        self.assertEqual(self.received, [(_type_ftp, _conn_name, 'Order 1234')])

# ################################################################################################################################

    def test_unregistered_conn_type_raises(self) -> 'None':

        envelope = {'conn_type': _type_ftp, 'conn_name': _conn_name, 'data': 'Order 1234'}

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn(_type_ftp, str(context.exception))

# ################################################################################################################################

    def test_registering_a_second_conn_type_does_not_disturb_the_first(self) -> 'None':

        self._register(_type_ftp)
        self._register(_type_smb)

        first = {'conn_type': _type_ftp, 'conn_name': _conn_name, 'data': 'Order 1234'}
        second = {'conn_type': _type_smb, 'conn_name': 'Archive', 'data': 'Order 5678'}

        deliver_envelope(self.server, 'test-cid', first)
        deliver_envelope(self.server, 'test-cid', second)

        expected = [
            (_type_ftp, _conn_name, 'Order 1234'),
            (_type_smb, 'Archive', 'Order 5678'),
        ]

        self.assertEqual(self.received, expected)

# ################################################################################################################################

    def test_a_handler_error_is_not_swallowed(self) -> 'None':
        """ What a handler raises is what reaches the delivery loop, which is what makes it retry.
        """

        def handler(server:'any_', cid:'str', conn_name:'str', data:'str') -> 'None':
            raise Exception('The connection refused the message')

        register_delivery_handler(_type_ftp, handler)

        envelope = {'conn_type': _type_ftp, 'conn_name': _conn_name, 'data': 'Order 1234'}

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn('The connection refused the message', str(context.exception))

# ################################################################################################################################
# ################################################################################################################################

class OutgoingPublisherTestCase(unittest.TestCase):
    """ What one publication to an outgoing connection turns into.
    """

    def setUp(self) -> 'None':

        self.server = MagicMock()
        self.server.config_manager._outgoing_sub_key_cache = set()
        self.server.config_manager._outgoing_sub_key_lock = threading.RLock()
        self.server.config_manager._push_subs = {}

        # The topic is what the config manager hands back to a publisher ..
        self.topic_name = get_outgoing_topic_name('rest', _conn_name)
        self.server.config_manager.ensure_outgoing_subscription.return_value = self.topic_name

        # .. and this is what the backend answers each publication with.
        publish_result = PublishResult()
        publish_result.msg_id = 'test-message-id-001'
        self.server.pubsub_backend.publish.return_value = publish_result

        self.publisher = OutgoingPublisher(self.server, 'rest', _conn_name)

# ################################################################################################################################

    def _get_published_envelope(self) -> 'any_':

        call_args = self.server.pubsub_backend.publish.call_args
        positional = call_args[0]
        envelope = positional[1]

        out = loads(envelope)
        return out

# ################################################################################################################################

    def test_publish_ensures_the_subscription_first(self) -> 'None':

        _ = self.publisher.publish('Order 1234')

        self.server.config_manager.ensure_outgoing_subscription.assert_called_once_with('rest', _conn_name)

# ################################################################################################################################

    def test_publish_goes_to_the_connection_topic(self) -> 'None':

        _ = self.publisher.publish('Order 1234')

        call_args = self.server.pubsub_backend.publish.call_args
        positional = call_args[0]

        self.assertEqual(positional[0], self.topic_name)

# ################################################################################################################################

    def test_envelope_names_the_connection_it_is_for(self) -> 'None':

        _ = self.publisher.publish('Order 1234')

        envelope = self._get_published_envelope()

        self.assertEqual(envelope['conn_type'], 'rest')
        self.assertEqual(envelope['conn_name'], _conn_name)
        self.assertEqual(envelope['data'], 'Order 1234')

# ################################################################################################################################

    def test_data_that_is_not_text_is_serialized(self) -> 'None':
        """ A document published as a dict reaches the handler as the JSON that document is.
        """
        _ = self.publisher.publish({'order_id': 1234, 'customer': 'Maria Kowalska'})

        envelope = self._get_published_envelope()
        data = loads(envelope['data'])

        self.assertEqual(data['order_id'], 1234)
        self.assertEqual(data['customer'], 'Maria Kowalska')

# ################################################################################################################################

    def test_publish_returns_what_the_backend_answered(self) -> 'None':

        out = self.publisher.publish('Order 1234')
        self.assertEqual(out.msg_id, 'test-message-id-001')

# ################################################################################################################################

    def test_publish_options_reach_the_backend(self) -> 'None':
        """ Expiration, priority and everything else a publication may carry go through untouched.
        """
        _ = self.publisher.publish('Order 1234', priority=7, expiration=60)

        call_args = self.server.pubsub_backend.publish.call_args
        keyword = call_args[1]

        self.assertEqual(keyword['priority'], 7)
        self.assertEqual(keyword['expiration'], 60)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
