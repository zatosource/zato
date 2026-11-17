# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from base64 import b64encode
from time import monotonic

# gevent
import gevent
from gevent import sleep

# Zato
from pubsub_rest.documents import get_production_documents
from pubsub_rest.runner import run_cleanup_once
from pubsub_rest.transport import RESTClient
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer
    from pubsub_rest.transport import Credentials
    from zato.common.typing_ import any_, anydict, anylist, floatlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The size budget of one pull, which is the largest that the REST interface accepts and which a document of 10 MB fits in.
_max_len = 20_000_000

# How many messages one pull returns at most.
_max_messages = 1000

# Documents at least this large are the ones the budget is checked with.
_large_document_min_size = 9_000_000

# How many of the large documents one partner receives.
_large_document_count = 3

# How many callers publish to the topics of the topic scenario at the same time.
_topic_publisher_count = 200

# How many messages the fan-out topic receives and how many callers pull for its subscribers at once.
_fan_out_message_count = 20
_fan_out_puller_count = 100

# How many messages the mixed scenario publishes, with the priorities and expirations it cycles through, in seconds.
_mixed_message_count = 100
_priority_count = 10
_short_expiration = 1
_long_expiration = 3_600

# How much binary data one binary message holds, in bytes.
_binary_size = 1_000_000

# The share of the publications whose duration is at most the reported percentile.
_percentile = 0.99

# ################################################################################################################################
# ################################################################################################################################

def _as_received(data:'str') -> 'any_':
    """ The data of a message as a pull returns it, which is the JSON document it holds, if it holds one.
    """
    try:
        out = json.loads(data)
    except ValueError:
        out = data

    return out

# ################################################################################################################################

class _Publisher:
    """ Publishes messages and keeps the size of each, by its msg_id.
    """
    def __init__(self, server:'PubSubServer') -> 'None':
        self.base_url = server.base_url
        self.credentials:'Credentials' = server.properties['publisher']
        self.sizes:'anydict' = {}

    def new_client(self) -> 'RESTClient':
        out = RESTClient(self.base_url, self.credentials)
        return out

    def publish(self, client:'RESTClient', topic_name:'str', data:'str', **fields:'any_') -> 'str':
        response = client.publish(topic_name, {'data': data, **fields})

        out = response['msg_id']
        self.sizes[out] = len(data.encode('utf8'))

        return out

# ################################################################################################################################

def _pull_all(server:'PubSubServer', publisher:'_Publisher', credentials:'Credentials') -> 'anylist':
    """ Pulls everything in the queue of one subscriber, checking that each batch is within the size budget,
    unless it is a single message larger than the budget.
    """
    client = RESTClient(server.base_url, credentials)
    out:'anylist' = []

    while True:
        response = client.pull(_max_messages, _max_len)
        messages = response['messages']

        if not messages:
            break

        total_len = 0
        msg_ids:'strlist' = []

        for message in messages:
            msg_id = message['meta']['msg_id']
            msg_ids.append(msg_id)
            total_len += publisher.sizes[msg_id]

        assert total_len <= _max_len or len(messages) == 1, total_len

        _ = client.ack(msg_ids)
        out.extend(messages)

    client.close()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_large_documents_flow(server:'PubSubServer', publisher:'_Publisher') -> 'None':
    """ Documents of 10 MB reach the partner intact, in batches within the 20 MB budget.
    """
    topic_name = 'shapes.large'

    large:'strlist' = []

    for document in get_production_documents():
        if len(document) >= _large_document_min_size:
            large.append(document)

    assert large, 'No large documents in the production mix'

    client = publisher.new_client()
    expected:'anylist' = []

    for index in range(_large_document_count):
        document = large[index % len(large)]
        expected.append(_as_received(document))
        _ = publisher.publish(client, topic_name, document)

    client.close()

    received:'anylist' = []

    for message in _pull_all(server, publisher, server.properties[topic_name]):
        received.append(message['data'])

    assert received == expected

# ################################################################################################################################

def _run_binary_flow(server:'PubSubServer', publisher:'_Publisher') -> 'None':
    """ Binary content in base64 and text with control characters and characters outside of the BMP
    reach the subscriber byte for byte.
    """
    topic_name = 'shapes.binary'

    binary = os.urandom(_binary_size)

    payloads:'strlist' = [
        b64encode(binary).decode('ascii'),
        '\x01\x02\x03\x1f\x7f control characters',
        'Zażółć gęślą jaźń - Ελληνικά - 日本語 - \U0001F4E6\U0001F69A',
        '{"emoji": "\\ud83d\\udce6", "escaped_nul": "\\u0000"}',
    ]

    client = publisher.new_client()
    expected:'anylist' = []

    for payload in payloads:
        expected.append(_as_received(payload))
        _ = publisher.publish(client, topic_name, payload)

    client.close()

    received:'anylist' = []

    for message in _pull_all(server, publisher, server.properties[topic_name]):
        received.append(message['data'])

    assert received == expected

# ################################################################################################################################

def _publish_to_topics(publisher:'_Publisher', topic_names:'strlist', first:'int', step:'int') -> 'floatlist':
    client = publisher.new_client()
    out:'floatlist' = []

    for index in range(first, len(topic_names), step):
        started = monotonic()
        _ = publisher.publish(client, topic_names[index], f'topic-message-{index}')
        out.append(monotonic() - started)

    client.close()

    return out

