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
from zato.common.pubsub.outgoing import conn_locators, delivery_handlers, deliver_envelope, find_outgoing_conn, \
    get_outgoing_sub_config, get_outgoing_sub_key, get_outgoing_topic_name, locate_outgoing_conn, OutgoingPublisher, \
    parse_outgoing_sub_key, register_outgoing_conn_type
from zato.common.pubsub.sql.backend import PublishResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The connection types these tests register handlers for - names of things that could be published
# to, none of which is a type the product itself registers.
_type_ftp = 'ftp-test'
_type_smb = 'smb-test'

# The connection most of the assertions use - the id it keeps for as long as it exists
# and the name it goes by.
_conn_id = 17
_conn_name = 'Order Intake'

# The name that same connection goes by after it has been renamed.
_conn_name_renamed = 'Order Intake EU'

# The id of the second connection, the one the registry tests deliver to as well.
_other_conn_id = 23

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

    def test_sub_key_is_built_from_the_connection_id(self) -> 'None':
        """ The queue is named after what a rename leaves alone, which is the connection's id.
        """
        out = get_outgoing_sub_key('rest', _conn_id)
        self.assertEqual(out, 'zato.out.rest.17')

# ################################################################################################################################

    def test_sub_key_does_not_change_when_the_connection_is_renamed(self) -> 'None':
        before = get_outgoing_sub_key('rest', _conn_id)
        after = get_outgoing_sub_key('rest', _conn_id)

        self.assertEqual(before, after)

# ################################################################################################################################

    def test_sub_key_round_trips_through_parse(self) -> 'None':
        sub_key = get_outgoing_sub_key('rest', _conn_id)
        conn_type, conn_id = parse_outgoing_sub_key(sub_key)

        self.assertEqual(conn_type, 'rest')
        self.assertEqual(conn_id, _conn_id)

# ################################################################################################################################

    def test_parsed_connection_id_is_a_number(self) -> 'None':
        """ It is what a connection is looked up by, so it comes back as what it was published under.
        """
        sub_key = get_outgoing_sub_key('rest', _conn_id)
        _, conn_id = parse_outgoing_sub_key(sub_key)

        self.assertIsInstance(conn_id, int)

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
        sub_key = get_outgoing_sub_key('rest', _conn_id)

        out = get_outgoing_sub_config(sub_key, topic_name)

        self.assertEqual(out['sub_key'], sub_key)
        self.assertEqual(out['topic_name'], topic_name)
        self.assertEqual(out['push_type'], PubSub.Push_Type.Service)
        self.assertEqual(out['push_service_name'], PubSub.Outgoing.Delivery_Service)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingRegistryTestCase(unittest.TestCase):
    """ Which connection a published message is given to, and through which handler.
    """

    def setUp(self) -> 'None':
        self.server = MagicMock()
        self.received:'anylist' = []

        # The connections these tests deliver to, by the id each of them is published to under
        self.connections = {
            _conn_id: _conn_name,
            _other_conn_id: 'Archive',
        }

        self._forget_test_types()

# ################################################################################################################################

    def tearDown(self) -> 'None':
        self._forget_test_types()

# ################################################################################################################################

    def _forget_test_types(self) -> 'None':

        for conn_type in (_type_ftp, _type_smb):
            _ = delivery_handlers.pop(conn_type, None)
            _ = conn_locators.pop(conn_type, None)

# ################################################################################################################################

    def _register(self, conn_type:'str') -> 'None':

        received = self.received
        connections = self.connections

        def locator(server:'any_', conn_id:'int') -> 'anytuple':

            conn_name = connections.get(conn_id)

            if not conn_name:
                return ()

            # The wrapper a locator answers with is whatever the handler needs, here the name itself
            out = (conn_name, conn_name)
            return out

        def handler(server:'any_', cid:'str', wrapper:'any_', data:'str') -> 'None':
            received.append((conn_type, wrapper, data))

        register_outgoing_conn_type(conn_type, locator, handler)

# ################################################################################################################################

    def test_envelope_reaches_the_handler_of_its_type(self) -> 'None':

        self._register(_type_ftp)

        envelope = {'conn_type': _type_ftp, 'conn_id': _conn_id, 'conn_name': _conn_name, 'data': 'Order 1234'}
        deliver_envelope(self.server, 'test-cid', envelope)

        self.assertEqual(self.received, [(_type_ftp, _conn_name, 'Order 1234')])

# ################################################################################################################################

    def test_a_renamed_connection_still_receives_the_message(self) -> 'None':
        """ The envelope carries the name from before the rename and the id, and it is the id that decides.
        """
        self._register(_type_ftp)
        self.connections[_conn_id] = _conn_name_renamed

        envelope = {'conn_type': _type_ftp, 'conn_id': _conn_id, 'conn_name': _conn_name, 'data': 'Order 1234'}
        deliver_envelope(self.server, 'test-cid', envelope)

        self.assertEqual(self.received, [(_type_ftp, _conn_name_renamed, 'Order 1234')])

