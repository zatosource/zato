# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from hashlib import sha256
from time import monotonic

# gevent
import gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import text

# Zato
from production_documents import get_production_documents
from runner import get_count_mismatches
from zato.common.api import PubSub
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The size budget of one fetch, which a document of 10 MB has to fit in.
_max_len = PubSub.Message.Default_Max_Len

# Documents at least this large are the ones the budget is checked with.
_large_document_min_size = 9_000_000

# How many of the large documents one partner receives.
_large_document_count = 5

# How many topics the topic scenario uses, and how many callers publish to them at the same time.
_topic_count = 10_000
_topic_publisher_count = 200

# How many subscribers one topic fans out to, how many messages it receives and how many subscribers pull at once.
_fan_out_subscriber_count = 1_000
_fan_out_message_count = 20
_fan_out_puller_count = 100

# The priorities and expirations the mixed scenario cycles through, in seconds.
_mixed_message_count = 100
_short_expiration = 1
_long_expiration = 3_600

# How much binary data one binary message holds, in bytes.
_binary_size = 1_000_000

# ################################################################################################################################
# ################################################################################################################################

def _digest(data:'str') -> 'str':
    out = sha256(data.encode('utf8')).hexdigest()
    return out

# ################################################################################################################################

def _pull_all(backend:'SQLPubSubBackend', sub_key:'str') -> 'anylist':
    """ Pulls everything in one subscriber's queue, checking that each batch is within the size budget,
    unless it is a single message larger than the budget.
    """
    out:'anylist' = []

    while True:
        messages = backend.pull_messages(sub_key, max_messages=1000)

        if not messages:
            break

        total_len = 0
        for message in messages:
            total_len += len(message['data'])

        assert total_len <= _max_len or len(messages) == 1, total_len

        out.extend(messages)

    return out

# ################################################################################################################################

def _run_large_documents_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Documents of 10 MB reach the partner intact, in batches within the 20 MB budget.
    """
    topic_name = 'shapes.large'
    sub_key = 'zpsk.shapes.large'

    backend.subscribe(sub_key, topic_name)

    large:'strlist' = []

    for document in get_production_documents():
        if len(document) >= _large_document_min_size:
            large.append(document)

    assert large, 'No large documents in the production mix'

    digests:'strlist' = []

    for index in range(_large_document_count):
        document = large[index % len(large)]
        digests.append(_digest(document))
        _ = backend.publish(topic_name, document)

    received:'strlist' = []

    for message in _pull_all(backend, sub_key):
        received.append(_digest(message['data']))

    assert received == digests

# ################################################################################################################################

def _run_binary_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Binary content in base64 and text with control characters and characters outside of the BMP
    reach the subscriber byte for byte.
    """
    topic_name = 'shapes.binary'
    sub_key = 'zpsk.shapes.binary'

    backend.subscribe(sub_key, topic_name)

    binary = CryptoManager.generate_bytes(_binary_size)

    payloads:'strlist' = [
        b64encode(binary).decode('ascii'),
        '\x01\x02\x03\x1f\x7f control characters',
        'Zażółć gęślą jaźń - Ελληνικά - 日本語 - \U0001F4E6\U0001F69A',
        '{"emoji": "\\ud83d\\udce6", "escaped_nul": "\\u0000"}',
    ]

    for payload in payloads:
        _ = backend.publish(topic_name, payload)

    received:'strlist' = []

    for message in _pull_all(backend, sub_key):
        received.append(message['data'])

    assert received == payloads

# ################################################################################################################################

def _publish_to_topics(backend:'SQLPubSubBackend', topic_names:'strlist', first:'int', step:'int') -> 'list[float]':
    out:'list[float]' = []

    for index in range(first, len(topic_names), step):
        started = monotonic()
        _ = backend.publish(topic_names[index], f'topic-message-{index}')
        out.append(monotonic() - started)

    return out

# ################################################################################################################################

def _run_many_topics_flow(backend:'SQLPubSubBackend') -> 'None':
    """ One subscriber of 10,000 topics receives one message from each of them, published concurrently.
    """
    sub_key = 'zpsk.shapes.topics'

    topic_names:'strlist' = []

    for index in range(_topic_count):
        topic_name = f'shapes.topics.{index:05d}'
        topic_names.append(topic_name)
        backend.subscribe(sub_key, topic_name)

    greenlets:'anylist' = []

    for first in range(_topic_publisher_count):
        greenlet = gevent.spawn(_publish_to_topics, backend, topic_names, first, _topic_publisher_count)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    durations:'list[float]' = []
    for greenlet in greenlets:
        durations.extend(greenlet.value)

    durations.sort()
    p99 = durations[int(len(durations) * 0.99)]
    print(f'Publication to {_topic_count} topics, p99 {p99 * 1000:.0f} ms', flush=True)

    received_topics:'strlist' = []

    for message in _pull_all(backend, sub_key):
        received_topics.append(message['topic_name'])

    assert sorted(received_topics) == topic_names

