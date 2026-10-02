# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The producer settings of an outgoing connection - every compression type, confirmations and exactly once,
# and the TLS listener with the encrypted client key and its password.

# stdlib
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import read_topic
from zato.common.api import KAFKA

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import KafkaSuite

# ################################################################################################################################
# ################################################################################################################################

Receiver = 'test.kafka.receiver'

Compression_Types = tuple(elem.id for elem in KAFKA.COMPRESSION())

# ################################################################################################################################
# ################################################################################################################################

_compression_yaml = """
  - name: {name}
    address: {address}
    topic: {topic}
    compression: {compression}
"""

_yaml = """
outgoing_kafka:
{compression_connections}
  - name: {outgoing_one}
    address: {address}
    topic: {topic}
    acks: 1
    is_idempotent: false

  - name: {outgoing_none}
    address: {address}
    topic: {topic}
    acks: 0
    is_idempotent: false

  - name: {outgoing_exactly_once}
    address: {address}
    topic: {topic}
    acks: 1
    is_idempotent: true

  - name: {outgoing_tls}
    address: {ssl_address}
    topic: {topic_tls}
    ssl: true
    ssl_ca_file: {ca_cert}
    ssl_cert_file: {client_cert}
    ssl_key_file: {client_key}
    ssl_key_password: {key_password}

  - name: {outgoing_tls_wrong_password}
    address: {ssl_address}
    topic: {topic_tls}
    ssl: true
    ssl_ca_file: {ca_cert}
    ssl_cert_file: {client_cert}
    ssl_key_file: {client_key}
    ssl_key_password: not-the-password
    send_timeout: 3

channel_kafka:
  - name: {channel_tls}
    address: {ssl_address}
    topics:
      - {topic_tls}
    group_id: {group_tls}
    service: {receiver}
    auto_offset_reset: earliest
    ssl: true
    ssl_ca_file: {ca_cert}
    ssl_cert_file: {client_cert}
    ssl_key_file: {client_key}
    ssl_key_password: {key_password}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    topic: str
    topic_tls: str
    group_tls: str
    outgoing_one: str
    outgoing_none: str
    outgoing_exactly_once: str
    outgoing_tls: str
    outgoing_tls_wrong_password: str
    channel_tls: str
    compression: 'dict[str, str]'

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'KafkaSuite') -> 'Names':
    """ The connections of this module, imported once.
    """
    compression = {elem: kafka_suite.new_name(f'outgoing.{elem}') for elem in Compression_Types}

    out = Names(
        topic=kafka_suite.new_name('topic.producer'),
        topic_tls=kafka_suite.new_name('topic.tls'),
        group_tls=kafka_suite.new_name('group.tls'),
        outgoing_one=kafka_suite.new_name('outgoing.acks.one'),
        outgoing_none=kafka_suite.new_name('outgoing.acks.none'),
        outgoing_exactly_once=kafka_suite.new_name('outgoing.exactly.once'),
        outgoing_tls=kafka_suite.new_name('outgoing.tls'),
        outgoing_tls_wrong_password=kafka_suite.new_name('outgoing.tls.wrong'),
        channel_tls=kafka_suite.new_name('channel.tls'),
        compression=compression,
    )

    kafka_suite.create_topic(out.topic)
    kafka_suite.create_topic(out.topic_tls)

    compression_connections = ''.join(
        _compression_yaml.format(name=name, address=kafka_suite.address, topic=out.topic, compression=elem)
        for elem, name in compression.items()
    )

    tls = kafka_suite.kafka.tls
    fields = out._asdict()
    _ = fields.pop('compression')

    yaml = _yaml.format(
        address=kafka_suite.address,
        ssl_address=kafka_suite.ssl_address,
        receiver=Receiver,
        compression_connections=compression_connections,
        ca_cert=tls.ca_cert,
        client_cert=tls.client_cert,
        client_key=tls.encrypted_client_key,
        key_password=tls.key_password,
        **fields,
    )
    kafka_suite.import_yaml(yaml)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _assert_on_topic(kafka_suite:'KafkaSuite', topic:'str', payload:'str') -> 'None':
    """ The payload is on the topic exactly once.
    """
    messages = read_topic(kafka_suite.address, topic, 1_000, timeout=5)
    found = [elem for elem in messages if elem.value == payload.encode('utf8')]

    assert len(found) == 1, found

# ################################################################################################################################

@pytest.mark.parametrize('compression', Compression_Types)
def test_each_compression_type_delivers(kafka_suite:'KafkaSuite', names:'Names', compression:'str') -> 'None':
    """ A message sent with each codec is on the topic as it was sent.
    """
    payload = kafka_suite.new_name(f'payload.{compression}') * 20
    result = kafka_suite.send(names.compression[compression], payload)

    messages = read_topic(kafka_suite.address, names.topic, 1, from_offset=result['offset'], partition=0)
    assert messages[0].value == payload.encode('utf8')

# ################################################################################################################################

def test_one_confirmation(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A send waiting for one Kafka instance only comes back with where the message landed.
    """
    payload = kafka_suite.new_name('payload.one')
    result = kafka_suite.send(names.outgoing_one, payload)

    assert result['offset'] >= 0
    _assert_on_topic(kafka_suite, names.topic, payload)

# ################################################################################################################################

def test_no_confirmation(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A send that waits for no confirmation succeeds and the message still reaches the topic,
    though where it landed is not known.
    """
    payload = kafka_suite.new_name('payload.none')
    result = kafka_suite.send(names.outgoing_none, payload)

    assert result['is_ok']
    _assert_on_topic(kafka_suite, names.topic, payload)

# ################################################################################################################################

def test_exactly_once_sends_once(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ With exactly once on, a connection set to one confirmation still delivers - the bridge raises the confirmations
    to all Kafka instances, which exactly once needs - and the topic holds the message once.
    """
    payload = kafka_suite.new_name('payload.exactly.once')
    result = kafka_suite.send(names.outgoing_exactly_once, payload)

    assert result['offset'] >= 0
    _assert_on_topic(kafka_suite, names.topic, payload)

# ################################################################################################################################

def test_tls_with_the_encrypted_key_and_its_password(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A send over the TLS listener with the password-protected client key reaches a channel reading over TLS the same way.
    """
    payload = kafka_suite.new_name('payload.tls')
    result = kafka_suite.send(names.outgoing_tls, payload)

    assert result['offset'] >= 0

    received = kafka_suite.wait_for_payload(payload)
    assert received[0]['headers'][KAFKA.Header.Channel] == names.channel_tls

# ################################################################################################################################

def test_tls_with_the_wrong_key_password_does_not_connect(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A connection whose key password is wrong can neither be pinged nor send.
    """
    ping = kafka_suite.invoke('ping-connection', connection=names.outgoing_tls_wrong_password)
    assert not ping['is_ok'], ping

    payload = kafka_suite.new_name('payload.tls.wrong')
    result = kafka_suite.invoke('send', connection=names.outgoing_tls_wrong_password, payload=payload)
    assert not result['is_ok'], result

# ################################################################################################################################
# ################################################################################################################################
