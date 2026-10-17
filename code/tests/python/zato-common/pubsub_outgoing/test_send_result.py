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
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.delivery import DeliveryExhausted
from zato.common.pubsub.dlq import get_dlq_topic_name, Header_Attempts, Header_Error, Header_Error_Class, Key_DLQ, move_to_dlq
from zato.common.pubsub.outgoing import Attempts_Direct, Attempts_None, conn_directions, conn_locators, delivery_handlers, \
    dlq_settings_readers, get_outgoing_sub_key, get_outgoing_topic_name, Key_Attempts, Key_CID, Key_Conn_ID, Key_Conn_Name, \
    Key_Conn_Type, Key_Data, Key_Method, Key_Request, OutgoingPublisher, register_outgoing_conn_type, retry_policy_builders, \
    SendRejected, SendResult
from zato.common.pubsub.sql.backend import PublishResult
from zato.common.util.retry import RetryPolicy
from zato.server.base.config_manager.outgoing_queues import OutgoingQueueDepth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

_conn_type = 'rest-test'
_conn_id = 17
_conn_name = 'Order Intake'

# The retries a connection has unless a test says otherwise
_max_retries = 2

_cid = 'test-cid-001'

_accepted_response = 'HTTP 200 accepted'

_rejected_response = 'HTTP 500 rejected'
_rejected_error = 'HTTP 500 Internal Server Error'

# What an endpoint that will never take this message answers with
_refused_response = 'HTTP 400 refused'
_refused_error = 'HTTP 400 Bad Request'

_timeout_error = 'Timeout error: the endpoint did not answer'

_queue_error = 'The database is not available'

_request = {
    Key_Method: 'POST',
    Key_Data: '{"order_id": 1234}',
}

# ################################################################################################################################
# ################################################################################################################################

class _Attempt:
    """ The direct attempt of a connection type.
    """

    def __init__(self, outcome:'str') -> 'None':
        self.outcome = outcome
        self.calls = 0

    def __call__(self) -> 'any_':
        self.calls += 1

        if self.outcome == 'accepted':
            return _accepted_response

        elif self.outcome == 'rejected':
            raise SendRejected(_rejected_error, _rejected_response)

        elif self.outcome == 'refused':
            raise SendRejected(_refused_error, _refused_response, is_permanent=True)

        else:
            raise Exception(_timeout_error)

# ################################################################################################################################
# ################################################################################################################################

class SendOrQueueTestCase(unittest.TestCase):
    """ Every combination of what the endpoint and the queue do comes back as a SendResult.
    """

    def setUp(self) -> 'None':

        self.server = MagicMock()
        self.depth = OutgoingQueueDepth()
        self.server.config_manager.outgoing_queue_depth = self.depth

        self.topic_name = get_outgoing_topic_name(_conn_type, _conn_name)
        self.server.config_manager.ensure_outgoing_subscription.return_value = (self.topic_name, _conn_name)

        self.server.config_manager.get_outgoing_publish_lock.return_value = threading.RLock()

        self.server.config_manager.get_pubsub_topic_backend.return_value = None

        # The backend stores each message under the id it is given
        def _publish(*args:'any_', **kwargs:'any_') -> 'PublishResult':
            out = PublishResult()
            out.msg_id = kwargs['msg_id']
            return out

        self.server.pubsub_backend.publish.side_effect = _publish

        # The connection's retries and its DLQ switch, as each test sets them
        self.max_retries = _max_retries
        self.use_dlq = False

        self._register_conn_type()

        # The DLQ the config manager moves a message to
        self.dlq_topic_name = get_dlq_topic_name(_conn_type, _conn_name)
        self.server.config_manager.ensure_outgoing_dlq.return_value = (self.dlq_topic_name, _conn_name)

        def _move_to_outgoing_dlq(cid:'str', envelope:'stranydict', exhausted:'DeliveryExhausted') -> 'str':
            out = move_to_dlq(self.server, cid, envelope, exhausted)
            return out

        self.server.config_manager.move_to_outgoing_dlq.side_effect = _move_to_outgoing_dlq

        self.publisher = OutgoingPublisher(self.server, _conn_type, _conn_id)
        self.sub_key = get_outgoing_sub_key(_conn_type, _conn_id)