# ################################################################################################################################

def _pull_subscribers(backend:'SQLPubSubBackend', sub_keys:'strlist', first:'int', step:'int') -> 'anydict':
    out:'anydict' = {}

    for index in range(first, len(sub_keys), step):
        sub_key = sub_keys[index]
        out[sub_key] = _pull_all(backend, sub_key)

    return out

# ################################################################################################################################

def _run_fan_out_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Each of 1,000 subscribers of one topic receives every message once, and each message
    loses its payload once the last subscriber received it.
    """
    topic_name = 'shapes.fan-out'

    sub_keys:'strlist' = []

    for index in range(_fan_out_subscriber_count):
        sub_key = f'zpsk.shapes.fan-out.{index:04d}'
        sub_keys.append(sub_key)
        backend.subscribe(sub_key, topic_name)

    documents = get_production_documents()
    expected:'strlist' = []

    for index in range(_fan_out_message_count):
        document = documents[index % len(documents)]
        if len(document) >= _large_document_min_size:
            document = documents[0]
        expected.append(_digest(document))
        _ = backend.publish(topic_name, document)

    greenlets:'anylist' = []

    for first in range(_fan_out_puller_count):
        greenlet = gevent.spawn(_pull_subscribers, backend, sub_keys, first, _fan_out_puller_count)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    received_count = 0

    for greenlet in greenlets:
        for sub_key, messages in greenlet.value.items():

            digests:'strlist' = []
            for message in messages:
                digests.append(_digest(message['data']))

            assert digests == expected, sub_key
            received_count += 1

    assert received_count == _fan_out_subscriber_count

    # Every message was received by all its subscribers, so none of them keeps its payload.
    with backend.engine.connect() as connection:
        query = text('select count(*) from pubsub_message where topic_name = :topic_name and payload is not null')
        with_payload = connection.execute(query, {'topic_name': topic_name}).scalar_one()

    assert with_payload == 0

# ################################################################################################################################

def _run_mixed_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Messages of mixed priorities and expirations are received highest priority first, in the order
    of publication within one priority, the expired ones are not received, and the cleanup removes them.
    """
    topic_name = 'shapes.mixed'
    sub_key = 'zpsk.shapes.mixed'

    backend.subscribe(sub_key, topic_name)

    live:'list[tuple[int, int, str]]' = []

    for index in range(_mixed_message_count):

        priority = index % 10

        if index % 2:
            expiration = _short_expiration
        else:
            expiration = _long_expiration

        result = backend.publish(topic_name, f'mixed-message-{index}', priority=priority, expiration=expiration)

        if expiration == _long_expiration:
            live.append((-priority, index, result.msg_id))

    sleep(_short_expiration * 2)

    live.sort()

    expected:'strlist' = []
    for _ignored_priority, _ignored_index, msg_id in live:
        expected.append(msg_id)

    received:'strlist' = []
    for message in _pull_all(backend, sub_key):
        received.append(message['msg_id'])

    assert received == expected

    # The cleanup removes the expired messages, which nobody received ..
    swept = PubSubCleanup().sweep_once()
    assert swept['expired'] >= _mixed_message_count // 2, swept

    with backend.engine.connect() as connection:
        query = text('select count(*) from pubsub_message where topic_name = :topic_name and payload is not null')
        with_payload = connection.execute(query, {'topic_name': topic_name}).scalar_one()

    # .. and every live message was received, so none of them keeps its payload.
    assert with_payload == 0

# ################################################################################################################################
# ################################################################################################################################

def test_data_shapes(stability_env:'strstrdict') -> 'None':
    """ Documents of 10 MB at the 20 MB budget, binary content, 10,000 topics, fan-out to 1,000 subscribers,
    and mixed priorities and expirations, each received intact and in order, with the counts equal to the rows.
    """
    backend = SQLPubSubBackend()
    backend.take_over()

    _run_large_documents_flow(backend)
    _run_binary_flow(backend)
    _run_mixed_flow(backend)
    _run_many_topics_flow(backend)
    _run_fan_out_flow(backend)

    mismatches = get_count_mismatches()
    assert not mismatches, mismatches

# ################################################################################################################################
# ################################################################################################################################
