# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQ rule, on every pub/sub backend.

# stdlib
import time
from json import loads

# Zato
from zato.common.api import HTTP_SOAP, PubSub, SCHEDULER
from zato.common.defaults import default_cluster_id
from zato.common.pubsub.dlq import Header_Rounds, Key_DLQ
from zato.common.pubsub.outgoing import Key_DLQ_Rounds

# Test support
from _dlq_helpers import Attempts_Per_Round, DLQ_Run, get_dlq, Get_Job_By_Name, get_topic_messages, invoke, \
    Retry_Message, run_dlq_rule, send_to_dlq, subscribe_topic
from _helpers import Connections, edit_connection, Forward_Topic, get_client, get_connection, get_receiver, \
    wait_for_queue_empty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

# One connection per action of the rule
_retry_conn = Connections['dlq_retry']
_forward_conn = Connections['dlq_forward']
_discard_conn = Connections['dlq_discard']
_keep_conn = Connections['dlq_keep']

# As the template declares them
_retry_conn_rounds = 2
_interval_seconds = 1
_past_interval_seconds = _interval_seconds + 0.5

# An interval no test outlasts
_long_interval_seconds = 600

# Longer than one round of the connection
_return_timeout_seconds = PubSub.Outgoing.Retry_Round_Wait + 10.0
_poll_interval_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

def _wait_past_interval() -> 'None':
    """ Waits until a message that just moved to the DLQ is old enough for the rule to act on it.
    """
    time.sleep(_past_interval_seconds)

# ################################################################################################################################

def _wait_for_rounds(client:'AdminClient', conn_name:'str', rounds:'int') -> 'anydict':
    """ Blocks until a connection's DLQ holds one message that the rule has put back that many times, then returns it.
    """
    deadline = time.monotonic() + _return_timeout_seconds

    while time.monotonic() < deadline:

        dlq = get_dlq(client, conn_name)
        messages = dlq['messages']

        if len(messages) == 1 and messages[0]['document'][Key_DLQ][Header_Rounds] == rounds:
            out = messages[0]
            return out

        time.sleep(_poll_interval_seconds)

    raise AssertionError(f'Timed out waiting for a DLQ message of `{conn_name}` with {rounds} rounds')

# ################################################################################################################################
# ################################################################################################################################

def test_the_rule_is_a_scheduler_job_that_runs_every_minute() -> 'None':
    """ The server declares the rule's job on startup.
    """
    client = get_client()

    job = invoke(client, Get_Job_By_Name, {'cluster_id': default_cluster_id, 'name': PubSub.Outgoing.DLQ_Job_Name})

    assert job['service_name'] == DLQ_Run
    assert job['job_type'] == SCHEDULER.JOB_TYPE.INTERVAL_BASED
    assert job['is_active'] is True
    assert job['minutes'] == PubSub.Outgoing.DLQ_Job_Interval_Minutes

# ################################################################################################################################

def test_retry_puts_the_message_back_as_many_times_as_allowed_and_then_leaves_it() -> 'None':
    """ Under the retry action the rule puts a message back into the queue once its interval passed.
    """
    client = get_client()
    receiver = get_receiver('dlq_retry')

    receiver.refuse_all()

    try:
        message = send_to_dlq(client, _retry_conn, receiver, {'seq': 1})
        assert message['document'][Key_DLQ][Header_Rounds] == 0

        for rounds in range(1, _retry_conn_rounds + 1):
            _wait_past_interval()

            counts = run_dlq_rule(client)
            assert counts[_retry_conn] == 1, counts

            message = _wait_for_rounds(client, _retry_conn, rounds)
            assert message['document'][Key_DLQ_Rounds] == rounds

        receiver.accept_all()
        _wait_past_interval()

        counts = run_dlq_rule(client)
        assert _retry_conn not in counts, counts

        dlq = get_dlq(client, _retry_conn)
        assert len(dlq['messages']) == 1
        assert dlq['messages'][0]['msg_id'] == message['msg_id']

        before = len(receiver.wait_for_requests(0))
        _ = invoke(client, Retry_Message, {'sub_key': dlq['sub_key'], 'msg_id': message['msg_id']})

        requests = receiver.wait_for_requests(before + 1)
        assert loads(requests[-1].body) == {'seq': 1}

        _ = wait_for_queue_empty(client, _retry_conn)
        assert get_dlq(client, _retry_conn)['messages'] == []

    finally:
        receiver.accept_all()

# ################################################################################################################################