# ################################################################################################################################

    def tearDown(self) -> 'None':

        for registry in (conn_locators, delivery_handlers, conn_directions, retry_policy_builders, dlq_settings_readers):
            _ = registry.pop(_conn_type, None)

# ################################################################################################################################

    def _register_conn_type(self) -> 'None':

        def locator(server:'any_', conn_id:'int') -> 'anytuple':
            out = (_conn_name, _conn_name)
            return out

        def handler(server:'any_', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
            pass

        def retry_policy(wrapper:'any_') -> 'RetryPolicy':
            config = {
                _retry.Field_Max_Retries: self.max_retries,
            }
            out = RetryPolicy.from_config(config, _retry)
            return out

        def dlq_settings(wrapper:'any_') -> 'stranydict':
            out = {
                HTTP_SOAP.DLQ.Field_Use_DLQ: self.use_dlq,
            }
            return out

        register_outgoing_conn_type(_conn_type, locator, handler, retry_policy=retry_policy, dlq_settings=dlq_settings)

# ################################################################################################################################

    def _get_published_envelope(self) -> 'stranydict':

        call_args = self.server.pubsub_backend.publish.call_args
        positional = call_args[0]
        envelope = positional[1]

        out = loads(envelope)
        return out

# ################################################################################################################################

    def _make_the_queue_raise(self) -> 'None':
        self.server.pubsub_backend.publish.side_effect = Exception(_queue_error)

# ################################################################################################################################

    def _assert_flags_are_consistent(self, result:'SendResult') -> 'None':
        """ Of the four flags, at most one is ever on.
        """
        self.assertIsInstance(result, SendResult)

        flags_on = [result.is_ok, result.is_in_queue, result.is_in_dlq, result.is_rejected].count(True)
        self.assertLessEqual(flags_on, 1)

# ################################################################################################################################

    def test_an_accepted_message_is_ok_and_not_queued(self) -> 'None':

        attempt = _Attempt('accepted')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertTrue(result.is_ok)
        self.assertFalse(result.is_in_queue)
        self.assertEqual(result.response, _accepted_response)
        self.assertEqual(result.error, '')
        self.assertEqual(result.msg_id, '')

        self.assertEqual(attempt.calls, 1)
        self.server.pubsub_backend.publish.assert_not_called()
        self.assertEqual(self.depth.get(self.sub_key), 0)

# ################################################################################################################################

    def _assert_msg_id_is_the_envelope_one(self, result:'SendResult') -> 'None':
        """ The id a result carries is the one stamped into the envelope that went to the queue.
        """
        call_args = self.server.pubsub_backend.publish.call_args
        envelope = loads(call_args[0][1])

        self.assertEqual(result.msg_id, envelope['msg_id'])
        self.assertEqual(call_args[1]['msg_id'], envelope['msg_id'])

# ################################################################################################################################

    def test_a_message_turned_down_for_now_goes_to_the_queue(self) -> 'None':

        attempt = _Attempt('rejected')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertTrue(result.is_in_queue)
        self.assertFalse(result.is_rejected)
        self._assert_msg_id_is_the_envelope_one(result)

        self.assertEqual(result.error, _rejected_error)
        self.assertEqual(result.response, _rejected_response)

        self.assertEqual(attempt.calls, 1)
        self.assertEqual(self.depth.get(self.sub_key), 1)

# ################################################################################################################################

    def test_a_message_turned_down_for_good_is_not_queued(self) -> 'None':
        """ The endpoint said the message itself is wrong, so the queue would only hand it
        the same answer again - the result says so and the answer travels with it.
        """
        attempt = _Attempt('refused')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertFalse(result.is_in_queue)
        self.assertTrue(result.is_rejected)

        self.assertEqual(result.error, _refused_error)
        self.assertEqual(result.response, _refused_response)
        self.assertEqual(result.msg_id, '')

        self.assertEqual(attempt.calls, 1)
        self.server.pubsub_backend.publish.assert_not_called()
        self.assertEqual(self.depth.get(self.sub_key), 0)

# ################################################################################################################################

    def test_a_message_turned_down_for_good_behind_others_waits_its_turn(self) -> 'None':
        """ With others already in the queue nothing touches the wire, so the endpoint's
        refusal is not known yet and the message waits like any other.
        """
        self.depth.raise_(self.sub_key)

        attempt = _Attempt('refused')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertTrue(result.is_in_queue)
        self.assertFalse(result.is_rejected)
        self.assertEqual(attempt.calls, 0)

# ################################################################################################################################

    def test_a_message_that_did_not_reach_the_endpoint_goes_to_the_queue(self) -> 'None':

        attempt = _Attempt('timeout')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertTrue(result.is_in_queue)
        self._assert_msg_id_is_the_envelope_one(result)

        self.assertEqual(result.error, _timeout_error)
        self.assertIsNone(result.response)

# ################################################################################################################################

    def test_the_envelope_of_a_direct_attempt_counts_one_attempt(self) -> 'None':

        attempt = _Attempt('rejected')
        _ = self.publisher.send_or_queue(_cid, _request, attempt)

        envelope = self._get_published_envelope()

        self.assertEqual(envelope[Key_Attempts], Attempts_Direct)
        self.assertEqual(envelope[Key_CID], _cid)
        self.assertEqual(envelope[Key_Conn_Type], _conn_type)
        self.assertEqual(envelope[Key_Conn_ID], _conn_id)
        self.assertEqual(envelope[Key_Conn_Name], _conn_name)
        self.assertEqual(envelope[Key_Request], _request)

# ################################################################################################################################

    def test_a_message_behind_others_does_not_touch_the_wire(self) -> 'None':
        """ Other messages wait in the queue already.
        """
        self.depth.raise_(self.sub_key)

        attempt = _Attempt('accepted')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertTrue(result.is_in_queue)
        self._assert_msg_id_is_the_envelope_one(result)
        self.assertEqual(result.error, '')

        self.assertEqual(attempt.calls, 0)

        envelope = self._get_published_envelope()
        self.assertEqual(envelope[Key_Attempts], Attempts_None)

        self.assertEqual(self.depth.get(self.sub_key), 2)

# ################################################################################################################################

    def test_a_queue_that_cannot_store_the_message_leaves_both_flags_off(self) -> 'None':

        self._make_the_queue_raise()

        attempt = _Attempt('rejected')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertFalse(result.is_in_queue)
        self.assertEqual(result.msg_id, '')

        self.assertEqual(result.error, _queue_error)

        self.assertEqual(self.depth.get(self.sub_key), 0)

# ################################################################################################################################

    def test_a_queue_that_cannot_store_a_message_behind_others_leaves_both_flags_off(self) -> 'None':

        self.depth.raise_(self.sub_key)
        self._make_the_queue_raise()

        attempt = _Attempt('accepted')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertFalse(result.is_in_queue)
        self.assertEqual(result.error, _queue_error)
        self.assertEqual(attempt.calls, 0)

        self.assertEqual(self.depth.get(self.sub_key), 1)

# ################################################################################################################################

    def test_a_message_with_no_retries_that_did_not_reach_the_endpoint_is_not_queued(self) -> 'None':

        self.max_retries = 0

        attempt = _Attempt('timeout')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertFalse(result.is_in_queue)
        self.assertFalse(result.is_in_dlq)
        self.assertEqual(result.msg_id, '')
        self.assertEqual(result.error, _timeout_error)

        self.assertEqual(attempt.calls, 1)
        self.server.pubsub_backend.publish.assert_not_called()
        self.assertEqual(self.depth.get(self.sub_key), 0)

# ################################################################################################################################

    def test_a_message_with_no_retries_turned_down_for_now_is_not_queued(self) -> 'None':

        self.max_retries = 0

        attempt = _Attempt('rejected')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_in_queue)
        self.assertFalse(result.is_in_dlq)
        self.assertEqual(result.error, _rejected_error)
        self.assertEqual(result.response, _rejected_response)

        self.server.pubsub_backend.publish.assert_not_called()
        self.assertEqual(self.depth.get(self.sub_key), 0)

