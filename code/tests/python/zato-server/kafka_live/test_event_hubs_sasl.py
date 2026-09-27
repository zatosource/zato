# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from typing import NamedTuple

# Zato
from live_kafka.event_hubs import ModuleCtx as EventHubsCtx
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import KafkaLiveEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The service the test drives from the outside
    Invoke_Service = 'test.kafka.live.invoke'

    # The service the channels route to
    Receiver_Service = 'test.kafka.live.receiver'

    # How long a freshly imported connection has to reach Event Hubs
    Propagation_Timeout       = 300
    Propagation_Poll_Interval = 3

    # How long a message sent has to come back through the channel
    Delivery_Timeout       = 120
    Delivery_Poll_Interval = 1

    # How long the deployed services have to appear
    Deploy_Timeout       = 60
    Deploy_Poll_Interval = 1

# ################################################################################################################################
# ################################################################################################################################

_plain_yaml = """
security:
  - name: {security_name}
    type: basic_auth
    username: {username}
    password: {password}
    realm: zato

channel_kafka:
  - name: {channel_name}
    address: {address}
    topic: {topic}
    group_id: {group_id}
    service: {service}
    security: {security_name}
    sasl_mechanism: PLAIN
    ssl: true

outgoing_kafka:
  - name: {outgoing_name}
    address: {address}
    topic: {topic}
    security: {security_name}
    sasl_mechanism: PLAIN
    ssl: true
"""

_oauth_yaml = """
security:
  - name: {security_name}
    type: bearer_token
    username: {username}
    password: {password}
    auth_endpoint: {token_url}
    scopes: {scope}

channel_kafka:
  - name: {channel_name}
    address: {address}
    topic: {topic}
    group_id: {group_id}
    service: {service}
    security: {security_name}
    sasl_mechanism: OAUTHBEARER
    ssl: true

outgoing_kafka:
  - name: {outgoing_name}
    address: {address}
    topic: {topic}
    security: {security_name}
    sasl_mechanism: OAUTHBEARER
    ssl: true
"""

# ################################################################################################################################
# ################################################################################################################################

def _invoke(client:'AdminClient', mode:'str', **fields:'str') -> 'anydict':
    """ One call to the invoker service deployed to the test server.
    """
    request = {'mode': mode, **fields}

    out = client.invoke(ModuleCtx.Invoke_Service, request)
    return out

# ################################################################################################################################

def _wait_until_deployed(client:'AdminClient') -> 'None':
    """ Waits for the hot-deployed invoker to answer.
    """
    now = time.monotonic()
    deadline = now + ModuleCtx.Deploy_Timeout

    while time.monotonic() < deadline:
        try:
            _ = _invoke(client, 'ping')
        except Exception:
            time.sleep(ModuleCtx.Deploy_Poll_Interval)
        else:
            return

    raise Exception(f'Service {ModuleCtx.Invoke_Service} did not deploy within {ModuleCtx.Deploy_Timeout}s')

# ################################################################################################################################

def _wait_until_pingable(client:'AdminClient', outgoing_name:'str', mechanism:'str') -> 'None':
    """ Retries the ping until the freshly imported connection reaches Event Hubs, or fails with the last error.
    """
    now = time.monotonic()
    timeout = ModuleCtx.Propagation_Timeout
    deadline = now + timeout
    last_error = ''

    while time.monotonic() < deadline:
        response = _invoke(client, 'ping-connection', connection=outgoing_name)

        if response['is_ok']:
            return

        last_error = response['error']
        time.sleep(ModuleCtx.Propagation_Poll_Interval)

    msg = f'Connection {outgoing_name} ({mechanism}) could not be pinged within {timeout}s, last error: {last_error}'
    raise Exception(msg)

# ################################################################################################################################

def _send_until_accepted(client:'AdminClient', outgoing_name:'str', mechanism:'str', payload:'str') -> 'None':
    """ Retries the send until the broker accepts it, or fails with the last error.
    """
    now = time.monotonic()
    timeout = ModuleCtx.Propagation_Timeout
    deadline = now + timeout
    last_error = ''

    while time.monotonic() < deadline:
        response = _invoke(client, 'send', connection=outgoing_name, payload=payload)

        if response['is_ok']:
            return

        last_error = response['error']
        time.sleep(ModuleCtx.Propagation_Poll_Interval)

    msg = f'Connection {outgoing_name} ({mechanism}) rejected every message for {timeout}s, last error: {last_error}'
    raise Exception(msg)

