# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The confirmation levels of an outgoing connection against instances going away - what the help texts on the
# dashboard promise is what these prove. With all Kafka instances confirming, a send during a leader change either
# arrives once or fails out loud. With one instance confirming, a message the leader confirmed but had not yet handed
# to the others is gone once the leader is. With no confirmation, a send succeeds while nothing is listening.

# stdlib
import threading
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

# How many sends go out while the leader is being stopped
Sends_During_Stop = 20

# How long a send has, the retry policy on top of it
Send_Timeout = 5

# How long to wait once the followers are frozen before sending - a follower's fetch request that was already at the
# leader when it froze is answered with whatever the leader appends next, so the send waits for that to be over
Fetch_Settle = 2.0

# How many times a warm-up without confirmation is sent before giving up, and how long each is given to land
Warm_Up_Attempts = 5
Warm_Up_Wait = 3.0

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
outgoing_kafka:
  - name: {outgoing_all}
    address: {address}
    topic: {topic_all}
    acks: all
    is_idempotent: true
    send_timeout: {send_timeout}
    max_retries: 2
    retry_sleep_time: 1

  - name: {outgoing_one}
    address: {address}
    topic: {topic_one}
    acks: 1
    is_idempotent: false
    send_timeout: {send_timeout}

  - name: {outgoing_none}
    address: {address}
    topic: {topic_none}
    acks: 0
    is_idempotent: false
    send_timeout: {send_timeout}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    topic_all: str
    topic_one: str
    topic_none: str
    outgoing_all: str
    outgoing_one: str
    outgoing_none: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'ClusterSuite') -> 'Names':
    """ One connection per confirmation level, each with a one-partition topic of its own, so there is one leader to go after.
    """
    out = Names(
        topic_all=kafka_suite.new_name('topic.acks.all'),
        topic_one=kafka_suite.new_name('topic.acks.one'),
        topic_none=kafka_suite.new_name('topic.acks.none'),
        outgoing_all=kafka_suite.new_name('outgoing.acks.all'),
        outgoing_one=kafka_suite.new_name('outgoing.acks.one'),
        outgoing_none=kafka_suite.new_name('outgoing.acks.none'),
    )

    for topic in (out.topic_all, out.topic_one, out.topic_none):
        kafka_suite.create_topic(topic)

    yaml = _yaml.format(address=kafka_suite.address, send_timeout=Send_Timeout, **out._asdict())
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _payloads_on_topic(kafka_suite:'ClusterSuite', topic:'str') -> 'list[bytes]':
    messages = read_topic(kafka_suite.bootstrap, topic, 1_000, timeout=5)
    out = [elem.value for elem in messages]

    return out

# ################################################################################################################################

def _warm_up_without_confirmation(kafka_suite:'ClusterSuite', connection:'str', topic:'str') -> 'str':
    """ Sends through a connection that waits for no confirmation until a message is seen to land - an instance that
    stopped leading the topic since the connection last looked only drops such a message and hangs up, and the
    connection then looks the leader up again, which has to be over before anything is frozen.
    """
    for _ in range(Warm_Up_Attempts):
        before = kafka_suite.cluster.end_offset(topic)
        payload = kafka_suite.new_name('payload.acks.none.warm')
        _ = kafka_suite.send(connection, payload)

        deadline = time.monotonic() + Warm_Up_Wait

        while time.monotonic() < deadline:
            if kafka_suite.cluster.end_offset(topic) > before:
                return payload
            time.sleep(0.2)

    raise AssertionError(f'No warm-up message landed on `{topic}` in {Warm_Up_Attempts} attempts')

# ################################################################################################################################

def _lose_the_leaders_copy(kafka_suite:'ClusterSuite', topic:'str', leader:'int', followers:'list[int]') -> 'None':
    """ Kills the leader while the followers are frozen, then thaws them so one of them takes over without whatever
    the leader alone had, and brings the old leader back as a follower that drops what the new leader never saw.
    """
    cluster = kafka_suite.cluster

    cluster.kill_instance(leader, needs_wait=False)

    for index in followers:
        cluster.resume_instance(index)

    _ = cluster.wait_until_leader_moves(topic, 0, leader)

    cluster.start_instance(leader)
    cluster.wait_until_all_in_sync(topic)

# ################################################################################################################################
# ################################################################################################################################

