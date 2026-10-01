# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from datetime import datetime, timezone

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# Live Fabric
from live_fabric.common import ModuleCtx as FabricCtx
from live_fabric.render import events_objects

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FabricLiveEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The service the tests drive from the outside
    Invoke_Service = 'test.fabric.events.invoke'

    # The service the alerts channel routes to
    Receiver_Service = 'test.fabric.events.receiver'

    # The Fabric connection deployed to the test server, the one the eventhouse queries go through
    Connection_Name = 'test.fabric.main'

    # How long a freshly imported connection has to reach the eventstream
    Propagation_Timeout       = 300
    Propagation_Poll_Interval = 3

    # How long an event has to come back through the alerts channel
    Delivery_Timeout       = 180
    Delivery_Poll_Interval = 2

    # How long an event has to show up in the eventhouse
    Ingestion_Timeout       = 600
    Ingestion_Poll_Interval = 10

# ################################################################################################################################
# ################################################################################################################################

def _invoke(client:'AdminClient', mode:'str', **fields:'object') -> 'anydict':
    """ One call to the invoker service deployed to the test server.
    """
    request = {'mode': mode, **fields}

    out = client.invoke(ModuleCtx.Invoke_Service, request)
    return out

# ################################################################################################################################

def _wait_until_pingable(client:'AdminClient', connection:'str'=FabricCtx.Events_Outgoing_Name) -> 'None':
    """ Retries the ping until the outgoing connection reaches the eventstream, or fails with the last error.
    """
    now = time.monotonic()
    timeout = ModuleCtx.Propagation_Timeout
    deadline = now + timeout
    last_error = ''

    while time.monotonic() < deadline:
        response = _invoke(client, 'ping-connection', connection=connection)

        if response['is_ok']:
            return

        last_error = response['error']
        time.sleep(ModuleCtx.Propagation_Poll_Interval)

    msg = f'Connection {connection} could not be pinged within {timeout}s, last error: {last_error}'
    raise Exception(msg)

# ################################################################################################################################

def _send(client:'AdminClient', event:'anydict', connection:'str'=FabricCtx.Events_Outgoing_Name) -> 'None':
    """ Sends one event through the outgoing connection.
    """
    response = _invoke(client, 'send', connection=connection, event=event)

    if not response['is_ok']:
        error = response['error']
        raise Exception(f'Connection {connection} rejected the event: {error}')

# ################################################################################################################################

def _wait_until_received(client:'AdminClient', marker:'str') -> 'anydict':
    """ Waits for the alert with this marker to come back through the alerts channel into the receiver service.
    """
    now = time.monotonic()
    timeout = ModuleCtx.Delivery_Timeout
    deadline = now + timeout

    while time.monotonic() < deadline:
        response = _invoke(client, 'get-received')

        for received in response['received']:
            if received['item_id'] == marker:
                return received

        time.sleep(ModuleCtx.Delivery_Poll_Interval)

    msg = f'Marker {marker} did not come back through a channel within {timeout}s'
    raise Exception(msg)

# ################################################################################################################################

def _query(client:'AdminClient', state:'anydict', query:'str', database:'str'='') -> 'anydict':
    """ Runs a KQL query against the eventhouse through the Fabric connection.
    """
    out = _invoke(client, 'query',
        connection=ModuleCtx.Connection_Name,
        workspace_id=state['workspace_id'],
        eventhouse_id=state['eventhouse_id'],
        database=database,
        query=query)

    return out

# ################################################################################################################################

def _wait_until_ingested(client:'AdminClient', state:'anydict', marker:'str') -> 'anydict':
    """ Waits for the event carrying the marker to be readable from the eventhouse and returns its row.
    """
    now = time.monotonic()
    timeout = ModuleCtx.Ingestion_Timeout
    deadline = now + timeout

    query = f'{FabricCtx.Events_Table} | where admission_id == "{marker}"'

    while time.monotonic() < deadline:

        # No database is named - the eventhouse's default one is resolved by the connection
        response = _query(client, state, query)

        if response['error']:
            raise Exception(f'Query against {FabricCtx.Eventhouse_Name} failed: {response["error"]}')

        rows = response['rows']
        if rows:
            out = rows[0]
            return out

        time.sleep(ModuleCtx.Ingestion_Poll_Interval)

    raise Exception(f'Event {marker} did not reach table {FabricCtx.Events_Table} within {timeout}s')

# ################################################################################################################################

def _now() -> 'str':
    """ The current moment, as the eventhouse's datetime column expects it.
    """
    now = datetime.now(timezone.utc)

    out = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def events_client(fabric_live:'FabricLiveEnvironment', deployed_client:'AdminClient') -> 'AdminClient':
    """ Imports the events objects with the alerts channel routed to the receiver service, waits for the connection.
    """
    lines = events_objects(fabric_live.fabric.state, alerts_service=ModuleCtx.Receiver_Service)
    yaml = '\n'.join(lines)
    _ = fabric_live.zato.import_yaml('fabric_live_events.yaml', yaml)

    _wait_until_pingable(deployed_client)

    return deployed_client

# ################################################################################################################################
# ################################################################################################################################

