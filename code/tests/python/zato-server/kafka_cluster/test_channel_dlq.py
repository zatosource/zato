# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQ of a Kafka channel on the cluster - the DLQ is a pub/sub topic, not Kafka, so a message in it survives the
# instance its source partition was on going away, a retry from it while that partition has no leader fails on the
# service alone, counts a round and stays rather than being lost, and a forward from it still publishes while every
# Kafka instance is down.

# stdlib
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import produce
from zato.common.api import PubSub
from zato.common.pubsub.dlq import Header_Rounds, Key_DLQ
from zato.common.pubsub.outgoing import Key_Data, Key_Request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ClusterSuite
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

Receiver = 'test.kafka.receiver'
Receiver_Two = 'test.kafka.receiver.two'

# How many times the rule puts a message back under the retry action
DLQ_Retries = 2

# How long a message has to reach the DLQ
DLQ_Timeout = PubSub.Delivery.Retry_Round_Wait + 20.0

# The topics live on one instance alone, so that instance going away leaves their partition without a leader
Replication_Factor = 1

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
channel_kafka:
  - name: {channel_retry}
    address: {address}
    topics:
      - {topic_retry}
    group_id: {group_retry}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: retry
    dlq_retries: {dlq_retries}
    dlq_retry_interval: 0

  - name: {channel_forward}
    address: {address}
    topics:
      - {topic_forward}
    group_id: {group_forward}
    service: {receiver_two}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: forward
    dlq_forward_to: {forward_topic}
    dlq_keep_header: true
    dlq_retry_interval: 0
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    channel_retry: str
    channel_forward: str
    topic_retry: str
    topic_forward: str
    group_retry: str
    group_forward: str
    forward_topic: str
    forward_sub_key: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'ClusterSuite') -> 'Names':
    out = Names(
        channel_retry=kafka_suite.new_name('channel.dlq.retry'),
        channel_forward=kafka_suite.new_name('channel.dlq.forward'),
        topic_retry=kafka_suite.new_name('topic.dlq.retry'),
        topic_forward=kafka_suite.new_name('topic.dlq.forward'),
        group_retry=kafka_suite.new_name('group.dlq.retry'),
        group_forward=kafka_suite.new_name('group.dlq.forward'),
        forward_topic=kafka_suite.new_name('forward'),
        forward_sub_key=kafka_suite.new_name('forward.sub'),
    )

    for topic in (out.topic_retry, out.topic_forward):
        kafka_suite.create_topic(topic, replication_factor=Replication_Factor)

    yaml = _yaml.format(
        address=kafka_suite.address,
        receiver=Receiver,
        receiver_two=Receiver_Two,
        dlq_retries=DLQ_Retries,
        **out._asdict(),
    )
    kafka_suite.import_yaml(yaml)

    kafka_suite.subscribe_topic(out.forward_topic, out.forward_sub_key)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _send_to_dlq(kafka_suite:'ClusterSuite', conn_name:'str', topic:'str', receiver:'str') -> 'anydict':
    """ Produces a message the receiver refuses and returns what the DLQ holds of it.
    """
    before = {elem['msg_id'] for elem in kafka_suite.dlq(conn_name)['messages']}
    kafka_suite.set_behaviour(receiver, fail_always=True)

    payload = kafka_suite.new_name('payload')
    _ = produce(kafka_suite.bootstrap, topic, payload)

    dlq = kafka_suite.wait_for_dlq_count(conn_name, len(before) + 1, timeout=DLQ_Timeout)
    new = [elem for elem in dlq['messages'] if elem['msg_id'] not in before]

    assert len(new) == 1, dlq
    assert new[0]['document'][Key_Request][Key_Data] == payload

    out = new[0]
    return out

# ################################################################################################################################

