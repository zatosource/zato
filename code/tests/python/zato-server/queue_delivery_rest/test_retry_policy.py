# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue retries as the connection's retry fields say, on every pub/sub backend.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK, UNAUTHORIZED

# Zato
from zato.common.api import HTTP_SOAP, PubSub

# Test support
from _helpers import Connections, edit_connection, get_client, get_connection, get_receiver, send, wait_for_queue_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import intlist
    from _receiver import RecordingReceiver

    floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

_orders_conn = Connections['orders']
_no_retries_conn = Connections['no_retries']

# As the template declares them
_orders_max_retries = 2
_orders_sleep_time = 1
_orders_backoff_threshold = 10
_orders_backoff_multiplier = 1

_round_wait = PubSub.Outgoing.Retry_Round_Wait

# Scheduling slack of a measured wait
_slack = 0.2

# ################################################################################################################################
# ################################################################################################################################

def _get_gaps(receiver:'RecordingReceiver') -> 'floatlist':
    """ How long passed between each request and the one before it, in the order the endpoint saw them.
    """
    out = []
    requests = receiver.requests

    for index in range(1, len(requests)):
        gap = requests[index].received_at - requests[index - 1].received_at
        out.append(gap)

    return out

# ################################################################################################################################

def _get_statuses(receiver:'RecordingReceiver') -> 'intlist':
    """ The statuses the endpoint answered with, in the order the attempts arrived.
    """
    out = [request.status_code for request in receiver.requests]
    return out

# ################################################################################################################################

def _restore_orders(client:'AdminClient') -> 'None':
    """ Puts the orders connection's retry fields back to what the template gave it.
    """
    _ = edit_connection(client, _orders_conn, {
        _retry.Field_Max_Retries: _orders_max_retries,
        _retry.Field_Sleep_Time: _orders_sleep_time,
        _retry.Field_Backoff_Threshold: _orders_backoff_threshold,
        _retry.Field_Backoff_Multiplier: _orders_backoff_multiplier,
    })

# ################################################################################################################################
# ################################################################################################################################

def test_the_attempts_run_out_and_the_message_arrives_in_the_next_round() -> 'None':
    """ Two retries and an endpoint that turns down three attempts.
    """
    client = get_client()
    receiver = get_receiver('orders')

    receiver.answer_next([INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK])

    result = send(client, _orders_conn, {'order_id': 'three-then-ok'})
    assert result['is_in_queue'] is True

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1

    statuses = _get_statuses(receiver)
    assert statuses == [INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK]

    gaps = _get_gaps(receiver)

    assert gaps[0] >= _orders_sleep_time - _slack, gaps
    assert gaps[0] < _round_wait, gaps

    assert gaps[1] >= _orders_sleep_time - _slack, gaps
    assert gaps[1] < _round_wait, gaps

    assert gaps[2] >= _round_wait + _orders_sleep_time - _slack, gaps

    queue = wait_for_queue_empty(client, _orders_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_every_failure_counts_whatever_its_reason() -> 'None':
    """ An endpoint that answers 401 is one failed attempt like any other.
    """
    client = get_client()
    receiver = get_receiver('orders')

    receiver.answer_next([UNAUTHORIZED, OK])

    result = send(client, _orders_conn, {'order_id': 'unauthorized-once'})
    assert result['is_in_queue'] is True
    assert result['error'].startswith(f'HTTP {UNAUTHORIZED}')

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1

    statuses = _get_statuses(receiver)
    assert statuses == [UNAUTHORIZED, OK]

    gaps = _get_gaps(receiver)
    assert gaps[0] >= _orders_sleep_time - _slack, gaps
    assert gaps[0] < _round_wait, gaps

# ################################################################################################################################

def test_no_retries_means_one_attempt_from_the_queue_per_round() -> 'None':
    """ A connection that allows no retries still tries a waiting message once per round.
    """
    client = get_client()
    receiver = get_receiver('no_retries')

    receiver.answer_next([INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK])

    result = send(client, _no_retries_conn, {'order_id': 'no-retries'})
    assert result['is_in_queue'] is True

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1

    statuses = _get_statuses(receiver)
    assert statuses == [INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK]

    gaps = _get_gaps(receiver)
    assert gaps[0] >= _retry.Default_Sleep_Time - _slack, gaps
    assert gaps[1] >= _round_wait + _retry.Default_Sleep_Time - _slack, gaps

    queue = wait_for_queue_empty(client, _no_retries_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_multiplier_grows_the_sleep_and_the_threshold_ends_the_round() -> 'None':
    """ With a multiplier of two the second sleep is twice the first.
    """
    client = get_client()
    receiver = get_receiver('orders')

    _ = edit_connection(client, _orders_conn, {
        _retry.Field_Max_Retries: 5,
        _retry.Field_Sleep_Time: 1,
        _retry.Field_Backoff_Threshold: 3,
        _retry.Field_Backoff_Multiplier: 2,
    })

    try:
        receiver.answer_next([INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK])

        result = send(client, _orders_conn, {'order_id': 'capped'})
        assert result['is_in_queue'] is True

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1

        statuses = _get_statuses(receiver)
        assert statuses == [INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK]

        gaps = _get_gaps(receiver)

        assert gaps[0] >= 1 - _slack, gaps
        assert gaps[0] < 2, gaps

        assert gaps[1] >= 2 - _slack, gaps
        assert gaps[1] < _round_wait, gaps

        assert gaps[2] >= _round_wait + 1 - _slack, gaps

        queue = wait_for_queue_empty(client, _orders_conn)
        assert queue['depth'] == 0

    finally:
        _restore_orders(client)

# ################################################################################################################################

def test_an_edit_of_the_retries_applies_to_the_next_message() -> 'None':
    """ Turning the retries off through the server's own edit service changes how the very next message is retried.
    """
    client = get_client()
    receiver = get_receiver('orders')

    _ = edit_connection(client, _orders_conn, {_retry.Field_Max_Retries: 0})

    try:
        after = get_connection(client, _orders_conn)
        assert after[_retry.Field_Max_Retries] == 0

        receiver.answer_next([INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK])

        result = send(client, _orders_conn, {'order_id': 'edited'})
        assert result['is_in_queue'] is True

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1

        statuses = _get_statuses(receiver)
        assert statuses == [INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR, OK]

        gaps = _get_gaps(receiver)
        assert gaps[1] >= _round_wait + _orders_sleep_time - _slack, gaps

        queue = wait_for_queue_empty(client, _orders_conn)
        assert queue['depth'] == 0

    finally:
        _restore_orders(client)

# ################################################################################################################################
# ################################################################################################################################