def test_with_all_instances_a_send_during_a_leader_change_arrives_once_or_fails_out_loud(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    """ Sends keep going while the leader of the topic is stopped - each one either reports success and is on the topic
    exactly once, or reports an error and is not on the topic at all. Nothing is lost quietly and nothing is doubled.
    """
    cluster = kafka_suite.cluster
    topic = names.topic_all

    # The connection has to know the cluster before the leader goes
    warm_up = kafka_suite.new_name('payload.acks.all.warm')
    _ = kafka_suite.send(names.outgoing_all, warm_up)

    leader = cluster.leader_of(topic, 0)
    stopper = threading.Thread(target=cluster.stop_instance, args=(leader,))

    results:'list[tuple[str, anydict]]' = []

    stopper.start()

    try:
        for idx in range(Sends_During_Stop):
            payload = kafka_suite.new_name(f'payload.acks.all.{idx}')
            result = kafka_suite.invoke('send', connection=names.outgoing_all, payload=payload)
            results.append((payload, result))
    finally:
        stopper.join()

    _ = cluster.wait_until_leader_moves(topic, 0, leader)

    cluster.start_instance(leader)
    cluster.wait_until_all_in_sync(topic)

    on_topic = _payloads_on_topic(kafka_suite, topic)
    assert on_topic.count(warm_up.encode('utf8')) == 1

    for payload, result in results:
        count = on_topic.count(payload.encode('utf8'))

        if result['is_ok']:
            assert count == 1, (payload, result, count)
        else:
            assert count == 0, (payload, result, count)
            assert result['error'], result

# ################################################################################################################################

def test_with_one_instance_a_confirmed_message_the_others_never_saw_is_gone_with_the_leader(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    """ The followers are frozen, the leader confirms a send from its own log alone, and then the leader is killed.
    A follower takes over without the message, the old leader drops it when it rejoins, and the next message takes
    the offset the confirmed one had.
    """
    cluster = kafka_suite.cluster
    topic = names.topic_one

    warm_up = kafka_suite.new_name('payload.acks.one.warm')
    _ = kafka_suite.send(names.outgoing_one, warm_up)

    leader = cluster.leader_of(topic, 0)
    followers = [elem.index for elem in cluster.instances if elem.index != leader]

    for index in followers:
        cluster.pause_instance_now(index)

    time.sleep(Fetch_Settle)

    confirmed = kafka_suite.new_name('payload.acks.one.confirmed')
    result = kafka_suite.send(names.outgoing_one, confirmed)
    confirmed_offset = result['offset']

    _lose_the_leaders_copy(kafka_suite, topic, leader, followers)

    on_topic = _payloads_on_topic(kafka_suite, topic)
    assert warm_up.encode('utf8') in on_topic
    assert confirmed.encode('utf8') not in on_topic, on_topic

    # The offset is free again, so the next message takes it
    after = kafka_suite.new_name('payload.acks.one.after')
    result = kafka_suite.send(names.outgoing_one, after)
    assert result['offset'] == confirmed_offset, (result, confirmed_offset)

# ################################################################################################################################

def test_with_no_confirmation_a_send_succeeds_while_every_instance_is_frozen_and_the_message_is_lost(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    """ Every instance is frozen, the send still reports success at once, because nothing was waited for, and once the
    leader is killed and the cluster is whole again the message is nowhere.
    """
    cluster = kafka_suite.cluster
    topic = names.topic_none

    warm_up = _warm_up_without_confirmation(kafka_suite, names.outgoing_none, topic)

    leader = cluster.leader_of(topic, 0)
    followers = [elem.index for elem in cluster.instances if elem.index != leader]

    for instance in cluster.instances:
        cluster.pause_instance_now(instance.index)

    time.sleep(Fetch_Settle)

    unconfirmed = kafka_suite.new_name('payload.acks.none.unconfirmed')

    start = time.monotonic()
    result = kafka_suite.send(names.outgoing_none, unconfirmed)
    elapsed = time.monotonic() - start

    # It came back long before the timeout, with no offset to speak of
    assert elapsed < Send_Timeout, elapsed
    assert result['offset'] < 0, result

    _lose_the_leaders_copy(kafka_suite, topic, leader, followers)

    on_topic = _payloads_on_topic(kafka_suite, topic)
    assert warm_up.encode('utf8') in on_topic
    assert unconfirmed.encode('utf8') not in on_topic, on_topic

# ################################################################################################################################
# ################################################################################################################################
