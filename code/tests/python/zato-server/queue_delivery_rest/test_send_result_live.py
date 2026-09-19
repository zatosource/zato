# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a send with the queue switch on comes back with, on every pub/sub backend.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK
from json import loads

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Attempts_Direct, Key_Attempts, Key_CID, Key_Conn_Name, Key_Conn_Type, Key_Data, \
    Key_Headers, Key_Method, Key_Params, Key_Request, OutgoingType

# Test support
from _helpers import Connections, get_client, get_queue, get_receiver, read, send, wait_for_audit_events, \
    wait_for_queue_depth, wait_for_queue_empty

# ################################################################################################################################
# ################################################################################################################################

_queue_conn = Connections['orders']
_plain_conn = Connections['plain']

# The receiver records header names in lower case
_test_header = 'X-Test-Source'
_test_header_value = 'billing'
_recorded_test_header = _test_header.lower()
_recorded_cid_header = 'x-zato-cid'

# ################################################################################################################################
# ################################################################################################################################

def _assert_flags_are_consistent(result:'dict') -> 'None':
    """ A send with the switch on always comes back with a result and never with both flags on.
    """
    assert result['raised'] == '', result
    assert result['is_send_result'] is True, result
    assert not (result['is_ok'] and result['is_in_queue']), result

# ################################################################################################################################
# ################################################################################################################################

def test_an_accepted_send_is_ok_and_nothing_is_stored() -> 'None':
    """ The endpoint accepts on the direct attempt.
    """
    client = get_client()
    receiver = get_receiver('orders')

    result = send(client, _queue_conn, {'order_id': 'ok-1'})

    _assert_flags_are_consistent(result)
    assert result['is_ok'] is True
    assert result['is_in_queue'] is False
    assert result['msg_id'] == ''
    assert result['error'] == ''
    assert result['response']['status_code'] == OK

    requests = receiver.wait_for_requests(1)
    assert len(requests) == 1
    assert loads(requests[0].body) == {'order_id': 'ok-1'}

    queue = get_queue(client, _queue_conn)
    assert queue['depth'] == 0
    assert queue['messages'] == []

# ################################################################################################################################

def test_a_rejected_send_goes_to_the_queue_and_arrives_later() -> 'None':
    """ The endpoint answers 500.
    """
    client = get_client()
    receiver = get_receiver('orders')

    receiver.answer_next([INTERNAL_SERVER_ERROR])

    headers = {_test_header: _test_header_value}
    result = send(client, _queue_conn, {'order_id': 'rejected-1'}, headers)

    _assert_flags_are_consistent(result)
    assert result['is_ok'] is False
    assert result['is_in_queue'] is True
    assert result['msg_id'].startswith('zpsm')
    assert result['error'].startswith(f'HTTP {INTERNAL_SERVER_ERROR}')
    assert result['response']['status_code'] == INTERNAL_SERVER_ERROR

    cid = result['cid']

    queue = get_queue(client, _queue_conn)

    if queue['messages']:
        envelope = queue['messages'][0]['envelope']

        assert queue['messages'][0]['msg_id'] == result['msg_id']
        assert envelope[Key_Conn_Type] == OutgoingType.REST
        assert envelope[Key_Conn_Name] == _queue_conn
        assert envelope[Key_CID] == cid
        assert envelope[Key_Attempts] == Attempts_Direct

        request = envelope[Key_Request]
        assert request[Key_Method] == 'POST'
        assert loads(request[Key_Data]) == {'order_id': 'rejected-1'}
        assert request[Key_Headers] == headers
        assert request[Key_Params] == {}

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1
    assert loads(accepted[0].body) == {'order_id': 'rejected-1'}
    assert accepted[0].headers[_recorded_test_header] == _test_header_value
    assert accepted[0].headers[_recorded_cid_header] == cid

    statuses = [request.status_code for request in receiver.requests]
    assert statuses == [INTERNAL_SERVER_ERROR, OK]

    queue = wait_for_queue_empty(client, _queue_conn)
    assert queue['depth'] == 0
    assert queue['messages'] == []

