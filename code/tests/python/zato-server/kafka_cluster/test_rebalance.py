# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A rebalance on a channel - two channels in one consumer group share the partitions of one topic, the instance that
# coordinates the group is killed midway through the stream and started again later, and every message written
# before, during and after reaches a service exactly once. The coordinator going away without a word leaves the group
# without one for longer than the session timeout, so both channels drop their partitions and join again, which is
# the partition movement the bridge's pause and resume and its handling of offsets after a rebalance are tested against.
# The receivers are slow and the channels take few messages in flight, so partitions are paused and resumed throughout.

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import group_assignments, produce, wait_for_assignment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ClusterSuite
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

Receiver_One = 'test.kafka.receiver'
Receiver_Two = 'test.kafka.receiver.two'

# The topic has this many partitions for the two channels to share
Partition_Count = 6

# How many messages each burst of the stream carries
Burst_Size = 30

# The receivers take this long over each message, so there are always messages in flight
Receiver_Sleep = 0.1

# How many messages each channel takes in flight before the bridge pauses its partitions
Max_In_Flight = 3

# How long a burst has to be received - the receivers are slow on purpose
Burst_Timeout = 120.0

# How long to wait once a burst is received, so the offsets of its last messages are committed before the coordinator goes
Commit_Wait = 6.0

# How long to wait at the end for anything that would still arrive twice
Late_Wait = Receiver_Sleep * Max_In_Flight * 2

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
channel_kafka:
  - name: {channel_one}
    address: {address}
    topics:
      - {topic}
    group_id: {group}
    service: {receiver_one}
    auto_offset_reset: earliest
    max_in_flight: {max_in_flight}

  - name: {channel_two}
    address: {address}
    topics:
      - {topic}
    group_id: {group}
    service: {receiver_two}
    auto_offset_reset: earliest
    max_in_flight: {max_in_flight}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    topic: str
    group: str
    channel_one: str
    channel_two: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'ClusterSuite') -> 'Names':
    out = Names(
        topic=kafka_suite.new_name('topic.rebalance'),
        group=kafka_suite.new_name('group.rebalance'),
        channel_one=kafka_suite.new_name('channel.rebalance.one'),
        channel_two=kafka_suite.new_name('channel.rebalance.two'),
    )

    kafka_suite.create_topic(out.topic, Partition_Count)

    yaml = _yaml.format(
        address=kafka_suite.address,
        receiver_one=Receiver_One,
        receiver_two=Receiver_Two,
        max_in_flight=Max_In_Flight,
        **out._asdict(),
    )
    kafka_suite.import_yaml(yaml)

    # Both channels hold their partitions before anything is written
    wait_for_assignment(kafka_suite.bootstrap, out.group, out.topic, partition_count=Partition_Count)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _burst(kafka_suite:'ClusterSuite', names:'Names', label:'str') -> 'strlist':
    """ Writes one burst of messages over every partition and returns their payloads.
    """
    out:'strlist' = []

    for idx in range(Burst_Size):
        payload = kafka_suite.new_name(f'payload.rebalance.{label}.{idx}')
        _ = produce(kafka_suite.bootstrap, names.topic, payload, partition=idx % Partition_Count)
        out.append(payload)

    return out

# ################################################################################################################################

def _wait_for_burst(kafka_suite:'ClusterSuite', payloads:'strlist') -> 'None':
    """ Waits until every payload of a burst reached one of the two receivers.
    """
    wanted = set(payloads)
    _ = kafka_suite.wait_for_received(lambda elem: elem['data'] in wanted, len(payloads), timeout=Burst_Timeout)

# ################################################################################################################################

def _assert_each_once(kafka_suite:'ClusterSuite', payloads:'strlist') -> 'None':
    """ Every payload reached a receiver exactly once, counting both receivers together.
    """
    received:'anylist' = kafka_suite.received()
    counts = {payload: 0 for payload in payloads}

    for elem in received:
        if elem['data'] in counts:
            counts[elem['data']] += 1

    twice = {payload: count for payload, count in counts.items() if count != 1}
    assert not twice, twice

# ################################################################################################################################

def _members_holding_partitions(kafka_suite:'ClusterSuite', names:'Names') -> 'int':
    assignments = group_assignments(kafka_suite.bootstrap, names.group)
    out = len([partitions for partitions in assignments.values() if partitions])

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_message_reaches_a_service_once_across_a_rebalance(kafka_suite:'ClusterSuite', names:'Names') -> 'None':
    """ Both channels share the topic, the group's coordinator is killed and started again, and the three bursts
    around that are each received exactly once.
    """
    cluster = kafka_suite.cluster

    kafka_suite.set_behaviour(Receiver_One, sleep=Receiver_Sleep)
    kafka_suite.set_behaviour(Receiver_Two, sleep=Receiver_Sleep)

    # Both channels hold partitions, so the group has two working members
    assert _members_holding_partitions(kafka_suite, names) == 2
    members_before = set(group_assignments(kafka_suite.bootstrap, names.group))

    # The first burst, with the cluster whole
    first = _burst(kafka_suite, names, 'first')
    _wait_for_burst(kafka_suite, first)
    time.sleep(Commit_Wait)

    # The coordinator goes away without a word, the group times out and both channels join again ..
    coordinator = cluster.coordinator_of(names.group)
    cluster.kill_instance(coordinator)

    # .. the second burst is written while they are still finding their way back ..
    second = _burst(kafka_suite, names, 'second')

    wait_for_assignment(kafka_suite.bootstrap, names.group, names.topic, partition_count=Partition_Count)
    assert _members_holding_partitions(kafka_suite, names) == 2

    # .. the members are new ones, so the partitions did move ..
    members_after = set(group_assignments(kafka_suite.bootstrap, names.group))
    assert members_after != members_before, (members_before, members_after)

    _wait_for_burst(kafka_suite, second)

    # .. and the third burst comes with the instance back
    cluster.start_instance(coordinator)
    cluster.wait_until_all_in_sync(names.topic)

    third = _burst(kafka_suite, names, 'third')
    _wait_for_burst(kafka_suite, third)

    # Nothing was lost and nothing came twice
    time.sleep(Late_Wait)
    _assert_each_once(kafka_suite, first + second + third)

    # Each receiver got some of the traffic - the partitions were shared, not held by one channel
    assert kafka_suite.received(Receiver_One), 'Receiver one got nothing'
    assert kafka_suite.received(Receiver_Two), 'Receiver two got nothing'

# ################################################################################################################################
# ################################################################################################################################