def test_admission_event_reaches_the_eventhouse(
    fabric_live:'FabricLiveEnvironment',
    events_client:'AdminClient',
    ) -> 'None':
    """ An admission event sent through the outgoing connection ends up in the Events table.
    """
    marker = 'ADM-TEST-' + CryptoManager.generate_hex_string()

    event = {
        'event_type': 'admission',
        'location': 'Riverside',
        'occurred_at': _now(),
        'admission_id': marker,
    }

    _send(events_client, event)

    row = _wait_until_ingested(events_client, fabric_live.fabric.state, marker)

    assert row['event_type'] == 'admission'
    assert row['location'] == 'Riverside'

# ################################################################################################################################

def test_query_events_with_database(
    fabric_live:'FabricLiveEnvironment',
    events_client:'AdminClient',
    ) -> 'None':
    """ A query names the KQL database explicitly and gets its rows back.
    """
    state = fabric_live.fabric.state
    query = f'{FabricCtx.Events_Table} | count'

    response = _query(events_client, state, query, database=state['kql_database_name'])

    assert response['error'] == ''

    rows = response['rows']
    assert len(rows) == 1
    assert 'Count' in rows[0]

# ################################################################################################################################

def test_query_events_bad_query(
    fabric_live:'FabricLiveEnvironment',
    events_client:'AdminClient',
    ) -> 'None':
    """ A query against a table that does not exist is reported as a KQL error.
    """
    response = _query(events_client, fabric_live.fabric.state, 'NoSuchTable | count')

    assert response['rows'] == []
    assert 'Fabric KQL error' in response['error']

# ################################################################################################################################

def test_stock_alert_comes_back_through_the_channel(events_client:'AdminClient') -> 'None':
    """ A stock event below the reorder level is filtered by the eventstream into the alerts channel.
    """
    marker = 'ITM-TEST-' + CryptoManager.generate_hex_string()

    _ = _invoke(events_client, 'clear-received')

    event = {
        'event_type': FabricCtx.Alert_Event_Type,
        'location': 'Oak Hill',
        'occurred_at': _now(),
        'item_id': marker,
        'quantity': 12,
        'reorder_level': 40,
    }

    _send(events_client, event)
    alert = _wait_until_received(events_client, marker)

    # The receiver read these from self.request.input, so the channel delivered the event as parsed JSON.
    assert alert['location'] == 'Oak Hill'
    assert alert['quantity'] == 12
    assert alert['reorder_level'] == 40


# ################################################################################################################################

_plain_yaml = """
security:
  - name: {events_key_name}
    type: basic_auth
    username: {username}
    password: {events_password}
    realm: zato

  - name: {alerts_key_name}
    type: basic_auth
    username: {username}
    password: {alerts_password}
    realm: zato

outgoing_kafka:
  - name: {outgoing_name}
    address: {events_address}
    topic: {events_topic}
    security: {events_key_name}
    sasl_mechanism: PLAIN
    ssl: true

channel_kafka:
  - name: {channel_name}
    address: {alerts_address}
    topic: {alerts_topic}
    group_id: {group_id}
    service: {service}
    security: {alerts_key_name}
    sasl_mechanism: PLAIN
    ssl: true
"""

def test_plain_round_trip(
    fabric_live:'FabricLiveEnvironment',
    events_client:'AdminClient',
    ) -> 'None':
    """ A stock alert sent under SASL PLAIN with the eventstream's keys comes back through a PLAIN channel.
    """
    state = fabric_live.fabric.state
    suffix = CryptoManager.generate_hex_string()

    events_key_name = f'test.fabric.events.plain.events-key.{suffix}'
    alerts_key_name = f'test.fabric.events.plain.alerts-key.{suffix}'
    outgoing_name = f'test.fabric.events.plain.outgoing.{suffix}'
    channel_name = f'test.fabric.events.plain.channel.{suffix}'

    # The source and the destination are separate event hubs, each with keys of its own. The destination's
    # consumer group is taken by the OAUTHBEARER channel, so this one reads under $Default, which every
    # event hub has, and $$ stands for a literal $ in enmasse.
    yaml = _plain_yaml.format(
        events_key_name=events_key_name,
        alerts_key_name=alerts_key_name,
        username=FabricCtx.Plain_Username,
        events_password=state['events_connection_string'],
        alerts_password=state['alerts_connection_string'],
        outgoing_name=outgoing_name,
        events_address=f'{state["events_namespace"]}:{FabricCtx.Kafka_Port}',
        events_topic=state['events_topic'],
        channel_name=channel_name,
        alerts_address=f'{state["alerts_namespace"]}:{FabricCtx.Kafka_Port}',
        alerts_topic=state['alerts_topic'],
        group_id='$$Default',
        service=ModuleCtx.Receiver_Service,
    )

    _ = fabric_live.zato.import_yaml(f'fabric_live_plain_{suffix}.yaml', yaml)
    _wait_until_pingable(events_client, outgoing_name)

    marker = 'ITEM-PLAIN-' + suffix

    event = {
        'event_type': FabricCtx.Alert_Event_Type,
        'item_id': marker,
        'location': 'Oak Hill',
        'quantity': 12,
        'reorder_level': 40,
        'occurred_at': _now(),
    }

    _send(events_client, event, outgoing_name)
    alert = _wait_until_received(events_client, marker)

    assert alert['location'] == 'Oak Hill'

# ################################################################################################################################
# ################################################################################################################################