# ################################################################################################################################

    def test_a_connection_that_is_gone_raises(self) -> 'None':
        """ What is raised names the connection, so a log line says which one it was.
        """
        self._register(_type_ftp)
        del self.connections[_conn_id]

        envelope = {'conn_type': _type_ftp, 'conn_id': _conn_id, 'conn_name': _conn_name, 'data': 'Order 1234'}

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn(str(_conn_id), str(context.exception))
        self.assertIn(_conn_name, str(context.exception))

# ################################################################################################################################

    def test_find_answers_with_nothing_for_a_connection_that_is_gone(self) -> 'None':
        """ This is what a server starting up uses, where a connection deleted meanwhile is not an error.
        """
        self._register(_type_ftp)
        del self.connections[_conn_id]

        out = find_outgoing_conn(self.server, _type_ftp, _conn_id)
        self.assertFalse(out)

# ################################################################################################################################

    def test_locate_answers_with_the_current_name(self) -> 'None':

        self._register(_type_ftp)
        self.connections[_conn_id] = _conn_name_renamed

        conn_name, _ = locate_outgoing_conn(self.server, _type_ftp, _conn_id)
        self.assertEqual(conn_name, _conn_name_renamed)

# ################################################################################################################################

    def test_unregistered_conn_type_raises(self) -> 'None':

        envelope = {'conn_type': _type_ftp, 'conn_id': _conn_id, 'conn_name': _conn_name, 'data': 'Order 1234'}

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn(_type_ftp, str(context.exception))

# ################################################################################################################################

    def test_registering_a_second_conn_type_does_not_disturb_the_first(self) -> 'None':

        self._register(_type_ftp)
        self._register(_type_smb)

        first = {'conn_type': _type_ftp, 'conn_id': _conn_id, 'conn_name': _conn_name, 'data': 'Order 1234'}
        second = {'conn_type': _type_smb, 'conn_id': _other_conn_id, 'conn_name': 'Archive', 'data': 'Order 5678'}

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

        def locator(server:'any_', conn_id:'int') -> 'anytuple':
            out = (_conn_name, _conn_name)
            return out

        def handler(server:'any_', cid:'str', wrapper:'any_', data:'str') -> 'None':
            raise Exception('The connection refused the message')

        register_outgoing_conn_type(_type_ftp, locator, handler)

        envelope = {'conn_type': _type_ftp, 'conn_id': _conn_id, 'conn_name': _conn_name, 'data': 'Order 1234'}

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
        self.server.config_manager._outgoing_conn_locks = {}
        self.server.config_manager._push_subs = {}

        # The topic and the connection's current name are what the config manager hands back ..
        self.topic_name = get_outgoing_topic_name('rest', _conn_name)
        self.server.config_manager.ensure_outgoing_subscription.return_value = (self.topic_name, _conn_name)

        # .. the publication takes the connection's own lock while it runs ..
        self.lock = threading.RLock()
        self.server.config_manager.get_outgoing_publish_lock.return_value = self.lock

        # .. and this is what the backend answers each publication with.
        publish_result = PublishResult()
        publish_result.msg_id = 'test-message-id-001'
        self.server.pubsub_backend.publish.return_value = publish_result

        self.publisher = OutgoingPublisher(self.server, 'rest', _conn_id)

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

        self.server.config_manager.ensure_outgoing_subscription.assert_called_once_with('rest', _conn_id)

# ################################################################################################################################

    def test_publish_takes_the_connection_lock(self) -> 'None':
        """ It is held for as long as the publication runs, which is what a rename waits for.
        """
        _ = self.publisher.publish('Order 1234')

        self.server.config_manager.get_outgoing_publish_lock.assert_called_once_with('rest', _conn_id)

# ################################################################################################################################

    def test_publish_goes_to_the_connection_topic(self) -> 'None':

        _ = self.publisher.publish('Order 1234')

        call_args = self.server.pubsub_backend.publish.call_args
        positional = call_args[0]

        self.assertEqual(positional[0], self.topic_name)

# ################################################################################################################################

    def test_publish_goes_to_the_topic_of_the_current_name(self) -> 'None':
        """ A connection renamed since the publisher was built is published to under its new topic.
        """
        renamed_topic = get_outgoing_topic_name('rest', _conn_name_renamed)
        self.server.config_manager.ensure_outgoing_subscription.return_value = (renamed_topic, _conn_name_renamed)

        _ = self.publisher.publish('Order 1234')

        call_args = self.server.pubsub_backend.publish.call_args
        positional = call_args[0]

        self.assertEqual(positional[0], renamed_topic)

# ################################################################################################################################

    def test_envelope_carries_the_connection_id(self) -> 'None':
        """ The id is what the message is delivered by, because a rename does not touch it.
        """
        _ = self.publisher.publish('Order 1234')

        envelope = self._get_published_envelope()

        self.assertEqual(envelope['conn_type'], 'rest')
        self.assertEqual(envelope['conn_id'], _conn_id)
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
