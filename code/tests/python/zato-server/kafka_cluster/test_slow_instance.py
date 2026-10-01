# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A slow instance - one instance is frozen rather than stopped, so requests to it hang instead of failing. A channel
# reading partitions the other instances lead is not held up by it, and a send to a partition the frozen instance
# leads fails within send_timeout rather than hanging the service that sent it.

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import produce, wait_for_assignment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ClusterSuite

# ################################################################################################################################
# ################################################################################################################################

Receiver = 'test.kafka.receiver'

# One partition per instance, so each instance leads one of them
Partition_Count = 3

# How long one send has
Send_Timeout = 3

# How much longer than that a send may take to come back
Send_Margin = 4.0

# A message to a partition the others lead has this long to arrive while one instance is frozen
Receive_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
outgoing_kafka:
  - name: {outgoing}
    address: {address}
    topic: {topic}
    acks: all
    send_timeout: {send_timeout}

channel_kafka:
  - name: {channel}
    address: {address}
    topics:
      - {topic}
    group_id: {group}
    service: {receiver}
    auto_offset_reset: earliest
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    topic: str
    group: str
    outgoing: str
    channel: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'ClusterSuite') -> 'Names':
    out = Names(
        topic=kafka_suite.new_name('topic.slow'),
        group=kafka_suite.new_name('group.slow'),
        outgoing=kafka_suite.new_name('outgoing.slow'),
        channel=kafka_suite.new_name('channel.slow'),
    )

    kafka_suite.create_topic(out.topic, Partition_Count)

    yaml = _yaml.format(address=kafka_suite.address, receiver=Receiver, send_timeout=Send_Timeout, **out._asdict())
    kafka_suite.import_yaml(yaml)

    wait_for_assignment(kafka_suite.bootstrap, out.group, out.topic, partition_count=Partition_Count)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _partitions_by_leader(kafka_suite:'ClusterSuite', topic:'str') -> 'dict[int, list[int]]':
    """ The partitions each instance leads, by the instance's index.
    """
    out:'dict[int, list[int]]' = {}

    for partition in range(Partition_Count):
        leader = kafka_suite.cluster.leader_of(topic, partition)
        out.setdefault(leader, []).append(partition)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_frozen_instance_delays_neither_the_other_partitions_nor_the_service_sending_to_it(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    cluster = kafka_suite.cluster

    # The connection and the channel have to know the cluster before an instance freezes
    warm_up = kafka_suite.new_name('payload.slow.warm')
    _ = kafka_suite.send(names.outgoing, warm_up)
    _ = kafka_suite.wait_for_payload(warm_up)

    by_leader = _partitions_by_leader(kafka_suite, names.topic)
    assert len(by_leader) == Partition_Count, by_leader

    # The frozen instance is not the one coordinating the channel's group - a frozen coordinator is a different episode,
    # the group as a whole has to find a new one before anything is received again
    coordinator = cluster.coordinator_of(names.group)
    frozen = [elem.index for elem in cluster.instances if elem.index != coordinator][0]

    frozen_partition = by_leader[frozen][0]
    other_partition = [elem for leader, partitions in by_leader.items() if leader != frozen for elem in partitions][0]

    # Frozen without waiting for the cluster to notice - for a while it is simply an instance that does not answer
    cluster.pause_instance_now(frozen)

    try:
        # A send to the frozen instance's partition fails within the timeout rather than hanging ..
        hung = kafka_suite.new_name('payload.slow.hung')

        start = time.monotonic()
        result = kafka_suite.invoke('send', connection=names.outgoing, payload=hung, partition=frozen_partition)
        elapsed = time.monotonic() - start

        assert elapsed < Send_Timeout + Send_Margin, elapsed
        assert result['is_ok'] is False, result
        assert 'timed out' in result['error'], result

        # .. and a message to a partition another instance leads reaches the service as usual
        unaffected = kafka_suite.new_name('payload.slow.unaffected')
        _ = produce(kafka_suite.bootstrap, names.topic, unaffected, partition=other_partition)
        _ = kafka_suite.wait_for_payload(unaffected, timeout=Receive_Timeout)

    finally:
        cluster.resume_instance(frozen)

    cluster.wait_until_all_in_sync(names.topic)

    # The service never saw the message that failed
    kafka_suite.not_received(lambda elem: elem['data'] == hung, within=2.0)

# ################################################################################################################################
# ################################################################################################################################