def _rounds_of(kafka_suite:'ClusterSuite', conn_name:'str', payload:'str') -> 'int':
    """ How many times the rule has put one message back so far - minus one when the message is not there any more.
    A retry that fails again files the message under a new id, so it is found by what it carries.
    """
    for elem in kafka_suite.dlq(conn_name)['messages']:
        if elem['document'][Key_Request][Key_Data] == payload:
            out:'int' = elem['document'][Key_DLQ][Header_Rounds]
            return out

    return -1

# ################################################################################################################################
# ################################################################################################################################

def test_a_dlq_message_survives_its_instance_and_a_retry_without_a_leader_fails_counts_a_round_and_stays(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    """ The topic's one instance is stopped once the message is in the DLQ - the message is still there, a retry that
    the service turns down counts a round and leaves it there, a retry the service accepts takes it out, all with the
    partition leaderless, and the channel picks up again once the instance is back.
    """
    cluster = kafka_suite.cluster
    conn_name = names.channel_retry

    message = _send_to_dlq(kafka_suite, conn_name, names.topic_retry, Receiver)
    payload = message['document'][Key_Request][Key_Data]

    def is_ours(elem:'anydict') -> 'bool':
        return elem['data'] == payload

    # The service saw it once, when it refused it
    _ = kafka_suite.wait_for_received(is_ours, 1)

    # The one instance the topic lives on goes away ..
    leader = cluster.leader_of(names.topic_retry, 0)
    cluster.stop_instance(leader)
    assert cluster.leader_of(names.topic_retry, 0) == -1

    # .. the DLQ still holds the message ..
    assert _rounds_of(kafka_suite, conn_name, payload) == 0

    # .. a retry the service turns down counts a round and the message stays ..
    counts = kafka_suite.run_dlq_rule()
    assert counts[conn_name] == 1, counts

    _ = kafka_suite.wait_for_received(is_ours, 2)
    assert _rounds_of(kafka_suite, conn_name, payload) == 1

    # .. and a retry the service accepts takes it out - Kafka had no part in either
    kafka_suite.set_behaviour(Receiver)

    counts = kafka_suite.run_dlq_rule()
    assert counts[conn_name] == 1, counts

    replays = kafka_suite.wait_for_received(is_ours, 3)
    assert replays[-1]['outcome'] == 'ok'
    assert _rounds_of(kafka_suite, conn_name, payload) == -1

    # The instance comes back and the channel reads again
    cluster.start_instance(leader)
    cluster.wait_until_all_in_sync(names.topic_retry)

    after = kafka_suite.new_name('payload.after')
    _ = produce(kafka_suite.bootstrap, names.topic_retry, after)
    _ = kafka_suite.wait_for_payload(after)

# ################################################################################################################################

def test_a_forward_from_the_dlq_publishes_while_every_instance_is_down(kafka_suite:'ClusterSuite', names:'Names') -> 'None':
    """ The DLQ and the topic a forward goes to are pub/sub topics, so with Kafka down altogether the forward still happens.
    """
    cluster = kafka_suite.cluster
    conn_name = names.channel_forward

    _ = kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key)

    message = _send_to_dlq(kafka_suite, conn_name, names.topic_forward, Receiver_Two)

    for instance in cluster.instances:
        cluster.stop_instance(instance.index)

    assert not cluster.running_instances()

    counts = kafka_suite.run_dlq_rule()
    assert counts[conn_name] == 1, counts

    forwarded = kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key)
    assert len(forwarded) == 1, forwarded
    assert forwarded[0]['document'] == message['document']

    assert kafka_suite.dlq(conn_name)['messages'] == []

    # Everything back, the channel reads again
    cluster.restore_all()
    cluster.wait_until_all_in_sync(names.topic_forward)

    kafka_suite.set_behaviour(Receiver_Two)

    after = kafka_suite.new_name('payload.after')
    _ = produce(kafka_suite.bootstrap, names.topic_forward, after)
    _ = kafka_suite.wait_for_payload(after, timeout=60.0)

# ################################################################################################################################
# ################################################################################################################################
