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
from zato.common.pubsub.outgoing import Attempts_Direct, Attempts_None, get_outgoing_sub_key, get_outgoing_topic_name, \
    Key_Attempts, Key_CID, Key_Conn_ID, Key_Conn_Name, Key_Conn_Type, Key_Data, Key_Method, Key_Request, OutgoingPublisher, \
    SendRejected, SendResult
from zato.common.pubsub.sql.backend import PublishResult
from zato.server.base.config_manager.outgoing_queues import OutgoingQueueDepth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_conn_type = 'rest'
_conn_id = 17
_conn_name = 'Order Intake'

_cid = 'test-cid-001'

_accepted_response = 'HTTP 200 accepted'

_rejected_response = 'HTTP 500 rejected'
_rejected_error = 'HTTP 500 Internal Server Error'

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

        self.publisher = OutgoingPublisher(self.server, _conn_type, _conn_id)
        self.sub_key = get_outgoing_sub_key(_conn_type, _conn_id)

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
        """ The two flags are never both on.
        """
        self.assertIsInstance(result, SendResult)
        self.assertFalse(result.is_ok and result.is_in_queue)

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

    def test_a_rejected_message_goes_to_the_queue(self) -> 'None':

        attempt = _Attempt('rejected')
        result = self.publisher.send_or_queue(_cid, _request, attempt)

        self._assert_flags_are_consistent(result)
        self.assertFalse(result.is_ok)
        self.assertTrue(result.is_in_queue)
        self._assert_msg_id_is_the_envelope_one(result)

        self.assertEqual(result.error, _rejected_error)
        self.assertEqual(result.response, _rejected_response)

        self.assertEqual(attempt.calls, 1)
        self.assertEqual(self.depth.get(self.sub_key), 1)

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

    def test_nothing_raises(self) -> 'None':
        """ Nothing raises.
        """
        outcomes = ('accepted', 'rejected', 'timeout')
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

        self.assertEqual(len(results), 12)

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
