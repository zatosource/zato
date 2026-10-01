# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The outgoing DLQ on the cluster - with the queue on and every instance down, sends pile up in the queue, the retry
# policy runs out and the messages move to the DLQ with Kafka's timeout in the header, a sweep raises the DLQ alert
# about the connection, and once the instances are back a retry from the DLQ delivers each message to the topic once.
#
# The instances are stopped rather than frozen - a frozen one still takes what reached its socket before the freeze
# once it thaws, and a message both on the topic and in the DLQ would then arrive twice when retried.

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import read_topic
from zato.common.alerting.seed.rules_queue import DLQ_Messages_Rule
from zato.common.audit_log.common import AuditSource
from zato.common.pubsub.dlq import Header_Error, Header_Reason, Key_DLQ
from zato.common.pubsub.outgoing import Key_Data, Key_Request

# Test support
from queue_delivery.alerting import get_alerts_raised, get_newest_audit_event_id, run_sweep

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ClusterSuite
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many messages are sent while Kafka is down
Message_Count = 3

# How long one attempt has
Send_Timeout = 2

# One round of the queue is this many attempts, a second apart
Max_Retries = 1
Sleep_Time = 1

# How long the messages have to reach the DLQ - each goes through its round of attempts in turn
DLQ_Timeout = Message_Count * (Max_Retries + 1) * (Send_Timeout + Sleep_Time + 2) + 30.0

# How long a retry from the DLQ has to land on the topic
Retry_Timeout = 60.0

# How long the connection is given to find the instances again once they are back - while every instance was down
# the connection's attempts to reconnect grew further and further apart, up to ten seconds between them
Reconnect_Wait = 15.0

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
outgoing_kafka:
  - name: {outgoing}
    address: {address}
    topic: {topic}
    acks: all
    send_timeout: {send_timeout}
    use_queue: true
    use_dlq: true
    dlq_action: keep
    max_retries: {max_retries}
    retry_sleep_time: {sleep_time}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    topic: str
    outgoing: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'ClusterSuite') -> 'Names':
    out = Names(
        topic=kafka_suite.new_name('topic.outgoing.dlq'),
        outgoing=kafka_suite.new_name('outgoing.dlq'),
    )

    kafka_suite.create_topic(out.topic)

    yaml = _yaml.format(
        address=kafka_suite.address,
        send_timeout=Send_Timeout,
        max_retries=Max_Retries,
        sleep_time=Sleep_Time,
        **out._asdict(),
    )
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _queue_depth(kafka_suite:'ClusterSuite', conn_name:'str') -> 'int':
    out:'int' = kafka_suite.client.invoke('test.queue-delivery.get-queue', {'conn_name': conn_name})['depth']
    return out

# ################################################################################################################################

def _dlq_alerts(conn_name:'str', since_id:'int') -> 'anylist':
    out = [elem for elem in get_alerts_raised(conn_name, since_id) if elem['rule'] == DLQ_Messages_Rule]
    return out

# ################################################################################################################################

def _wait_for_payloads_on_topic(kafka_suite:'ClusterSuite', topic:'str', payloads:'strlist') -> 'list[bytes]':
    """ Waits until every payload is on the topic and returns everything the topic holds.
    """
    deadline = time.monotonic() + Retry_Timeout
    wanted = {elem.encode('utf8') for elem in payloads}
    out:'list[bytes]' = []

    while time.monotonic() < deadline:
        out = [elem.value for elem in read_topic(kafka_suite.bootstrap, topic, 1_000, timeout=3)]

        if wanted <= set(out):
            return out

        time.sleep(1)

    raise Exception(f'Not every payload reached `{topic}` within {Retry_Timeout}s: {out}')

# ################################################################################################################################
# ################################################################################################################################

def test_sends_while_kafka_is_down_queue_up_move_to_the_dlq_raise_the_alert_and_a_retry_delivers_each_once(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    cluster = kafka_suite.cluster
    conn_name = names.outgoing

    # The connection has to know the cluster before it goes
    warm_up = kafka_suite.new_name('payload.outgoing.dlq.warm')
    _ = kafka_suite.send(conn_name, warm_up)

    # Nothing about the connection before anything went wrong
    since_id = get_newest_audit_event_id()
    run_sweep(kafka_suite.client)
    assert _dlq_alerts(conn_name, since_id) == []

    for instance in cluster.instances:
        cluster.stop_instance(instance.index)

    assert not cluster.running_instances()

    try:
        # Every send comes back with its message in the queue ..
        payloads:'strlist' = []

        for idx in range(Message_Count):
            payload = kafka_suite.new_name(f'payload.outgoing.dlq.{idx}')
            result = kafka_suite.send(conn_name, payload)
            assert result['is_in_queue'] is True, result
            payloads.append(payload)

        # .. the queue holds what has not been given up on yet ..
        assert _queue_depth(kafka_suite, conn_name) >= 1

        # .. and once the retry policy has run out for each, they are all in the DLQ with Kafka's timeout in the header
        dlq = kafka_suite.wait_for_dlq_count(conn_name, Message_Count, timeout=DLQ_Timeout)
        assert _queue_depth(kafka_suite, conn_name) == 0

        in_dlq = [elem['document'][Key_Request][Key_Data] for elem in dlq['messages']]
        assert sorted(in_dlq) == sorted(payloads), in_dlq

        for message in dlq['messages']:
            header:'anydict' = message['document'][Key_DLQ]
            assert 'timed out' in header[Header_Error], header
            assert header[Header_Reason], header

        # The sweep raises the DLQ alert about the connection, filed under the Kafka outgoing source
        since_id = get_newest_audit_event_id()
        run_sweep(kafka_suite.client)

        alerts = _dlq_alerts(conn_name, since_id)
        assert len(alerts) == 1, alerts
        assert alerts[0]['source'] == AuditSource.Kafka_Outgoing, alerts
        assert conn_name in alerts[0]['message'], alerts
        assert f'{Message_Count} messages in the DLQ' in alerts[0]['message'], alerts

    finally:
        cluster.restore_all()

    cluster.wait_until_all_in_sync(names.topic)
    time.sleep(Reconnect_Wait)

    # With Kafka back, a retry of everything in the DLQ delivers each message once
    _ = kafka_suite.dlq_action('retry-all-messages', sub_key=dlq['sub_key'])

    on_topic = _wait_for_payloads_on_topic(kafka_suite, names.topic, payloads)

    for payload in payloads:
        assert on_topic.count(payload.encode('utf8')) == 1, (payload, on_topic)

    assert on_topic.count(warm_up.encode('utf8')) == 1

    assert kafka_suite.dlq(conn_name)['messages'] == []
    assert _queue_depth(kafka_suite, conn_name) == 0

    # And a sweep says nothing about the connection any more
    since_id = get_newest_audit_event_id()
    run_sweep(kafka_suite.client)
    assert _dlq_alerts(conn_name, since_id) == []

# ################################################################################################################################
# ################################################################################################################################
