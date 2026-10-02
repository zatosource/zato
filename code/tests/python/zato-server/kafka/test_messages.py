# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a message carries both ways - keys, headers and metadata, several topics on one channel, routing,
# tombstones and the commit that keeps a delivered message from coming back.

# stdlib
from base64 import b64encode
from time import sleep
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import committed_offset, headers_as_text, produce, read_topic, wait_until_committed
from zato.common.api import KAFKA

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import KafkaSuite
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_header = KAFKA.Header

Receiver = 'test.kafka.receiver'
Receiver_Two = 'test.kafka.receiver.two'
Receiver_Three = 'test.kafka.receiver.three'

Route_Header = 'route-to'
Route_Value = 'three'

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
channel_kafka:
  - name: {channel}
    address: {address}
    topics:
      - {topic_a}
      - {topic_b}
    group_id: {group}
    service: {receiver}
    auto_offset_reset: earliest
    routing:
      - topic: {topic_b}
        service: {receiver_two}
      - header_name: {route_header}
        header_value: {route_value}
        service: {receiver_three}

  - name: {channel_tombstones}
    address: {address}
    topics:
      - {topic_tombstones}
    group_id: {group_tombstones}
    service: {receiver}
    auto_offset_reset: earliest
    should_deliver_tombstones: true