# ################################################################################################################################

    def test_a_message_with_no_retries_moves_to_the_dlq_when_the_dlq_is_on(self) -> 'None':

        self.max_retries = 0
        self.use_dlq = True

        attempt = _Attempt('timeout')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_in_queue)
        self.assertTrue(result.is_in_dlq)
        self.assertEqual(result.error, _timeout_error)

        self.assertEqual(attempt.calls, 1)
        self.assertEqual(self.depth.get(self.sub_key), 0)

        call_args = self.server.pubsub_backend.publish.call_args
        positional = call_args[0]
        topic_name = positional[0]
        document = loads(positional[1])
        header = document[Key_DLQ]

        self.assertEqual(topic_name, self.dlq_topic_name)
        self.assertEqual(result.msg_id, call_args[1]['msg_id'])
        self.assertEqual(document[Key_Request], _request)
        self.assertEqual(header[Header_Attempts], Attempts_Direct)
        self.assertEqual(header[Header_Error], _timeout_error)
        self.assertEqual(header[Header_Error_Class], 'Exception')

# ################################################################################################################################

    def test_a_message_with_no_retries_behind_others_is_queued(self) -> 'None':
        """ Nothing touches the wire, so the queue makes the message's one attempt.
        """
        self.max_retries = 0
        self.depth.raise_(self.sub_key)

        attempt = _Attempt('timeout')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertTrue(result.is_in_queue)
        self.assertEqual(attempt.calls, 0)

        envelope = self._get_published_envelope()
        self.assertEqual(envelope[Key_Attempts], Attempts_None)

