# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Discovery and failover - a connection whose address names one instance alone finds the others through it, keeps
# sending after that instance is stopped and across every instance being stopped and started in turn, and a channel
# keeps receiving while its first-contact instance is down. Each of the four runs once over plaintext and once over TLS.

# stdlib
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import produce, read_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ClusterSuite
    from live_kafka.tls import KafkaTLS
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

Receiver = 'test.kafka.receiver'

# How the two transports are told apart in the names of connections and topics
Plaintext = 'plaintext'
TLS = 'tls'

Transports = (Plaintext, TLS)

# ################################################################################################################################
# ################################################################################################################################

_tls_yaml = """
    ssl: true
    ssl_ca_file: {ca_cert}
    ssl_cert_file: {client_cert}
    ssl_key_file: {client_key}
    ssl_key_password: {key_password}
"""

_yaml = """
outgoing_kafka:
  - name: {outgoing}
    address: {address}
    topic: {topic}
    max_retries: 3
    retry_sleep_time: 1
{tls}
channel_kafka:
  - name: {channel}
    address: {address}
    topics:
      - {topic}
    group_id: {group}
    service: {receiver}
    auto_offset_reset: earliest
{tls}
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    transport: str
    topic: str
    group: str
    outgoing: str
    channel: str
    tls: 'KafkaTLS | None'

# ################################################################################################################################

@pytest.fixture(scope='module')
def names_by_transport(kafka_suite:'ClusterSuite') -> 'dict[str, Names]':
    """ The connections of this module, one pair per transport, imported once - each pointing at the first instance alone.
    """
    out:'dict[str, Names]' = {}
    cluster = kafka_suite.cluster

    for transport in Transports:

        is_tls = transport == TLS
        tls = cluster.tls if is_tls else None

        names = Names(
            transport=transport,
            topic=kafka_suite.new_name(f'topic.failover.{transport}'),
            group=kafka_suite.new_name(f'group.failover.{transport}'),
            outgoing=kafka_suite.new_name(f'outgoing.failover.{transport}'),
            channel=kafka_suite.new_name(f'channel.failover.{transport}'),
            tls=tls,
        )
        kafka_suite.create_topic(names.topic)

        if tls:
            address = cluster[0].ssl_address
            tls_yaml = _tls_yaml.format(
                ca_cert=tls.ca_cert,
                client_cert=tls.client_cert,
                client_key=tls.encrypted_client_key,
                key_password=tls.key_password,
            )
        else:
            address = cluster[0].address
            tls_yaml = ''

        yaml = _yaml.format(
            address=address,
            receiver=Receiver,
            tls=tls_yaml,
            **{key: value for key, value in names._asdict().items() if key not in ('transport', 'tls')},
        )
        kafka_suite.import_yaml(yaml)

        out[transport] = names

    return out

# ################################################################################################################################
# ################################################################################################################################

def _read_all(kafka_suite:'ClusterSuite', names:'Names') -> 'list[bytes]':
    """ Every payload the topic holds, read through the instances that are up right now.
    """
    address = kafka_suite.cluster.ssl_bootstrap if names.tls else kafka_suite.bootstrap

    if names.tls:
        running = kafka_suite.cluster.running_instances()
        address = ','.join(elem.ssl_address for elem in running)

    messages = read_topic(address, names.topic, 1_000, timeout=5, tls=names.tls)
    out = [elem.value for elem in messages]

    return out

# ################################################################################################################################

def _produce(kafka_suite:'ClusterSuite', names:'Names', payload:'str') -> 'None':
    """ Writes one message behind Zato's back, through the instances that are up right now.
    """
    if names.tls:
        running = kafka_suite.cluster.running_instances()
        address = ','.join(elem.ssl_address for elem in running)
    else:
        address = kafka_suite.bootstrap

    _ = produce(address, names.topic, payload, tls=names.tls)

# ################################################################################################################################

def _assert_each_once(kafka_suite:'ClusterSuite', names:'Names', payloads:'anylist') -> 'None':
    """ The topic holds each of the payloads exactly once.
    """
    on_topic = _read_all(kafka_suite, names)

    for payload in payloads:
        assert on_topic.count(payload.encode('utf8')) == 1, (payload, on_topic)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('transport', Transports)
def test_a_connection_keeps_sending_after_its_only_named_instance_is_stopped(
    kafka_suite:'ClusterSuite',
    names_by_transport:'dict[str, Names]',
    transport:'str',
    ) -> 'None':
    """ The address names the first instance alone, yet a send still arrives once that instance is stopped, because the
    connection learnt of the others from it.
    """
    names = names_by_transport[transport]
    cluster = kafka_suite.cluster

    before = kafka_suite.new_name(f'payload.before.{transport}')
    _ = kafka_suite.send(names.outgoing, before)

    cluster.stop_instance(0)

    during = kafka_suite.new_name(f'payload.during.{transport}')
    _ = kafka_suite.send(names.outgoing, during)

    cluster.start_instance(0)
    cluster.wait_until_all_in_sync(names.topic)

    _assert_each_once(kafka_suite, names, [before, during])

# ################################################################################################################################

@pytest.mark.parametrize('transport', Transports)
def test_a_connection_keeps_sending_while_every_instance_is_stopped_and_started_in_turn(
    kafka_suite:'ClusterSuite',
    names_by_transport:'dict[str, Names]',
    transport:'str',
    ) -> 'None':
    """ A rolling restart of the whole cluster loses nothing and doubles nothing.
    """
    names = names_by_transport[transport]
    cluster = kafka_suite.cluster
    payloads:'anylist' = []

    for instance in cluster.instances:

        cluster.stop_instance(instance.index)

        payload = kafka_suite.new_name(f'payload.rolling.{instance.index}.{transport}')
        _ = kafka_suite.send(names.outgoing, payload)
        payloads.append(payload)

        cluster.start_instance(instance.index)
        cluster.wait_until_all_in_sync(names.topic)

    _assert_each_once(kafka_suite, names, payloads)

# ################################################################################################################################

@pytest.mark.parametrize('transport', Transports)
def test_a_channel_keeps_receiving_while_its_only_named_instance_is_down(
    kafka_suite:'ClusterSuite',
    names_by_transport:'dict[str, Names]',
    transport:'str',
    ) -> 'None':
    """ The channel's address names the first instance alone - messages written while it is down still reach the service,
    and so do the ones written once it is back.
    """
    names = names_by_transport[transport]
    cluster = kafka_suite.cluster

    before = kafka_suite.new_name(f'payload.channel.before.{transport}')
    _produce(kafka_suite, names, before)
    _ = kafka_suite.wait_for_payload(before)

    cluster.stop_instance(0)

    during = kafka_suite.new_name(f'payload.channel.during.{transport}')
    _produce(kafka_suite, names, during)
    _ = kafka_suite.wait_for_payload(during)

    cluster.start_instance(0)
    cluster.wait_until_all_in_sync(names.topic)

    after = kafka_suite.new_name(f'payload.channel.after.{transport}')
    _produce(kafka_suite, names, after)
    _ = kafka_suite.wait_for_payload(after)

    # Each reached the service once
    received = kafka_suite.received(Receiver)
    for payload in (before, during, after):
        assert len([elem for elem in received if elem['data'] == payload]) == 1, received

# ################################################################################################################################
# ################################################################################################################################