def test_a_message_the_rule_put_back_arrives_when_the_endpoint_accepts_it() -> 'None':
    """ The rule's retry is a delivery like any other.
    """
    client = get_client()
    receiver = get_receiver('dlq_retry')

    _ = send_to_dlq(client, _retry_conn, receiver, {'seq': 7})
    _wait_past_interval()

    counts = run_dlq_rule(client)
    assert counts[_retry_conn] == 1, counts

    requests = receiver.wait_for_requests(Attempts_Per_Round + 1)
    assert len(requests) == Attempts_Per_Round + 1
    assert loads(requests[-1].body) == {'seq': 7}

    _ = wait_for_queue_empty(client, _retry_conn)
    assert get_dlq(client, _retry_conn)['messages'] == []

# ################################################################################################################################

def test_forward_publishes_the_message_to_the_connection_topic_with_its_header() -> 'None':
    """ Under the forward action the rule publishes a due message to the topic the connection names.
    """
    client = get_client()
    receiver = get_receiver('dlq_forward')

    subscribe_topic(client, Forward_Topic)
    _ = get_topic_messages(client, Forward_Topic)

    message = send_to_dlq(client, _forward_conn, receiver, {'seq': 1})
    _wait_past_interval()

    counts = run_dlq_rule(client)
    assert counts[_forward_conn] == 1, counts

    forwarded = get_topic_messages(client, Forward_Topic)
    assert len(forwarded) == 1

    assert forwarded[0]['document'] == message['document']
    assert Key_DLQ in forwarded[0]['document']

    assert get_dlq(client, _forward_conn)['messages'] == []

# ################################################################################################################################

def test_discard_empties_the_dlq() -> 'None':
    """ Under the discard action a due message is taken out of the DLQ and goes nowhere else.
    """
    client = get_client()
    receiver = get_receiver('dlq_discard')

    subscribe_topic(client, Forward_Topic)
    _ = get_topic_messages(client, Forward_Topic)

    _ = send_to_dlq(client, _discard_conn, receiver, {'seq': 1})
    _wait_past_interval()

    counts = run_dlq_rule(client)
    assert counts[_discard_conn] == 1, counts

    assert get_dlq(client, _discard_conn)['messages'] == []
    assert get_topic_messages(client, Forward_Topic) == []

# ################################################################################################################################

def test_keep_leaves_the_message_where_it_is() -> 'None':
    """ Under the keep action the rule does not touch the connection's DLQ at all.
    """
    client = get_client()
    receiver = get_receiver('dlq_keep')

    message = send_to_dlq(client, _keep_conn, receiver, {'seq': 1})
    _wait_past_interval()

    counts = run_dlq_rule(client)
    assert _keep_conn not in counts, counts

    dlq = get_dlq(client, _keep_conn)
    assert len(dlq['messages']) == 1
    assert dlq['messages'][0]['msg_id'] == message['msg_id']

# ################################################################################################################################

def test_a_message_too_recent_for_the_interval_waits_for_a_later_run() -> 'None':
    """ The rule acts on a message only once its last round is at least the connection's interval behind it.
    """
    client = get_client()
    receiver = get_receiver('dlq_discard')

    _ = edit_connection(client, _discard_conn, {_dlq.Field_Retry_Interval: _long_interval_seconds})

    try:
        after = get_connection(client, _discard_conn)
        assert after[_dlq.Field_Retry_Interval] == _long_interval_seconds

        _ = send_to_dlq(client, _discard_conn, receiver, {'seq': 1})
        _wait_past_interval()

        counts = run_dlq_rule(client)
        assert _discard_conn not in counts, counts
        assert len(get_dlq(client, _discard_conn)['messages']) == 1

    finally:
        _ = edit_connection(client, _discard_conn, {_dlq.Field_Retry_Interval: _interval_seconds})

    counts = run_dlq_rule(client)
    assert counts[_discard_conn] == 1, counts
    assert get_dlq(client, _discard_conn)['messages'] == []

# ################################################################################################################################

def test_an_edit_of_the_action_applies_to_the_next_run() -> 'None':
    """ An action changed through the server's edit service is what the very next run of the rule carries out.
    """
    client = get_client()
    receiver = get_receiver('dlq_keep')

    _ = send_to_dlq(client, _keep_conn, receiver, {'seq': 1})
    _ = edit_connection(client, _keep_conn, {
        _dlq.Field_Action: _dlq.Action.Discard,
        _dlq.Field_Retry_Interval: _interval_seconds,
    })

    try:
        after = get_connection(client, _keep_conn)
        assert after[_dlq.Field_Action] == _dlq.Action.Discard

        _wait_past_interval()

        counts = run_dlq_rule(client)
        assert counts[_keep_conn] == 1, counts
        assert get_dlq(client, _keep_conn)['messages'] == []

    finally:
        _ = edit_connection(client, _keep_conn, {
            _dlq.Field_Action: _dlq.Action.Keep,
            _dlq.Field_Retry_Interval: _dlq.Default_Retry_Interval,
        })

# ################################################################################################################################
# ################################################################################################################################