# ################################################################################################################################

def _run_many_topics_flow(server:'PubSubServer', publisher:'_Publisher') -> 'float':
    """ One subscriber of 10,000 topics receives one message from each of them, published concurrently.
    Returns the p99 of the publications, in seconds.
    """
    topic_names:'strlist' = server.properties['topic_names']

    greenlets:'anylist' = []

    for first in range(_topic_publisher_count):
        greenlet = gevent.spawn(_publish_to_topics, publisher, topic_names, first, _topic_publisher_count)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    durations:'floatlist' = []
    for greenlet in greenlets:
        durations.extend(greenlet.value)

    durations.sort()
    p99 = durations[int(len(durations) * _percentile)]

    received_topics:'strlist' = []

    for message in _pull_all(server, publisher, server.properties['shapes.topics']):
        received_topics.append(message['meta']['topic_name'])

    assert sorted(received_topics) == topic_names

    return p99

# ################################################################################################################################

def _pull_subscribers(
    server:'PubSubServer',
    publisher:'_Publisher',
    subscribers:'list[Credentials]',
    first:'int',
    step:'int',
    ) -> 'anydict':

    out:'anydict' = {}

    for index in range(first, len(subscribers), step):
        credentials = subscribers[index]
        out[credentials.username] = _pull_all(server, publisher, credentials)

    return out

# ################################################################################################################################

def _run_fan_out_flow(server:'PubSubServer', publisher:'_Publisher') -> 'None':
    """ Each of 1,000 subscribers of one topic receives every message once, and each message
    loses its payload once the last subscriber received it.
    """
    topic_name = server.properties['fan_out_topic']
    subscribers:'list[Credentials]' = server.properties['fan_out']

    documents = get_production_documents()
    client = publisher.new_client()
    expected:'anylist' = []

    for index in range(_fan_out_message_count):
        document = documents[index % len(documents)]
        if len(document) >= _large_document_min_size:
            document = documents[0]
        expected.append(_as_received(document))
        _ = publisher.publish(client, topic_name, document)

    client.close()

    greenlets:'anylist' = []

    for first in range(_fan_out_puller_count):
        greenlet = gevent.spawn(_pull_subscribers, server, publisher, subscribers, first, _fan_out_puller_count)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    received_count = 0

    for greenlet in greenlets:
        for username, messages in greenlet.value.items():

            received:'anylist' = []
            for message in messages:
                received.append(message['data'])

            assert received == expected, username
            received_count += 1

    assert received_count == len(subscribers)

    # Every message was received by all its subscribers, so none of them keeps its payload.
    rows = server.get_topic_rows(topic_name)
    assert rows['payloads'] == 0, rows

# ################################################################################################################################

def _run_mixed_flow(server:'PubSubServer', publisher:'_Publisher') -> 'None':
    """ Messages of mixed priorities and expirations are received highest priority first, in the order
    of publication within one priority, the expired ones are not received, and the cleanup removes them.
    """
    topic_name = 'shapes.mixed'

    client = publisher.new_client()
    live:'list[tuple[int, int, str]]' = []

    for index in range(_mixed_message_count):

        priority = index % _priority_count

        if index % 2:
            expiration = _short_expiration
        else:
            expiration = _long_expiration

        msg_id = publisher.publish(client, topic_name, f'mixed-message-{index}', priority=priority, expiration=expiration)

        if expiration == _long_expiration:
            live.append((-priority, index, msg_id))

    client.close()

    sleep(_short_expiration * 2)

    live.sort()

    expected:'strlist' = []
    for _ignored_priority, _ignored_index, msg_id in live:
        expected.append(msg_id)

    received:'strlist' = []
    for message in _pull_all(server, publisher, server.properties[topic_name]):
        received.append(message['meta']['msg_id'])

    assert received == expected

    # The cleanup removes the expired messages, which nobody received, so what is left are the traces of the live ones,
    # each of which was received and therefore keeps no payload.
    run_cleanup_once()

    rows = server.get_topic_rows(topic_name)

    assert rows['messages'] == len(live), rows
    assert rows['payloads'] == 0, rows

# ################################################################################################################################
# ################################################################################################################################

def test_data_shapes(server:'PubSubServer') -> 'None':
    """ Documents of 10 MB at the 20 MB budget, binary content, 10,000 topics, fan-out to 1,000 subscribers,
    and mixed priorities and expirations, each received intact and in order, with the counts equal to the rows.
    """
    measurement = start_measurement(server.get_client(), server.get_database())
    publisher = _Publisher(server)

    _run_large_documents_flow(server, publisher)
    _run_binary_flow(server, publisher)
    _run_mixed_flow(server, publisher)
    many_topics_p99 = _run_many_topics_flow(server, publisher)
    _run_fan_out_flow(server, publisher)

    _ = report_result(measurement, 'pubsub-data-shapes', {'many_topics_publish_p99_seconds': many_topics_p99})

    mismatches = server.get_count_mismatches()
    assert not mismatches, mismatches

# ################################################################################################################################
# ################################################################################################################################
