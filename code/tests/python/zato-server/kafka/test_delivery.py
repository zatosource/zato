# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a channel delivers - retries with backoff and the rounds after them with the DLQ off, deduplication
# and one slow channel leaving another alone.

# stdlib
from time import monotonic, sleep
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import produce, wait_until_committed
from zato.common.api import KAFKA, PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import KafkaSuite

# ################################################################################################################################
# ################################################################################################################################

_consumer = KAFKA.Consumer

Receiver = 'test.kafka.receiver'
Receiver_Two = 'test.kafka.receiver.two'
Receiver_Three = 'test.kafka.receiver.three'

Dedup_Header = 'msg-id'
Dedup_TTL = 120

# The retry policy of the channel with the DLQ off - sleeps of 1, 2 and 4 seconds between four attempts
Max_Retries = 3
Sleep_Time = 1

# How much a measured gap may exceed the configured sleep
Gap_Slack = 1.5

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
    use_dlq: false
    max_retries: {max_retries}
    retry_sleep_time: {sleep_time}

  - name: {channel_dedup}
    address: {address}
    topics:
      - {topic_dedup}
    group_id: {group_dedup}
    service: {receiver}
    auto_offset_reset: earliest
    dedup_header: {dedup_header}
    dedup_ttl: {dedup_ttl}

  - name: {channel_slow}
    address: {address}
    topics:
      - {topic_slow}
    group_id: {group_slow}
    service: {receiver_two}
    auto_offset_reset: earliest

  - name: {channel_fast}
    address: {address}
    topics:
      - {topic_fast}
    group_id: {group_fast}
    service: {receiver_three}
    auto_offset_reset: earliest
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    channel_retry: str
    channel_dedup: str
    channel_slow: str
    channel_fast: str
    topic_retry: str
    topic_dedup: str
    topic_slow: str
    topic_fast: str
    group_retry: str
    group_dedup: str
    group_slow: str
    group_fast: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'KafkaSuite') -> 'Names':
    """ The connections of this module, imported once.
    """
    out = Names(
        channel_retry=kafka_suite.new_name('channel.retry'),
        channel_dedup=kafka_suite.new_name('channel.dedup'),
        channel_slow=kafka_suite.new_name('channel.slow'),
        channel_fast=kafka_suite.new_name('channel.fast'),
        topic_retry=kafka_suite.new_name('topic.retry'),
        topic_dedup=kafka_suite.new_name('topic.dedup'),
        topic_slow=kafka_suite.new_name('topic.slow'),
        topic_fast=kafka_suite.new_name('topic.fast'),
        group_retry=kafka_suite.new_name('group.retry'),
        group_dedup=kafka_suite.new_name('group.dedup'),
        group_slow=kafka_suite.new_name('group.slow'),
        group_fast=kafka_suite.new_name('group.fast'),
    )

    for topic in (out.topic_retry, out.topic_dedup, out.topic_slow, out.topic_fast):
        kafka_suite.create_topic(topic)

    yaml = _yaml.format(
        address=kafka_suite.address,
        receiver=Receiver,
        receiver_two=Receiver_Two,
        receiver_three=Receiver_Three,
        dedup_header=Dedup_Header,
        dedup_ttl=Dedup_TTL,
        max_retries=Max_Retries,
        sleep_time=Sleep_Time,
        **out._asdict(),
    )
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_failing_message_is_retried_with_backoff_and_redelivered_in_the_next_round(
    kafka_suite:'KafkaSuite',
    names:'Names',
    ) -> 'None':
    """ With the DLQ off a message whose every attempt failed is tried again a round later, under the same cid,
    the sleeps between attempts growing with the multiplier, and the offset is committed once it goes through.
    """
    attempts_per_round = Max_Retries + 1
    kafka_suite.set_behaviour(Receiver, fail_times=attempts_per_round)

    payload = kafka_suite.new_name('payload')
    landed = produce(kafka_suite.address, names.topic_retry, payload)

    round_wait = PubSub.Delivery.Retry_Round_Wait
    expected_sleeps = [Sleep_Time * 2 ** idx for idx in range(Max_Retries)] + [round_wait]
    timeout = sum(expected_sleeps) + 30

    invocations = kafka_suite.wait_for_payload(payload, attempts_per_round + 1, timeout=timeout)

    assert [elem['outcome'] for elem in invocations] == ['failed'] * attempts_per_round + ['ok']
    assert len({elem['cid'] for elem in invocations}) == 1

    gaps = [invocations[idx + 1]['time'] - invocations[idx]['time'] for idx in range(len(invocations) - 1)]

    for gap, expected in zip(gaps, expected_sleeps):
        assert expected <= gap < expected + Gap_Slack, (gaps, expected_sleeps)

    _ = wait_until_committed(kafka_suite.address, names.group_retry, names.topic_retry, 0, landed.offset + 1)

# ################################################################################################################################

def test_a_repeat_of_a_delivered_message_is_not_delivered_again(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ Two messages with the same dedup header are one delivery, a third with another value is delivered,
    and every one of them is committed. The delivered value is remembered in Redis for the channel's TTL.
    """
    payload = kafka_suite.new_name('payload')
    repeat = kafka_suite.new_name('payload.repeat')
    other = kafka_suite.new_name('payload.other')

    dedup_value = kafka_suite.new_name('dedup')
    other_value = kafka_suite.new_name('dedup.other')

    _ = produce(kafka_suite.address, names.topic_dedup, payload, headers={Dedup_Header: dedup_value})
    _ = produce(kafka_suite.address, names.topic_dedup, repeat, headers={Dedup_Header: dedup_value})
    landed = produce(kafka_suite.address, names.topic_dedup, other, headers={Dedup_Header: other_value})

    _ = kafka_suite.wait_for_payload(payload)
    _ = kafka_suite.wait_for_payload(other)
    _ = wait_until_committed(kafka_suite.address, names.group_dedup, names.topic_dedup, 0, landed.offset + 1)

    sleep(1)
    assert not [elem for elem in kafka_suite.received() if elem['data'] == repeat]

    channel_id = kafka_suite.connection(names.channel_dedup)['id']
    key = f'{_consumer.Dedup_Key_Prefix}{channel_id}:{dedup_value}'

    assert kafka_suite.redis.exists(key)
    assert 0 < kafka_suite.redis.ttl(key) <= Dedup_TTL

# ################################################################################################################################

def test_a_slow_channel_does_not_delay_another(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ While one channel's service is busy, a message on another channel goes through at once.
    """
    slow_time = 4
    kafka_suite.set_behaviour(Receiver_Two, sleep=slow_time)

    slow_payload = kafka_suite.new_name('payload.slow')
    fast_payload = kafka_suite.new_name('payload.fast')

    start = monotonic()
    _ = produce(kafka_suite.address, names.topic_slow, slow_payload)
    _ = produce(kafka_suite.address, names.topic_fast, fast_payload)

    _ = kafka_suite.wait_for_payload(fast_payload, timeout=slow_time - 1)
    elapsed = monotonic() - start
    assert elapsed < slow_time - 1, elapsed

    assert not [elem for elem in kafka_suite.received() if elem['data'] == slow_payload]

    _ = kafka_suite.wait_for_payload(slow_payload, timeout=slow_time + 10)

# ################################################################################################################################
# ################################################################################################################################