# ################################################################################################################################

    def test_nothing_raises(self) -> 'None':
        """ Nothing raises.
        """
        outcomes = ('accepted', 'rejected', 'refused', 'timeout')
        results:'anylist' = []

        for outcome in outcomes:
            for is_queue_empty in (True, False):
                for does_queue_raise in (False, True):

                    self.setUp()

                    if not is_queue_empty:
                        self.depth.raise_(self.sub_key)

                    if does_queue_raise:
                        self._make_the_queue_raise()

                    attempt = _Attempt(outcome)
                    result = self.publisher.send_or_queue(_cid, _request, attempt)

                    self._assert_flags_are_consistent(result)
                    results.append(result)

        self.assertEqual(len(results), 16)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingQueueDepthTestCase(unittest.TestCase):
    """ The count of what each queue holds.
    """

    def test_an_unknown_queue_is_empty(self) -> 'None':
        depth = OutgoingQueueDepth()
        self.assertEqual(depth.get('zato.out.rest.1'), 0)

# ################################################################################################################################

    def test_raising_and_lowering(self) -> 'None':
        depth = OutgoingQueueDepth()

        depth.raise_('zato.out.rest.1')
        depth.raise_('zato.out.rest.1')
        depth.raise_('zato.out.rest.2')

        self.assertEqual(depth.get('zato.out.rest.1'), 2)
        self.assertEqual(depth.get('zato.out.rest.2'), 1)

        depth.lower('zato.out.rest.1', 2)

        self.assertEqual(depth.get('zato.out.rest.1'), 0)
        self.assertEqual(depth.get('zato.out.rest.2'), 1)

# ################################################################################################################################

    def test_counts_read_at_startup(self) -> 'None':
        depth = OutgoingQueueDepth()
        depth.set_counts({'zato.out.rest.1': 2, 'zato.out.rest.3': 5})

        self.assertEqual(depth.get('zato.out.rest.1'), 2)
        self.assertEqual(depth.get('zato.out.rest.2'), 0)
        self.assertEqual(depth.get('zato.out.rest.3'), 5)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
