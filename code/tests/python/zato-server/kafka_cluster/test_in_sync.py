# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Too few instances in sync - the cluster wants all but one instance to hold a message before it is confirmed, so with
# two of the three stopped a send with all Kafka instances confirming cannot go through. It fails within send_timeout
# rather than hanging, the message waits in the connection's queue as the Delivery tab says, and once an instance
# is back the queue drains on its own.

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import read_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ClusterSuite
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How long one attempt has - what fails fast means here
Send_Timeout = 3

# How much longer than that a failed send may take to come back, the retry policy's one extra attempt included
Send_Margin = 6.0

# How long the queue has to drain once an instance is back - a round of the queue comes every few seconds
Drain_Timeout = 60.0

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
    use_dlq: false
    max_retries: 1
    retry_sleep_time: 1
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
        topic=kafka_suite.new_name('topic.in.sync'),
        outgoing=kafka_suite.new_name('outgoing.in.sync'),
    )

    kafka_suite.create_topic(out.topic)

    yaml = _yaml.format(address=kafka_suite.address, send_timeout=Send_Timeout, **out._asdict())
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _queue(kafka_suite:'ClusterSuite', conn_name:'str') -> 'anydict':
    out = kafka_suite.client.invoke('test.queue-delivery.get-queue', {'conn_name': conn_name})
    return out

# ################################################################################################################################

def _queue_row(kafka_suite:'ClusterSuite', conn_name:'str') -> 'anydict':
    """ The connection's row on the Delivery tab's list of queues.
    """
    rows = kafka_suite.client.invoke('zato.pubsub.outgoing.get-queue-list')['items']
    out = [elem for elem in rows if elem['name'] == conn_name][0]

    return out

# ################################################################################################################################

def _wait_for_queue_depth(kafka_suite:'ClusterSuite', conn_name:'str', expected:'int', timeout:'float') -> 'None':
    deadline = time.monotonic() + timeout
    depth = -1

    while time.monotonic() < deadline:
        depth = _queue(kafka_suite, conn_name)['depth']

        if depth == expected:
            return

        time.sleep(0.5)

    raise Exception(f'Queue of `{conn_name}` did not reach a depth of {expected} within {timeout}s, last: {depth}')

# ################################################################################################################################
# ################################################################################################################################

def test_a_send_with_too_few_instances_in_sync_fails_fast_waits_in_the_queue_and_drains_once_one_is_back(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    cluster = kafka_suite.cluster

    # The connection has to know the cluster before two of its instances go
    warm_up = kafka_suite.new_name('payload.in.sync.warm')
    _ = kafka_suite.send(names.outgoing, warm_up)

    leader = cluster.leader_of(names.topic, 0)
    others = [elem.index for elem in cluster.instances if elem.index != leader]

    for index in others:
        cluster.stop_instance(index)

    # The leader is the only instance left in sync, one short of what the cluster wants
    metadata = cluster.metadata(names.topic)
    assert len(metadata.topics[names.topic].partitions[0].isrs) == 1, metadata.topics[names.topic].partitions[0].isrs

    payload = kafka_suite.new_name('payload.in.sync')

    start = time.monotonic()
    result = kafka_suite.send(names.outgoing, payload)
    elapsed = time.monotonic() - start

    # The send came back within the timeout, with the message in the queue rather than on the topic ..
    assert elapsed < Send_Timeout + Send_Margin, elapsed
    assert result['is_in_queue'] is True, result
    assert 'timed out' in result['send_error'], result

    # .. the queue holds it and the Delivery tab says so ..
    queue = _queue(kafka_suite, names.outgoing)
    assert queue['depth'] == 1, queue
    assert [elem['envelope']['request']['data'] for elem in queue['messages']] == [payload]

    row = _queue_row(kafka_suite, names.outgoing)
    assert row['queue_depth'] == 1, row
    assert row['dlq_depth'] == 0, row

    # .. nothing of it is on the topic yet ..
    on_topic = read_topic(kafka_suite.bootstrap, names.topic, 1_000, timeout=3)
    assert payload.encode('utf8') not in [elem.value for elem in on_topic]

    # .. and once an instance is back the queue drains by itself
    cluster.start_instance(others[0])

    _wait_for_queue_depth(kafka_suite, names.outgoing, 0, Drain_Timeout)

    cluster.start_instance(others[1])
    cluster.wait_until_all_in_sync(names.topic)

    on_topic = read_topic(kafka_suite.bootstrap, names.topic, 1_000, timeout=5)
    values = [elem.value for elem in on_topic]

    assert values.count(payload.encode('utf8')) == 1, values
    assert values.count(warm_up.encode('utf8')) == 1, values

    row = _queue_row(kafka_suite, names.outgoing)
    assert row['queue_depth'] == 0, row

# ################################################################################################################################
# ################################################################################################################################
