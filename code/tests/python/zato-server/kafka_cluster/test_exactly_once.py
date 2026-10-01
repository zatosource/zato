# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Exactly once under failure - the leader stores a message but cannot confirm it, because the topic wants every
# instance in sync and one of them is frozen, so the confirmation does not come, Kafka reports the attempt as timed
# out with the message already in its log, and the connection sends again. With exactly once on, Kafka knows the
# second copy for what it is and the topic holds the message once. With exactly once off, the topic holds it twice.

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

# Kafka answers a produce request it cannot complete within this long with a timeout, the record it appended staying
# where it is - the default of the client library, which the bridge does not change
Broker_Request_Timeout = 30.0

# The frozen instance is thawed this long after the send started - past the timeout above, so the attempt Kafka had
# already stored has been reported as failed and the connection has sent again by then
Thaw_After = Broker_Request_Timeout + 10.0

# How long one send may take - the whole episode, the second attempt included, has to fit in it
Send_Timeout = 90

# A topic that wants every instance in sync before a message is confirmed
Topic_Config = {'min.insync.replicas': '3'}

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
outgoing_kafka:
  - name: {outgoing_exactly_once}
    address: {address}
    topic: {topic_exactly_once}
    acks: all
    is_idempotent: true
    send_timeout: {send_timeout}

  - name: {outgoing_at_least_once}
    address: {address}
    topic: {topic_at_least_once}
    acks: all
    is_idempotent: false
    send_timeout: {send_timeout}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    topic_exactly_once: str
    topic_at_least_once: str
    outgoing_exactly_once: str
    outgoing_at_least_once: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'ClusterSuite') -> 'Names':
    out = Names(
        topic_exactly_once=kafka_suite.new_name('topic.exactly.once'),
        topic_at_least_once=kafka_suite.new_name('topic.at.least.once'),
        outgoing_exactly_once=kafka_suite.new_name('outgoing.exactly.once'),
        outgoing_at_least_once=kafka_suite.new_name('outgoing.at.least.once'),
    )

    for topic in (out.topic_exactly_once, out.topic_at_least_once):
        kafka_suite.create_topic(topic, config=Topic_Config)

    yaml = _yaml.format(address=kafka_suite.address, send_timeout=Send_Timeout, **out._asdict())
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _send_with_a_frozen_follower(kafka_suite:'ClusterSuite', connection:'str', topic:'str', payload:'str') -> 'anydict':
    """ Freezes one follower of the topic, sends through the connection and thaws the follower while the send is still
    waiting, returning what the send reported once it came back.
    """
    cluster = kafka_suite.cluster

    leader = cluster.leader_of(topic, 0)
    follower = [elem.index for elem in cluster.instances if elem.index != leader][0]

    cluster.pause_instance_now(follower)

    results:'list[anydict]' = []

    def _send() -> 'None':
        results.append(kafka_suite.invoke('send', connection=connection, payload=payload))

    sender = threading.Thread(target=_send)
    sender.start()

    time.sleep(Thaw_After)

    # The send is still out there - the topic cannot confirm it without the frozen instance
    assert sender.is_alive(), results

    cluster.resume_instance(follower)
    cluster.wait_until_all_in_sync(topic)

    sender.join(Send_Timeout)
    assert not sender.is_alive(), 'The send never came back'

    out = results[0]
    return out

# ################################################################################################################################

def _count_on_topic(kafka_suite:'ClusterSuite', topic:'str', payload:'str') -> 'int':
    messages = read_topic(kafka_suite.bootstrap, topic, 1_000, timeout=5)
    out = len([elem for elem in messages if elem.value == payload.encode('utf8')])

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_with_exactly_once_on_a_message_stored_but_not_confirmed_is_on_the_topic_once(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    """ The first attempt is stored and then failed, the second one is recognised as the same message.
    """
    warm_up = kafka_suite.new_name('payload.exactly.once.warm')
    _ = kafka_suite.send(names.outgoing_exactly_once, warm_up)

    payload = kafka_suite.new_name('payload.exactly.once')
    result = _send_with_a_frozen_follower(kafka_suite, names.outgoing_exactly_once, names.topic_exactly_once, payload)

    assert result['is_ok'], result
    assert _count_on_topic(kafka_suite, names.topic_exactly_once, payload) == 1

# ################################################################################################################################

def test_with_exactly_once_off_the_same_message_is_on_the_topic_twice(
    kafka_suite:'ClusterSuite',
    names:'Names',
    ) -> 'None':
    """ The same episode without exactly once - the second attempt is a second copy.
    """
    warm_up = kafka_suite.new_name('payload.at.least.once.warm')
    _ = kafka_suite.send(names.outgoing_at_least_once, warm_up)

    payload = kafka_suite.new_name('payload.at.least.once')
    result = _send_with_a_frozen_follower(kafka_suite, names.outgoing_at_least_once, names.topic_at_least_once, payload)

    assert result['is_ok'], result
    assert _count_on_topic(kafka_suite, names.topic_at_least_once, payload) == 2

# ################################################################################################################################
# ################################################################################################################################