# ################################################################################################################################

def test_an_endpoint_that_is_down_gives_the_same() -> 'None':
    """ Nothing listens on the endpoint's port.
    """
    client = get_client()
    receiver = get_receiver('orders')

    receiver.stop()

    try:
        result = send(client, _queue_conn, {'order_id': 'down-1'})

        _assert_flags_are_consistent(result)
        assert result['is_ok'] is False
        assert result['is_in_queue'] is True
        assert result['msg_id'].startswith('zpsm')
        assert 'Connection error' in result['error']
        assert result['response'] is None

        queue = get_queue(client, _queue_conn)

        if queue['messages']:
            envelope = queue['messages'][0]['envelope']
            assert envelope[Key_CID] == result['cid']
            assert envelope[Key_Attempts] == Attempts_Direct

    finally:
        receiver.start()

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1
    assert loads(accepted[0].body) == {'order_id': 'down-1'}

    queue = wait_for_queue_depth(client, _queue_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_a_read_goes_to_the_wire_while_the_queue_holds_messages() -> 'None':
    """ A GET is never a delivery.
    """
    client = get_client()
    receiver = get_receiver('orders')

    receiver.refuse_all()

    queued = send(client, _queue_conn, {'order_id': 'waiting-1'})
    assert queued['is_in_queue'] is True

    result = read(client, _queue_conn)

    assert result['is_send_result'] is False
    assert result['is_ok'] is False
    assert result['response']['status_code'] != OK

    receiver.accept_all()

    result = read(client, _queue_conn)

    assert result['is_send_result'] is False
    assert result['is_ok'] is True
    assert result['response']['status_code'] == OK

    methods = [request.method for request in receiver.requests]
    assert methods.count('GET') == 2

    queue = wait_for_queue_depth(client, _queue_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_behaves_as_it_always_did() -> 'None':
    """ The same endpoints make a connection with the switch off answer with the response, or raise.
    """
    client = get_client()
    receiver = get_receiver('plain')

    receiver.answer_next([INTERNAL_SERVER_ERROR])

    result = send(client, _plain_conn, {'order_id': 'plain-1'})

    assert result['raised'] == ''
    assert result['is_send_result'] is False
    assert result['is_ok'] is False
    assert result['response']['status_code'] == INTERNAL_SERVER_ERROR

    receiver.stop()

    try:
        result = send(client, _plain_conn, {'order_id': 'plain-2'})
    finally:
        receiver.start()

    assert result['raised'] != ''
    assert 'Connection error' in result['error']

    queue = get_queue(client, _plain_conn)
    assert queue['depth'] == 0
    assert queue['messages'] == []

# ################################################################################################################################

def test_every_attempt_from_the_queue_is_in_the_audit_log_under_the_callers_cid() -> 'None':
    """ The connection records the direct attempt under the sending service's cid.
    """
    client = get_client()
    receiver = get_receiver('orders')

    receiver.answer_next([INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR])

    result = send(client, _queue_conn, {'order_id': 'audit-1'})
    assert result['is_in_queue'] is True

    cid = result['cid']

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1

    statuses = [request.status_code for request in receiver.requests]
    assert statuses == [INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK]

    sent_events = wait_for_audit_events(cid, AuditEvent.Request_Sent, 3)
    assert len(sent_events) == 3

    for event in sent_events:
        assert event['cid'] == cid
        assert event['object_name'] == _queue_conn

    received_events = wait_for_audit_events(cid, AuditEvent.Response_Received, 3)
    assert len(received_events) == 3

    received_statuses = [event['status'].split(' ')[0] for event in received_events]
    assert received_statuses == [str(INTERNAL_SERVER_ERROR), str(INTERNAL_SERVER_ERROR), str(OK)]

    queue = wait_for_queue_depth(client, _queue_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################
# ################################################################################################################################