outgoing_kafka:
  - name: {outgoing}
    address: {address}
    topic: {topic_a}

  - name: {outgoing_tombstones}
    address: {address}
    topic: {topic_tombstones}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    channel: str
    channel_tombstones: str
    outgoing: str
    outgoing_tombstones: str
    topic_a: str
    topic_b: str
    topic_tombstones: str
    group: str
    group_tombstones: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'KafkaSuite') -> 'Names':
    """ The connections of this module, imported once.
    """
    out = Names(
        channel=kafka_suite.new_name('channel'),
        channel_tombstones=kafka_suite.new_name('channel.tombstones'),
        outgoing=kafka_suite.new_name('outgoing'),
        outgoing_tombstones=kafka_suite.new_name('outgoing.tombstones'),
        topic_a=kafka_suite.new_name('topic.a'),
        topic_b=kafka_suite.new_name('topic.b'),
        topic_tombstones=kafka_suite.new_name('topic.tombstones'),
        group=kafka_suite.new_name('group'),
        group_tombstones=kafka_suite.new_name('group.tombstones'),
    )

    for topic in (out.topic_a, out.topic_b, out.topic_tombstones):
        kafka_suite.create_topic(topic)

    yaml = _yaml.format(
        address=kafka_suite.address,
        receiver=Receiver,
        receiver_two=Receiver_Two,
        receiver_three=Receiver_Three,
        route_header=Route_Header,
        route_value=Route_Value,
        **out._asdict(),
    )
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_key_and_headers_of_a_send_reach_the_topic(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ What a service sends with a key and headers is on the topic with that key and those headers.
    """
    payload = kafka_suite.new_name('payload')
    result = kafka_suite.send(names.outgoing, payload, key='order-1', headers={'h1': 'v1', 'h2': 'v2'})

    assert result['topic'] == names.topic_a
    assert result['partition'] == 0
    assert result['offset'] >= 0

    messages = read_topic(kafka_suite.address, names.topic_a, 1, from_offset=result['offset'], partition=0)
    assert len(messages) == 1, messages

    message = messages[0]
    assert message.value == payload.encode('utf8')
    assert message.key == b'order-1'
    assert message.offset == result['offset']
    assert headers_as_text(message) == {'h1': 'v1', 'h2': 'v2'}

# ################################################################################################################################

def test_key_headers_and_metadata_of_a_topic_message_reach_the_service(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A message produced behind Zato's back arrives with its key, its headers and the kafka.* metadata,
    a header that is not text arrives base64-encoded under the .b64 suffix.
    """
    payload = kafka_suite.new_name('payload')
    binary = b'\x00\x01\xff\xfe'

    landed = produce(kafka_suite.address, names.topic_a, payload, key='order-2', headers={'h1': 'v1', 'bin': binary})

    received = kafka_suite.wait_for_payload(payload)
    item = received[0]
    headers = item['headers']

    assert item['service'] == Receiver
    assert headers['h1'] == 'v1'
    assert headers['bin' + _header.B64_Suffix] == b64encode(binary).decode('ascii')
    assert 'bin' not in headers

    assert headers[_header.Key] == 'order-2'
    assert headers[_header.Topic] == names.topic_a
    assert headers[_header.Partition] == str(landed.partition)
    assert headers[_header.Offset] == str(landed.offset)
    assert headers[_header.Is_Tombstone] == 'false'
    assert headers[_header.Channel] == names.channel
    assert int(headers[_header.Timestamp]) > 0

# ################################################################################################################################

def test_one_channel_reads_several_topics_and_routes_by_topic(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ Both topics of the channel are read, and the one with a routing rule goes to that rule's service.
    """
    payload_a = kafka_suite.new_name('payload.a')
    payload_b = kafka_suite.new_name('payload.b')

    _ = produce(kafka_suite.address, names.topic_a, payload_a)
    _ = produce(kafka_suite.address, names.topic_b, payload_b)

    received_a = kafka_suite.wait_for_payload(payload_a)
    received_b = kafka_suite.wait_for_payload(payload_b)

    assert received_a[0]['service'] == Receiver
    assert received_a[0]['headers'][_header.Topic] == names.topic_a

    assert received_b[0]['service'] == Receiver_Two
    assert received_b[0]['headers'][_header.Topic] == names.topic_b

# ################################################################################################################################

def test_routing_by_header(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A header with the rule's value picks the rule's service, any other value falls through to the channel's own.
    """
    payload_match = kafka_suite.new_name('payload.match')
    payload_other = kafka_suite.new_name('payload.other')

    _ = produce(kafka_suite.address, names.topic_a, payload_match, headers={Route_Header: Route_Value})
    _ = produce(kafka_suite.address, names.topic_a, payload_other, headers={Route_Header: 'elsewhere'})

    assert kafka_suite.wait_for_payload(payload_match)[0]['service'] == Receiver_Three
    assert kafka_suite.wait_for_payload(payload_other)[0]['service'] == Receiver

# ################################################################################################################################

def test_tombstones_are_skipped_unless_the_channel_delivers_them(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A tombstone a service sends is on the topic with no value. A channel with tombstone delivery off commits past it
    without invoking anything, a channel with it on invokes its service with an empty payload and the tombstone header.
    """
    # The outgoing side - a delete is a tombstone on the topic ..
    result = kafka_suite.send(names.outgoing, '', key='gone-1', is_tombstone=True)
    offset = result['offset']

    messages = read_topic(kafka_suite.address, names.topic_a, 1, from_offset=offset, partition=0)
    assert messages[0].value is None
    assert messages[0].key == b'gone-1'

    # .. the channel with tombstones off commits past it and invokes nothing ..
    _ = wait_until_committed(kafka_suite.address, names.group, names.topic_a, 0, offset + 1)

    def has_first_key(item:'anydict') -> 'bool':
        out = item['headers'].get(_header.Key) == 'gone-1'
        return out

    kafka_suite.not_received(has_first_key, within=1)

    # .. and the channel with tombstones on delivers it.
    landed = produce(kafka_suite.address, names.topic_tombstones, None, key='gone-2')

    def has_second_key(item:'anydict') -> 'bool':
        out = item['headers'].get(_header.Key) == 'gone-2'
        return out

    received = kafka_suite.wait_for_received(has_second_key)
    item = received[0]

    assert item['data'] == ''
    assert item['headers'][_header.Is_Tombstone] == _header.Is_Tombstone_True
    assert item['headers'][_header.Offset] == str(landed.offset)
    assert item['headers'][_header.Channel] == names.channel_tombstones

# ################################################################################################################################

def test_a_delivered_message_is_committed_and_not_delivered_again(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ Once the service took a message its offset is committed, the recv stream has nothing pending
    and the message does not come back.
    """
    payload = kafka_suite.new_name('payload')
    landed = produce(kafka_suite.address, names.topic_tombstones, payload)

    _ = kafka_suite.wait_for_payload(payload)

    committed = wait_until_committed(kafka_suite.address, names.group_tombstones, names.topic_tombstones, 0, landed.offset + 1)

    channel_id = kafka_suite.connection(names.channel_tombstones)['id']
    assert kafka_suite.pending_count(channel_id) == 0

    # The topic holds the message once, so does the receiver, and nothing else arrives.
    on_topic = read_topic(kafka_suite.address, names.topic_tombstones, committed, timeout=5)
    assert [elem for elem in on_topic if elem.value == payload.encode('utf8')] == [on_topic[landed.offset]]

    sleep(2)
    deliveries = [elem for elem in kafka_suite.received() if elem['data'] == payload]
    assert len(deliveries) == 1, deliveries

    assert committed_offset(kafka_suite.address, names.group_tombstones, names.topic_tombstones, 0) == committed

# ################################################################################################################################
# ################################################################################################################################