# ################################################################################################################################

def _wait_until_received(client:'AdminClient', channel_name:'str', mechanism:'str', marker:'str') -> 'None':
    """ Waits for the marker to come back through the channel into the receiver service.
    """
    now = time.monotonic()
    timeout = ModuleCtx.Delivery_Timeout
    deadline = now + timeout

    while time.monotonic() < deadline:
        response = _invoke(client, 'get-received')
        received = response['received']

        if marker in received:
            return

        time.sleep(ModuleCtx.Delivery_Poll_Interval)

    msg = f'Channel {channel_name} ({mechanism}) did not deliver marker {marker} within {timeout}s'
    raise Exception(msg)

# ################################################################################################################################

class Names(NamedTuple):
    """ What one case calls the objects it imports.
    """
    mechanism: str
    security_name: str
    channel_name: str
    outgoing_name: str
    group_id: str

# ################################################################################################################################

def _new_names(mechanism:'str') -> 'Names':
    """ Names for one mechanism with a random suffix.
    """
    suffix = CryptoManager.generate_hex_string()

    out = Names(
        mechanism=mechanism,
        security_name=f'test.kafka.live.security.{mechanism}.{suffix}',
        channel_name=f'test.kafka.live.channel.{mechanism}.{suffix}',
        outgoing_name=f'test.kafka.live.outgoing.{mechanism}.{suffix}',
        group_id=f'zato-test-{mechanism}-{suffix}',
    )

    return out

# ################################################################################################################################

def _run_round_trip(kafka_live:'KafkaLiveEnvironment', names:'Names', yaml:'str') -> 'None':
    """ Imports the definitions, pings the outgoing connection, sends one message and waits for it to come back.
    """
    # Wait for the invoker to answer ..
    client = kafka_live.zato.client()
    _wait_until_deployed(client)

    # .. import the definitions ..
    file_name = f'kafka_live_{names.mechanism}.yaml'
    _ = kafka_live.zato.import_yaml(file_name, yaml)

    # .. ping until the connection is reachable ..
    _wait_until_pingable(client, names.outgoing_name, names.mechanism)

    # .. send one message ..
    _ = _invoke(client, 'clear-received')

    suffix = CryptoManager.generate_hex_string()
    marker = f'zato-kafka-live-{names.mechanism}-{suffix}'
    _send_until_accepted(client, names.outgoing_name, names.mechanism, marker)

    # .. and wait for it to come back.
    _wait_until_received(client, names.channel_name, names.mechanism, marker)

# ################################################################################################################################
# ################################################################################################################################

def test_plain_round_trip(kafka_live:'KafkaLiveEnvironment') -> 'None':
    """ A message sent under SASL PLAIN comes back through a channel using the same credentials.
    """
    event_hubs = kafka_live.event_hubs
    names = _new_names('plain')

    yaml = _plain_yaml.format(
        security_name=names.security_name,
        username=EventHubsCtx.Plain_Username,
        password=event_hubs.connection_string,
        channel_name=names.channel_name,
        outgoing_name=names.outgoing_name,
        address=event_hubs.bootstrap_address,
        topic=event_hubs.hub,
        group_id=names.group_id,
        service=ModuleCtx.Receiver_Service,
    )

    _run_round_trip(kafka_live, names, yaml)

# ################################################################################################################################

def test_oauthbearer_round_trip(kafka_live:'KafkaLiveEnvironment') -> 'None':
    """ A message sent under SASL OAUTHBEARER comes back through a channel using the same principal.
    """
    event_hubs = kafka_live.event_hubs
    names = _new_names('oauthbearer')

    yaml = _oauth_yaml.format(
        security_name=names.security_name,
        username=event_hubs.app_id,
        password=event_hubs.client_secret,
        token_url=event_hubs.token_url,
        scope=event_hubs.scope,
        channel_name=names.channel_name,
        outgoing_name=names.outgoing_name,
        address=event_hubs.bootstrap_address,
        topic=event_hubs.hub,
        group_id=names.group_id,
        service=ModuleCtx.Receiver_Service,
    )

    _run_round_trip(kafka_live, names, yaml)

# ################################################################################################################################
# ################################################################################################################################
