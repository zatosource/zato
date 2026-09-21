# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a send with the queue switch on comes back with, on every pub/sub backend.

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Attempts_Direct, Key_Attempts, Key_CID, Key_Conn_Name, Key_Conn_Type, Key_Request

# Test support
from queue_delivery.client import get_client, get_queue, read, send, wait_for_audit_events, wait_for_queue_depth, \
    wait_for_queue_empty
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_Orders, Conn_Plain

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def _assert_flags_are_consistent(result:'anydict') -> 'None':
    """ A send with the switch on always comes back with a result and never with both flags on.
    """
    assert result['raised'] == '', result
    assert result['is_send_result'] is True, result
    assert not (result['is_ok'] and result['is_in_queue']), result

# ################################################################################################################################
# ################################################################################################################################

class SendResultScenarios(ScenarioBase):

    def test_an_accepted_send_is_ok_and_nothing_is_stored(self) -> 'None':
        """ The endpoint accepts on the direct attempt.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        result = send(client, conn_name, {'order_id': 'ok-1'})

        _assert_flags_are_consistent(result)
        assert result['is_ok'] is True
        assert result['is_in_queue'] is False
        assert result['msg_id'] == ''
        assert result['error'] == ''
        assert result['response'] is not None

        requests = receiver.wait_for_requests(1)
        assert len(requests) == 1
        assert self.t.body_of(requests[0]) == {'order_id': 'ok-1'}

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 0
        assert queue['messages'] == []

# ################################################################################################################################

    def test_a_refused_send_goes_to_the_queue_and_arrives_later(self) -> 'None':
        """ The endpoint refuses the direct attempt.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_next(1)

        data = {'order_id': 'rejected-1'}
        result = send(client, conn_name, data)

        _assert_flags_are_consistent(result)
        assert result['is_ok'] is False
        assert result['is_in_queue'] is True
        assert result['msg_id'].startswith('zpsm')
        assert result['error'].startswith(self.t.refused_error_prefix), result['error']
        assert result['response'] is not None

        cid = result['cid']

        queue = get_queue(client, conn_name)

        if queue['messages']:
            envelope = queue['messages'][0]['envelope']

            assert queue['messages'][0]['msg_id'] == result['msg_id']
            assert envelope[Key_Conn_Type] == self.t.conn_type
            assert envelope[Key_Conn_Name] == conn_name
            assert envelope[Key_CID] == cid
            assert envelope[Key_Attempts] == Attempts_Direct

            self.t.check_envelope_request(envelope[Key_Request], data)

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1
        assert self.t.body_of(accepted[0]) == data

        assert receiver.acceptance() == [False, True]

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0
        assert queue['messages'] == []

# ################################################################################################################################

    def test_an_endpoint_that_is_down_gives_the_same(self) -> 'None':
        """ Nothing listens on the endpoint's port.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.stop()

        try:
            result = send(client, conn_name, {'order_id': 'down-1'})

            _assert_flags_are_consistent(result)
            assert result['is_ok'] is False
            assert result['is_in_queue'] is True
            assert result['msg_id'].startswith('zpsm')
            assert self.t.down_error_text in result['error'], result['error']
            assert result['response'] is None

            queue = get_queue(client, conn_name)

            if queue['messages']:
                envelope = queue['messages'][0]['envelope']
                assert envelope[Key_CID] == result['cid']
                assert envelope[Key_Attempts] == Attempts_Direct

        finally:
            receiver.start()

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1
        assert self.t.body_of(accepted[0]) == {'order_id': 'down-1'}

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_a_read_goes_to_the_wire_while_the_queue_holds_messages(self) -> 'None':
        """ A read is never a delivery.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        queued = send(client, conn_name, {'order_id': 'waiting-1'})
        assert queued['is_in_queue'] is True

        result = read(client, conn_name)

        assert result['is_send_result'] is False
        assert result['is_ok'] is False

        receiver.accept_all()

        result = read(client, conn_name)

        assert result['is_send_result'] is False
        assert result['is_ok'] is True

        assert len(receiver.reads()) == 2

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_the_switch_off_behaves_as_it_always_did(self) -> 'None':
        """ The same endpoints make a connection with the switch off answer with the response, or raise.
        """
        client = get_client()
        receiver = self.receiver(Conn_Plain)
        conn_name = self.conn(Conn_Plain)

        receiver.refuse_next(1)

        result = send(client, conn_name, {'order_id': 'plain-1'})

        assert result['raised'] == ''
        assert result['is_send_result'] is False
        assert result['is_ok'] is False

        receiver.stop()

        try:
            result = send(client, conn_name, {'order_id': 'plain-2'})
        finally:
            receiver.start()

        assert result['raised'] != ''
        assert self.t.down_error_text in result['error'], result['error']

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 0
        assert queue['messages'] == []

# ################################################################################################################################

    def test_every_attempt_from_the_queue_is_in_the_audit_log_under_the_callers_cid(self) -> 'None':
        """ The connection records the direct attempt and each one from the queue under the sending service's cid.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_next(2)

        result = send(client, conn_name, {'order_id': 'audit-1'})
        assert result['is_in_queue'] is True

        cid = result['cid']

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1

        assert receiver.acceptance() == [False, False, True]

        sent_events = wait_for_audit_events(cid, AuditEvent.Request_Sent, 3)
        assert len(sent_events) == 3

        for event in sent_events:
            assert event['cid'] == cid
            assert event['object_name'] == conn_name

        received_events = wait_for_audit_events(cid, AuditEvent.Response_Received, 3)
        assert len(received_events) == 3

        for event in received_events:
            assert event['cid'] == cid
            assert event['object_name'] == conn_name

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################
# ################################################################################################################################
